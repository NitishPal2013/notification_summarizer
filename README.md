# Notification Summarizer

A web application for summarizing regulatory notifications from India and USA using AI-powered summarization.

## Features

- **Country Selection**: Choose between India and USA notification data
- **Interactive Dropdown**: Browse notifications by title and date
- **AI-Powered Summaries**: Generate summaries using Google's Gemini 2.0 Flash model
- **Summary Caching**: Store generated summaries for future use
- **Responsive UI**: Built with Streamlit for easy deployment

## Setup

### Prerequisites

- Python 3.8+
- Google AI API key

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your Google API key
```

3. Run the application:
```bash
streamlit run src/app.py
```

## Usage

1. **Select Country**: Use the sidebar to choose between India and USA
2. **Browse Notifications**: Use the dropdown to select a notification
3. **View Summary**: If a summary exists, it will be displayed. Otherwise, click "Generate Summary"
4. **Generate New Summaries**: Use the "Generate Summary" button to create AI-powered summaries

## Data Structure

### India Data (IND_data.csv)
- id: Unique identifier
- date: Notification date
- title: Notification title
- url: Source URL
- text: Full text content
- summary: Generated summary (added automatically)

### USA Data (USA_data.csv)
- id: Unique identifier (auto-generated)
- date: Notification date
- title: Notification title
- url: Source URL
- text: Full text content
- summary: Generated summary (added automatically)

## Architecture

### Phase 1: CSV-Based (Current)
- Data stored in CSV files
- Summaries cached in CSV
- Real-time summary generation

### Phase 2: MongoDB Integration (Planned)
- Data migrated to MongoDB
- Improved performance and scalability
- Advanced querying capabilities

## API Keys

You need a Google AI API key to use the summarization feature:

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GOOGLE_API_KEY`

## Development

The project structure:
```
src/
├── models/
│   └── data_models.py      # Data models and CSV handling
├── services/
│   └── gemini_service.py   # Gemini AI integration
└── app.py                  # Main Streamlit application
```
