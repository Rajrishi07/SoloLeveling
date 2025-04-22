# XP Scoring System - Refactored for Normalized 0-100 Scaling and Consistent XP Output

import math

def normalize_score(value, noob, average, elite, inverse=False):
    """
    Non-linear normalization using a piecewise curve:
    - Noob to Average: grows faster
    - Average to Elite: slower growth
    Ensures noobs still earn meaningful XP and elite feels earned
    """
    if inverse:
        value = max(min(value, noob), elite)
        if value >= average:
            score = ((noob - value) / (noob - average)) * 50
        else:
            score = 50 + ((average - value) / (average - elite)) * 50
    else:
        value = max(min(value, elite), noob)
        if value <= average:
            score = ((value - noob) / (average - noob)) * 50
        else:
            score = 50 + ((value - average) / (elite - average)) * 50
    return min(max(score, 0), 100)

def score_to_xp(score, scale=100000):
    """
    Convert a 0-100 score to XP with the following characteristics:
    - Minimum XP of 7000 (for score = 0)
    - Maximum XP of 100000 (for score = 100)
    - Non-linear growth using modified sigmoid:
      - Slower growth from 0-30 (noob range: 7000-40000 XP)
      - Faster growth from 30-60 (average range: 40000-75000 XP)
      - Slower growth from 60-100 (elite range: 75000-100000 XP)
    """
    # Normalize score to -3 to 3 range for sigmoid
    x = (score - 50) / 16.67  
    
    # Calculate sigmoid from 0 to 1
    sigmoid = 1 / (1 + math.exp(-x))
    
    # Scale sigmoid to 7000-100000 range
    xp = 7000 + (sigmoid * (100000 - 7000))
    
    return round(xp)

def calculate_total_xp(metrics, bodyweight=70, gender='male', body_type='mesomorph'):
    """
    Calculate total XP with category-wise breakdown
    Returns a dictionary with individual category scores, XP, and total XP
    """
    # Calculate individual category scores
    strength = strength_score(metrics, bodyweight, gender)
    dexterity = dexterity_score(metrics)
    perception = perception_score(metrics)
    agility = agility_score(metrics, gender, bodyweight, body_type)
    vitality = vitality_score(metrics, gender, bodyweight)
    willpower = willpower_score(metrics)
    charisma = charisma_score(metrics)
    
    # Calculate XP for each category
    strength_xp = score_to_xp(strength)
    dexterity_xp = score_to_xp(dexterity)
    perception_xp = score_to_xp(perception)
    agility_xp = score_to_xp(agility)
    vitality_xp = score_to_xp(vitality)
    willpower_xp = score_to_xp(willpower)
    charisma_xp = score_to_xp(charisma)
    
    # Calculate total score and XP
    total_score = (strength + dexterity + perception + agility + vitality + willpower + charisma) / 7
    total_xp = score_to_xp(total_score)
    
    return {
        'scores': {
            'strength': strength,
            'dexterity': dexterity,
            'perception': perception,
            'agility': agility,
            'vitality': vitality,
            'willpower': willpower,
            'charisma': charisma,
            'total': total_score
        },
        'xp': {
            'strength': strength_xp,
            'dexterity': dexterity_xp,
            'perception': perception_xp,
            'agility': agility_xp,
            'vitality': vitality_xp,
            'willpower': willpower_xp,
            'charisma': charisma_xp,
            'total': total_xp
        }
    }

# -------------------------- STRENGTH --------------------------
def strength_score(metrics, bodyweight=70, gender='male'):
    gender = gender.lower()
    bw = bodyweight
    strength_refs = {
        'male': {
            'deadlift_kg': (1.0, 2.0, 3.0),
            'benchpress_kg': (0.5, 1.25, 2.0),
            'squat_kg': (0.75, 1.75, 2.75),
            'pushups': (10, 35, 75),
            'pullups': (2, 12, 30),
            'squats': (10, 35, 75),
            'deadhang': (25, 60, 120)
        },
        'female': {
            'deadlift_kg': (0.8, 1.6, 2.4),
            'benchpress_kg': (0.25, 0.75, 1.5),
            'squat_kg': (0.5, 1.25, 2.0),
            'pushups': (2, 20, 50),
            'pullups': (1, 6, 15),
            'squats': (10, 30, 60),
            'deadhang': (25, 60, 130)
        }
    }
    refs = strength_refs[gender]
    scores = []
    for key, value in metrics.items():
        if key in refs:  # Only process strength-related metrics
            if 'kg' in key:
                noob, avg, elite = [r * bw for r in refs[key]]
            else:
                noob, avg, elite = refs[key]
            scores.append(normalize_score(value, noob, avg, elite))
    return round(sum(scores) / len(scores), 2) if scores else 0

