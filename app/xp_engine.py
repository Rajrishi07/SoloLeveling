# xp_engine.py (fully updated and functional)
from datetime import datetime, timedelta
from bson import ObjectId
from flask_pymongo import PyMongo
from flask_login import current_user
from operator import mul
from functools import reduce
import math

def calculate_xp_with_debuffs(category_xp, active_debuffs):
    xp_multiplier = reduce(mul, [d.get("xp_gain_multiplier", 1.0) for d in active_debuffs], 1.0)
    adjusted = {cat: math.ceil(xp * xp_multiplier) for cat, xp in category_xp.items()}
    return adjusted, sum(adjusted.values())

def calculate_penalty_with_debuffs(base_penalty, active_debuffs):
    penalty_multiplier = max([d.get("penalty_multiplier", 1.0) for d in active_debuffs], default=1.0)
    adjusted = {cat: int(abs(xp) * penalty_multiplier) * -1 for cat, xp in base_penalty.items()}
    return adjusted, sum(adjusted.values())

def log_task_completion(mongo: PyMongo, user_id, task_name, adjusted_category_xp):
    task_log = {
        "user_id": ObjectId(user_id),
        "task_name": task_name,
        "date": datetime.utcnow(),
        "status": "completed",
        "reason": None,
        "category_xp": adjusted_category_xp
    }
    mongo.db.tasks_log.insert_one(task_log)

def log_xp_earned(mongo: PyMongo, user_id, adjusted_category_xp, total_xp):
    xp_log = {
        "user_id": ObjectId(user_id),
        "amount": total_xp,
        "source": "task",
        "date": datetime.utcnow(),
        "category_xp": adjusted_category_xp
    }
    mongo.db.xp_logs.insert_one(xp_log)

def apply_xp_to_user(mongo: PyMongo, user_id, category_xp, total_xp):
    update = {"xp": total_xp}
    for cat, xp in category_xp.items():
        update[cat] = xp
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$inc": update})

def fetch_active_debuffs(mongo: PyMongo, user_id):
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    return user.get("active_debuffs", []) if user else []

def apply_penalty_log(mongo: PyMongo, user_id, task_name, adjusted_penalty, total_penalty):
    mongo.db.xp_logs.insert_one({
        "user_id": ObjectId(user_id),
        "amount": total_penalty,
        "source": "penalty",
        "date": datetime.utcnow(),
        "category_xp": adjusted_penalty,
        "description": f"Penalty for missing: {task_name}"
    })
    apply_xp_to_user(mongo, user_id, adjusted_penalty, total_penalty)

def apply_debuff(mongo: PyMongo, user_id, debuff):
    duration = debuff.get("duration_days", 1)
    now = datetime.utcnow()
    new_debuff = {
        "start_date": now,
        "end_date": now + timedelta(days=duration),
        "xp_gain_multiplier": debuff.get("xp_gain_multiplier", 1.0),
        "penalty_multiplier": debuff.get("penalty_multiplier", 1.0),
        "severity": debuff.get("severity", "low"),
        "description": debuff.get("description", "")
    }
    
    mongo.db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"active_debuffs": new_debuff}}
    )

def apply_missed_task_penalty(mongo: PyMongo, user_id, task):
    task_name = task.get("name", "Unknown Task")
    base_penalty = task.get("category_xp", {})

    active_debuffs = fetch_active_debuffs(mongo, user_id)
    adjusted_penalty, total_penalty = calculate_penalty_with_debuffs(base_penalty, active_debuffs)

    apply_penalty_log(mongo, user_id, task_name, adjusted_penalty, total_penalty)

    if task.get("penalty"):
        apply_debuff(mongo, user_id, task["penalty"])

def complete_task_flow(mongo: PyMongo, current_user, quest_id, quest_name, category_xp):
    user_id = ObjectId(current_user.get_id())
    print("Starting quest flow")
    print("Details of quest", quest_name, category_xp)
    quest = mongo.db.tasks.find_one({"_id": ObjectId(quest_id)})
    if not quest:
        print("Quest not found")
        return False
    print("Fetching debuffs")
    active_debuffs = fetch_active_debuffs(mongo, user_id)
    print("Adjusting XP")
    adjusted_xp, total_xp = calculate_xp_with_debuffs(category_xp, active_debuffs)
    print("Logging quest completion")
    log_task_completion(mongo, user_id, quest_name, adjusted_xp)
    print("Applying XP")
    log_xp_earned(mongo, user_id, adjusted_xp, total_xp)
    print("Updating user XP")
    apply_xp_to_user(mongo, user_id, adjusted_xp, total_xp)
    print("Updating user XP log")
    current_user.update_user_task_log(adjusted_xp)
    print("User XP Updated")
    return True
