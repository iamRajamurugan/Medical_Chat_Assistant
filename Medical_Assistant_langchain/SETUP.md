# Medical Assistant Setup Guide

## Quick Start

Your Medical Assistant is almost ready! You just need to add your API keys.

## Step 1: Get Your API Keys

### Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

### Supabase Credentials
1. Go to [Supabase](https://supabase.com)
2. Sign up/Sign in
3. Create a new project
4. Go to Settings > API
5. Copy:
   - Project URL (something like: `https://xxxxx.supabase.co`)
   - Anon public key (starts with `eyJ...`)

## Step 2: Update Your .env File

Open the `.env` file in your project folder and replace the placeholder values:

```env
# Gemini API Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_actual_supabase_anon_key_here
```

## Step 3: Run the Application

```bash
# Activate virtual environment
.\medical_env\Scripts\Activate.ps1

# Run the application
python central.py
```

The application will be available at `http://localhost:8501`

## Features

- 🏥 Medical chat assistant
- 📋 Health profile management
- 💬 Chat history
- 📊 Health summaries
- 🚨 Emergency detection

## Need Help?

- Gemini API is free with usage limits
- Supabase has a generous free tier
- Both services require account creation but are free to start

---

## Database Tables (Auto-created)

The app will automatically create these tables in your Supabase database:

- `user_profiles` - User information and health data
- `chat_sessions` - Chat conversation history
- `health_summaries` - Generated health insights