# -------------------------- DEXTERITY --------------------------
def dexterity_score(metrics):
    refs = {
        'typing_wpm': (20, 40, 120),
        'typing_accuracy': (85, 92, 98),
        'reaction_time': (0.30, 0.273, 0.150),
        'tap_accuracy': (80, 90, 100),
        'cube_time': (120, 30, 8)
    }
    inverses = {'reaction_time', 'cube_time'}
    scores = []
    
    # Handle all metrics
    for key, value in metrics.items():
        if key in refs:  # Only process dexterity-related metrics
            noob, avg, elite = refs[key]
            scores.append(normalize_score(value, noob, avg, elite, inverse=(key in inverses)))
    
    if not scores:
        return 0
    return round(sum(scores) / len(scores), 2)

# -------------------------- AGILITY --------------------------
def agility_score(metrics, gender='male', bodyweight=70, body_type='mesomorph'):
    gender = gender.lower()
    refs = {
        'male': {
            'sprint_100m': (14.0, 12.0, 10.1),
            'side_hops': (25, 40, 50),
            'y_test': (60, 80, 100),
            'dual_task_score': (60, 80, 100),
            'change_direction_reaction': (0.90, 0.70, 0.50)
        },
        'female': {
            'sprint_100m': (16.0, 13.5, 11.5),
            'side_hops': (20, 35, 45),
            'y_test': (60, 80, 100),
            'dual_task_score': (60, 80, 100),
            'change_direction_reaction': (1.0, 0.8, 0.6)
        }
    }
    inverses = {'sprint_100m', 'change_direction_reaction'}
    
    # Add body type influence
    body_type = body_type.lower()
    body_type_modifier = {
        'ectomorph': 0.98,
        'mesomorph': 1.0,
        'endomorph': 1.05
    }.get(body_type, 1.0)

    if bodyweight > 80:
        bw_factor = 1.03 * body_type_modifier
    elif bodyweight < 60:
        bw_factor = 0.97 * body_type_modifier
    else:
        bw_factor = 1.0 * body_type_modifier  # Reduced penalty

    scores = []
    for key, value in metrics.items():
        if key in refs[gender]:  # Only process agility-related metrics
            noob, avg, elite = refs[gender][key]
            if key in inverses:
                value *= bw_factor  # Penalize time-based agility metrics with weight
            scores.append(normalize_score(value, noob, avg, elite, inverse=(key in inverses)))
    return round(sum(scores) / len(scores), 2) if scores else 0

# -------------------------- PERCEPTION --------------------------
def adjusted_color_score(level, min_level=0, max_level=30, base_score=100):
    """
    Calculate adjusted score for color differentiation based on level achieved.
    """
    if level <= min_level:
        return 0  # If no progress is made, score is 0
    if level >= max_level:
        return base_score  # If max level is reached, assign max score

    score = 0

    # Levels 0-10, scaling from 0 to 20
    if 0 <= level <= 10:
        score = ((level - 0) / (10 - 0)) * 20  # Scales from 0 to 20
    # Levels 10-15, scaling from 20 to 50
    elif 10 < level <= 15:
        score = ((level - 10) / (15 - 10)) * 30 + 20  # Scales from 20 to 50
    # Levels 15-23, scaling from 50 to 75
    elif 15 < level <= 23:
        score = ((level - 15) / (23 - 15)) * 25 + 50  # Scales from 50 to 75
    # Levels 23-30, scaling from 75 to 100
    elif level > 23:
        score = ((level - 23) / (30 - 23)) * 25 + 75  # Scales from 75 to 100

    return round(score)

