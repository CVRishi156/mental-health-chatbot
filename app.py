from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# Comprehensive solutions database
SOLUTIONS = {
    "stress": {
        "description": "Stress Management Solutions",
        "tips": [
            "Practice 4-7-8 breathing (inhale 4s, hold 7s, exhale 8s)",
            "Try progressive muscle relaxation before bed",
            "Schedule regular digital detox periods",
            "Maintain consistent sleep schedule"
        ],
        "base_routine": {
            "06:00-06:15": "Deep breathing exercises",
            "06:15-06:45": "Gentle yoga/stretching",
            "07:00-07:30": "Healthy breakfast (protein + complex carbs)",
            "12:30-13:15": "Balanced lunch with vegetables",
            "18:30-19:30": "Family/friends quality time",
            "21:00-21:30": "Wind down routine",
            "21:30-06:00": "Quality sleep (8.5 hours)"
        }
    },
    "anxiety": {
        "description": "Anxiety Management Solutions",
        "tips": [
            "Practice grounding (5 things you see, 4 touch, 3 hear, 2 smell, 1 taste)",
            "Create a 'worry period' later in the day",
            "Try alternate nostril breathing",
            "Limit caffeine and news consumption"
        ],
        "base_routine": {
            "06:00-06:15": "Guided meditation",
            "06:15-06:45": "Light exercise",
            "07:00-07:30": "Protein-rich breakfast",
            "12:30-13:15": "Omega-3 rich lunch",
            "16:00-16:15": "Calming tea break",
            "19:00-19:30": "Digital detox",
            "21:00-21:30": "Relaxation",
            "21:30-06:00": "Quality sleep"
        }
    },
    "depression": {
        "description": "Depression Management Solutions",
        "tips": [
            "Practice behavioral activation (schedule rewarding activities)",
            "Get sunlight within 1 hour of waking",
            "Break tasks into tiny, manageable steps",
            "Create a 'done list' to track accomplishments"
        ],
        "base_routine": {
            "06:00-06:15": "Sunlight exposure",
            "06:15-06:45": "Gentle movement",
            "07:00-07:30": "Nutrient-dense breakfast",
            "12:30-13:15": "Healthy lunch",
            "15:00-15:30": "Short walk outside",
            "18:30-19:30": "Social connection",
            "21:00-21:30": "Wind down routine",
            "21:30-06:00": "Quality sleep"
        }
    },
    "anger": {
        "description": "Anger Management Solutions",
        "tips": [
            "Practice STOP technique (Stop, Take breath, Observe, Proceed)",
            "Use physical activity to release tension",
            "Write an unsent letter to express feelings",
            "Identify triggers and early warning signs"
        ],
        "base_routine": {
            "06:00-06:15": "Mindful breathing",
            "06:15-06:45": "Cooling breakfast (smoothie)",
            "07:00-07:30": "Anger prevention planning",
            "12:30-13:15": "Balanced lunch",
            "16:00-16:30": "Physical release (exercise)",
            "19:00-19:30": "Cool-down period",
            "21:00-21:30": "Forgiveness reflection",
            "21:30-06:00": "Quality sleep"
        }
    },
    "loneliness": {
        "description": "Loneliness Solutions",
        "tips": [
            "Reach out to one person daily",
            "Join group activities regularly",
            "Practice self-compassion exercises",
            "Consider pet therapy or volunteering"
        ],
        "base_routine": {
            "06:00-06:15": "Positive affirmations",
            "06:15-06:45": "Plan social connections",
            "07:00-07:30": "Healthy breakfast",
            "12:30-13:15": "Lunch with company",
            "15:00-15:30": "Community activity",
            "18:30-19:30": "Family/friends dinner",
            "21:00-21:30": "Gratitude practice",
            "21:30-06:00": "Quality sleep"
        }
    }
}

# Store user-modified timetables
user_timetables = {}

@app.route('/')
def home():
    return "Mental Health Companion Backend is running!"

