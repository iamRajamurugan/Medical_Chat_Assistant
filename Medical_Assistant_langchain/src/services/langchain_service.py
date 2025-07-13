from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from typing import List, Dict, Any, Optional
import sys
import os

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.dirname(current_dir)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from config import Config
from database.supabase_manager import SupabaseManager

class MedicalChatService:
    """LangChain-powered medical chatbot service"""
    
    def __init__(self):
        self.llm = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.db = SupabaseManager()
        self.setup_llm()
        self.setup_chain()
    
    def setup_llm(self):
        """Initialize Google Gemini LLM through LangChain"""
        try:
            Config.validate_config()
            if not Config.GEMINI_API_KEY:
                raise ValueError("Gemini API key is required")
            
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=Config.GEMINI_API_KEY,
                temperature=0.7,
                max_tokens=1000
            )
            print("LangChain Gemini LLM initialized successfully")
        except Exception as e:
            print(f"Error initializing LLM: {e}")
            raise
    
    def setup_chain(self):
        """Setup the conversation chain with medical prompt"""
        self.medical_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an advanced medical assistant AI with extensive knowledge equivalent to a licensed physician. Your role is to provide comprehensive medical guidance including:

🏥 **PRIMARY CAPABILITIES:**
1. Diagnose conditions based on symptoms described
2. Recommend specific medications with dosages and administration
3. Provide detailed treatment plans and protocols
4. Suggest follow-up care and monitoring
5. Explain medical procedures and their necessity
6. Offer preventive care recommendations
7. Provide drug interaction warnings and contraindications

💊 **MEDICATION RECOMMENDATIONS:**
- Always provide specific medication names (both generic and brand names)
- Include typical dosages for adults (adjust for age/weight when mentioned)
- Specify administration routes (oral, topical, injection, etc.)
- Mention frequency and duration of treatment
- Include common side effects and warnings
- Suggest over-the-counter alternatives when appropriate

🩺 **DIAGNOSTIC APPROACH:**
- Analyze symptoms systematically
- Consider differential diagnoses
- Recommend appropriate tests or examinations
- Provide likelihood assessments for conditions
- Suggest red flags that require immediate attention

📋 **TREATMENT PROTOCOLS:**
- Offer first-line treatment options
- Provide alternative therapies if first-line fails
- Include lifestyle modifications
- Suggest when to follow up or seek specialist care

⚠️ **MEDICAL DISCLAIMERS:**
While I provide comprehensive medical guidance including medication recommendations, please note:
- This advice is for educational and informational purposes
- Individual responses to medications may vary
- Always verify dosages and contraindications with current medical literature
- Seek immediate medical attention for emergencies
- Consult healthcare professionals for personalized care

**RESPONSE FORMAT:**
Always structure responses as:
1. **Likely Condition(s):** [Diagnosis with confidence level]
2. **Recommended Medications:** [Specific drugs with dosages]
3. **Treatment Plan:** [Step-by-step approach]
4. **Monitoring:** [What to watch for]
5. **Follow-up:** [When to seek further care]