def perception_score(metrics):
    refs = {
        'pattern_recognition': (40, 70, 100),
        'spatial_rotation': (40, 70, 100),
        'auditory_discrimination': (40, 70, 100),
        'peripheral_response': (60, 85, 100),
        'color_diff_level': (30, 70, 100),
        'object_tracking': (50, 75, 100)
    }
    scores = []
    for key, value in metrics.items():
        if key in refs:  # Only process perception-related metrics

            if key == 'color_diff_level':
                scores.append(adjusted_color_score(float(value)))
            elif key in ['spatial_rotation', 'peripheral_response', 'object_tracking']:
                # Multiply the input value by 10 before normalization
                value = float(value) * 10
                noob, avg, elite = refs[key]
                scores.append(normalize_score(value, noob, avg, elite))
            elif key == 'auditory_discrimination':
                # Multiply the input value by 5 before normalization
                value = float(value) * 5
                noob, avg, elite = refs[key]
                scores.append(normalize_score(value, noob, avg, elite))
            else:
                noob, avg, elite = refs[key]
                scores.append(normalize_score(float(value), noob, avg, elite))
    return round(sum(scores) / len(scores), 2) if scores else 0

# -------------------------- VITALITY --------------------------
def vitality_score(metrics, gender='male', bodyweight=70):
    gender = gender.lower()
    refs = {
        'male': {
            'rhr': (90, 75, 52),
            'sleep_quality': (60, 80, 100),
            'vo2_max': (35, 42, 60),
            'hrv': (50, 70, 100),
            'step_test_recovery': (30, 40, 50),
            'hydration_liters': (2.0, 2.5, 3.0)
        },
        'female': {
            'rhr': (95, 79, 56),
            'sleep_quality': (60, 80, 100),
            'vo2_max': (30, 38, 55),
            'hrv': (50, 70, 100),
            'step_test_recovery': (30, 40, 50),
            'hydration_liters': (1.8, 2.3, 2.8)
        }
    }
    inverses = {'rhr'}
    bw_liters = bodyweight * 0.04  # Approximate daily hydration need in liters
    scores = []
    for key, value in metrics.items():
        if key in refs[gender]:  # Only process vitality-related metrics
            if key == 'hydration_liters':
                noob = bw_liters * 0.7
                avg = bw_liters * 0.9
                elite = bw_liters * 1.1
            else:
                noob, avg, elite = refs[gender][key]
            scores.append(normalize_score(value, noob, avg, elite, inverse=(key in inverses)))
    return round(sum(scores) / len(scores), 2) if scores else 0

# -------------------------- WILLPOWER --------------------------
def willpower_score(metrics):
    refs = {
        'plank_time': (90, 150, 300),
        'meditation_minutes': (10, 15, 30),
        'deep_work_block': (20, 60, 90),
        'detox_tasks_done': (3, 5, 7),
        'delayed_gratification_score': (60, 80, 100),
        'wall_sit_time': (60, 120, 180),
        'wakeup_consistency': (3, 5, 7)
    }
    scores = []
    for key, value in metrics.items():
        if key in refs:  # Only process willpower-related metrics
            noob, avg, elite = refs[key]
            scores.append(normalize_score(value, noob, avg, elite))
    return round(sum(scores) / len(scores), 2) if scores else 0

# -------------------------- CHARISMA --------------------------
def charisma_score(metrics):
    refs = {
        'empathy_score': (40, 70, 100),
        'active_listening_minutes': (10, 30, 60),
        'new_social_interactions': (1, 4, 7),
        'conflict_resolution_score': (40, 70, 100),
        'humor_score': (40, 70, 100),
        'public_presence_score': (40, 70, 100)
    }
    scores = []
    for key, value in metrics.items():
        if key in refs:  # Only process charisma-related metrics
            noob, avg, elite = refs[key]
            scores.append(normalize_score(value, noob, avg, elite))
    return round(sum(scores) / len(scores), 2) if scores else 0
# -------------------------- INTELLIGENCE --------------------------
def intelligence_score(metrics):
    refs = {
        'memory_span': (5, 7, 10),
        'logic_test_percentile': (40, 70, 95),
        'problem_solving_speed': (180, 90, 30),  # Lower is better
        'reading_speed_wpm': (150, 250, 450),
        'code_challenge_score': (30, 70, 95)
    }
    inverses = {'problem_solving_speed'}
    scores = []

    for key, value in metrics.items():
        if key in refs:  # Only process intelligence-related metrics
            noob, avg, elite = refs[key]
            scores.append(normalize_score(value, noob, avg, elite, inverse=(key in inverses)))

    return round(sum(scores) / len(scores), 2) if scores else 0
