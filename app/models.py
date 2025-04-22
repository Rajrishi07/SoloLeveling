from re import M
from site import ENABLE_USER_SITE
from webbrowser import get
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo
from bson.objectid import ObjectId
from datetime import datetime, timedelta, date
from app.utils import get_title
from app.prompts import generate_quest


class User(UserMixin):
    def __init__(self, username, email, password_hash=None, xp=0, level=1, rank='E',
                 strength=0, dexterity=0, perception=0, agility=0, 
                 vitality=0, willpower=0, charisma=0, intelligence=0, exam_history=None, _id=None, 
                 title=None, task_logs=None, streaks=None, habit_quests=None,
                 last_daily_refresh=None, daily_quests=None, 
                 last_weekly_refresh=None, weekly_quests=None,
                 elite_quests=None, epic_quests=None, completed_quests=None, active_debuffs=None,
                 gold=0, crystals=0, essence_dust=0, shadow_tokens=0):  # Fixed quest parameter names
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.xp = xp
        self.level = level
        self.rank = rank
        self.strength = strength
        self.dexterity = dexterity
        self.perception = perception
        self.agility = agility
        self.vitality = vitality
        self.willpower = willpower
        self.charisma = charisma
        self.intelligence = intelligence
        self.exam_history = exam_history or []
        self._id = _id
        self.title = title if title else get_title(rank, level)
        self.task_logs = task_logs or []
        self.habit_quests = habit_quests
        self.streaks = streaks or {}  # Initialize streaks
        self.last_daily_refresh = last_daily_refresh
        self.daily_quests = daily_quests or []
        self.last_weekly_refresh = last_weekly_refresh
        self.weekly_quests = weekly_quests or []
        self.elite_quests = elite_quests or []
        self.epic_quests = epic_quests or []
        self.completed_quests = completed_quests or []
        self.active_debuffs = active_debuffs or []
        self.gold = gold
        self.crystals = crystals
        self.essence_dust = essence_dust
        self.shadow_tokens = shadow_tokens

    def get_id(self):
        return str(self._id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def save(self):
        if not self._id:
            # New user
            result = mongo.db.users.insert_one({
                'username': self.username,
                'email': self.email,
                'password_hash': self.password_hash,
                'xp': self.xp,
                'level': self.level,
                'rank': self.rank,
                'strength': self.strength,
                'dexterity': self.dexterity,
                'perception': self.perception,
                'agility': self.agility,
                'vitality': self.vitality,
                'willpower': self.willpower,
                'charisma': self.charisma,
                'intelligence':self.intelligence,
                'exam_history': self.exam_history,
                'title': self.title,
                'task_logs': self.task_logs,
                'streaks': self.streaks,  # Initialize streaks
                'habit_quests': self.habit_quests,  # Initialize habit_quests
                'daily_quests': [],
                "weekly_quests": [] ,
                "epic_quests": [],
                "elite_quests": [],
                "completed_quests": [],
                'active_debuffs': self.active_debuffs,  # Initialize active_debuffs
                'gold': self.gold,
                'crystals': self.crystals,
                'essence_dust': self.essence_dust,
                'shadow_tokens': self.shadow_tokens
            })
            self._id = result.inserted_id
        else:
            # Update existing user
            mongo.db.users.update_one(
                {'_id': self._id},
                {'$set': {
                    'username': self.username,
                    'email': self.email,
                    'password_hash': self.password_hash,
                    'xp': self.xp,
                    'level': self.level,
                    'rank': self.rank,
                    'strength': self.strength,
                    'dexterity': self.dexterity,
                    'perception': self.perception,
                    'agility': self.agility,
                    'vitality': self.vitality,
                    'willpower': self.willpower,
                    'charisma': self.charisma,
                    'intelligence':self.intelligence,
                    'exam_history': self.exam_history,
                    'title': self.title,
                    'active_debuffs': self.active_debuffs,  # Update active_debuffs
                    'gold': self.gold,
                    'crystals': self.crystals,
                    'essence_dust': self.essence_dust,
                    'shadow_tokens': self.shadow_tokens
                }}
            )

    
    @classmethod
    def get_by_id(cls, user_id):
        try:
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                user_data['_id'] = user_data['_id']
                return cls(**user_data)
        except:
            return None

    @classmethod
    def get_by_username(cls, username):
        user_data = mongo.db.users.find_one({'username': username})
        if user_data:
            user_data['_id'] = user_data['_id']
            print(user_data)
            return cls(**user_data)
        return None

    @classmethod
    def get_by_email(cls, email):
        user_data = mongo.db.users.find_one({'email': email})
        if user_data:
            user_data['_id'] = user_data['_id']
            return cls(**user_data)
        return None

    def add_exam_result(self, exam_data, results):
        """Add a new exam result to the user's history"""
        exam_result = {
            'timestamp': datetime.utcnow(),
            'exam_data': exam_data,
            'results': results
        }
        print("Adding exam Results:")
        self.exam_history.append(exam_result)
        print("Saving User:")
        self.save()

    def get_exam_history(self):
        """Get the user's exam history"""
        return self.exam_history

    def update_title(self):
        """Update the user's title based on their current rank and level"""
        new_title = get_title(self.rank, self.level)
        if new_title != self.title:
            self.title = new_title
            mongo.db.users.update_one(
                {"username": self.username},
                {"$set": {"title": new_title}}
            )
        return new_title

    def update_stats(self, stats_dict):
        """Update user stats with new values"""
        # Update instance attributes
        for stat, value in stats_dict.items():
            if hasattr(self, stat):
                setattr(self, stat, value)

    
    def get_quests(self):
        today = datetime.combine(date.today(), datetime.min.time())
    
        if self.last_daily_refresh != today:
            print("Refreshing Daily Quests")
            daily_quests = generate_quest(type="daily", user=self)
            if daily_quests:
                self.check_debuffs();
                # Insert quests into tasks collection and get their IDs
                print("Inserting Daily Quest:")
                quest_ids = []
                for quest in daily_quests:
                    quest['user_id'] = self._id
                    quest['created_at'] = today
                    result = mongo.db.tasks.insert_one(quest)
                    quest_ids.append(result.inserted_id)
                habit_ids_cursor = mongo.db.tasks.find({"type": "habit"}, {"_id": 1})
                habit_ids = [doc["_id"] for doc in habit_ids_cursor]  # Extract raw ObjectId values
                # Update user with quest IDs
                mongo.db.users.update_one(
                    {"_id": self._id},
                    {"$set": {
                        "last_daily_refresh": today,
                        "daily_quests": quest_ids,
                        "habit_quests": habit_ids,
                    }}
                )
                print("Daily Quest Inserted:")
                self.daily_quests = quest_ids
                self.last_daily_refresh = today
                

        if self.last_weekly_refresh is None or (datetime.now() - self.last_weekly_refresh) > timedelta(days=7):
            print("Refreshing Weekly Quests")
            weekly_quests = generate_quest(type="weekly", user=self)
            if weekly_quests:
                # Insert quests into tasks collection
                print("Inserting Weekly Quest:")
                quest_ids = []
                for quest in weekly_quests:
                    
                    quest['user_id'] = self._id
                    quest['created_at'] = today
                    quest['user_id'] = self._id
                    quest['created_at'] = today
                    result = mongo.db.tasks.insert_one(quest)
                    quest_ids.append(result.inserted_id)
                
                # Update user with quest IDs
                mongo.db.users.update_one(
                    {"_id": self._id},
                    {"$set": {
                        "last_weekly_refresh": today,
                        "weekly_quests": quest_ids
                    }}
                )
                self.weekly_quests = quest_ids
                self.last_weekly_refresh = today
    
        if not getattr(self, "elite_quests", None):
            print("Refreshing Elite Quests")
            elite_quests = generate_quest(type="elite", user=self)
            print("Elite Quest : ", elite_quests)
            if elite_quests:
                # Insert quests into tasks collection
                quest_ids = []
                print("Inserting Elite Quest:")
                for quest in elite_quests:
                    quest['user_id'] = self._id
                    quest['created_at'] = today
                    result = mongo.db.tasks.insert_one(quest)
                    quest_ids.append(result.inserted_id)
                print("Elite Quest Inserted:")
                # Update user with quest IDs
                mongo.db.users.update_one(
                    {"_id": self._id},
                    {"$set": {"elite_quests": quest_ids}}
                )
                self.elite_quests = quest_ids
                print("Elite Quest Inserted to:")
        if not getattr(self, "epic_quests", None):
            print("Refreshing Epic Quests")
            epic_quests = generate_quest(type="epic", user=self)
            if epic_quests:
                # Insert quests into tasks collection
                quest_ids = []
                print("Inserting Epic Quest:")
                for quest in epic_quests:
                    quest['user_id'] = self._id
                    quest['created_at'] = today
                    result = mongo.db.tasks.insert_one(quest)
                    quest_ids.append(result.inserted_id)
                
                # Update user with quest IDs
                mongo.db.users.update_one(
                    {"_id": self._id},
                    {"$set": {"epic_quests": quest_ids}}
                )
                self.epic_quests = quest_ids


    def get_quests_of(self, quest_type):
        """Get quests of a specific type"""
        field_name = f"{quest_type}_quests"
        if hasattr(self, field_name):
            quest_ids = getattr(self, field_name)
            if quest_ids:
                return list(mongo.db.tasks.find({"_id": {"$in": quest_ids}}))


    def is_quest_completed(self, quest_id):
        """Check if a quest is completed"""
        if isinstance(quest_id, str):
            quest_id = ObjectId(quest_id)

        if not hasattr(self, 'completed_quests') or self.completed_quests is None:
            # Initialize if missing
            mongo.db.users.update_one(
                {"_id": self._id},
                {"$set": {"completed_quests": []}}
            )
            self.completed_quests = []
            return False

        return quest_id in self.completed_quests


    def update_user_task_log(self, category_xp):
        print("Logging started")
        today = date.today()
        today = datetime.combine(today, datetime.min.time())
        # Total XP for this quest
        gained_xp = sum(category_xp.values())

        # Build dynamic $inc fields for each XP category
        category_inc_fields = {
            f"task_logs.$.category_xp.{k}": v
            for k, v in category_xp.items()
        }
        category_inc_fields.update({
            "task_logs.$.quests_completed": 1,
            "task_logs.$.xp_gained": gained_xp
        })
        # Check if today's log already exists
        existing_log = mongo.db.users.find_one({
            "_id": ObjectId(self._id),
            "task_logs.date": today
        })
        print("Existing log:", bool(existing_log))
        if existing_log:
            # Update today's log
            mongo.db.users.update_one(
                {
                    "_id": ObjectId(self._id),
                    "task_logs.date": today
                },
                {
                    "$inc": category_inc_fields
                }
            )
        else:
            # Create a new log for today
            print("No log found for today, creating new log...")
            new_log = {
                "date": today,
                "quests_completed": 1,
                "xp_gained": gained_xp,
                "category_xp": category_xp
            }

            mongo.db.users.update_one(
                {"_id": ObjectId(self._id)},
                {
                    "$push": {
                        "task_logs": new_log
                    }
                }
            )

    def update_streak(self, task_id):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        
        # Find the current streak for that task using task_id
        user = mongo.db.users.find_one({"_id": ObjectId(self._id)})
        streaks = user.get("streaks", {})
    
        # Get current streak info for the task
        task_streak = streaks.get(task_id, {
            "current_streak": 0,
            "longest_streak": 0,
            "last_completed": None
        })
    
        last_completed = task_streak.get("last_completed")
        if last_completed:
            last_completed = last_completed.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if last_completed == yesterday:
                # Continue the streak
                task_streak["current_streak"] += 1
            elif last_completed < yesterday:
                # Reset the streak
                task_streak["current_streak"] = 1
        else:
            # First time completing this task
            task_streak["current_streak"] = 1
    
        # Update longest streak
        task_streak["longest_streak"] = max(task_streak["longest_streak"], task_streak["current_streak"])
        task_streak["last_completed"] = today
    
        # Update the streaks in the database
        streaks[task_id] = task_streak
        mongo.db.users.update_one(
            {"_id": ObjectId(self._id)},
            {"$set": {"streaks": streaks}}
        )
        print("Streak Updated")



    def mark_quest_complete(self, quest_id):
        """Mark a quest as completed"""
        if isinstance(quest_id, str):
            quest_id = ObjectId(quest_id)

        if quest_id not in self.completed_quests:
            self.completed_quests.append(quest_id)
            mongo.db.users.update_one(
                {"_id": self._id},
                {"$push": {"completed_quests": quest_id}}
            )




    def check_debuffs(self):

        """Check for any incomplete daily or habit tasks and apply penalties."""
        print("Checking for debuffs")

        # Combine quests and check for incomplete ones
        if self.daily_quests is None or self.habit_quests is None:
            return
        all_task_ids = self.daily_quests + self.habit_quests
        completed = set(self.completed_quests)
        incomplete_tasks = [task_id for task_id in all_task_ids if task_id not in completed]

        active_quests = set(self.daily_quests) | set(self.habit_quests)
        self.completed_quests = list(set(completed) - active_quests)

        mongo.db.users.update_one(
            {"_id": self._id},
            {"$set": {"completed_quests": self.completed_quests}}
        )
        # Get current debuffs from DB or use attribute if it exists
        if hasattr(self, 'active_debuffs'):
            active_debuffs = self.active_debuffs
        else:
            user_data = mongo.db.users.find_one({'_id': self._id}, {"active_debuffs": 1})
            active_debuffs = user_data.get('active_debuffs', [])

        # Apply penalties for incomplete tasks
        for task_id in incomplete_tasks:
            task = mongo.db.tasks.find_one({'_id': task_id})
            penalty = task.get('penalty') if task else None

            if penalty:
                existing = next((d for d in active_debuffs if d['name'] == penalty['name']), None)
                print("Existing Debuff:", existing)
                if existing:
                    # Stack the penalty
                    existing['xp_gain_multiplier'] *= penalty['xp_gain_multiplier']
                    existing['duration_days'] += penalty['duration_days']
                else:
                    active_debuffs.append(penalty)

        # Update in DB and optionally in-memory
        mongo.db.users.update_one(
            {'_id': self._id},
            {'$set': {'active_debuffs': active_debuffs}}
        )
        self.active_debuffs = active_debuffs  # Keep in sync in memory too

        


    

    def update_currency(self, difficulty):
        print("Updating Currency for difficulty:", difficulty)
        currency_reward_logic = {
            "easy": {"gold": 5, "crystals": 0, "shadow_tokens": 0, "essence_dust": 10},
            "moderate": {"gold": 8, "crystals": 0, "shadow_tokens": 0, "essence_dust": 20},
            "medium": {"gold": 12, "crystals": 1, "shadow_tokens": 0, "essence_dust": 35},
            "challenging": {"gold": 18, "crystals": 1, "shadow_tokens": 0, "essence_dust": 50},
            "hard": {"gold": 25, "crystals": 2, "shadow_tokens": 0, "essence_dust": 75},
            "extreme": {"gold": 35, "crystals": 3, "shadow_tokens": 0, "essence_dust": 120},
            "epic": {"gold": 50, "crystals": 4, "shadow_tokens": 1, "essence_dust": 180},
            "legendary": {"gold": 75, "crystals": 6, "shadow_tokens": 2, "essence_dust": 250}
        }
        if difficulty in currency_reward_logic:
            rewards = currency_reward_logic[difficulty]
            self.gold += rewards["gold"]
            self.crystals += rewards["crystals"]
            self.essence_dust += rewards["essence_dust"]
            self.shadow_tokens += rewards["shadow_tokens"]
            self.save_currency()
        else:
            print(f"Unknown difficulty: {difficulty}")
    def save_currency(self):
        mongo.db.users.update_one(
            {"_id": self._id},
            {"$set": {
                "gold": self.gold,
                "crystals": self.crystals,
                "shadow_tokens": self.shadow_tokens,
                "essence_dust": self.essence_dust
            }}
        )

    def update_oncomplete(self, quest_id):
        
        try:
            # Ensure quest_id is ObjectId if needed
            quest_oid = ObjectId(quest_id) if isinstance(quest_id, str) else quest_id

        except Exception as e:
            print("Error comparing quest IDs:", e)
            return
        if quest_oid in self.elite_quests:
            print("Removing quest from elite_quests ")
            self.elite_quests = []
            mongo.db.users.update_one(
                {"_id": self._id},
                {"$set": {"elite_quests": []}}
            )
        elif quest_oid in self.epic_quests:
            print("Removing quest from epic_quests")
            self.epic_quests = []
            mongo.db.users.update_one(
                {"_id": self._id},
                {"$set": {"epic_quests": []}}
            )
            
    