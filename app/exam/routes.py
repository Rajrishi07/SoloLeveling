from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import exam_bp
from .xp_calculator_2 import (
    intelligence_score, strength_score, dexterity_score, agility_score,
    perception_score, vitality_score, willpower_score,
    charisma_score, score_to_xp, calculate_total_xp
)

def get_rank_with_level(total_xp):
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

    for rank, low, high in rank_ranges:
        if total_xp >= low:
            span = high - low + 1
            level_span = span // 10
            level = min((total_xp - low) // level_span + 1, 10)
            current_level_xp = total_xp - (low + (level - 1) * level_span)
            
            return {
                'rank': rank,
                'level': level,
                'display': f"{rank}-{level}",
                'xp_needed': (low + level * level_span) - total_xp if level < 10 else 0,
                'current_level_xp': current_level_xp,
                'level_span': level_span,
                'range_low': low,
                'range_high': high
            }

    # Fallback for XP below minimum
    return {
        'rank': 'G',
        'level': 1,
        'display': 'G-1',
        'xp_needed': rank_ranges[-1][1] - total_xp,  # Distance to rank G minimum
        'current_level_xp': 0,
        'level_span': rank_ranges[-1][1] // 10,
        'range_low': 0,
        'range_high': rank_ranges[-1][2]
    }

@exam_bp.route('/')
@login_required
def exam():
    if current_user.exam_history:
        return redirect(url_for('dashboard'))
    return render_template('exam.html')

@exam_bp.route('/submit_exam', methods=['POST'])
@login_required
def submit_exam():
    try:
        data = request.get_json()
        
        # Convert all metric values to float
        metrics = {
            # Strength metrics
            'deadlift_kg': float(data.get('deadlift_kg', 0)),
            'benchpress_kg': float(data.get('benchpress_kg', 0)),
            'squat_kg': float(data.get('squat_kg', 0)),
            'pushups': float(data.get('pushups', 0)),
            'pullups': float(data.get('pullups', 0)),
            'squats': float(data.get('squats', 0)),
            'deadhang':float(data.get('deadhang', 0)),
            
            # Dexterity metrics
            'typing_wpm': float(data.get('typing_wpm', 0)),
            'typing_accuracy': float(data.get('typing_accuracy', 0)),
            'reaction_time': float(data.get('reaction_time', 0)),
            'tap_accuracy': float(data.get('tap_accuracy', 0)),
            'cube_time': float(data.get('cube_time', 0)),
            
            # Perception metrics
            'pattern_recognition': float(data.get('pattern_recognition', 0)),
            'spatial_rotation': float(data.get('spatial_rotation', 0)),
            'auditory_discrimination': float(data.get('auditory_discrimination', 0)),
            'peripheral_response': float(data.get('peripheral_response', 0)),
            'color_diff_level': float(data.get('color_diff_level', 0)),
            'object_tracking': float(data.get('object_tracking', 0)),
            
            # Agility metrics
            'sprint_100m': float(data.get('sprint_100m', 0)),
            'side_hops': float(data.get('side_hops', 0)),
            'y_test': float(data.get('y_test', 0)),
            'dual_task_score': float(data.get('dual_task_score', 0)),
            'change_direction_reaction': float(data.get('change_direction_reaction', 0)),
            
            # Vitality metrics
            'rhr': float(data.get('rhr', 0)),
            'sleep_quality': float(data.get('sleep_quality', 0)),
            'vo2_max': float(data.get('vo2_max', 0)),
            'hrv': float(data.get('hrv', 0)),
            'step_test_recovery': float(data.get('step_test_recovery', 0)),
            'hydration_liters': float(data.get('hydration_liters', 0)),
            
            # Willpower metrics
            'plank_time': float(data.get('plank_time', 0)),
            'meditation_minutes': float(data.get('meditation_minutes', 0)),
            'deep_work_block': float(data.get('deep_work_block', 0)),
            'detox_tasks_done': float(data.get('detox_tasks_done', 0)),
            'delayed_gratification_score': float(data.get('delayed_gratification_score', 0)),
            'wall_sit_time': float(data.get('wall_sit_time', 0)),
            'wakeup_consistency': float(data.get('wakeup_consistency', 0)),
            
            # Charisma metrics
            'empathy_score': float(data.get('empathy_score', 0)),
            'active_listening_minutes': float(data.get('active_listening_minutes', 0)),
            'new_social_interactions': float(data.get('new_social_interactions', 0)),
            'conflict_resolution_score': float(data.get('conflict_resolution_score', 0)),
            'humor_score': float(data.get('humor_score', 0)),
            'public_presence_score': float(data.get('public_presence_score', 0)),

            #inteligence metrics
            'memory_span': float(data.get('memory_span', 0)),
            'logic_test_percentile': float(data.get('logic_test_percentile', 0)),
            'problem_solving_speed': float(data.get('problem_solving_speed', 0)),
            'reading_speed_wpm': float(data.get('reading_speed_wpm', 0)),
            'code_challenge_score': float(data.get('code_challenge_score', 0))

        }
        
        # Get user attributes
        bodyweight = float(data.get('bodyweight', 70))
        gender = data.get('gender', 'male')
        body_type = data.get('bodyType', 'mesomorph')
        
        print("\nMetrics Recieved :", metrics)
        strength_score_value = strength_score(metrics, bodyweight, gender)
        strength_xp = score_to_xp(strength_score_value)

        dexterity_score_value = dexterity_score(metrics)
        dexterity_xp = score_to_xp(dexterity_score_value)

        perception_score_value = perception_score(metrics)
        perception_xp = score_to_xp(perception_score_value)

        agility_score_value = agility_score(metrics, gender, bodyweight, body_type)
        agility_xp = score_to_xp(agility_score_value)

        vitality_score_value = vitality_score(metrics, gender, bodyweight)
        vitality_xp = score_to_xp(vitality_score_value)

        willpower_score_value = willpower_score(metrics)
        willpower_xp = score_to_xp(willpower_score_value)

        charisma_score_value = charisma_score(metrics)
        charisma_xp = score_to_xp(charisma_score_value)

        intelligence_score_value = intelligence_score(metrics)    
        intelligence_xp = score_to_xp(intelligence_score_value)

        # Calculate total XP
        total_xp = (
            strength_xp + dexterity_xp + perception_xp + agility_xp +
            vitality_xp + willpower_xp + charisma_xp + intelligence_xp
        )
        print("\nTotal XP:", total_xp)
        # Get rank and level information
        print("\nGetting rank info")
        rank_info = get_rank_with_level(total_xp)
        print("\nRank info:", rank_info)
        # Prepare results dictionary
        results = {
            'strength_score': strength_score_value,
            'strength_xp': strength_xp,
            'dexterity_score': dexterity_score_value,
            'dexterity_xp': dexterity_xp,
            'perception_score': perception_score_value,
            'perception_xp': perception_xp,
            'agility_score': agility_score_value,
            'agility_xp': agility_xp,
            'vitality_score': vitality_score_value,
            'vitality_xp': vitality_xp,
            'willpower_score': willpower_score_value,
            'willpower_xp': willpower_xp,
            'charisma_score': charisma_score_value,
            'charisma_xp': charisma_xp,
            'intelligence_score': intelligence_score_value,
            'intelligence_xp': intelligence_xp,
            'total_xp': total_xp,
            'rank_info': rank_info
        }
        print("\nAdding exam Results:")
        # Store exam results in user's document
        current_user.add_exam_result(data, results)
        print("\nExam Results added")
        # Update user stats
        stats = {
            'xp': total_xp,
            'level': rank_info['level'],
            'rank': rank_info['rank'],
            'strength': strength_xp,
            'dexterity': dexterity_xp,
            'perception': perception_xp,
            'agility': agility_xp,
            'vitality': vitality_xp,
            'willpower': willpower_xp,
            'charisma': charisma_xp,
            'intelligence': intelligence_xp
        }
        print("\nUpdating user stats: ")
        current_user.update_stats(stats)
        
        current_user.xp = total_xp
        current_user.rank = rank_info['rank']
        current_user.level = rank_info['level']
        current_user.update_title()  # Update the title based on new rank and level
        current_user.save()
        
        return jsonify({
            'success': True,
            'message': 'Exam submitted successfully!',
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error submitting exam: {str(e)}'
        }), 500

