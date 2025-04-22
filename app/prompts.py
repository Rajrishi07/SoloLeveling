prompt_daily = """
You are a gamified fitness and lifestyle assistant generating daily quests under the theme “Marked Hunts”. The player is in their early-to-mid progression stage, working on developing consistent habits across all stat categories:

📌 Stat Categories: strength, agility, vitality, perception, dexterity, willpower, charisma, intelligence

📌 Objective:
Generate a list of **6 tasks**, each of **easy** or **medium** difficulty. These should:
- Be small to moderate-effort daily tasks that promote physical health, mental discipline, awareness, or social alignment
- Stay grounded in everyday reality. Avoid bizarre setups (e.g., full sensory deprivation, total isolation, cold plunges).
- Be realistically doable in regular environments like home, gym, park, or office
- Stay within the Solo Leveling theme — no skill-based or artistic prompts like composing music or designing logos
- Prioritize consistency, habit-building, short exercises, light reflection, or simple mindset training

📌 Difficulty Definitions:
- **Easy (20 to 40 XP)**: Simple daily habits (e.g., 10 push-ups, walk 10 minutes, drink 2L water, 5-min deep breathing)
- **Medium (40 to 80 XP)**: Moderate effort requiring up to 30 mins or intentional focus (e.g., 20-min bodyweight workout, 15-min journaling, no phone during lunch)

📌 Personalization Input:
Consider the user's ongoing stat development:
- All-time category XP change: {xp_diff_dict}
- Previous task logs: {task_logs}
"""

daily_example = """
📦 Output Format (strict):
Respond with a valid Python list of dictionaries. No markdown, no explanations. Use the format below exactly:
🔔 Only include a penalty for core, mission-critical tasks — ones where failure would damage user progress (e.g., hydration, training, no-screen detox).
❌ Leave penalty: null or omit it entirely for optional or non-crucial challenges. Do NOT add penalties to all tasks.
Dont show category_xp for categories having 0 XP.

category_xp_changes:
python
'''
[
  {{
    "name": "Task name",
    "description": "What the user is meant to do.",
    "type": "Daily",
    "category_xp": {{
      "willpower": 30
    }},
    "difficulty": "easy",
    "streak_eligible": False,
    "tags": ["routine", "discipline"],
    "penalty": None
  }},
  {{
    "name": "Task name",
    "description": "What the user is meant to do.",
    "type": "Daily",
    "category_xp": {{
      "strength": 40
    }},
    "difficulty": "medium",
    "streak_eligible": False,
    "tags": ["fitness", "focus"],
    "penalty": {{
      "name": "Weakened Resolve",
      "description": "Skipping core habits weakens your inner discipline.",
      "xp_gain_multiplier": 0.85,
      "duration_days": 1,
      "status": "inactive",
      "severity": "mild"
    }}
  }},
  ...
]
"""


prompt_weekly = """
The player enters the “Riftborn Trials” — short-term, high-effort quests designed to push limits without crossing into unsafe or socially awkward territory.

📌 Stat Categories: strength, agility, vitality, perception, dexterity, willpower, charisma, intelligence

📌 Task Criteria:
Generate **2 weekly quests** of **hard** or **extreme** difficulty. These must:
- Be doable in **1–4 days max**
- Push discipline, endurance, or focus, without requiring isolation, pain tolerance extremes, or uncommon environments
- Fit within a modern lifestyle (gym, home, park, quiet space)
- Avoid things like: “24h in a dark room,” “30-day monk mode,” or “no food for 3 days”

📌 Difficulty Definitions:
- **Hard (100–180 XP)**: 1–2 intense sessions (e.g., full-body workout, full focus session, social mission)
- **Extreme (200–250 XP)**: A demanding but normal-world task (e.g., 10K hike, 24h screen detox, multi-hour workout)

📌 Personalization Input:
- All-time stat change: {xp_diff_dict}
- Daily task logs: {task_logs}
"""

