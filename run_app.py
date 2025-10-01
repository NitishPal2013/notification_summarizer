#!/usr/bin/env python3
"""
Main application runner
Choose between CSV-based or MongoDB-based implementation
"""
import streamlit as st
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    st.set_page_config(
        page_title="Notification Summarizer",
        page_icon="📋",
        layout="wide"
    )
    
    st.title("📋 Notification Summarizer")
    st.markdown("Choose your implementation:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Phase 1: CSV-Based")
        st.markdown("""
        ✅ **Ready to use!**
        - Data stored in CSV files
        - Real-time summary generation
        - Summary caching in CSV
        - Good for development and testing
        """)
        
        if st.button("🚀 Launch CSV Version", type="primary"):
            # Import and run CSV version
            from src.app import main as csv_main
            csv_main()
    
    with col2:
        st.header("Phase 2: MongoDB-Based")
        st.markdown("""
        ✅ **Ready to use!**
        - Data stored in MongoDB
        - Better performance and scalability
        - Advanced querying capabilities
        - Production-ready
        """)
        
        if st.button("🚀 Launch MongoDB Version"):
            # Import and run MongoDB version
            from src.app_mongodb import main as mongodb_main
            mongodb_main()
    
    st.markdown("---")
    st.markdown("### Setup Instructions")
    
    with st.expander("CSV Version Setup"):
        st.markdown("""
        1. Install dependencies: `pip install -r requirements.txt`
        2. Set up Google API key in `.env` file
        3. Run: `streamlit run src/app.py`
        """)
    
    with st.expander("MongoDB Version Setup"):
        st.markdown("""
        1. Install dependencies: `pip install -r requirements.txt`
        2. Set up MongoDB (local or cloud)
        3. Set up Google API key in `.env` file
        4. Run migration: `python src/utils/migration_script.py`
        5. Run: `streamlit run src/app_mongodb.py`
        """)

if __name__ == "__main__":
    main()
