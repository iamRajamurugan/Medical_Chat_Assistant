import google.generativeai as genai
from typing import Dict, List, Any
import json
from datetime import datetime
import sys
import os

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.dirname(current_dir)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from config import Config

class GeminiService:
    """Service for interacting with Google's Gemini AI model"""
    
    def __init__(self):
        self.model = None
        self.initialize_model()
    
    def initialize_model(self):
        """Initialize the Gemini model"""
        try:
            # Validate configuration first
            Config.validate_config()
            
            if not Config.GEMINI_API_KEY:
                raise ValueError("Gemini API key must be provided")
            
            # Check for placeholder values
            if (Config.GEMINI_API_KEY.startswith('your_') or 
                Config.GEMINI_API_KEY == 'your_gemini_api_key_here'):
                raise ValueError("Please replace placeholder value in .env file with actual Gemini API key")
            
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            print("Gemini model initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Gemini model: {e}")
            raise
    
    def create_medical_prompt(self, user_query: str, health_info: Dict[str, Any] = None, 
                            chat_history: List[Dict[str, Any]] = None) -> str:
        """Create a comprehensive medical prompt with context"""
        
        base_prompt = """You are an advanced medical assistant AI with extensive clinical knowledge equivalent to a licensed physician. Your capabilities include:

🏥 **MEDICAL EXPERTISE:**
- Comprehensive symptom analysis and differential diagnosis
- Specific medication recommendations with dosages
- Treatment protocols and clinical guidelines
- Drug interaction analysis and contraindication assessment
- Emergency medical protocols and first aid guidance

💊 **MEDICATION PRESCRIBING GUIDELINES:**
- Provide specific medication names (generic and brand)
- Include precise dosages based on condition severity
- Specify administration routes and frequency
- Detail treatment duration and tapering schedules
- Mention common side effects and monitoring requirements
- Suggest alternative medications for contraindications

🩺 **DIAGNOSTIC APPROACH:**
- Analyze symptoms systematically
- Consider patient history and risk factors
- Recommend appropriate diagnostic tests
- Provide likelihood assessments for conditions
- Identify red flags requiring immediate attention

📋 **TREATMENT PROTOCOLS:**
- First-line medication therapy
- Alternative treatments if first-line fails
- Combination therapy when appropriate
- Lifestyle modifications and non-pharmacological interventions
- Follow-up care and monitoring schedules

**RESPONSE STRUCTURE:**
1. **Clinical Assessment:** [Condition diagnosis with confidence level]
2. **Recommended Medications:** [Specific drugs with exact dosages]
3. **Treatment Plan:** [Comprehensive management approach]
4. **Monitoring:** [Side effects and efficacy monitoring]
5. **Follow-up:** [When to reassess or seek specialist care]

⚠️ **MEDICAL DISCLAIMER:**
While I provide comprehensive medical guidance including specific medication recommendations, this information is for educational purposes. Individual responses may vary, and professional medical consultation is recommended for personalized care.

**BE SPECIFIC AND CLINICAL:** Always provide exact medication names, dosages, and administration instructions as a physician would."""
        
        # Add health information context
        if health_info:
            health_context = f"\n\n**PATIENT HEALTH PROFILE:**\n"
            for key, value in health_info.items():
                if value:
                    health_context += f"- {key.replace('_', ' ').title()}: {value}\n"
            base_prompt += health_context
        
        # Add chat history context
        if chat_history:
            history_context = f"\n\n**PREVIOUS CONSULTATION HISTORY:**\n"
            for chat in chat_history[-5:]:  # Last 5 messages for context
                history_context += f"Patient: {chat.get('message', '')}\n"
                history_context += f"Doctor: {chat.get('response', '')}\n\n"
            base_prompt += history_context
        
        # Add current query
        base_prompt += f"\n\n**CURRENT MEDICAL CONSULTATION:**\nPatient Query: {user_query}\n\n"
        base_prompt += "**PROVIDE COMPREHENSIVE MEDICAL RESPONSE WITH SPECIFIC MEDICATION RECOMMENDATIONS:**"
        
        return base_prompt
    
    def generate_response(self, prompt: str) -> str:
        """Generate a response using Gemini"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again later or consult with a healthcare professional."
    
    def process_medical_query(self, user_query: str, health_info: Dict[str, Any] = None, 
                             chat_history: List[Dict[str, Any]] = None) -> str:
        """Process a medical query with full context"""
        prompt = self.create_medical_prompt(user_query, health_info, chat_history)
        return self.generate_response(prompt)
    
    def analyze_symptoms(self, symptoms: str, health_info: Dict[str, Any] = None) -> str:
        """Analyze symptoms and provide guidance"""
        prompt = f"""You are a medical assistant. A user has described the following symptoms: {symptoms}
        
        Health Information: {health_info or 'Not provided'}
        
        Please provide:
        1. Possible general explanations for these symptoms
        2. When to seek immediate medical attention
        3. General self-care recommendations
        4. Important questions to ask a healthcare provider
        
        Remember to emphasize the importance of professional medical consultation."""
        
        return self.generate_response(prompt)
    
    def generate_health_recommendations(self, health_info: Dict[str, Any]) -> str:
        """Generate personalized health recommendations"""
        prompt = f"""Based on the following health information, provide general wellness recommendations:
        
        Health Information: {json.dumps(health_info, indent=2)}
        
        Please provide:
        1. General lifestyle recommendations
        2. Preventive care suggestions
        3. Areas to discuss with healthcare providers
        4. General wellness tips
        
        Keep recommendations general and emphasize consulting healthcare professionals."""
        
        return self.generate_response(prompt)
