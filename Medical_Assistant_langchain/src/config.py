import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # Application Configuration
    MAX_CHAT_HISTORY = 10
    DEFAULT_TEMPERATURE = 0.7
    
    @staticmethod
    def validate_config():
        """Validate that all required configuration is present"""
        required_vars = {
            'GEMINI_API_KEY': 'Google Gemini API key',
            'SUPABASE_URL': 'Supabase project URL', 
            'SUPABASE_KEY': 'Supabase anon key'
        }
        missing_vars = []
        invalid_vars = []
        
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value:
                missing_vars.append(f"{var} ({description})")
            elif (value.startswith('your_') or 
                  value == 'your_gemini_api_key_here' or 
                  value == 'your_supabase_url_here' or 
                  value == 'your_supabase_anon_key_here' or
                  value == 'YOUR_GEMINI_API_KEY' or
                  value == 'YOUR_SUPABASE_URL' or
                  value == 'YOUR_SUPABASE_KEY'):
                invalid_vars.append(f"{var} ({description})")
        
        if missing_vars or invalid_vars:
            error_msg = "Configuration Error:\n"
            if missing_vars:
                error_msg += "Missing environment variables:\n"
                for var in missing_vars:
                    error_msg += f"  - {var}\n"
            if invalid_vars:
                error_msg += "Invalid placeholder values found:\n"
                for var in invalid_vars:
                    error_msg += f"  - {var}\n"
            error_msg += "\nPlease update your .env file with actual values."
            raise ValueError(error_msg)
        
        return True