weekly_exmple="""
📦 Output Format (strict):
Return a **Python list of dictionaries**. No markdown or extra text. Use the exact structure below (this is just a format reference):
🔔 Only include a penalty for core, mission-critical tasks — ones where failure would damage user progress (e.g., hydration, training, no-screen detox).
❌ Leave penalty: null or omit it entirely for optional or non-crucial challenges. Do NOT add penalties to all tasks.
Dont show category_xp for categories having 0 XP.

[
  {
    "name": "Task Name",
    "description": "Clear, actionable task that represents high effort.",
    "type": "weekly",
    "category_xp": {
      "strength": 90,
      "vitality": 60
    },
    "difficulty": "hard",
    "streak_eligible": False,
    "tags": ["cardio", "discipline"],
    "penalty": {
      "name": "Lethargic Pulse",
      "trigger": "missed_cardio",
      "description": "Your energy feels off-balance after missing the challenge.",
      "xp_gain_multiplier": 0.8,
      "duration_days": 2,
      "severity": "moderate"
    }
  },
  ...
]
"""

prompt_elite = """
The user is ready for a peak-level mission under “Wraith's Call”. This task should feel intense and transformative — but **grounded, safe, and socially reasonable**.

📌 Stat Categories: strength, agility, vitality, perception, dexterity, willpower, charisma, intelligence

📌 Theme:
- Think of this like a solo hunter’s personal raid — a major real-life challenge that proves resolve, not a mental breakdown trigger
- No sensory deprivation, extreme fasting, isolation, sleep deprivation, or danger
- No tasks that require more than **30 days** or raise concern from others

📌 Difficulty:
- **Epic (300–500 XP)**: Serious transformation over 3–20 days. Think: major health reset, discipline streak, or cognitive grind

📌 Personalization Input:
- All-time stat change: {xp_diff_dict}
- Daily task logs: {task_logs}
"""

elite_example="""
📦 Output Format (strict):
Return **one** Python dictionary wrapped in a list. Follow this structure *exactly*:
🔔 Only include a penalty for core, mission-critical tasks — ones where failure would damage user progress (e.g., hydration, training, no-screen detox).
❌ Leave penalty: null or omit it entirely for optional or non-crucial challenges. Do NOT add penalties to all tasks.
Dont show category_xp for categories having 0 XP.

[
  {
    "name": "Name of the task",
    "description": "Detailed description of what needs to be done and the real-life effort it represents.",
    "type": "elite",
    "category_xp": {
      "strength": 0,
      "agility": 0,
      "vitality": 0,
      "perception": 0,
      "dexterity": 0,
      "willpower": 0,
      "charisma": 0,
      "intelligence": 0
    },
    "difficulty": "epic",
    "streak_eligible": False,
    "tags": ["high_effort", "discipline", "personal_growth"],
    "penalty": {
      "name": "Shadow's Regret",
      "trigger": "failed_epic_task",
      "description": "The weight of failure hangs over you after abandoning your epic quest.",
      "xp_gain_multiplier": 0.75,
      "duration_days": 3,
      "severity": "severe"
    }
  }
]
"""

prompt_epic = """
You are generating a legendary-tier challenge under the banner of “Eclipse Trials” — the most difficult quests in the Solo Leveling-inspired system. This is not about pain or punishment — it’s about real transformation, delivered through a thrilling, doable, but extremely high-effort task.

📌 Stat Categories: strength, agility, vitality, perception, dexterity, willpower, charisma, intelligence

📌 Objective:
Generate **1 “epic” quest**, more difficult than elite, that:
- Is meant to be completed over **7 to 14 days** (not longer than 21)
- Demands sustained discipline, structure, or willpower
- Feels adventurous or intense — like a raid, bootcamp, or personal awakening
- Still fits into a modern lifestyle (can be done from home, gym, local area — no travel, no dangerous stunts)

📌 Task Themes:
- Can be a full-week regimen (e.g., workout streak, focus training, digital minimalism reboot)
- Can involve mixed-discipline daily missions (e.g., social + physical + mindset)
- Can include a specific condition or limitation (e.g., no sugar + daily journaling + workout = triple challenge)
- Can include light roleplay or storytelling to enhance immersion — but it **must** remain grounded in reality

📌 Forbidden:
- No full isolation, no sensory deprivation, no extreme fasting, no quitting jobs, no dangerous challenges
- No passive or abstract goals (e.g., “be your best self,” “be more aware”) — must be **clearly actionable**

📌 Difficulty:
- **Epic (500–700 XP)**: The hardest non-permanent task — requires daily attention, will feel like a transformation arc

📌 Personalization Input:
- All-time stat change: {xp_diff_dict}
- Daily task logs: {task_logs}
"""

