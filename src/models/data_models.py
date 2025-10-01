from dataclasses import dataclass
from typing import Optional, List
import pandas as pd
from datetime import datetime

@dataclass
class Notification:
    """Data model for notification entries"""
    id: str
    date: str
    title: str
    url: str
    text: str
    summary: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class CountryData:
    """Data model for country-specific notification data"""
    country: str
    notifications: List[Notification]
    total_count: int

class DataLoader:
    """Utility class for loading and managing CSV data"""
    
    def __init__(self, data_dir: str = "./"):
        self.data_dir = data_dir
        self.india_data = None
        self.usa_data = None
    
    def load_india_data(self) -> pd.DataFrame:
        """Load India notification data from CSV"""
        if self.india_data is None:
            try:
                self.india_data = pd.read_csv(f"{self.data_dir}/IND_data.csv")
                # Standardize column names
                self.india_data.columns = ['index', 'id', 'date', 'title', 'url', 'text']
                # Add summary column if it doesn't exist
                if 'summary' not in self.india_data.columns:
                    self.india_data['summary'] = None
                # Clean the data
                self.india_data = self.india_data.fillna('')
            except Exception as e:
                print(f"Error loading India data: {e}")
                return pd.DataFrame()
        return self.india_data
    
    def load_usa_data(self) -> pd.DataFrame:
        """Load USA notification data from CSV"""
        if self.usa_data is None:
            try:
                self.usa_data = pd.read_csv(f"{self.data_dir}/USA_data.csv")
                # Standardize column names
                self.usa_data.columns = ['index', 'date', 'title', 'url', 'text']
                # Add id column (use index as id)
                self.usa_data['id'] = self.usa_data['index'].astype(str)
                # Add summary column if it doesn't exist
                if 'summary' not in self.usa_data.columns:
                    self.usa_data['summary'] = None
                # Clean the data
                self.usa_data = self.usa_data.fillna('')
            except Exception as e:
                print(f"Error loading USA data: {e}")
                return pd.DataFrame()
        return self.usa_data
    
    def get_notification_by_id(self, country: str, notification_id: str) -> Optional[Notification]:
        """Get specific notification by ID"""
        if country.lower() == 'india':
            data = self.load_india_data()
        elif country.lower() == 'usa':
            data = self.load_usa_data()
        else:
            return None
        
        # Convert id column to string for comparison
        data['id'] = data['id'].astype(str)
        row = data[data['id'] == str(notification_id)]
        
        if row.empty:
            return None
        
        row = row.iloc[0]
        return Notification(
            id=str(row['id']),
            date=str(row['date']),
            title=str(row['title']),
            url=str(row['url']),
            text=str(row['text']),
            summary=row['summary'] if pd.notna(row['summary']) else None
        )
    
    def save_summary(self, country: str, notification_id: str, summary: str):
        """Save generated summary back to CSV"""
        if country.lower() == 'india':
            data = self.load_india_data()
            data.loc[data['id'] == notification_id, 'summary'] = summary
            data.to_csv(f"{self.data_dir}/IND_data.csv", index=False)
        elif country.lower() == 'usa':
            data = self.load_usa_data()
            data.loc[data['id'] == notification_id, 'summary'] = summary
            data.to_csv(f"{self.data_dir}/USA_data.csv", index=False)
    
    def get_dropdown_options(self, country: str) -> List[dict]:
        """Get formatted dropdown options for UI"""
        if country.lower() == 'india':
            data = self.load_india_data()
        elif country.lower() == 'usa':
            data = self.load_usa_data()
        else:
            return []
        
        # Limit to first 100 entries for better performance
        data_subset = data.head(100)
        
        options = []
        for _, row in data_subset.iterrows():
            # Clean the data
            title = str(row['title']).strip()
            date = str(row['date']).strip()
            summary = row['summary'] if pd.notna(row['summary']) else None
            has_summary = summary is not None and str(summary).strip() != ''
            
            options.append({
                'id': str(row['id']),
                'title': title,
                'date': date,
                'has_summary': has_summary
            })
        
        return options
