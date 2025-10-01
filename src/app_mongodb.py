import streamlit as st
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

from services.mongodb_service import MongoDBService
from services.gemini_service import GeminiService

# Page configuration
st.set_page_config(
    page_title="Notification Summarizer (MongoDB)",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def get_mongodb_service():
    return MongoDBService()

@st.cache_resource
def get_gemini_service():
    return GeminiService()

def main():
    st.title("📋 Notification Summarizer (MongoDB)")
    st.markdown("**Step 1:** Select a country → **Step 2:** Choose a notification → **Step 3:** View/Generate summary")
    
    # Initialize services
    mongodb_service = get_mongodb_service()
    gemini_service = get_gemini_service()
    
    # Check MongoDB connection
    if not mongodb_service.is_connected():
        st.error("❌ MongoDB connection failed. Please check your MongoDB setup.")
        st.info("Make sure MongoDB is running and accessible.")
        return
    
    # Sidebar for country selection
    st.sidebar.header("Configuration")
    country = st.sidebar.selectbox(
        "Select Country",
        ["India", "USA"],
        help="Choose the country for notification data"
    )
    
    # Show database statistics
    stats = mongodb_service.get_collection_stats(country)
    if stats:
        st.sidebar.metric("Total Notifications", stats.get('total_notifications', 0))
        st.sidebar.metric("With Summaries", stats.get('with_summaries', 0))
        st.sidebar.metric("Without Summaries", stats.get('without_summaries', 0))
    
    # Check if Gemini is available
    if not gemini_service.is_available():
        st.sidebar.warning("⚠️ Gemini AI not available. Summaries cannot be generated.")
    
    # Load dropdown options
    try:
        options = mongodb_service.get_dropdown_options(country)
        
        if not options:
            st.warning("No notifications found for the selected country.")
            # Debug information
            with st.expander("🔍 Debug Information"):
                st.write(f"Country: {country}")
                st.write(f"MongoDB connected: {mongodb_service.is_connected()}")
                stats = mongodb_service.get_collection_stats(country)
                st.write(f"Collection stats: {stats}")
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
                notification = mongodb_service.get_notification_by_id(country, selected_id)
                
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
                                    # Save summary to MongoDB
                                    success = mongodb_service.save_summary(country, selected_id, summary)
                                    
                                    if success:
                                        # Update notification object
                                        notification.summary = summary
                                        
                                        st.success("✅ Summary generated and saved successfully!")
                                        st.write(summary)
                                        
                                        # Refresh the page to show updated data
                                        st.rerun()
                                    else:
                                        st.error("Failed to save summary to database.")
                                else:
                                    st.error("❌ Failed to generate summary. Please try again.")
                    else:
                        st.warning("⚠️ Gemini AI service is not available. Cannot generate summary.")
            else:
                st.info("👆 Please select a notification from the dropdown to view its summary.")
        
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.write("Please check if MongoDB is running and accessible.")

if __name__ == "__main__":
    main()