from typing import Dict, List, Any
import uuid
from datetime import datetime
import sys
import os

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.dirname(current_dir)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.gemini_service import GeminiService
from database.supabase_manager import SupabaseManager
from utils.helpers import validate_email, sanitize_input, validate_health_info

class MedicalAssistantService:
    """Main service class for the medical assistant"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
        self.db_manager = SupabaseManager()
    
    def create_user_session(self, name: str, email: str, 
                           health_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new user session"""
        try:
            # Validate input
            if not validate_email(email):
                return {"error": "Invalid email address"}
            
            # Generate user ID
            user_id = str(uuid.uuid4())
            
            # Create user profile
            user_profile = self.db_manager.create_user_profile(
                user_id=user_id,
                name=sanitize_input(name),
                email=email,
                health_info=health_info or {}
            )
            
            if user_profile:
                return {
                    "success": True,
                    "user_id": user_id,
                    "message": "User session created successfully"
                }
            else:
                return {"error": "Failed to create user session"}
                
        except Exception as e:
            return {"error": f"Error creating user session: {str(e)}"}
    
    def get_user_session(self, user_id: str) -> Dict[str, Any]:
        """Get user session information"""
        try:
            user_profile = self.db_manager.get_user_profile(user_id)
            if user_profile:
                return {
                    "success": True,
                    "user_profile": user_profile
                }
            else:
                return {"error": "User session not found"}
        except Exception as e:
            return {"error": f"Error fetching user session: {str(e)}"}
    
    def update_health_info(self, user_id: str, health_info: Dict[str, Any]) -> Dict[str, Any]:
        """Update user's health information"""
        try:
            # Validate health info
            validated_info = validate_health_info(health_info)
            
            success = self.db_manager.update_user_health_info(user_id, validated_info)
            if success:
                return {
                    "success": True,
                    "message": "Health information updated successfully"
                }
            else:
                return {"error": "Failed to update health information"}
        except Exception as e:
            return {"error": f"Error updating health info: {str(e)}"}
    
    def process_medical_query(self, user_id: str, query: str) -> Dict[str, Any]:
        """Process a medical query from the user"""
        try:
            # Sanitize input
            query = sanitize_input(query)
            
            # Get user profile and health info
            user_profile = self.db_manager.get_user_profile(user_id)
            if not user_profile:
                return {"error": "User session not found"}
            
            # Get chat history for context
            chat_history = self.db_manager.get_chat_history(user_id, limit=5)
            
            # Generate response using Gemini
            response = self.gemini_service.process_medical_query(
                user_query=query,
                health_info=user_profile.get('health_info', {}),
                chat_history=chat_history
            )
            
            # Save the conversation
            chat_record = self.db_manager.save_chat_message(
                user_id=user_id,
                message=query,
                response=response,
                message_type='medical_query'
            )
            
            return {
                "success": True,
                "response": response,
                "chat_id": chat_record.get('id') if chat_record else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error processing medical query: {str(e)}"}
    
    def analyze_symptoms(self, user_id: str, symptoms: str) -> Dict[str, Any]:
        """Analyze symptoms for the user"""
        try:
            # Get user profile
            user_profile = self.db_manager.get_user_profile(user_id)
            if not user_profile:
                return {"error": "User session not found"}
            
            # Generate symptom analysis
            analysis = self.gemini_service.analyze_symptoms(
                symptoms=symptoms,
                health_info=user_profile.get('health_info', {})
            )
            
            # Save the conversation
            chat_record = self.db_manager.save_chat_message(
                user_id=user_id,
                message=f"Symptom analysis: {symptoms}",
                response=analysis,
                message_type='symptom_analysis'
            )
            
            return {
                "success": True,
                "analysis": analysis,
                "chat_id": chat_record.get('id') if chat_record else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error analyzing symptoms: {str(e)}"}
    
    def get_health_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get personalized health recommendations"""
        try:
            # Get user profile
            user_profile = self.db_manager.get_user_profile(user_id)
            if not user_profile:
                return {"error": "User session not found"}
            
            # Generate recommendations
            recommendations = self.gemini_service.generate_health_recommendations(
                health_info=user_profile.get('health_info', {})
            )
            
            # Save the conversation
            chat_record = self.db_manager.save_chat_message(
                user_id=user_id,
                message="Health recommendations request",
                response=recommendations,
                message_type='health_recommendations'
            )
            
            return {
                "success": True,
                "recommendations": recommendations,
                "chat_id": chat_record.get('id') if chat_record else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error generating recommendations: {str(e)}"}
    
    def get_chat_history(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get user's chat history"""
        try:
            history = self.db_manager.get_chat_history(user_id, limit)
            return {
                "success": True,
                "history": history
            }
        except Exception as e:
            return {"error": f"Error fetching chat history: {str(e)}"}
    
    def clear_chat_history(self, user_id: str) -> Dict[str, Any]:
        """Clear user's chat history"""
        try:
            success = self.db_manager.delete_chat_history(user_id)
            if success:
                return {
                    "success": True,
                    "message": "Chat history cleared successfully"
                }
            else:
                return {"error": "Failed to clear chat history"}
        except Exception as e:
            return {"error": f"Error clearing chat history: {str(e)}"}
