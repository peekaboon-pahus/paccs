from flask import Flask, render_template, request, jsonify
import json
import os
import hashlib
import random

app = Flask(__name__)

# Load films database
def load_films():
    try:
        with open('films_database.json', 'r') as f:
            return json.load(f)
    except:
        return []

# Load users
def load_users():
    try:
        with open('paccs_users.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open('paccs_users.json', 'w') as f:
        json.dump(users, f, indent=2)

films_data = load_films()

# ========== PAGE ROUTES ==========

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/browse')
def browse():
    return render_template('index.html')

@app.route('/analyze')
def analyze():
    return render_template('index.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/submit')
def submit_page():
    return render_template('submit.html')

@app.route('/music')
def music_page():
    return render_template('music.html')

# ========== API ROUTES ==========

@app.route('/api/films')
def get_films():
    return jsonify({
        'films': films_data[:100] if films_data else [],
        'total': len(films_data),
        'analyzed': len(films_data),
        'avg_score': 7.2
    })

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    users = load_users()
    
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    name = data.get('name', '')
    
    if email in users:
        return jsonify({'success': False, 'error': 'Email already exists'})
    
    if len(password) < 6:
        return jsonify({'success': False, 'error': 'Password must be 6+ characters'})
    
    users[email] = {
        'name': name,
        'email': email,
        'password': hashlib.sha256(password.encode()).hexdigest(),
        'credits': 3,
        'films': []
    }
    save_users(users)
    
    return jsonify({
        'success': True,
        'user': {'name': name, 'email': email, 'credits': 3}
    })

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    users = load_users()
    
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    if email not in users:
        return jsonify({'success': False, 'error': 'Email not found'})
    
    if users[email]['password'] != hashed:
        return jsonify({'success': False, 'error': 'Wrong password'})
    
    return jsonify({
        'success': True,
        'user': {
            'name': users[email]['name'],
            'email': email,
            'credits': users[email]['credits']
        }
    })

@app.route('/api/user/stats')
def user_stats():
    email = request.args.get('email', '')
    users = load_users()
    
    if email in users:
        return jsonify({
            'success': True,
            'films_analyzed': len(users[email].get('films', [])),
            'avg_score': 7.5,
            'festival_matches': 12,
            'recent_films': users[email].get('films', [])[-5:]
        })
    return jsonify({'success': False})

@app.route('/api/submit-film', methods=['POST'])
def submit_film():
    data = request.json
    film = data.get('film', {})
    email = data.get('email', '')
    
    users = load_users()
    
    if email not in users:
        return jsonify({'success': False, 'error': 'User not found'})
    
    if users[email]['credits'] <= 0:
        return jsonify({'success': False, 'error': 'No credits remaining'})
    
    # Content check
    from content_checker import ContentChecker
    checker = ContentChecker()
    check_result = checker.check_film(film)
    
    if not check_result['approved']:
        return jsonify({
            'success': False, 
            'error': 'Content check failed',
            'issues': check_result['issues']
        })
    
    # Use credit
    users[email]['credits'] -= 1
    
    # Add film
    film_id = f"FILM_{len(users[email].get('films', [])) + 1}"
    film['id'] = film_id
    film['score'] = round(5 + random.random() * 4, 1)
    film['date'] = __import__('datetime').datetime.now().isoformat()
    
    if 'films' not in users[email]:
        users[email]['films'] = []
    users[email]['films'].append(film)
    
    save_users(users)
    
    return jsonify({
        'success': True,
        'film_id': film_id,
        'credits_remaining': users[email]['credits'],
        'safety_check': check_result
    })

@app.route('/api/process', methods=['POST'])
def process_film():
    data = request.json
    film_index = data.get('film_index', 0)
    
    if films_data and film_index < len(films_data):
        film = films_data[film_index]
    else:
        film = {'title': 'Unknown'}
    
    score = round(5 + random.random() * 4, 1)
    
    return jsonify({
        'success': True,
        'film_id': f"FILM_{film_index}",
        'final_score': score,
        'score': score,
        'pathway': random.choice(['FESTIVAL', 'STREAMING', 'THEATRICAL']),
        'success_prediction': {
            'festival_selection': random.randint(40, 90),
            'distribution_deal': random.randint(20, 60),
            'award_nomination': random.randint(5, 30),
            'viral_potential': random.randint(3, 25)
        },
        'comparison': {
            'overall': {'percentile': random.randint(60, 95)},
            'genre': {'percentile': random.randint(50, 90)}
        },
        'quality_assessment': {'score': round(6 + random.random() * 3, 1)},
        'market_assessment': {'score': round(5 + random.random() * 4, 1)},
        'revenue_estimate': {
            'low_estimate': random.randint(1000, 5000),
            'high_estimate': random.randint(5000, 20000)
        },
        'festival_matches': [
            {'name': 'Sundance', 'match_score': random.randint(70, 95)},
            {'name': 'SXSW', 'match_score': random.randint(60, 90)},
            {'name': 'Tribeca', 'match_score': random.randint(55, 85)}
        ],
        'distributor_matches': [
            {'name': 'A24', 'match_score': random.randint(60, 90)},
            {'name': 'Netflix', 'match_score': random.randint(50, 85)},
            {'name': 'MUBI', 'match_score': random.randint(55, 88)}
        ]
    })

@app.route('/api/analyze-music', methods=['POST'])
def analyze_music():
    data = request.json
    
    genre = data.get('genre', 'ambient')
    tempo = data.get('tempo_bpm', 120)
    duration = data.get('duration_seconds', 180)
    
    # Genre mappings
    genre_data = {
        'orchestral': {'film_fit': ['drama', 'epic', 'documentary'], 'license_value': 'high'},
        'electronic': {'film_fit': ['sci-fi', 'thriller', 'action'], 'license_value': 'medium'},
        'ambient': {'film_fit': ['documentary', 'drama', 'art-house'], 'license_value': 'medium'},
        'acoustic': {'film_fit': ['indie', 'romance', 'documentary'], 'license_value': 'medium'},
        'rock': {'film_fit': ['action', 'comedy', 'coming-of-age'], 'license_value': 'medium'},
        'jazz': {'film_fit': ['noir', 'drama', 'romance'], 'license_value': 'high'},
        'folk': {'film_fit': ['indie', 'documentary', 'drama'], 'license_value': 'low'},
        'hip-hop': {'film_fit': ['urban', 'documentary', 'comedy'], 'license_value': 'medium'},
        'classical': {'film_fit': ['period', 'drama', 'documentary'], 'license_value': 'high'}
    }.get(genre, {'film_fit': ['general'], 'license_value': 'medium'})
    
    # Calculate scores
    scores = {
        'production_quality': round(6.0 + random.random() * 3.5, 1),
        'composition': round(5.5 + random.random() * 4, 1),
        'emotional_impact': round(6.0 + random.random() * 3.5, 1),
        'originality': round(5.0 + random.random() * 4, 1),
        'sync_potential': round(6.0 + random.random() * 3.5, 1),
        'versatility': round(5.5 + random.random() * 4, 1)
    }
    
    overall = sum(scores.values()) / len(scores)
    
    # Mood detection
    if tempo < 80:
        mood = random.choice(['melancholic', 'peaceful', 'mysterious'])
    elif tempo < 120:
        mood = random.choice(['romantic', 'hopeful', 'nostalgic'])
    else:
        mood = random.choice(['uplifting', 'energetic', 'tense'])
    
    # Scene types
    scene_map = {
        'uplifting': ['victory moments', 'happy endings', 'montages'],
        'melancholic': ['sad scenes', 'flashbacks', 'endings'],
        'tense': ['chase scenes', 'suspense', 'confrontations'],
        'peaceful': ['nature scenes', 'meditation', 'transitions'],
        'energetic': ['action sequences', 'sports', 'party scenes'],
        'mysterious': ['reveals', 'investigations', 'openings'],
        'romantic': ['love scenes', 'reunions', 'proposals'],
        'hopeful': ['character growth', 'new beginnings', 'sunrise scenes'],
        'nostalgic': ['flashbacks', 'memories', 'reunions']
    }
    
    # Revenue estimate
    if overall >= 8:
        revenue = '$500 - $5,000'
    elif overall >= 7:
        revenue = '$200 - $2,000'
    elif overall >= 6:
        revenue = '$50 - $500'
    else:
        revenue = '$0 - $100'
    
    # Recommendations
    recs = []
    if scores['production_quality'] < 7:
        recs.append('Consider professional mixing/mastering')
    if scores['originality'] < 7:
        recs.append('Add unique elements to stand out')
    if scores['sync_potential'] < 7:
        recs.append('Create instrumental version for sync licensing')
    if not recs:
        recs.append('Track is ready for sync licensing submissions!')
    
    return jsonify({
        'overall_score': round(overall, 1),
        'track_info': {
            'genre': genre,
            'tempo_bpm': tempo,
            'duration': f"{duration // 60}:{duration % 60:02d}",
            'detected_mood': mood.title()
        },
        'scores': scores,
        'film_suitability': {
            'best_fit_genres': genre_data['film_fit'],
            'scene_types': scene_map.get(mood, ['general scenes']),
            'sync_license_value': genre_data['license_value']
        },
        'revenue_potential': {
            'sync_license_range': revenue
        },
        'recommendations': recs
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)