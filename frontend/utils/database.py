"""
Database utilities for daily activity logging.
Uses SQLite to store caregiver observations and patient activities.
"""
import sqlite3
import os
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Database path
DB_DIR = os.path.join(os.path.dirname(__file__), '../../data')
DB_PATH = os.path.join(DB_DIR, 'daily_logs.db')


def init_database() -> None:
    """Initialize the database and create tables if they don't exist."""
    # Create data directory if it doesn't exist
    os.makedirs(DB_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create daily_logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date DATE NOT NULL,
        patient_name TEXT,
        
        -- Nutrition & Hydration
        meals_eaten INTEGER DEFAULT 0,
        snacks_eaten INTEGER DEFAULT 0,
        water_glasses INTEGER DEFAULT 0,
        
        -- Behavioral Observations
        wandering_incidents INTEGER DEFAULT 0,
        agitation_episodes INTEGER DEFAULT 0,
        confusion_episodes INTEGER DEFAULT 0,
        
        -- Health & Wellness
        hours_slept REAL DEFAULT 0,
        bathroom_accidents INTEGER DEFAULT 0,
        fell_today BOOLEAN DEFAULT 0,
        
        -- Medication & Care
        medications_taken BOOLEAN DEFAULT 1,
        refused_medication BOOLEAN DEFAULT 0,
        
        -- Mood & Social (1-5 scale)
        mood_rating INTEGER DEFAULT 3,
        social_engagement INTEGER DEFAULT 3,
        
        -- Activities
        physical_activity_minutes INTEGER DEFAULT 0,
        cognitive_activities BOOLEAN DEFAULT 0,
        
        -- Notes
        notes TEXT,
        caregiver_name TEXT,
        
        -- Timestamps
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        UNIQUE(log_date, patient_name)
    )
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")


def save_daily_log(log_data: Dict) -> Tuple[bool, str]:
    """
    Save or update a daily log entry.
    
    Args:
        log_data: Dictionary with log fields
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if entry exists for this date and patient
        cursor.execute(
            "SELECT id FROM daily_logs WHERE log_date = ? AND patient_name = ?",
            (log_data['log_date'], log_data.get('patient_name', 'Unknown'))
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update existing entry
            cursor.execute("""
            UPDATE daily_logs SET
                meals_eaten = ?,
                snacks_eaten = ?,
                water_glasses = ?,
                wandering_incidents = ?,
                agitation_episodes = ?,
                confusion_episodes = ?,
                hours_slept = ?,
                bathroom_accidents = ?,
                fell_today = ?,
                medications_taken = ?,
                refused_medication = ?,
                mood_rating = ?,
                social_engagement = ?,
                physical_activity_minutes = ?,
                cognitive_activities = ?,
                notes = ?,
                caregiver_name = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE log_date = ? AND patient_name = ?
            """, (
                log_data['meals_eaten'],
                log_data['snacks_eaten'],
                log_data['water_glasses'],
                log_data['wandering_incidents'],
                log_data['agitation_episodes'],
                log_data['confusion_episodes'],
                log_data['hours_slept'],
                log_data['bathroom_accidents'],
                log_data['fell_today'],
                log_data['medications_taken'],
                log_data['refused_medication'],
                log_data['mood_rating'],
                log_data['social_engagement'],
                log_data['physical_activity_minutes'],
                log_data['cognitive_activities'],
                log_data['notes'],
                log_data['caregiver_name'],
                log_data['log_date'],
                log_data.get('patient_name', 'Unknown')
            ))
            message = "Daily log updated successfully!"
        else:
            # Insert new entry
            cursor.execute("""
            INSERT INTO daily_logs (
                log_date, patient_name,
                meals_eaten, snacks_eaten, water_glasses,
                wandering_incidents, agitation_episodes, confusion_episodes,
                hours_slept, bathroom_accidents, fell_today,
                medications_taken, refused_medication,
                mood_rating, social_engagement,
                physical_activity_minutes, cognitive_activities,
                notes, caregiver_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_data['log_date'],
                log_data.get('patient_name', 'Unknown'),
                log_data['meals_eaten'],
                log_data['snacks_eaten'],
                log_data['water_glasses'],
                log_data['wandering_incidents'],
                log_data['agitation_episodes'],
                log_data['confusion_episodes'],
                log_data['hours_slept'],
                log_data['bathroom_accidents'],
                log_data['fell_today'],
                log_data['medications_taken'],
                log_data['refused_medication'],
                log_data['mood_rating'],
                log_data['social_engagement'],
                log_data['physical_activity_minutes'],
                log_data['cognitive_activities'],
                log_data['notes'],
                log_data['caregiver_name']
            ))
            message = "Daily log saved successfully!"
        
        conn.commit()
        conn.close()
        return True, message
    
    except Exception as e:
        logger.error(f"Error saving daily log: {str(e)}")
        return False, f"Error: {str(e)}"


def get_daily_log(log_date: date, patient_name: str = "Unknown") -> Optional[Dict]:
    """
    Retrieve a daily log for a specific date.
    
    Args:
        log_date: Date to retrieve
        patient_name: Patient name
    
    Returns:
        Dictionary with log data or None if not found
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM daily_logs WHERE log_date = ? AND patient_name = ?",
            (log_date, patient_name)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    except Exception as e:
        logger.error(f"Error retrieving daily log: {str(e)}")
        return None


def get_logs_by_date_range(
    start_date: date,
    end_date: date,
    patient_name: str = "Unknown"
) -> List[Dict]:
    """
    Retrieve logs for a date range.
    
    Args:
        start_date: Start date
        end_date: End date
        patient_name: Patient name
    
    Returns:
        List of log dictionaries
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT * FROM daily_logs 
        WHERE log_date BETWEEN ? AND ? 
        AND patient_name = ?
        ORDER BY log_date DESC
        """, (start_date, end_date, patient_name))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception as e:
        logger.error(f"Error retrieving logs by date range: {str(e)}")
        return []


def get_recent_logs(limit: int = 7, patient_name: str = "Unknown") -> List[Dict]:
    """
    Get the most recent logs.
    
    Args:
        limit: Number of logs to retrieve
        patient_name: Patient name
    
    Returns:
        List of recent log dictionaries
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT * FROM daily_logs 
        WHERE patient_name = ?
        ORDER BY log_date DESC 
        LIMIT ?
        """, (patient_name, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception as e:
        logger.error(f"Error retrieving recent logs: {str(e)}")
        return []


def delete_log(log_date: date, patient_name: str = "Unknown") -> Tuple[bool, str]:
    """
    Delete a daily log.
    
    Args:
        log_date: Date of log to delete
        patient_name: Patient name
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM daily_logs WHERE log_date = ? AND patient_name = ?",
            (log_date, patient_name)
        )
        
        conn.commit()
        rows_deleted = cursor.rowcount
        conn.close()
        
        if rows_deleted > 0:
            return True, "Log deleted successfully!"
        else:
            return False, "No log found for this date."
    
    except Exception as e:
        logger.error(f"Error deleting log: {str(e)}")
        return False, f"Error: {str(e)}"
