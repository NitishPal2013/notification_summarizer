from pymongo import MongoClient
from typing import Optional, List, Dict
import os
from datetime import datetime
from models.data_models import Notification
from dotenv import load_dotenv

load_dotenv()

class MongoDBService:
    """Service class for MongoDB operations"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB"""
        try:
            mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            database_name = os.getenv('MONGODB_DATABASE', 'notification_summarizer')
            
            self.client = MongoClient(mongodb_uri)
            self.db = self.client[database_name]
            
            # Create collections if they don't exist
            self._ensure_collections()
            
        except Exception as e:
            print(f"Failed to connect to MongoDB: {str(e)}")
            self.client = None
            self.db = None
    
    def _ensure_collections(self):
        """Ensure required collections exist with indexes"""
        if not self.is_connected():
            return
        
        try:
            # Create indexes for better performance
            self.db.india_notifications.create_index("id", unique=True)
            self.db.usa_notifications.create_index("id", unique=True)
            self.db.india_notifications.create_index("date")
            self.db.usa_notifications.create_index("date")
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")
    
    def is_connected(self) -> bool:
        """Check if MongoDB connection is active"""
        try:
            # Test the connection by pinging the server
            if self.client is None:
                return False
            self.client.admin.command('ping')
            return True
        except Exception:
            return False
    
    def get_notification_by_id(self, country: str, notification_id: str) -> Optional[Notification]:
        """Get notification by ID from MongoDB"""
        if not self.is_connected():
            return None
        
        collection_name = f"{country.lower()}_notifications"
        collection = self.db[collection_name]
        
        try:
            document = collection.find_one({"id": notification_id})
            if document:
                return Notification(
                    id=str(document['id']),
                    date=str(document['date']),
                    title=str(document['title']),
                    url=str(document['url']),
                    text=str(document['text']),
                    summary=document.get('summary'),
                    created_at=document.get('created_at'),
                    updated_at=document.get('updated_at')
                )
        except Exception as e:
            print(f"Error retrieving notification: {str(e)}")
        
        return None
    
    def get_dropdown_options(self, country: str, limit: int = 1000) -> List[Dict]:
        """Get dropdown options for UI"""
        if not self.is_connected():
            return []
        
        collection_name = f"{country.lower()}_notifications"
        collection = self.db[collection_name]
        
        try:
            cursor = collection.find(
                {},
                {"id": 1, "title": 1, "date": 1, "summary": 1}
            ).limit(limit)
            
            options = []
            for doc in cursor:
                options.append({
                    'id': str(doc['id']),
                    'title': str(doc['title']),
                    'date': str(doc['date']),
                    'has_summary': bool(doc.get('summary') and str(doc['summary']).strip())
                })
            
            return options
            
        except Exception as e:
            print(f"Error retrieving dropdown options: {str(e)}")
            return []
    
    def save_summary(self, country: str, notification_id: str, summary: str) -> bool:
        """Save summary to MongoDB"""
        if not self.is_connected():
            return False
        
        collection_name = f"{country.lower()}_notifications"
        collection = self.db[collection_name]
        
        try:
            result = collection.update_one(
                {"id": notification_id},
                {
                    "$set": {
                        "summary": summary,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error saving summary: {str(e)}")
            return False
    
    def insert_notification(self, country: str, notification: Notification) -> bool:
        """Insert a new notification into MongoDB"""
        if not self.is_connected():
            return False
        
        collection_name = f"{country.lower()}_notifications"
        collection = self.db[collection_name]
        
        try:
            document = {
                "id": notification.id,
                "date": notification.date,
                "title": notification.title,
                "url": notification.url,
                "text": notification.text,
                "summary": notification.summary,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = collection.insert_one(document)
            return result.inserted_id is not None
        except Exception as e:
            print(f"Error inserting notification: {str(e)}")
            return False
    
    def get_collection_stats(self, country: str) -> Dict:
        """Get collection statistics"""
        if not self.is_connected():
            return {}
        
        collection_name = f"{country.lower()}_notifications"
        collection = self.db[collection_name]
        
        try:
            total_count = collection.count_documents({})
            with_summary = collection.count_documents({"summary": {"$exists": True, "$ne": None, "$ne": ""}})
            
            return {
                "total_notifications": total_count,
                "with_summaries": with_summary,
                "without_summaries": total_count - with_summary
            }
        except Exception as e:
            print(f"Error getting collection stats: {str(e)}")
            return {}
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
