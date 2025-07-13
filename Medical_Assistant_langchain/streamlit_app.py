import streamlit as st
import uuid
import sys
import os
from datetime import datetime

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.langchain_service import MedicalChatService
from config import Config

def initialize_app():
    """Initialize the application"""
    try:
        # Validate configuration
        Config.validate_config()
        
        # Initialize session state
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        
        if 'chat_service' not in st.session_state:
            st.session_state.chat_service = MedicalChatService()
        
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            # Load existing chat history
            load_chat_history()
        
        return True
        
    except Exception as e:
        st.error(f"Failed to initialize application: {e}")
        st.error("Please check your configuration and try again.")
        return False

def load_chat_history():
    """Load existing chat history from database"""
    try:
        chat_service = st.session_state.chat_service
        history = chat_service.db.get_chat_history(st.session_state.session_id, 20)
        
        st.session_state.chat_history = [
            (chat['message'], chat['response']) 
            for chat in history
        ]
    except Exception as e:
        print(f"Error loading chat history: {e}")

def main():
    """Main application function"""
    st.set_page_config(
        page_title="Medical Assistant Chatbot",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize app
    if not initialize_app():
        st.stop()
    
    # Header
    st.title("🏥 Medical Assistant Chatbot")
    st.markdown("Ask me anything about your health, symptoms, medications, or medical concerns.")
    
    # Sidebar
    with st.sidebar:
        st.header("🩺 Medical Assistant")
        st.markdown("---")
        
        # Quick actions
        st.subheader("Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🆘 First Aid"):
                st.session_state.quick_message = "I need first aid advice for an emergency situation."
        
        with col2:
            if st.button("💊 Get Medication"):
                st.session_state.quick_message = "I need specific medication recommendations for my condition. Please provide exact drug names and dosages."
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("🤒 Symptoms"):
                st.session_state.quick_message = "I'm experiencing symptoms and need a complete medical consultation with medication recommendations."
        
        with col4:
            if st.button("🏥 Prescription"):
                st.session_state.quick_message = "I need a detailed prescription for my medical condition with specific medications and dosages."
        
        # Additional medication-focused buttons
        st.subheader("Medication Services")
        
        col5, col6 = st.columns(2)
        
        with col5:
            if st.button("📋 Drug Info"):
                st.session_state.quick_message = "I need detailed information about a specific medication including dosage, side effects, and interactions."
        
        with col6:
            if st.button("⚠️ Drug Interactions"):
                st.session_state.quick_message = "I need to check for drug interactions between my medications."
        
        col7, col8 = st.columns(2)
        
        with col7:
            if st.button("🔄 Alternative Meds"):
                st.session_state.quick_message = "I need alternative medication options for my condition due to side effects or allergies."
        
        with col8:
            if st.button("📊 Dosage Adjustment"):
                st.session_state.quick_message = "I need help adjusting my medication dosage based on my response to treatment."
        
        st.markdown("---")
        
        # Chat history management
        st.subheader("Chat Management")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_service.clear_chat_history(st.session_state.session_id)
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
            st.rerun()
        
        if st.button("🔄 New Session"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.chat_history = []
            st.success("New session started!")
            st.rerun()
        
        st.markdown("---")
        
        # Medical disclaimer
        st.subheader("⚠️ Medical Disclaimer")
        st.caption("""
        This AI medical assistant provides comprehensive clinical guidance including specific medication recommendations.
        
        **Enhanced Capabilities:**
        - Specific medication names and dosages
        - Clinical diagnosis and treatment protocols
        - Drug interaction analysis
        - Emergency medical guidance
        
        **Important Notes:**
        - Information provided is for educational purposes
        - Individual responses to medications may vary
        - Professional medical consultation recommended for personalized care
        - Call emergency services for life-threatening situations
        - Verify medication information with healthcare providers
        """)
        
        st.markdown("---")
        st.caption("Powered by Google Gemini & LangChain | Advanced Medical AI")
    
    # Main chat interface
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        if st.session_state.chat_history:
            for i, (user_msg, assistant_msg) in enumerate(st.session_state.chat_history):
                with st.chat_message("user"):
                    st.write(user_msg)
                with st.chat_message("assistant"):
                    st.write(assistant_msg)
        else:
            # Welcome message
            with st.chat_message("assistant"):
                st.write("""
                👋 **Welcome to your Advanced Medical Assistant!**
                
                I'm an AI medical assistant with comprehensive clinical knowledge. I can help you with:
                
                💊 **MEDICATION SERVICES:**
                - Specific medication recommendations with exact dosages
                - Drug interaction analysis and contraindication checks
                - Alternative medication options and generic equivalents
                - Dosage adjustments and tapering schedules
                - Side effect management and monitoring protocols
                
                🩺 **MEDICAL CONSULTATIONS:**
                - Comprehensive symptom analysis and diagnosis
                - Detailed treatment plans and protocols
                - Emergency medical guidance and first aid
                - Preventive care and health maintenance
                - Follow-up care recommendations
                
                📋 **CLINICAL EXPERTISE:**
                - Differential diagnosis with probability assessments
                - Laboratory test recommendations
                - Specialist referral guidance
                - Medical procedure explanations
                
                **HOW TO GET SPECIFIC MEDICATIONS:**
                Simply describe your symptoms or condition, and I'll provide:
                - Exact medication names (generic and brand)
                - Precise dosages and administration instructions
                - Treatment duration and monitoring requirements
                - Alternative options if needed
                
                **Example:** "I have a headache and fever" → I'll recommend specific medications with exact dosages
                
                **How can I help you today?**
                
                *Note: While I provide comprehensive medical guidance including specific medication recommendations, this information is for educational purposes. Individual responses may vary, and professional medical consultation is recommended for personalized care.*
                """)
    
    # Handle quick action messages
    if hasattr(st.session_state, 'quick_message'):
        prompt = st.session_state.quick_message
        delattr(st.session_state, 'quick_message')
        
        # Process the quick message
        process_user_message(prompt)
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask me about your health..."):
        process_user_message(prompt)

def process_user_message(prompt):
    """Process user message and generate response"""
    # Add user message to chat history
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.chat_service.chat(
                    prompt,
                    st.session_state.session_id
                )
                st.write(response)
                
                # Add to session chat history
                st.session_state.chat_history.append((prompt, response))
                
            except Exception as e:
                error_message = f"I apologize, but I'm experiencing technical difficulties. Please try again later. Error: {str(e)}"
                st.error(error_message)
                st.session_state.chat_history.append((prompt, error_message))

if __name__ == "__main__":
    main()
