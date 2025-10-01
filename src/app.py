import streamlit as st
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

from models.data_models import DataLoader
from services.gemini_service import GeminiService

# Page configuration
st.set_page_config(
    page_title="Notification Summarizer",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def get_data_loader():
    return DataLoader()

@st.cache_resource
def get_gemini_service():
    return GeminiService()

def main():
    st.title("📋 Notification Summarizer")
    st.markdown("**Step 1:** Select a country → **Step 2:** Choose a notification → **Step 3:** View/Generate summary")
    
    # Initialize services
    data_loader = get_data_loader()
    gemini_service = get_gemini_service()
    
    # Sidebar for country selection
    st.sidebar.header("Configuration")
    country = st.sidebar.selectbox(
        "Select Country",
        ["India", "USA"],
        help="Choose the country for notification data"
    )
    
    # Check if Gemini is available
    if not gemini_service.is_available():
        st.sidebar.warning("⚠️ Gemini AI not available. Summaries cannot be generated.")
    
    # Load dropdown options
    try:
        options = data_loader.get_dropdown_options(country)
        
        if not options:
            st.warning("No notifications found for the selected country.")
            # Debug information
            with st.expander("🔍 Debug Information"):
                st.write(f"Country: {country}")
                st.write(f"Data directory: {data_loader.data_dir}")
                if country.lower() == 'india':
                    data = data_loader.load_india_data()
                    st.write(f"India data shape: {data.shape}")
                    st.write(f"India data columns: {list(data.columns)}")
                else:
                    data = data_loader.load_usa_data()
                    st.write(f"USA data shape: {data.shape}")
                    st.write(f"USA data columns: {list(data.columns)}")
            return
        
        # Create dropdown with "Select notification" as first option
        option_labels = ["🔍 Select a notification..."]
        option_values = [None]
        
        for option in options:
            title_preview = option['title'][:60] + "..." if len(option['title']) > 60 else option['title']
            label = f"{title_preview} | {option['date']}"
            if option['has_summary']:
                label += " ✅"
            option_labels.append(label)
            option_values.append(option['id'])
        
        # Main content area
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.header(f"{country} Notifications")
            
            selected_index = st.selectbox(
                "Choose Notification",
                range(len(option_labels)),
                format_func=lambda x: option_labels[x],
                help="Select a notification to view its summary"
            )
            
            # Get selected notification
            selected_id = option_values[selected_index]
            notification = None
            
            if selected_id is not None:
                notification = data_loader.get_notification_by_id(country, selected_id)
                
                if notification:
                    st.subheader("📄 Notification Details")
                    st.write(f"**Title:** {notification.title}")
                    st.write(f"**Date:** {notification.date}")
                    st.write(f"**URL:** {notification.url}")
                    
                    # Show text preview
                    with st.expander("📖 View Full Text"):
                        st.text(notification.text[:1500] + "..." if len(notification.text) > 1500 else notification.text)
            else:
                st.info("👆 Please select a notification from the dropdown above to view details.")
        
        with col2:
            st.header("📝 Summary")
            
            if selected_id is not None and notification:
                # Check if summary exists
                if notification.summary and str(notification.summary).strip():
                    st.success("✅ Summary Available")
                    st.write(notification.summary)
                else:
                    st.info("📝 No summary available")
                    
                    # Generate summary button
                    if gemini_service.is_available():
                        if st.button("🤖 Generate Summary", type="primary", use_container_width=True):
                            with st.spinner("🔄 Generating summary using Gemini AI..."):
                                summary = gemini_service.generate_summary(
                                    notification.text, 
                                    notification.title
                                )
                                
                                if summary:
                                    # Save summary to CSV
                                    data_loader.save_summary(country, selected_id, summary)
                                    
                                    st.success("✅ Summary generated successfully!")
                                    st.write(summary)
                                    
                                    # Refresh the page to show updated data
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to generate summary. Please try again.")
                    else:
                        st.warning("⚠️ Gemini AI service is not available. Cannot generate summary.")
            else:
                st.info("👆 Please select a notification from the dropdown to view its summary.")
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.write("Please check if the CSV files exist and are properly formatted.")

if __name__ == "__main__":
    main()
