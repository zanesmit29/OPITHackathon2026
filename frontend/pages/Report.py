"""
Report Page - Stable Version with Minimal Dependencies
Visualize daily log trends and export data.
"""
import sys
import os
from datetime import date, datetime, timedelta
import io

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import streamlit as st
import pandas as pd

from frontend.utils.database import (
    init_database,
    get_logs_by_date_range
)

# Initialize database
init_database()

# Page config
st.set_page_config(
    page_title="Alzheimer's Assistant - Reports",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Reports & Analytics")
st.markdown("Visualize trends and export your data")

# Get patient name
patient_name = st.session_state.get('patient_data', {}).get('name', 'Unknown')
if patient_name:
    st.info(f"👤 Viewing data for: **{patient_name}**")

st.markdown("---")

# Date range selector
st.subheader("📅 Select Date Range")
col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "Start Date",
        value=date.today() - timedelta(days=30),
        max_value=date.today()
    )

with col2:
    end_date = st.date_input(
        "End Date",
        value=date.today(),
        max_value=date.today(),
        min_value=start_date
    )

# Quick select buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Last 7 Days", use_container_width=True):
        start_date = date.today() - timedelta(days=6)
        st.rerun()
with col2:
    if st.button("Last 30 Days", use_container_width=True):
        start_date = date.today() - timedelta(days=29)
        st.rerun()
with col3:
    if st.button("Last 90 Days", use_container_width=True):
        start_date = date.today() - timedelta(days=89)
        st.rerun()

st.markdown("---")

# Fetch data safely
try:
    logs = get_logs_by_date_range(start_date, end_date, patient_name)
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

if not logs:
    st.warning(f"📭 No data found between {start_date} and {end_date}")
    st.info("💡 Start logging daily activities in the Daily Log page!")
    st.stop()

# Convert to DataFrame safely
try:
    df = pd.DataFrame(logs)
    df['log_date'] = pd.to_datetime(df['log_date'])
    df = df.sort_values('log_date')
    df_plot = df.set_index('log_date')
except Exception as e:
    st.error(f"Error processing data: {str(e)}")
    st.stop()

st.success(f"✅ Found {len(logs)} log entries")

st.markdown("---")

# Simple tabs - no complex widgets
tab1, tab2, tab3 = st.tabs([
    "📈 Trends", 
    "📊 Summary", 
    "💾 Export"
])

# TAB 1: TRENDS (Simplified)
with tab1:
    st.header("📈 Trends Over Time")
    
    try:
        # Nutrition
        st.subheader("🍽️ Nutrition & Hydration")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Meals Per Day**")
            st.line_chart(df_plot['meals_eaten'], height=200)
        
        with col2:
            st.markdown("**Snacks Per Day**")
            st.line_chart(df_plot['snacks_eaten'], height=200)
        
        with col3:
            st.markdown("**Water (glasses)**")
            st.line_chart(df_plot['water_glasses'], height=200)
        
        st.markdown("---")
        
        # Behavioral
        st.subheader("🚶 Behavioral Observations")
        behavioral_data = df_plot[['wandering_incidents', 'agitation_episodes', 'confusion_episodes']]
        st.line_chart(behavioral_data, height=300)
        
        st.markdown("---")
        
        # Sleep
        st.subheader("💤 Sleep Duration")
        st.bar_chart(df_plot['hours_slept'], height=300)
        
        st.markdown("---")
        
        # Mood
        st.subheader("😊 Mood & Engagement")
        mood_data = df_plot[['mood_rating', 'social_engagement']]
        st.line_chart(mood_data, height=300)
        
        st.markdown("---")
        
        # Activity
        st.subheader("🏃 Physical Activity")
        st.bar_chart(df_plot['physical_activity_minutes'], height=300)
        
    except Exception as e:
        st.error(f"Error rendering charts: {str(e)}")
        st.info("💡 Try selecting a smaller date range")

