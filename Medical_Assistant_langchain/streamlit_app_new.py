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
            if st.button("💊 Medication"):
                st.session_state.quick_message = "I need information about a medication."
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("🤒 Symptoms"):
                st.session_state.quick_message = "I'm experiencing some symptoms and need guidance."
        
        with col4:
            if st.button("🏥 When to See Doctor"):
                st.session_state.quick_message = "When should I see a doctor?"
        
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
        This chatbot provides general medical information for educational purposes only. 
        
        **Important:**
        - Not a substitute for professional medical advice
        - Always consult healthcare professionals for serious concerns
        - Call emergency services for life-threatening situations
        - Don't delay seeking medical care based on chatbot advice
        """)
        
        st.markdown("---")
        st.caption("Powered by Google Gemini & LangChain")
    
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
                👋 **Welcome to your Medical Assistant!**
                
                I'm here to help you with:
                - General health information and advice
                - Symptom guidance and when to seek care
                - Medication information and interactions
                - First aid and emergency guidance
                - Preventive care and wellness tips
                
                **How can I help you today?**
                
                *Remember: I provide general information only. For serious health concerns, always consult with healthcare professionals.*
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