Be thorough, specific, and professional in your recommendations."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        self.chain = (
            RunnablePassthrough.assign(
                chat_history=lambda x: self.memory.chat_memory.messages
            )
            | self.medical_prompt
            | self.llm
            | StrOutputParser()
        )
    
    def chat(self, message: str, session_id: str) -> str:
        """Process a chat message and return response"""
        try:
            # Load chat history from database
            self.load_chat_history(session_id)
            
            # Generate response
            response = self.chain.invoke({"input": message})
            
            # Save to memory
            self.memory.chat_memory.add_user_message(message)
            self.memory.chat_memory.add_ai_message(response)
            
            # Save to database
            self.db.save_chat_message(
                session_id=session_id,
                message=message,
                response=response,
                message_type="medical_query"
            )
            
            return response
            
        except Exception as e:
            print(f"Error in chat processing: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again later or consult a healthcare professional for medical advice."
    
    def load_chat_history(self, session_id: str, limit: int = 10):
        """Load chat history from database into memory"""
        try:
            history = self.db.get_chat_history(session_id, limit)
            
            # Clear existing memory
            self.memory.clear()
            
            # Add messages to memory in chronological order
            for chat in history:
                self.memory.chat_memory.add_user_message(chat['message'])
                self.memory.chat_memory.add_ai_message(chat['response'])
                
        except Exception as e:
            print(f"Error loading chat history: {e}")
    
    def clear_chat_history(self, session_id: str):
        """Clear chat history for a session"""
        try:
            self.memory.clear()
            self.db.delete_chat_history(session_id)
            return True
        except Exception as e:
            print(f"Error clearing chat history: {e}")
            return False
    
    def get_medical_suggestion(self, symptoms: List[str]) -> str:
        """Get medical suggestions based on symptoms"""
        symptoms_text = ", ".join(symptoms)
        prompt = f"""**MEDICAL CONSULTATION REQUEST**

Patient presents with symptoms: {symptoms_text}

Please provide a comprehensive medical assessment:

1. **DIFFERENTIAL DIAGNOSIS:** List 3-5 most likely conditions with probability percentages
2. **RECOMMENDED MEDICATIONS:** Specific drugs with exact dosages, frequency, and duration
3. **TREATMENT PROTOCOL:** Step-by-step treatment approach
4. **DIAGNOSTIC TESTS:** Recommend specific tests if needed
5. **MONITORING INSTRUCTIONS:** What symptoms to watch for
6. **FOLLOW-UP TIMELINE:** When to reassess or seek further care
7. **RED FLAGS:** Warning signs requiring immediate medical attention

Format your response as a medical consultation note with specific medication recommendations."""
        
        return self.chat(prompt, "medical_consultation")
    
    def get_medication_info(self, medication_name: str) -> str:
        """Get comprehensive information about a medication"""
        prompt = f"""**MEDICATION CONSULTATION for: {medication_name}**

Please provide a comprehensive medication profile including:

1. **DRUG CLASSIFICATION:** Category and mechanism of action
2. **CLINICAL INDICATIONS:** All approved uses and off-label applications
3. **DOSAGE PROTOCOLS:**
   - Adult dosing (standard and maximum)
   - Pediatric dosing (if applicable)
   - Elderly dosing considerations
   - Renal/hepatic dose adjustments
4. **ADMINISTRATION DETAILS:**
   - Route of administration
   - Timing (with/without food)
   - Special instructions
5. **CONTRAINDICATIONS:** Absolute and relative contraindications
6. **DRUG INTERACTIONS:** Major interactions with other medications
7. **SIDE EFFECTS:** Common and serious adverse reactions
8. **MONITORING REQUIREMENTS:** Lab tests or clinical monitoring needed
9. **ALTERNATIVE MEDICATIONS:** Similar drugs if this one isn't suitable
10. **COST CONSIDERATIONS:** Generic alternatives and insurance coverage

Provide this information as a detailed medication monograph."""
        
        return self.chat(prompt, "medication_inquiry")
    
    def get_first_aid_advice(self, emergency_type: str) -> str:
        """Get comprehensive first aid and emergency medical advice"""
        prompt = f"""**EMERGENCY MEDICAL PROTOCOL for: {emergency_type}**

Provide comprehensive emergency management including:

1. **IMMEDIATE ACTIONS:** Step-by-step first aid measures
2. **EMERGENCY MEDICATIONS:** Specific drugs that might be needed
   - Epinephrine for allergic reactions
   - Aspirin for cardiac events
   - Albuterol for respiratory distress
   - Glucose for hypoglycemia
3. **ASSESSMENT PROTOCOL:** How to evaluate severity
4. **WHEN TO CALL 911:** Specific criteria for emergency services
5. **HOSPITAL PREPARATION:** What information to provide to EMS
6. **FOLLOW-UP MEDICATIONS:** Drugs likely to be prescribed post-emergency
7. **PREVENTION STRATEGIES:** How to prevent recurrence

Structure as an emergency medical protocol with specific medication recommendations."""
        
        return self.chat(prompt, "first_aid_inquiry")
    
    def get_comprehensive_medical_consultation(self, symptoms: str, age: int = None, 
                                             medical_history: str = None) -> str:
        """Get comprehensive medical consultation with detailed medication recommendations"""
        prompt = f"""**COMPREHENSIVE MEDICAL CONSULTATION**

Patient Information:
- Symptoms: {symptoms}
- Age: {age if age else "Not specified"}
- Medical History: {medical_history if medical_history else "Not provided"}

Please provide a COMPLETE medical consultation including:

1. **CHIEF COMPLAINT ANALYSIS:**
   - Primary symptoms assessment
   - Symptom severity and duration analysis
   - Associated symptoms to consider

2. **DIFFERENTIAL DIAGNOSIS:**
   - List 3-5 most likely conditions with probability percentages
   - Include ICD-10 codes if applicable
   - Rule out serious conditions

3. **RECOMMENDED MEDICATIONS (Primary Focus):**
   - **First-line therapy:** Specific drug names with exact dosages
   - **Alternative options:** If patient has contraindications
   - **Combination therapy:** When multiple drugs are needed
   - **Administration details:** Route, frequency, with/without food
   - **Duration:** How long to take each medication
   - **Tapering schedules:** For medications requiring gradual discontinuation

4. **SPECIFIC DRUG RECOMMENDATIONS:**
   - Generic name (Brand name)
   - Exact dosage: mg/kg or fixed dose
   - Frequency: BID, TID, QID, PRN
   - Duration: Days, weeks, or ongoing
   - Special instructions

5. **MONITORING PROTOCOL:**
   - Side effects to watch for
   - Lab tests required
   - When to reassess effectiveness

6. **FOLLOW-UP MEDICATION ADJUSTMENTS:**
   - Dose titration schedules
   - When to switch medications
   - Combination therapy protocols

7. **EMERGENCY MEDICATIONS:**
   - Rescue medications if applicable
   - When to seek immediate care

Provide this as a detailed medical consultation with emphasis on specific medication recommendations."""
        
        return self.chat(prompt, "comprehensive_consultation")
    
    def get_medication_prescription(self, condition: str, patient_age: int = None, 
                                  allergies: str = None, current_meds: str = None) -> str:
        """Get specific medication prescription for a condition"""
        prompt = f"""**MEDICATION PRESCRIPTION REQUEST**

Condition: {condition}
Patient Age: {patient_age if patient_age else "Adult"}
Known Allergies: {allergies if allergies else "None reported"}
Current Medications: {current_meds if current_meds else "None reported"}

Please provide a DETAILED MEDICATION PRESCRIPTION including:

1. **PRIMARY MEDICATION REGIMEN:**
   - Drug name (generic and brand)
   - Strength: mg, mcg, units
   - Dosage form: tablets, capsules, liquid, injection
   - Quantity: # of tablets/ml to dispense
   - Administration: exact timing and method
   - Duration: specific number of days/weeks

2. **DOSING SCHEDULE:**
   - Morning dose: exact time and amount
   - Afternoon dose: if applicable
   - Evening dose: if applicable
   - PRN (as needed) instructions

3. **ALTERNATIVE MEDICATIONS:**
   - Second-line options if first choice fails
   - Generic alternatives to reduce cost
   - Different drug classes for contraindications

4. **DRUG INTERACTION WARNINGS:**
   - Interactions with current medications
   - Foods/supplements to avoid
   - Alcohol restrictions

5. **MONITORING REQUIREMENTS:**
   - Lab tests needed before starting
   - Ongoing monitoring schedule
   - Signs of toxicity to watch for

6. **PRESCRIPTION REFILL INSTRUCTIONS:**
   - Number of refills allowed
   - When to schedule follow-up
   - Criteria for medication adjustment

Format as a complete prescription with all necessary details a physician would provide."""
        
        return self.chat(prompt, "medication_prescription")
