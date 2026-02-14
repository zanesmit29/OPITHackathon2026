"""
Streamlit Application for Alzheimer's Assistant

This is a RAG-powered chat application for Alzheimer's caregiving information.

Run in Demo Mode (no backend needed):
    pip install streamlit
    streamlit run frontend/streamlit_app.py

Run in Production Mode (with backend):
    1. Set up backend dependencies in backend/requirements.txt
    2. Toggle "Demo Mode" OFF in the sidebar
    3. Chat will use real RAG agent

Expected Behavior:
- Demo Mode: Shows mock responses with simulated delays
- Production Mode: Integrates with backend/agent.py
- Patient info is optional and can be skipped
- All features work standalone without backend setup
"""

import sys
import os
import time
from typing import Dict, Optional, List
from datetime import datetime

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

import streamlit as st

# Configure page
st.set_page_config(
    page_title="Alzheimer's Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .demo-banner {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin-bottom: 1rem;
        border: 2px solid #ffc107;
    }
    .patient-info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .disclaimer {
        background-color: #f8d7da;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
        margin-top: 1rem;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# Mock responses for demo mode
DEMO_RESPONSES: List[str] = [
    "This is a demo response about Alzheimer's treatment. In real mode, this would use the RAG agent to provide evidence-based information about treatment options, including medications like cholinesterase inhibitors and memantine, as well as non-pharmacological approaches such as cognitive stimulation therapy. Always consult with healthcare professionals for personalized treatment recommendations.",
    
    "This is a demo response about Alzheimer's symptoms. The condition typically progresses through stages, starting with mild memory loss and confusion, advancing to difficulty with language and problem-solving, and eventually affecting basic daily activities. Early symptoms often include forgetting recent conversations or events, difficulty finding words, and challenges with complex tasks.",
    
    "This is a demo response about caregiving strategies. Effective caregiving involves creating a structured routine, maintaining a safe environment, using clear and simple communication, and providing activities that match the person's abilities. It's also crucial for caregivers to take care of their own physical and mental health through respite care and support groups.",
    
    "This is a demo response about nutrition and Alzheimer's. A balanced diet rich in fruits, vegetables, whole grains, and omega-3 fatty acids may support brain health. The Mediterranean diet has shown promise in research. Ensure adequate hydration and consider consultation with a dietitian for personalized meal planning, especially as the disease progresses.",
    
    "This is a demo response about behavioral management. Common behavioral changes in Alzheimer's include agitation, wandering, sundowning, and aggression. Effective strategies include identifying triggers, maintaining calm environments, redirecting attention, and establishing consistent routines. Music therapy, pet therapy, and reminiscence activities can also be beneficial."
]


def initialize_session_state() -> None:
    """Initialize session state variables."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'patient_data' not in st.session_state:
        st.session_state.patient_data = {
            'name': '',
            'age_years': None,
            'weight_kg': None,
            'height_cm': None,
            'diagnosis_timeframe': ''
        }
    
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    
    if 'show_patient_form' not in st.session_state:
        st.session_state.show_patient_form = True
    
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = True
    
    if 'query_count' not in st.session_state:
        st.session_state.query_count = 0
    
    if 'session_start' not in st.session_state:
        st.session_state.session_start = datetime.now()
    
    if 'backend_available' not in st.session_state:
        st.session_state.backend_available = None


def check_backend_availability() -> bool:
    """Check if backend agent is available."""
    if st.session_state.backend_available is not None:
        return st.session_state.backend_available
    
    try:
        # Try to import the agent module
        from agent import simple_groq_agent, simple_hf_agent
        st.session_state.backend_available = True
        return True
    except Exception as e:
        st.session_state.backend_available = False
        return False


def get_demo_response(query: str, patient_context: Optional[Dict] = None) -> str:
    """Generate a mock response for demo mode."""
    # Add artificial delay to simulate backend processing
    time.sleep(1.5)
    
    # Select response based on query keywords
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['treatment', 'medication', 'therapy']):
        response = DEMO_RESPONSES[0]
    elif any(word in query_lower for word in ['symptom', 'sign', 'stage']):
        response = DEMO_RESPONSES[1]
    elif any(word in query_lower for word in ['caregiv', 'care', 'help', 'support']):
        response = DEMO_RESPONSES[2]
    elif any(word in query_lower for word in ['diet', 'nutrition', 'food', 'eat']):
        response = DEMO_RESPONSES[3]
    elif any(word in query_lower for word in ['behavior', 'agitation', 'wandering', 'aggression']):
        response = DEMO_RESPONSES[4]
    else:
        # Default response
        response = DEMO_RESPONSES[0]
    
    # Add patient context if available
    if patient_context and patient_context.get('name'):
        response = f"For {patient_context['name']}, " + response.lower()
    
    return response


def get_agent_response(query: str, patient_context: Optional[Dict] = None) -> str:
    """Get response from backend agent."""
    try:
        # Import agent functions
        from agent import simple_groq_agent, simple_hf_agent
        
        # Augment query with patient context if available
        if patient_context and any(patient_context.values()):
            context_str = "Patient context: "
            if patient_context.get('name'):
                context_str += f"Name: {patient_context['name']}, "
            if patient_context.get('age_years'):
                context_str += f"Age: {patient_context['age_years']} years, "
            if patient_context.get('diagnosis_timeframe'):
                context_str += f"Diagnosis: {patient_context['diagnosis_timeframe']}, "
            
            augmented_query = f"{context_str}\n\nQuestion: {query}"
        else:
            augmented_query = query
        
        # Call the agent (try Groq first, fallback to HF)
        try:
            response = simple_groq_agent(augmented_query)
        except:
            response = simple_hf_agent(augmented_query)
        
        return response
    
    except Exception as e:
        # Log error and provide user-friendly message
        print(f"Error calling backend agent: {str(e)}")
        raise Exception(f"Backend agent error: {str(e)}")


def render_patient_form() -> None:
    """Render patient information form."""
    st.markdown("<h2 style='text-align: center;'>Welcome to Alzheimer's Assistant 🧠</h2>", unsafe_allow_html=True)
    
    st.info("💡 Patient information is optional. You can skip directly to chat or provide details for personalized responses.")
    
    # Skip to Chat button at the top
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⏭️ Skip to Chat", use_container_width=True, type="primary"):
            st.session_state.show_patient_form = False
            st.rerun()
    
    st.markdown("---")
    
    # Patient information form
    st.subheader("Patient Information (Optional)")
    
    with st.form("patient_form"):
        name = st.text_input("Patient Name", placeholder="e.g., John Doe")
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age (years)", min_value=0, max_value=120, value=None, step=1)
            weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=None, step=0.1)
        
        with col2:
            height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, value=None, step=0.1)
            diagnosis = st.text_input("Time Since Diagnosis", placeholder="e.g., 2 years")
        
        submitted = st.form_submit_button("Start Chat", use_container_width=True, type="primary")
        
        if submitted:
            # Store patient data in session state
            st.session_state.patient_data = {
                'name': name,
                'age_years': age,
                'weight_kg': weight,
                'height_cm': height,
                'diagnosis_timeframe': diagnosis
            }
            
            # Mark as authenticated if any patient info provided
            if any([name, age, weight, height, diagnosis]):
                st.session_state.is_authenticated = True
            
            st.session_state.show_patient_form = False
            st.rerun()


def render_sidebar() -> None:
    """Render sidebar with patient info and controls."""
    with st.sidebar:
        st.header("Settings & Information")
        
        # Demo Mode Toggle
        st.markdown("### Mode Selection")
        demo_mode = st.toggle(
            "Demo Mode 🎭",
            value=st.session_state.demo_mode,
            help="Enable demo mode to test UI with mock responses (no backend required)"
        )
        
        if demo_mode != st.session_state.demo_mode:
            st.session_state.demo_mode = demo_mode
            st.rerun()
        
        if st.session_state.demo_mode:
            st.info("🎭 Demo Mode Active - Using mock data")
        else:
            # Check backend availability
            if check_backend_availability():
                st.success("✅ Production Mode - Backend connected")
            else:
                st.warning("⚠️ Backend unavailable - Falling back to Demo Mode")
                st.session_state.demo_mode = True
        
        st.markdown("---")
        
        # Patient Information Display
        if st.session_state.is_authenticated and any(st.session_state.patient_data.values()):
            st.markdown("### Patient Information")
            st.markdown('<div class="patient-info-box">', unsafe_allow_html=True)
            
            patient = st.session_state.patient_data
            if patient.get('name'):
                st.write(f"**Name:** {patient['name']}")
            if patient.get('age_years'):
                st.write(f"**Age:** {patient['age_years']} years")
            if patient.get('weight_kg'):
                st.write(f"**Weight:** {patient['weight_kg']} kg")
            if patient.get('height_cm'):
                st.write(f"**Height:** {patient['height_cm']} cm")
            if patient.get('diagnosis_timeframe'):
                st.write(f"**Diagnosis:** {patient['diagnosis_timeframe']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
        
        # Session Statistics
        st.markdown("### Session Statistics")
        st.write(f"**Queries:** {st.session_state.query_count}")
        st.write(f"**Session Start:** {st.session_state.session_start.strftime('%H:%M:%S')}")
        
        st.markdown("---")
        
        # Control Buttons
        st.markdown("### Actions")
        
        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.query_count = 0
            st.rerun()
        
        if st.button("✏️ Update Patient Info", use_container_width=True):
            st.session_state.show_patient_form = True
            st.rerun()
        
        if st.session_state.is_authenticated:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.is_authenticated = False
                st.session_state.patient_data = {
                    'name': '',
                    'age_years': None,
                    'weight_kg': None,
                    'height_cm': None,
                    'diagnosis_timeframe': ''
                }
                st.session_state.chat_history = []
                st.session_state.query_count = 0
                st.session_state.show_patient_form = True
                st.rerun()


def render_chat_interface() -> None:
    """Render main chat interface."""
    # Demo mode banner
    if st.session_state.demo_mode:
        st.markdown(
            '<div class="demo-banner">🎭 <strong>Demo Mode</strong> - Using mock data for demonstration</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("<h1 class='main-header'>Alzheimer's Assistant Chat 💬</h1>", unsafe_allow_html=True)
    
    # Display disclaimer
    st.markdown(
        '<div class="disclaimer"><strong>⚠️ Disclaimer:</strong> This application is for informational purposes only and does not constitute medical advice. Always consult with qualified healthcare professionals for medical decisions.</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Display chat history
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    else:
        st.info("👋 Welcome! Ask me anything about Alzheimer's disease, caregiving strategies, symptoms, or treatment options.")
    
    # Chat input
    user_query = st.chat_input("Ask a question about Alzheimer's...")
    
    if user_query:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.session_state.query_count += 1
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_query)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Get response based on mode
                    if st.session_state.demo_mode or not check_backend_availability():
                        response = get_demo_response(user_query, st.session_state.patient_data)
                    else:
                        try:
                            response = get_agent_response(user_query, st.session_state.patient_data)
                        except Exception as e:
                            # Fallback to demo mode on error
                            st.warning("⚠️ Backend error - Using demo response")
                            response = get_demo_response(user_query, st.session_state.patient_data)
                    
                    st.write(response)
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                except Exception as e:
                    error_message = f"An error occurred: {str(e)}"
                    st.error(error_message)
                    
                    # Offer retry button
                    if st.button("🔄 Retry", key="retry_button"):
                        st.rerun()


def main() -> None:
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()
    
    # Render appropriate view
    if st.session_state.show_patient_form:
        render_patient_form()
    else:
        # Render sidebar
        render_sidebar()
        
        # Render chat interface
        render_chat_interface()


if __name__ == "__main__":
    main()
