"""
Migration script to transfer data from CSV to MongoDB
"""
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent))

from services.mongodb_service import MongoDBService
from models.data_models import Notification

class DataMigration:
    """Handle migration from CSV to MongoDB"""
    
    def __init__(self):
        self.mongodb_service = MongoDBService()
    
    def migrate_india_data(self, csv_path: str) -> bool:
        """Migrate India data from CSV to MongoDB"""
        if not self.mongodb_service.is_connected():
            print("MongoDB not connected. Cannot migrate data.")
            return False
        
        try:
            # Load CSV data
            df = pd.read_csv(csv_path)
            
            # Check if summary column already exists
            if 'summary' not in df.columns:
                df.columns = ['index', 'id', 'date', 'title', 'url', 'text']
                df['summary'] = None
            else:
                # If summary column exists, use the existing columns
                pass
            
            print(f"Migrating {len(df)} India notifications...")
            
            success_count = 0
            for _, row in df.iterrows():
                notification = Notification(
                    id=str(row['id']),
                    date=str(row['date']),
                    title=str(row['title']),
                    url=str(row['url']),
                    text=str(row['text']),
                    summary=row['summary'] if pd.notna(row['summary']) else None
                )
                
                if self.mongodb_service.insert_notification('india', notification):
                    success_count += 1
                
                if success_count % 1000 == 0:
                    print(f"Migrated {success_count} notifications...")
            
            print(f"Successfully migrated {success_count} India notifications")
            return True
            
        except Exception as e:
            print(f"Error migrating India data: {str(e)}")
            return False
    
    def migrate_usa_data(self, csv_path: str) -> bool:
        """Migrate USA data from CSV to MongoDB"""
        if not self.mongodb_service.is_connected():
            print("MongoDB not connected. Cannot migrate data.")
            return False
        
        try:
            # Load CSV data
            df = pd.read_csv(csv_path)
            
            # Check if summary column already exists
            if 'summary' not in df.columns:
                df.columns = ['index', 'date', 'title', 'url', 'text']
                df['id'] = df['index'].astype(str)
                df['summary'] = None
            else:
                # If summary column exists, use the existing columns
                df['id'] = df['index'].astype(str)
            
            print(f"Migrating {len(df)} USA notifications...")
            
            success_count = 0
            for _, row in df.iterrows():
                notification = Notification(
                    id=str(row['id']),
                    date=str(row['date']),
                    title=str(row['title']),
                    url=str(row['url']),
                    text=str(row['text']),
                    summary=row['summary'] if pd.notna(row['summary']) else None
                )
                
                if self.mongodb_service.insert_notification('usa', notification):
                    success_count += 1
                
                if success_count % 1000 == 0:
                    print(f"Migrated {success_count} notifications...")
            
            print(f"Successfully migrated {success_count} USA notifications")
            return True
            
        except Exception as e:
            print(f"Error migrating USA data: {str(e)}")
            return False
    
    def migrate_all_data(self, data_dir: str = ".") -> bool:
        """Migrate all data from CSV files to MongoDB"""
        print("Starting data migration from CSV to MongoDB...")
        
        # Check MongoDB connection
        if not self.mongodb_service.is_connected():
            print("MongoDB connection failed. Please check your MongoDB setup.")
            return False
        
        # Migrate India data
        india_success = self.migrate_india_data(f"{data_dir}/IND_data.csv")
        
        # Migrate USA data
        usa_success = self.migrate_usa_data(f"{data_dir}/USA_data.csv")
        
        if india_success and usa_success:
            print("✅ All data migrated successfully!")
            
            # Print statistics
            india_stats = self.mongodb_service.get_collection_stats('india')
            usa_stats = self.mongodb_service.get_collection_stats('usa')
            
            print(f"\nIndia notifications: {india_stats.get('total_notifications', 0)}")
            print(f"USA notifications: {usa_stats.get('total_notifications', 0)}")
            
            return True
        else:
            print("❌ Migration failed for some data")
            return False
    
    def verify_migration(self) -> bool:
        """Verify that migration was successful"""
        if not self.mongodb_service.is_connected():
            print("MongoDB not connected. Cannot verify migration.")
            return False
        
        print("Verifying migration...")
        
        # Check India data
        india_options = self.mongodb_service.get_dropdown_options('india', limit=5)
        print(f"India notifications in DB: {len(india_options)} (showing first 5)")
        
        # Check USA data
        usa_options = self.mongodb_service.get_dropdown_options('usa', limit=5)
        print(f"USA notifications in DB: {len(usa_options)} (showing first 5)")
        
        return len(india_options) > 0 and len(usa_options) > 0

def main():
    """Main migration function"""
    migration = DataMigration()
    
    print("=== CSV to MongoDB Migration ===")
    print("This will migrate all CSV data to MongoDB.")
    print("Make sure MongoDB is running and accessible.")
    
    # Run migration
    success = migration.migrate_all_data()
    
    if success:
        # Verify migration
        migration.verify_migration()
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed. Please check the logs above.")

if __name__ == "__main__":
    main()