# TAB 2: SUMMARY
with tab2:
    st.header("📊 Summary Statistics")
    
    try:
        total_days = len(df)
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Days Logged", total_days)
            st.metric("Avg Meals", f"{df['meals_eaten'].mean():.1f}")
            st.metric("Avg Water", f"{df['water_glasses'].mean():.1f}")
        
        with col2:
            st.metric("Avg Sleep", f"{df['hours_slept'].mean():.1f} hrs")
            st.metric("Total Falls", int(df['fell_today'].sum()))
            st.metric("Med Compliance", f"{(df['medications_taken'].sum()/total_days*100):.0f}%")
        
        with col3:
            st.metric("Total Wandering", int(df['wandering_incidents'].sum()))
            st.metric("Total Agitation", int(df['agitation_episodes'].sum()))
            st.metric("Total Confusion", int(df['confusion_episodes'].sum()))
        
        with col4:
            st.metric("Avg Mood", f"{df['mood_rating'].mean():.1f}/5")
            st.metric("Avg Engagement", f"{df['social_engagement'].mean():.1f}/5")
            st.metric("Avg Activity", f"{df['physical_activity_minutes'].mean():.0f} min")
        
        st.markdown("---")
        
        # Range Analysis
        st.subheader("📈 Range Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Best Recorded**")
            st.write(f"🍽️ Most Meals: {df['meals_eaten'].max()}")
            st.write(f"💧 Most Water: {df['water_glasses'].max()} glasses")
            st.write(f"😊 Best Mood: {df['mood_rating'].max()}/5")
            st.write(f"🏃 Most Active: {df['physical_activity_minutes'].max()} min")
        
        with col2:
            st.markdown("**Areas of Concern**")
            st.write(f"⚠️ Total Wandering: {df['wandering_incidents'].sum()}")
            st.write(f"⚠️ Total Agitation: {df['agitation_episodes'].sum()}")
            st.write(f"⚠️ Total Confusion: {df['confusion_episodes'].sum()}")
            st.write(f"⚠️ Total Falls: {df['fell_today'].sum()}")
        
        st.markdown("---")
        
        # Simple data preview
        st.subheader("📋 Recent Entries Preview")
        preview_df = df[['log_date', 'meals_eaten', 'water_glasses', 'hours_slept', 'mood_rating', 'caregiver_name']].copy()
        preview_df['log_date'] = preview_df['log_date'].dt.date
        preview_df = preview_df.sort_values('log_date', ascending=False).head(10)
        
        st.dataframe(
            preview_df,
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"Error calculating statistics: {str(e)}")

# TAB 3: EXPORT
with tab3:
    st.header("💾 Export Data")
    
    st.markdown("""
    ### Download Your Data
    Export your daily logs for sharing with healthcare providers or further analysis.
    """)
    
    try:
        # Prepare export dataframe
        export_df = df.copy()
        export_df['log_date'] = export_df['log_date'].dt.date
        
        col1, col2, col3 = st.columns(3)
        
        # CSV Export
        with col1:
            st.subheader("📄 CSV")
            csv_data = export_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=f"logs_{patient_name}_{start_date}_to_{end_date}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # Excel Export
        with col2:
            st.subheader("📊 Excel")
            excel_buffer = io.BytesIO()
            
            try:
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    export_df.to_excel(writer, sheet_name='Daily Logs', index=False)
                
                excel_data = excel_buffer.getvalue()
                
                st.download_button(
                    label="⬇️ Download Excel",
                    data=excel_data,
                    file_name=f"logs_{patient_name}_{start_date}_to_{end_date}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except:
                st.warning("Excel export unavailable. Use CSV instead.")
        
        # JSON Export
        with col3:
            st.subheader("📋 JSON")
            json_data = export_df.to_json(orient='records', date_format='iso', indent=2)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_data,
                file_name=f"logs_{patient_name}_{start_date}_to_{end_date}.json",
                mime="application/json",
                use_container_width=True
            )
        
        st.markdown("---")
        
        # Preview
        st.subheader("📋 Export Preview (First 5 Rows)")
        st.dataframe(export_df.head(), use_container_width=True, hide_index=True)
        
        # Metadata
        st.markdown("---")
        st.subheader("ℹ️ Export Information")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Patient:** {patient_name}")
            st.write(f"**Date Range:** {start_date} to {end_date}")
        with col2:
            st.write(f"**Total Records:** {len(export_df)}")
            st.write(f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    except Exception as e:
        st.error(f"Error preparing export: {str(e)}")

# Sidebar
with st.sidebar:
    st.header("📊 Report Info")
    st.markdown("""
    **Features:**
    - 📈 Visual trends
    - 📊 Statistics
    - 💾 Data export
    
    **Tip:** Use smaller date ranges for faster loading.
    """)
    
    if 'df' in locals():
        st.metric("Total Logs", len(df))