epic_example="""
📌 Output:
Return a single task as a **Python dictionary inside a list** using this format:
🔔 Only include a penalty for core, mission-critical tasks — ones where failure would damage user progress (e.g., hydration, training, no-screen detox).
❌ Leave penalty: null or omit it entirely for optional or non-crucial challenges. Do NOT add penalties to all tasks.
Dont show category_xp for categories having 0 XP.

[
  {
    "name": "Task Title",
    "description": "A detailed and motivating explanation of the challenge and how to complete it.",
    "type": "epic",
    "category_xp": {
      "strength": 0,
      "agility": 0,
      "vitality": 0,
      "perception": 0,
      "dexterity": 0,
      "willpower": 0,
      "charisma": 0,
      "intelligence": 0
    },
    "difficulty": "legendary",
    "streak_eligible": False,
    "tags": ["high_effort", "transformation", "discipline"],
    "penalty": {
      "name": "Eclipse Break",
      "trigger": "failed_epic_task",
      "description": "The eclipse fades — your resolve dims, your stats recoil. Missed greatness stings more than failure.",
      "xp_gain_multiplier": 0.6,
      "duration_days": 5,
      "severity": "critical"
    }
  }
]
"""

from google import genai
import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from app import mongo

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_KEY"))
categories = ["strength", "vitality", "perception", "charisma", "dexterity", "agility", "willpower", "intelligence"]

def calculate_xp_diff(user):
    xp_diff_dict = []
    if user and user.exam_history and len(user.exam_history) > 0:
        for category in categories:
            xp_diff_dict.append({
                "category": category,
                "xp_difference": getattr(user, category) - user.exam_history[0]["results"].get(category + "_xp", 0)
            })
    return xp_diff_dict

def get_task_logs(user):
    task_logs = []
    if user and user.task_logs:
        for log in user.task_logs[-7:]:
            task_logs.append({
                "date": log["date"],
                "category_xp_gained": log["category_xp"]
            })
    return task_logs

def format_xp_diff(xp_diff_dict):
    return "\n".join([f"{entry['category']}: {entry['xp_difference']} XP" for entry in xp_diff_dict])

def format_task_logs(task_logs):
    log_lines = []
    for log in task_logs:
        date = log["date"]
        category_xp = log["category_xp_gained"]
        xp_details = ", ".join([f"{k}: {v} XP" for k, v in category_xp.items()])
        log_lines.append(f"{date} — {xp_details}")
    return "\n".join(log_lines)


def generate_quest(type=None, user=None):
    try:
        if not type or not user:
            return None
            
        # Calculate XP differences and get task logs
        xp_diff_dict = calculate_xp_diff(user)
        task_logs = get_task_logs(user)
            
        # Select appropriate prompt based on quest type and format with user data
        if type == 'daily':
            prompt = prompt_daily.format(xp_diff_dict=format_xp_diff(xp_diff_dict), task_logs=format_task_logs(task_logs)) + daily_example
        elif type == 'weekly':
            prompt = prompt_weekly.format(xp_diff_dict=format_xp_diff(xp_diff_dict), task_logs=format_task_logs(task_logs)) + weekly_exmple
        elif type == 'elite':
            prompt = prompt_elite.format(xp_diff_dict=format_xp_diff(xp_diff_dict), task_logs=format_task_logs(task_logs)) + elite_example
        elif type == 'epic':
            prompt = prompt_epic.format(xp_diff_dict=format_xp_diff(xp_diff_dict), task_logs=format_task_logs(task_logs)) + epic_example
        else:
            return None
            
        print(f"Making API call to Gemini : type = {type}")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        print("API call successful")
        
        quest = text_to_quest(response.text)
        print("Quest returned as dictionary, Sending back to user")
        return quest
            
    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging: print any error
        return None

import json
import re

def text_to_quest(response):
    print(response)
    try:
        # Step 1: Remove markdown-style triple backticks and optional language hints
        response = re.sub(r"^```(?:python)?\s*", "", response.strip())
        response = re.sub(r"\s*```$", "", response.strip())

        # Step 2: Remove any inline comments like "# explanation"
        response = re.sub(r'#.*', '', response)

        # Step 3: Ensure true/false/null are lowercase (JSON standard)
        response = response.replace("True", "true").replace("False", "false").replace("None", "null")

        # Step 4: Parse using json.loads
        quests = json.loads(response)
        print("Returning quests as json")
        return quests

    except Exception as e:
        print(f"Error parsing AI response with json.loads: {str(e)}")
        return []