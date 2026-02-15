"""
Generate sample data for testing the Daily Log and Reports.
Run this script once to populate the database with random entries.

Usage:
    python frontend/utils/generate_sample_data.py
"""
import sys
import os
import random
from datetime import date, timedelta

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from frontend.utils.database import init_database, save_daily_log

# Initialize database
init_database()

def generate_sample_logs(patient_name="John Doe", days=60):
    """
    Generate sample daily logs for testing.
    
    Args:
        patient_name: Name of the patient
        days: Number of days of data to generate
    """
    print(f"🔄 Generating {days} days of sample data for {patient_name}...")
    
    # Starting date
    start_date = date.today() - timedelta(days=days-1)
    
    # Base values (will add random variation)
    base_values = {
        'meals_eaten': 3,
        'snacks_eaten': 2,
        'water_glasses': 6,
        'hours_slept': 8.0,
        'mood_rating': 3,
        'social_engagement': 3,
        'physical_activity_minutes': 30,
    }
    
    # Track trends over time (simulate disease progression)
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        # Simulate gradual changes over time
        progression_factor = day / days  # 0.0 to 1.0
        
        # Early stage: fewer incidents, better mood
        # Later stage: more incidents, lower mood
        
        # Nutrition (slight decline over time)
        meals = max(1, int(base_values['meals_eaten'] + random.randint(-1, 1) - progression_factor * 0.5))
        snacks = max(0, int(base_values['snacks_eaten'] + random.randint(-1, 2)))
        water = max(3, int(base_values['water_glasses'] + random.randint(-2, 2) - progression_factor * 1))
        
        # Behavioral (increase over time)
        wandering = random.randint(0, int(3 * progression_factor))
        agitation = random.randint(0, int(4 * progression_factor))
        confusion = random.randint(0, int(5 * progression_factor))
        
        # Sleep (slight decline and more variation)
        hours_slept = max(4.0, min(12.0, 
            base_values['hours_slept'] + random.uniform(-2, 1) - progression_factor * 0.5
        ))
        
        # Health incidents
        bathroom_accidents = random.randint(0, int(2 * progression_factor))
        fell_today = 1 if random.random() < (0.05 + 0.05 * progression_factor) else 0
        
        # Medication (occasional refusal, more common later)
        medications_taken = 0 if random.random() < (0.05 + 0.1 * progression_factor) else 1
        refused_medication = 1 if medications_taken == 0 else 0
        
        # Mood (decline over time with daily variation)
        mood_rating = max(1, min(5, 
            int(base_values['mood_rating'] + random.randint(-1, 1) - progression_factor * 1)
        ))
        social_engagement = max(1, min(5,
            int(base_values['social_engagement'] + random.randint(-1, 1) - progression_factor * 0.5)
        ))
        
        # Activities (decline over time)
        physical_activity = max(0, int(
            base_values['physical_activity_minutes'] + random.randint(-15, 20) - progression_factor * 10
        ))
        cognitive_activities = 1 if random.random() < (0.7 - 0.3 * progression_factor) else 0
        
        # Generate notes occasionally
        notes_options = [
            "",
            "Had a good day overall.",
            "Seemed more confused than usual.",
            "Enjoyed outdoor walk today.",
            "Resisted taking medication.",
            "Asked about family members repeatedly.",
            "Was calm and cooperative.",
            "Became agitated in the evening.",
            "Slept poorly last night.",
            "Good appetite today.",
            "Refused to eat lunch.",
            "Participated in puzzles.",
            "Watched favorite TV show.",
        ]
        notes = random.choice(notes_options) if random.random() < 0.3 else ""
        
        # Caregiver names
        caregivers = ["Alice", "Bob", "Carol", "David", "Emma"]
        caregiver = random.choice(caregivers)
        
        # Create log entry
        log_data = {
            'log_date': current_date,
            'patient_name': patient_name,
            'meals_eaten': meals,
            'snacks_eaten': snacks,
            'water_glasses': water,
            'wandering_incidents': wandering,
            'agitation_episodes': agitation,
            'confusion_episodes': confusion,
            'hours_slept': round(hours_slept, 1),
            'bathroom_accidents': bathroom_accidents,
            'fell_today': fell_today,
            'medications_taken': medications_taken,
            'refused_medication': refused_medication,
            'mood_rating': mood_rating,
            'social_engagement': social_engagement,
            'physical_activity_minutes': physical_activity,
            'cognitive_activities': cognitive_activities,
            'notes': notes,
            'caregiver_name': caregiver
        }
        
        # Save to database
        success, message = save_daily_log(log_data)
        
        if success:
            print(f"✅ {current_date}: {message}")
        else:
            print(f"❌ {current_date}: {message}")
    
    print(f"\n🎉 Successfully generated {days} days of sample data!")
    print(f"📊 You can now view the data in the Report page")


if __name__ == "__main__":
    # Configuration
    PATIENT_NAME = "John Doe"  # Change this to match your patient
    DAYS_OF_DATA = 60  # Generate 60 days of data
    
    print("="*60)
    print("📊 Daily Log Sample Data Generator")
    print("="*60)
    print(f"Patient: {PATIENT_NAME}")
    print(f"Days: {DAYS_OF_DATA}")
    print("="*60)
    
    # Ask for confirmation
    response = input("\n⚠️  This will add sample data to your database. Continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        generate_sample_logs(patient_name=PATIENT_NAME, days=DAYS_OF_DATA)
    else:
        print("❌ Cancelled. No data generated.")
