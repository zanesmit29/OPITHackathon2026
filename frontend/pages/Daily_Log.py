"""
Daily Activity Log Page - Starter Version
Track daily observations and activities for the patient.
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import streamlit as st
from frontend.utils.database import init_database, save_daily_log, get_daily_log

# Initialize database
init_database()

# Page config
st.set_page_config(
    page_title="Daily Activity Log",
    page_icon="📝",
    layout="wide"
)

# Title
st.title("📝 Daily Activity Log")
st.markdown("Track daily observations and activities.")

# Get patient name from session state
patient_name = st.session_state.get('patient_data', {}).get('name', 'Unknown')
if patient_name:
    st.info(f"👤 Logging for: **{patient_name}**")

st.markdown("---")

# Simple test form
st.header("Daily Log Entry")

with st.form("daily_log_form"):
    log_date = st.date_input("Date", value=date.today(), max_value=date.today())
    
    st.subheader("🍽️ Nutrition")
    col1, col2 = st.columns(2)
    with col1:
        meals_eaten = st.number_input("Meals Eaten", min_value=0, max_value=10, value=3)
    with col2:
        water_glasses = st.number_input("Glasses of Water", min_value=0, max_value=30, value=6)
    
    st.subheader("🚶 Behavioral Observations")
    col1, col2 = st.columns(2)
    with col1:
        wandering_incidents = st.number_input("Wandering Incidents", min_value=0, max_value=50, value=0)
    with col2:
        confusion_episodes = st.number_input("Confusion Episodes", min_value=0, max_value=50, value=0)
    
    st.subheader("💊 Health")
    col1, col2 = st.columns(2)
    with col1:
        hours_slept = st.number_input("Hours Slept", min_value=0.0, max_value=24.0, value=8.0, step=0.5)
    with col2:
        fell_today = st.checkbox("Fall Today?", value=False)
    
    st.subheader("📝 Notes")
    notes = st.text_area("Additional Notes", placeholder="Any observations, concerns, or highlights...")
    caregiver_name = st.text_input("Your Name", placeholder="Caregiver name")
    
    # Submit button
    submitted = st.form_submit_button("💾 Save Daily Log", type="primary", use_container_width=True)
    
    if submitted:
        # Prepare log data with all required fields
        log_data = {
            'log_date': log_date,
            'patient_name': patient_name,
            'meals_eaten': meals_eaten,
            'snacks_eaten': 0,  # Will add later
            'water_glasses': water_glasses,
            'wandering_incidents': wandering_incidents,
            'agitation_episodes': 0,  # Will add later
            'confusion_episodes': confusion_episodes,
            'hours_slept': hours_slept,
            'bathroom_accidents': 0,  # Will add later
            'fell_today': 1 if fell_today else 0,
            'medications_taken': 1,  # Default true
            'refused_medication': 0,  # Default false
            'mood_rating': 3,  # Will add later
            'social_engagement': 3,  # Will add later
            'physical_activity_minutes': 0,  # Will add later
            'cognitive_activities': 0,  # Will add later
            'notes': notes,
            'caregiver_name': caregiver_name
        }
        
        # Save to database
        success, message = save_daily_log(log_data)
        
        if success:
            st.success(message)
            st.balloons()
        else:
            st.error(message)

# Status message
st.markdown("---")
st.info("✅ Database initialized. Form ready to use!")

# Debug info in expander
with st.expander("🔧 Debug Info"):
    st.write(f"**Patient Name:** {patient_name}")
    st.write(f"**Database Path:** data/daily_logs.db")
    
    # Check if database file exists
    db_path = os.path.join(os.path.dirname(__file__), '../../data/daily_logs.db')
    if os.path.exists(db_path):
        st.success(f"✅ Database file exists: {db_path}")
    else:
        st.warning("⚠️ Database file not created yet. Save a log to create it.")
