import re
import html
from typing import Any, Dict, List

def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(input_text: str) -> str:
    """Sanitize user input to prevent XSS and other issues"""
    if not isinstance(input_text, str):
        return str(input_text)
    
    # Remove HTML tags and escape special characters
    sanitized = html.escape(input_text.strip())
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', sanitized)
    
    return sanitized

def format_chat_message(message: str, max_length: int = 1000) -> str:
    """Format chat message for display"""
    if len(message) > max_length:
        return message[:max_length] + "..."
    return message

def validate_health_info(health_info: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean health information"""
    valid_fields = [
        'age', 'gender', 'weight', 'height', 'allergies', 'medications',
        'medical_conditions', 'family_history', 'lifestyle', 'symptoms'
    ]
    
    cleaned_info = {}
    for field in valid_fields:
        if field in health_info:
            value = health_info[field]
            if isinstance(value, str):
                cleaned_info[field] = sanitize_input(value)
            elif isinstance(value, (int, float)):
                cleaned_info[field] = value
            elif isinstance(value, list):
                cleaned_info[field] = [sanitize_input(str(item)) for item in value]
    
    return cleaned_info

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp

def create_session_id() -> str:
    """Create a unique session ID"""
    import uuid
    return str(uuid.uuid4())

def parse_symptoms(symptoms_text: str) -> List[str]:
    """Parse symptoms from text input"""
    # Split by common delimiters
    symptoms = re.split(r'[,;\n]+', symptoms_text)
    
    # Clean and filter symptoms
    parsed_symptoms = []
    for symptom in symptoms:
        clean_symptom = sanitize_input(symptom.strip())
        if clean_symptom and len(clean_symptom) > 2:
            parsed_symptoms.append(clean_symptom)
    
    return parsed_symptoms

def is_emergency_keywords(message: str) -> bool:
    """Check if message contains emergency keywords"""
    emergency_keywords = [
        'emergency', 'urgent', 'severe pain', 'chest pain', 'difficulty breathing',
        'unconscious', 'bleeding', 'overdose', 'suicide', 'heart attack',
        'stroke', 'seizure', 'allergic reaction', 'choking'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in emergency_keywords)

def calculate_bmi(weight: float, height: float) -> float:
    """Calculate BMI from weight (kg) and height (cm)"""
    try:
        height_m = height / 100  # Convert cm to meters
        bmi = weight / (height_m ** 2)
        return round(bmi, 1)
    except:
        return 0.0

def get_bmi_category(bmi: float) -> str:
    """Get BMI category based on BMI value"""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"
