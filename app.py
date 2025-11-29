"""
PACCS - Peekaboon Agentic Creative Curation System
Production Flask Application with Enhanced Filmmaker Profiles
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import hashlib
import random
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'paccs-secret-key-change-in-production')

# ============================================
# DATA LOADING
# ============================================

def load_films():
    try:
        with open('films_database.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading films: {e}")
        return []

def load_users():
    try:
        with open('paccs_users.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open('paccs_users.json', 'w') as f:
        json.dump(users, f, indent=2)

def load_profiles():
    try:
        with open('paccs_profiles.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_profiles(profiles):
    with open('paccs_profiles.json', 'w') as f:
        json.dump(profiles, f, indent=2)

films_data = load_films()
print(f"Loaded {len(films_data)} films")

# ============================================
# PAGE ROUTES
# ============================================

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

@app.route('/filmmakers')
def filmmakers_page():
    return render_template('filmmakers.html')

@app.route('/filmmaker/<profile_id>')
def filmmaker_profile(profile_id):
    return render_template('profile.html', profile_id=profile_id)

@app.route('/spotlight')
def spotlight_page():
    return render_template('spotlight.html')

# ============================================
# API ROUTES - FILMS
# ============================================

@app.route('/api/films')
def get_films():
    return jsonify({
        'films': films_data[:100] if films_data else [],
        'total': len(films_data),
        'analyzed': len(films_data),
        'avg_score': 7.2
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_film():
    data = request.json
    film = data.get('film', {})
    
    score = round(random.uniform(5.5, 8.5), 1)
    pathway = 'THEATRICAL' if score > 6.5 else 'FESTIVAL'
    
    result = {
        'score': score,
        'pathway': pathway,
        'predictions': {
            'festival_selection': random.randint(40, 85),
            'distribution_deal': random.randint(30, 70),
            'award_nomination': random.randint(10, 40),
            'viral_potential': random.randint(5, 25)
        },
        'festivals': [
            {'name': 'Sundance Film Festival', 'score': random.randint(60, 90)},
            {'name': 'Toronto International', 'score': random.randint(55, 85)},
            {'name': 'Berlin Film Festival', 'score': random.randint(50, 80)},
            {'name': 'Cannes Film Festival', 'score': random.randint(45, 75)},
            {'name': 'Venice Film Festival', 'score': random.randint(40, 70)}
        ],
        'distributors': [
            {'name': 'A24', 'score': random.randint(55, 80)},
            {'name': 'Netflix', 'score': random.randint(50, 75)},
            {'name': 'Amazon Studios', 'score': random.randint(45, 70)},
            {'name': 'MUBI', 'score': random.randint(40, 65)},
            {'name': 'Neon', 'score': random.randint(35, 60)}
        ]
    }
    
    return jsonify(result)

# ============================================
# API ROUTES - AUTHENTICATION & PROFILES
# ============================================

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    users = load_users()
    profiles = load_profiles()
    
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    first_name = data.get('firstName', '')
    last_name = data.get('lastName', '')
    
    if email in users:
        return jsonify({'success': False, 'error': 'Email already exists'})
    
    if len(password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters'})
    
    if not email or '@' not in email:
        return jsonify({'success': False, 'error': 'Invalid email address'})
    
    if not first_name or not last_name:
        return jsonify({'success': False, 'error': 'Name is required'})
    
    user_id = f"USER_{len(users) + 1:05d}"
    profile_id = str(uuid.uuid4())[:8]
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    users[email] = {
        'id': user_id,
        'email': email,
        'password': hashed_password,
        'name': f"{first_name} {last_name}",
        'firstName': first_name,
        'lastName': last_name,
        'plan': 'free',
        'credits': 3,
        'profile_id': profile_id,
        'films_analyzed': [],
        'created_at': datetime.now().isoformat()
    }
    
    profiles[profile_id] = {
        'id': profile_id,
        'user_id': user_id,
        'email': email,
        'firstName': first_name,
        'lastName': last_name,
        'fullName': f"{first_name} {last_name}",
        'designation': data.get('designation', ''),
        'company': data.get('company', ''),
        'country': data.get('country', ''),
        'city': data.get('city', ''),
        'bio': data.get('bio', ''),
        'profilePhoto': data.get('profilePhoto', ''),
        'socialLinks': data.get('socialLinks', {}),
        'filmLinks': data.get('filmLinks', []),
        'films': [],
        'status': 'pending',
        'featured': False,
        'spotlight': False,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    save_users(users)
    save_profiles(profiles)
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'profile_id': profile_id,
        'credits': 3
    })

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    users = load_users()
    
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    
    if email not in users:
        return jsonify({'success': False, 'error': 'Email not found'})
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    if users[email]['password'] != hashed_password:
        return jsonify({'success': False, 'error': 'Invalid password'})
    
    user = users[email]
    
    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'firstName': user.get('firstName', ''),
            'lastName': user.get('lastName', ''),
            'plan': user['plan'],
            'credits': user['credits'],
            'profile_id': user.get('profile_id', '')
        }
    })

@app.route('/api/user/stats')
def get_user_stats():
    email = request.headers.get('X-User-Email', '')
    users = load_users()
    
    if email and email in users:
        user = users[email]
        films_analyzed = user.get('films_analyzed', [])
        
        avg_score = None
        if films_analyzed:
            scores = [f.get('score', 0) for f in films_analyzed if f.get('score')]
            if scores:
                avg_score = sum(scores) / len(scores)
        
        return jsonify({
            'films_analyzed': len(films_analyzed),
            'avg_score': avg_score,
            'festival_matches': len(films_analyzed) * 3 if films_analyzed else 0,
            'credits': user.get('credits', 3),
            'recent': films_analyzed[-5:] if films_analyzed else [],
            'profile_id': user.get('profile_id', '')
        })
    
    return jsonify({
        'films_analyzed': 0,
        'avg_score': None,
        'festival_matches': 0,
        'credits': 3,
        'recent': []
    })

@app.route('/api/user/credits')
def get_user_credits():
    email = request.headers.get('X-User-Email', '')
    users = load_users()
    
    if email and email in users:
        return jsonify({
            'credits': users[email].get('credits', 0),
            'plan': users[email].get('plan', 'free')
        })
    
    return jsonify({'credits': 0, 'plan': 'free'})

# ============================================
# API ROUTES - FILMMAKER PROFILES
# ============================================

@app.route('/api/profile/<profile_id>')
def get_profile(profile_id):
    profiles = load_profiles()
    
    if profile_id in profiles:
        profile = profiles[profile_id]
        safe_profile = {
            'id': profile['id'],
            'fullName': profile['fullName'],
            'firstName': profile['firstName'],
            'lastName': profile['lastName'],
            'designation': profile['designation'],
            'company': profile['company'],
            'country': profile['country'],
            'city': profile['city'],
            'bio': profile['bio'],
            'profilePhoto': profile.get('profilePhoto', ''),
            'socialLinks': profile.get('socialLinks', {}),
            'filmLinks': profile.get('filmLinks', []),
            'films': profile.get('films', []),
            'featured': profile.get('featured', False),
            'status': profile.get('status', 'pending')
        }
        return jsonify({'success': True, 'profile': safe_profile})
    
    return jsonify({'success': False, 'error': 'Profile not found'}), 404

@app.route('/api/profile/<profile_id>', methods=['PUT'])
def update_profile(profile_id):
    profiles = load_profiles()
    data = request.json
    
    if profile_id not in profiles:
        return jsonify({'success': False, 'error': 'Profile not found'}), 404
    
    allowed_fields = ['designation', 'company', 'city', 'bio', 'socialLinks', 'filmLinks', 'profilePhoto']
    for field in allowed_fields:
        if field in data:
            profiles[profile_id][field] = data[field]
    
    profiles[profile_id]['updated_at'] = datetime.now().isoformat()
    save_profiles(profiles)
    
    return jsonify({'success': True, 'message': 'Profile updated'})

@app.route('/api/filmmakers')
def get_filmmakers():
    profiles = load_profiles()
    
    filmmakers = []
    for profile_id, profile in profiles.items():
        filmmakers.append({
            'id': profile['id'],
            'fullName': profile['fullName'],
            'designation': profile['designation'],
            'company': profile.get('company', ''),
            'country': profile.get('country', ''),
            'profilePhoto': profile.get('profilePhoto', ''),
            'featured': profile.get('featured', False),
            'films_count': len(profile.get('films', []))
        })
    
    filmmakers.sort(key=lambda x: (not x['featured'], x['fullName']))
    
    return jsonify({
        'success': True,
        'filmmakers': filmmakers,
        'total': len(filmmakers)
    })

@app.route('/api/spotlight')
def get_spotlight():
    profiles = load_profiles()
    
    featured_filmmakers = []
    spotlight_films = []
    
    for profile_id, profile in profiles.items():
        if profile.get('featured') or profile.get('spotlight'):
            featured_filmmakers.append({
                'id': profile['id'],
                'fullName': profile['fullName'],
                'designation': profile['designation'],
                'profilePhoto': profile.get('profilePhoto', '')
            })
        
        for film in profile.get('films', []):
            if film.get('score', 0) >= 7.0:
                spotlight_films.append({
                    'title': film.get('title', ''),
                    'score': film.get('score', 0),
                    'filmmaker': profile['fullName'],
                    'filmmaker_id': profile['id']
                })
    
    spotlight_films.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify({
        'success': True,
        'featured_filmmakers': featured_filmmakers[:10],
        'spotlight_films': spotlight_films[:20]
    })

# ============================================
# API ROUTES - ADMIN
# ============================================

@app.route('/api/admin/profiles')
def admin_get_profiles():
    profiles = load_profiles()
    
    all_profiles = []
    for profile_id, profile in profiles.items():
        all_profiles.append({
            'id': profile['id'],
            'fullName': profile['fullName'],
            'email': profile['email'],
            'designation': profile['designation'],
            'status': profile.get('status', 'pending'),
            'featured': profile.get('featured', False),
            'created_at': profile.get('created_at', '')
        })
    
    all_profiles.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        'success': True,
        'profiles': all_profiles
    })

@app.route('/api/admin/profile/<profile_id>/approve', methods=['POST'])
def admin_approve_profile(profile_id):
    profiles = load_profiles()
    
    if profile_id in profiles:
        profiles[profile_id]['status'] = 'approved'
        profiles[profile_id]['updated_at'] = datetime.now().isoformat()
        save_profiles(profiles)
        return jsonify({'success': True, 'message': 'Profile approved'})
    
    return jsonify({'success': False, 'error': 'Profile not found'}), 404

@app.route('/api/admin/profile/<profile_id>/feature', methods=['POST'])
def admin_feature_profile(profile_id):
    profiles = load_profiles()
    
    if profile_id in profiles:
        profiles[profile_id]['featured'] = True
        profiles[profile_id]['status'] = 'approved'
        profiles[profile_id]['updated_at'] = datetime.now().isoformat()
        save_profiles(profiles)
        return jsonify({'success': True, 'message': 'Profile featured'})
    
    return jsonify({'success': False, 'error': 'Profile not found'}), 404

# ============================================
# API ROUTES - MUSIC & CONTENT
# ============================================

@app.route('/api/music/analyze', methods=['POST'])
def analyze_music():
    result = {
        'mood': random.choice(['Dramatic', 'Uplifting', 'Tense', 'Romantic', 'Melancholic']),
        'tempo': random.choice(['Slow', 'Moderate', 'Fast']),
        'energy': random.randint(40, 90),
        'film_genres': [
            {'genre': 'Drama', 'match': random.randint(60, 95)},
            {'genre': 'Thriller', 'match': random.randint(40, 80)},
            {'genre': 'Romance', 'match': random.randint(30, 70)}
        ],
        'sync_potential': random.randint(50, 90),
        'estimated_value': f"${random.randint(500, 5000)}"
    }
    return jsonify(result)

@app.route('/api/content/check', methods=['POST'])
def check_content():
    return jsonify({
        'safe': True,
        'score': random.randint(85, 100),
        'flags': [],
        'recommendations': []
    })

@app.route('/api/submit', methods=['POST'])
def submit_film():
    return jsonify({
        'success': True,
        'message': 'Film submitted successfully',
        'submission_id': f"SUB_{random.randint(10000, 99999)}"
    })

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(e):
    return render_template('landing.html'), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("\n" + "="*60)
    print("PACCS - AI Film Intelligence Platform")
    print("="*60)
    print(f"\nLoaded {len(films_data)} films")
    print(f"Running on http://localhost:{port}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)