@app.route('/chat')
def chat_interface():
    return send_from_directory('templates', 'index.html')

@app.route('/get', methods=['POST'])
def get_response():
    try:
        data = request.get_json()
        user_message = data.get('msg', '').lower()
        user_id = data.get('user_id', 'default')
        
        # Initialize user storage
        if user_id not in user_timetables:
            user_timetables[user_id] = {}
        
        # Identify problem
        problem = next((p for p in SOLUTIONS.keys() if p in user_message), None)
        
        # Handle initial problem selection
        if problem and not any(cmd in user_message for cmd in ["timetable", "modify", "add", "remove"]):
            # First show tips
            tips = SOLUTIONS[problem]["tips"]
            return jsonify({
                "response": f"<strong>{SOLUTIONS[problem]['description']}</strong><br><br>" +
                           "Try these solutions:<br>" + 
                           "".join([f"• {tip}<br>" for tip in tips]),
                "options": [f"Show {problem} timetable", "Different problem"],
                "problem": problem,
                "status": "tips"
            })
        
        # Handle timetable requests
        if problem and ("timetable" in user_message or "schedule" in user_message or "routine" in user_message):
            # Get or create timetable
            if problem not in user_timetables[user_id]:
                user_timetables[user_id][problem] = SOLUTIONS[problem]["base_routine"].copy()
            
            return jsonify({
                "response": f"Here's your {problem} management timetable:",
                "routine": user_timetables[user_id][problem],
                "problem": problem,
                "status": "timetable"
            })
        
        # Handle modifications
        if problem and ("add" in user_message or "remove" in user_message):
            routine = user_timetables[user_id].get(problem)
            if not routine:
                return jsonify({
                    "response": f"Please generate a {problem} timetable first",
                    "options": [f"Show {problem} timetable"],
                    "status": "error"
                })
            
            # Add activity
            if "add" in user_message:
                parts = user_message.split("add")[1].split("at")
                if len(parts) == 2:
                    activity = parts[0].strip()
                    time = parts[1].strip()
                    time_slot = convert_to_timeslot(time)
                    if time_slot:
                        routine[time_slot] = activity
                        return jsonify({
                            "response": f"✅ Added: {time_slot} - {activity}",
                            "routine": routine,
                            "problem": problem,
                            "status": "timetable_updated"
                        })
            
            # Remove activity
            elif "remove" in user_message:
                to_remove = user_message.split("remove")[1].strip()
                for time_slot in list(routine.keys()):
                    if to_remove.lower() in routine[time_slot].lower():
                        removed = routine.pop(time_slot)
                        return jsonify({
                            "response": f"❌ Removed: {time_slot} - {removed}",
                            "routine": routine,
                            "problem": problem,
                            "status": "timetable_updated"
                        })
            
            return jsonify({
                "response": "Couldn't process your request. Try: 'add yoga at 7 AM' or 'remove breakfast'",
                "status": "error"
            })
        
        # Default response
        return jsonify({
            "response": "I can help with stress, anxiety, depression, anger, or loneliness. What are you experiencing?",
            "options": list(SOLUTIONS.keys()),
            "status": "question"
        })
        
    except Exception as e:
        return jsonify({
            "response": "I encountered an error. Please try again.",
            "status": "error",
            "details": str(e)
        }), 500

def convert_to_timeslot(time_str):
    """Convert natural time to timeslot format (e.g., '7 AM' -> '07:00-07:30')"""
    try:
        if "am" in time_str.lower():
            hour = int(time_str.lower().split("am")[0].strip())
            if hour == 12: hour = 0
        elif "pm" in time_str.lower():
            hour = int(time_str.lower().split("pm")[0].strip())
            if hour != 12: hour += 12
        else:
            hour = int(time_str.split(":")[0])
        
        return f"{hour:02d}:00-{hour:02d}:30"
    except:
        return None

if __name__ == '_main_':
    app.run(host='0.0.0.0', port=5000, debug=True)