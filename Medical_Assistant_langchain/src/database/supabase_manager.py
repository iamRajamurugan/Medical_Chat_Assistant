from supabase import create_client, Client
from typing import Optional, Dict, List, Any
import json
from datetime import datetime
import uuid
import sys
import os

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.dirname(current_dir)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from config import Config

class SupabaseManager:
    """Manage Supabase database connections and operations for medical chatbot"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.connect()
    
    def connect(self):
        """Initialize Supabase client"""
        try:
            # Validate configuration first
            Config.validate_config()
            
            if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
                raise ValueError("Supabase URL and Key must be provided")
            
            # Check for placeholder values
            if (Config.SUPABASE_URL.startswith('your_') or 
                Config.SUPABASE_KEY.startswith('your_') or
                Config.SUPABASE_URL == 'your_supabase_url_here' or
                Config.SUPABASE_KEY == 'your_supabase_anon_key_here'):
                raise ValueError("Please replace placeholder values in .env file with actual Supabase credentials")
            
            self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            print("Successfully connected to Supabase")
        except ValueError as e:
            print(f"Configuration error: {e}")
            raise
        except Exception as e:
            print(f"Failed to connect to Supabase: {e}")
            raise
    
    def save_chat_message(self, session_id: str, message: str, 
                         response: str, message_type: str = 'medical_query') -> Dict[str, Any]:
        """Save a chat message and response"""
        try:
            chat_data = {
                'id': str(uuid.uuid4()),
                'session_id': session_id,
                'message': message,
                'response': response,
                'message_type': message_type,
                'timestamp': datetime.now().isoformat()
            }
            
            result = self.client.table('chat_conversations').insert(chat_data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error saving chat message: {e}")
            return None
    
    def get_chat_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get chat history for a session"""
        try:
            result = self.client.table('chat_conversations').select('*').eq('session_id', session_id).order('timestamp', desc=False).limit(limit).execute()
            return result.data or []
        except Exception as e:
            print(f"Error fetching chat history: {e}")
            return []
    
    def delete_chat_history(self, session_id: str) -> bool:
        """Delete chat history for a session"""
        try:
            result = self.client.table('chat_conversations').delete().eq('session_id', session_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting chat history: {e}")
            return False

    def create_chat_table(self) -> bool:
        """Create the chat conversations table if it doesn't exist"""
        try:
            # Note: This is handled by Supabase migration/SQL
            # The table should be created manually in Supabase dashboard
            return True
        except Exception as e:
            print(f"Error creating chat table: {e}")
            return False
