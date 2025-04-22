from flask_login import current_user
from datetime import datetime
import os
from dotenv import load_dotenv
from flask import current_app, Flask
from app import mongo  # Import the mongo object from the app module
from bson import ObjectId


RANK_TITLES = {
    "E": [
        {"levels": [1, 2, 3, 4], "title": "Unawakened"},
        {"levels": [5, 6, 7], "title": "Shadow Touched"},
        {"levels": [8, 9, 10], "title": "Waking Wanderer"}
    ],
    "D": [
        {"levels": [1, 2, 3, 4], "title": "Disciple of Grit"},
        {"levels": [5, 6, 7], "title": "Chainbreaker"},
        {"levels": [8, 9, 10], "title": "Wallwalker"}
    ],
    "C": [
        {"levels": [1, 2, 3, 4], "title": "Shadowbound"},
        {"levels": [5, 6, 7], "title": "Flameforged"},
        {"levels": [8, 9, 10], "title": "Guardian of Depths"}
    ],
    "B": [
        {"levels": [1, 2, 3, 4], "title": "Riftborn Hunter"},
        {"levels": [5, 6, 7], "title": "Mindbreaker"},
        {"levels": [8, 9, 10], "title": "Phantom Raider"}
    ],
    "A": [
        {"levels": [1, 2, 3, 4], "title": "Stormcaller"},
        {"levels": [5, 6, 7], "title": "Voidcaller"},
        {"levels": [8, 9, 10], "title": "Ascended Hunter"}
    ],
    "S": [
        {"levels": [1, 2, 3], "title": "Eye of the Monarch"},
        {"levels": [4, 5, 6, 7], "title": "Godslayer"},
        {"levels": [8, 9, 10], "title": "Sovereign of Shadows"}
    ]
}

def get_title(rank, level):
    """
    Get the title for a given rank and level.
    
    Args:
        rank (str): The player's rank (E through S)
        level (int): The player's level (1 through 10)
        
    Returns:
        str: The corresponding title for the rank and level
    """
    if rank not in RANK_TITLES:
        return "Unknown"
        
    for title_range in RANK_TITLES[rank]:
        if level in title_range["levels"]:
            return title_range["title"]
            
    return "Unknown" 

import json
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
        return quests

    except Exception as e:
        current_app.logger.error(f"Error parsing AI response with json.loads: {str(e)}")
        return []




