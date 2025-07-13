# Medical Assistant 🏥

A comprehensive medical assistant chatbot powered by Google's Gemini AI with Supabase backend for persistent chat history and user profiles.

## Features

- 💬 **Interactive Chat Interface**: Clean Streamlit-based chat interface
- 🧠 **Memory & Context**: Remembers previous conversations for better context
- 👤 **User Profiles**: Maintain personal health information for personalized responses
- 📊 **Health Tracking**: Track health metrics and get personalized recommendations
- 🔒 **Secure Storage**: Encrypted data storage with Supabase
- ⚡ **Real-time Responses**: Powered by Google's Gemini AI model
- 📱 **Responsive Design**: Simple, clean, and professional interface
- 🚨 **Emergency Detection**: Automatic detection of emergency keywords

## Installation

1. **Clone or download the project**
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root with:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_KEY=your_supabase_anon_key_here
   ```

## Setup Instructions

### 1. Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

### 2. Set up Supabase
1. Go to [Supabase](https://supabase.com/)
2. Create a new project
3. Go to Settings > API
4. Copy the URL and anon key to your `.env` file

### 3. Create Database Tables
Run these SQL commands in your Supabase SQL editor:

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  health_info JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Chat history table
CREATE TABLE chat_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  message TEXT NOT NULL,
  response TEXT NOT NULL,
  message_type TEXT DEFAULT 'medical_query',
  timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_timestamp ON chat_history(timestamp);
```

## Usage

### Run the Application
```bash
python central.py
```

Or alternatively:
```bash
streamlit run streamlit_app.py
```

The application will be available at `http://localhost:8501`

### Using the Medical Assistant

1. **Setup Profile**: First time users need to create a profile with basic information
2. **Chat Interface**: Ask health-related questions and get AI-powered responses
3. **Profile Management**: Update health information for personalized responses
4. **Health Summary**: View your health metrics and chat history
5. **Settings**: Manage your account and privacy settings

## Project Structure

```
Medical Assistant/
├── central.py                          # Main entry point
├── streamlit_app.py                    # Streamlit frontend
├── requirements.txt                    # Python dependencies
├── .env                               # Environment variables
├── .streamlit/
│   └── config.toml                    # Streamlit configuration
└── src/
    ├── __init__.py
    ├── config.py                      # Configuration management
    ├── services/
    │   ├── __init__.py
    │   ├── gemini_service.py          # AI service
    │   └── medical_assistant_service.py # Main service
    ├── database/
    │   ├── __init__.py
    │   └── supabase_manager.py        # Database operations
    └── utils/
        ├── __init__.py
        └── helpers.py                 # Utility functions
```

## Features Details

### Chat Interface
- Real-time chat with medical AI assistant
- Emergency keyword detection
- Quick suggestion buttons
- Chat history persistence
- Clear and intuitive interface

### Health Profile
- Personal information storage
- Health metrics tracking (BMI calculation)
- Medical conditions and medications
- Family history and lifestyle info
- Secure data encryption

### AI Assistant
- Powered by Google's Gemini Pro model
- Context-aware responses using chat history
- Personalized recommendations based on health profile
- Emergency situation detection
- Medical disclaimers and safety warnings

## Security & Privacy

- All data is encrypted and stored securely
- No data sharing with third parties
- User can delete their data at any time
- HIPAA-compliant data handling practices
- Emergency detection and appropriate responses

## Important Disclaimer

⚠️ **This application is for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with healthcare professionals for medical concerns.**

## Support

For issues or questions, please check the console output for detailed error messages. Common issues:

1. **Missing API Keys**: Ensure all environment variables are set correctly
2. **Database Connection**: Verify Supabase credentials and table creation
3. **Package Installation**: Run `pip install -r requirements.txt`

## License

This project is for educational and informational purposes only.
