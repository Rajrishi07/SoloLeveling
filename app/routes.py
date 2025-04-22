from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from bson import ObjectId
from app.models import User
from app import mongo 
from app.xp_engine import complete_task_flow

def create_routes(app):
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))

    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file('favicon.ico')

    def get_xp_to_next_level(total_xp):
        rank_ranges = [
        ('S', 700_000, 800_000),
        ('A', 550_000, 699_999),
        ('B', 400_000, 549_999),
        ('C', 275_000, 399_999),
        ('D', 175_000, 274_999),
        ('E', 100_000, 174_999),
        ('F', 40_000, 99_999),
        ('G', 0, 39_999)
    ]


        for i, (rank, low, high) in enumerate(rank_ranges):
            if total_xp >= low:
                span = high - low + 1
                level_span = span // 10
                level = min((total_xp - low) // level_span + 1, 10)
                level_start = low + (level - 1) * level_span
                level_end = low + level * level_span - 1

                if level < 10:
                    next_level_xp = level_end + 1
                    xp_needed = next_level_xp - total_xp
                    return {
                        'current_rank': rank,
                        'current_level': level,
                        'next': f"{rank}-{level + 1}",
                        'xp_to_next': xp_needed,
                        'level_start': level_start,
                        'level_end': level_end
                    }
                else:
                    # At level 10 of current rank
                    if i == 0:  # Already at top rank and level
                        return {
                            'current_rank': rank,
                            'current_level': 10,
                            'next': None,
                            'xp_to_next': 0,
                            'level_start': level_start,
                            'level_end': level_end
                        }
                    next_rank, next_low, _ = rank_ranges[i - 1]
                    xp_needed = next_low - total_xp
                    return {
                        'current_rank': rank,
                        'current_level': 10,
                        'next': f"{next_rank}-1",
                        'xp_to_next': xp_needed,
                        'level_start': level_start,
                        'level_end': level_end
                    }

        # Fallback for below minimum XP
        return {
            'current_rank': 'G',
            'current_level': 1,
            'next': 'G-2',
            'xp_to_next': 5_000 - total_xp,
            'level_start': 0,
            'level_end': 4_999
        }


    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.is_authenticated:
            next_level_info = get_xp_to_next_level(current_user.xp) or {}
            recent_task_logs = list(mongo.db.tasks_log.find({"user_id": ObjectId(current_user.get_id())}).sort("date", -1).limit(30))
            today_stat = {"category_xp": {
                "strength": 0,
                "dexterity": 0, 
                "perception": 0,
                "agility": 0,
            }}
            active_debuffs = current_user.active_debuffs
            xp_diff = []

            # Find today's stat from task_logs
            today = date.today()
            today_stat = None
            for log in current_user.task_logs:
                print("Task Log found")
                # Convert log date to date object if it's a datetime
                log_date = log.get("date")
                if log_date and isinstance(log_date, datetime):
                    log_date = log_date.date()
                    print("Log date:", log_date)
                elif isinstance(log_date, str):
                    # Optional: handle ISO string
                    log_date = datetime.fromisoformat(log_date).date()
                print(log_date, today)
                if log_date == today:
                    today_stat = log
                    break

            print("Today's stat:", today_stat)

            streaks = current_user.streaks  # A dict: {task_id: {streak_data}}
            # Prepare list of streaks with task names
            streak_info = []
            for task_id, streak_data in streaks.items():
                task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
                if task:
                    streak_info.append({
                        "task_name": task.get("name", "Unknown Task"),
                        "current_streak": streak_data.get("current_streak", 0),
                        "longest_streak": streak_data.get("longest_streak", 0)
                    })
            return render_template('dashboard.html',
                                next_level_info=next_level_info,
                                recent_task_logs=recent_task_logs,
                                today_stat=today_stat,
                                active_debuffs=active_debuffs,
                                xp_logs=current_user.task_logs,
                                xp_diff=xp_diff,
                                streak_info=streak_info
                                )
        return redirect(url_for('auth.login'))

    @app.route('/quests')
    @login_required
    def quests():
        current_user.get_quests()

        # Ensure all quest types are available before rendering
        if not all([
            getattr(current_user, "daily_quests", None),
            getattr(current_user, "weekly_quests", None),
            getattr(current_user, "elite_quests", None),
            getattr(current_user, "epic_quests", None),
            getattr(current_user, "habit_quests", None),
        ]):
            print("Some quests still loading — refreshing")
            return redirect(url_for('quests'))  # Reloads until all are ready
    
        return render_template('quests.html',
            daily_quests=current_user.get_quests_of('daily'),
            habit_quests=current_user.get_quests_of('habit'),
            challenge_quest=current_user.get_quests_of('weekly'),
            elite_quest=current_user.get_quests_of('elite'),
            exclusive_quests=current_user.get_quests_of('epic')
        )
   
    @app.route('/complete_quest', methods=['POST'])
    @login_required
    def complete_quest():
        data = request.json
        print(data)
        quest_id = data.get('questId')
        quest_name = data.get('questName')
        category_xp = data.get('categoryXp')
        streak_eligible = data.get('streakEligible', False)
        difficulty = data.get('difficulty')
        print("difficulty :", difficulty)
        try:
            # Call the new XP engine module
            success = complete_task_flow(mongo, current_user, quest_id, quest_name, category_xp)
        
            if not success:
                raise Exception("Quest completion failed")
            
            print("Streak eligible:", streak_eligible)
            if streak_eligible:
                print("Streak eligible, updating streak", quest_name)
                current_user.update_streak(task_id=quest_id)
            # Optional: mark the quest completed in the session or user model
            current_user.mark_quest_complete(quest_id)
            current_user.update_currency(difficulty)
            current_user.update_oncomplete(quest_id)
            return jsonify({
                "success": True,
                "completed": True,
                "quest_id": str(quest_id)
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            })            

    @app.route('/shop')
    @login_required
    def shop():
        items = list(mongo.db.shop_items.find({}))
        for item in items:
            item['_id'] = str(item['_id'])  # Make _id JSON serializable
        print(items)
        return render_template("shop.html", shop_items=items)


    return app