# XP Calculations Module - Realistic XP system with gender & weight adaptation

import math

def normalize_score(value, noob, average, elite, inverse=False):
    value = float(value)
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

def score_to_xp(score):
    x = (score - 50) / 16.67
    sigmoid = 1 / (1 + math.exp(-x))
    xp = 7000 + (sigmoid * (60000 - 7000))
    return round(xp)

def calculate_category_score(metrics, category_metrics):
    scores = []
    for metric_name, (noob, avg, elite, inverse) in category_metrics.items():
        if metric_name in metrics:
            scores.append(normalize_score(metrics[metric_name], noob, avg, elite, inverse))
    return round(sum(scores) / len(scores), 2) if scores else 0

# --- Category Functions ---

def strength_score(metrics, bodyweight=70, gender='male'):
    if gender == 'male':
        standards = {
            'deadlift_1rm': (bodyweight * 0.98, bodyweight * 1.8, bodyweight * 2.8),
            'bench_press_1rm': (bodyweight * 0.6, bodyweight * 1.16, bodyweight * 1.85),
            'squat_1rm': (bodyweight * 0.81, bodyweight * 1.51, bodyweight * 2.43)
        }
    else:
        standards = {
            'deadlift_1rm': (bodyweight * 0.58, bodyweight * 1.3, bodyweight * 2.32),
            'bench_press_1rm': (bodyweight * 0.26, bodyweight * 0.715, bodyweight * 1.4),
            'squat_1rm': (bodyweight * 0.45, bodyweight * 1.09, bodyweight * 2.0)
        }

    standards.update({
        'pullups': (1 if gender == 'female' else 5, 5 if gender == 'female' else 12, 12 if gender == 'female' else 20),
        'pushups': (5 if gender == 'female' else 15, 25 if gender == 'female' else 30, 50),
        'plank_hold': (60, 120, 240),
        'wall_sit': (45, 90, 180)
    })

    category_metrics = {}
    for k, v in standards.items():
        if len(v) == 4:
            category_metrics[k] = v
        else:
            category_metrics[k] = (*v, False)

    return calculate_category_score(metrics, category_metrics)


def vitality_score(metrics, gender='male', bodyweight=70):
    rhr_norm = (85, 70, 55) if gender == 'male' else (90, 75, 60)
    hydration_target = 0.035 * bodyweight  # Liters per kg bodyweight

    category_metrics = {
        'resting_heart_rate': (*rhr_norm, True),
        'step_test_recovery': (120, 102, 75, True),
        'sleep_duration': (6, 7, 9, False),
        'hydration': (hydration_target * 0.6, hydration_target, hydration_target * 1.3, False)
    }
    return calculate_category_score(metrics, category_metrics)

def agility_score(metrics, gender='male', bodyweight=70):
    if gender == 'male':
        sprint = (15.5, 13.0, 11.0)
    else:
        sprint = (17.0, 14.5, 12.5)

    category_metrics = {
        'sprint_100m': (*sprint, True),
        'side_hops': (15, 27, 40, False),
        'change_direction': (1000, 800, 700, True),
        'dual_task_score': (50, 70, 90, False)
    }
    return calculate_category_score(metrics, category_metrics)

def dexterity_score(metrics):
    category_metrics = {
        'typing_wpm': (40, 60, 80, False),
        'typing_accuracy': (85, 95, 99, False),
        'reaction_time': (300, 250, 200, True),
        'cube_time': (40, 30, 20, True)
    }
    return calculate_category_score(metrics, category_metrics)

def intelligence_score(metrics):
    category_metrics = {
        'memory_span': (6, 9, 12, False),
        'logic_test': (40, 60, 80, False),
        'reading_speed': (300, 500, 800, False),
        'code_challenge_score': (50, 70, 90, False)
    }
    return calculate_category_score(metrics, category_metrics)

def charisma_score(metrics):
    category_metrics = {
        'empathy_score': (50, 75, 90, False),
        'new_socials': (2, 5, 8, False),
        'conflict_resolution': (60, 80, 90, False),
        'public_presence': (50, 75, 90, False)
    }
    return calculate_category_score(metrics, category_metrics)

def willpower_score(metrics):
    category_metrics = {
        'plank_hold': (60, 120, 240, False),
        'meditation': (5, 15, 30, False),
        'deep_work': (30, 60, 120, False),
        'morning_routine': (3, 5, 7, False),
        'wall_sit': (60, 90, 180, False)
    }
    return calculate_category_score(metrics, category_metrics)

def perception_score(metrics):
    category_metrics = {
        'pattern_recognition': (60, 80, 95, False),
        'spatial_rotation': (5, 8, 10, False),
        'auditory_discrimination': (10, 15, 20, False),
        'color_differentiation': (13, 23, 35, True)
    }
    return calculate_category_score(metrics, category_metrics)

def calculate_total_xp(metrics, bodyweight=70, gender='male'):
    categories = {
        'strength': strength_score(metrics, bodyweight, gender),
        'vitality': vitality_score(metrics, gender, bodyweight),
        'agility': agility_score(metrics, gender, bodyweight),
        'dexterity': dexterity_score(metrics),
        'intelligence': intelligence_score(metrics),
        'charisma': charisma_score(metrics),
        'willpower': willpower_score(metrics),
        'perception': perception_score(metrics)
    }

    category_xp = {name: score_to_xp(score) for name, score in categories.items()}
    total_score = sum(categories.values()) / len(categories)
    total_xp = score_to_xp(total_score)

    return {
        'scores': {**categories, 'total': total_score},
        'xp': {**category_xp, 'total': total_xp}
    }
