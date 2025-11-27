"""
PACCS - Peekaboon Agentic Creative Curation System
Production Flask Application
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import hashlib
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'paccs-secret-key-change-in-production')

# ============================================
# DATA LOADING
# ============================================

def load_films():
    """Load films database"""
    try:
        with open('films_database.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading films: {e}")
        return []

def load_users():
    """Load users database"""
    try:
        with open('paccs_users.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    """Save users database"""
    with open('paccs_users.json', 'w') as f:
        json.dump(users, f, indent=2)

# Load films on startup
films_data = load_films()
print(f"Loaded {len(films_data)} films")

# ============================================
# PAGE ROUTES
# ============================================

@app.route('/')
def landing():
    """Landing page"""
    return render_template('landing.html')

@app.route('/browse')
def browse():
    """Browse films page"""
    return render_template('index.html')

@app.route('/analyze')
def analyze():
    """Analyze page - same as browse"""
    return render_template('index.html')

@app.route('/signup')
def signup_page():
    """Signup page"""
    return render_template('signup.html')

@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')

@app.route('/dashboard')
def dashboard_page():
    """User dashboard"""
    return render_template('dashboard.html')

@app.route('/submit')
def submit_page():
    """Submit film page"""
    return render_template('submit.html')

@app.route('/music')
def music_page():
    """Music analyzer page"""
    return render_template('music.html')

# ============================================
# API ROUTES - FILMS
# ============================================

@app.route('/api/films')
def get_films():
    """Get films for browse page"""
    return jsonify({
        'films': films_data[:100] if films_data else [],
        'total': len(films_data),
        'analyzed': len(films_data),
        'avg_score': 7.2
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_film():
    """Analyze a film and return results"""
    data = request.json
    film = data.get('film', {})
    
    # Generate analysis (in production, this would use AI agents)
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
# API ROUTES - AUTHENTICATION
# ============================================

@app.route('/api/signup', methods=['POST'])
def api_signup():
    """Handle user signup"""
    data = request.json
    users = load_users()
    
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    name = data.get('name', '')
    
    # Validation
    if email in users:
        return jsonify({'success': False, 'error': 'Email already exists'})
    
    if len(password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters'})
    
    if not email or '@' not in email:
        return jsonify({'success': False, 'error': 'Invalid email address'})
    
    # Create user
    user_id = f"USER_{len(users) + 1:05d}"
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    users[email] = {
        'id': user_id,
        'email': email,
        'password': hashed_password,
        'name': name,
        'plan': 'free',
        'credits': 3,
        'films_analyzed': [],
        'created_at': datetime.now().isoformat()
    }
    
    save_users(users)
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'credits': 3
    })

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle user login"""
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
            'plan': user['plan'],
            'credits': user['credits']
        }
    })

@app.route('/api/user/stats')
def get_user_stats():
    """Get user statistics for dashboard"""
    email = request.headers.get('X-User-Email', '')
    users = load_users()
    
    if email and email in users:
        user = users[email]
        films_analyzed = user.get('films_analyzed', [])
        
        # Calculate average score only if films have been analyzed
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
            'recent': films_analyzed[-5:] if films_analyzed else []
        })
    
    # Default response for non-logged in or new users
    return jsonify({
        'films_analyzed': 0,
        'avg_score': None,
        'festival_matches': 0,
        'credits': 3,
        'recent': []
    })

@app.route('/api/user/credits')
def get_user_credits():
    """Get user credit balance"""
    email = request.headers.get('X-User-Email', '')
    users = load_users()
    
    if email and email in users:
        return jsonify({
            'credits': users[email].get('credits', 0),
            'plan': users[email].get('plan', 'free')
        })
    
    return jsonify({'credits': 0, 'plan': 'free'})

# ============================================
# API ROUTES - MUSIC ANALYZER
# ============================================

@app.route('/api/music/analyze', methods=['POST'])
def analyze_music():
    """Analyze music for film suitability"""
    data = request.json
    
    # Mock analysis results
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

# ============================================
# API ROUTES - CONTENT CHECKER
# ============================================

@app.route('/api/content/check', methods=['POST'])
def check_content():
    """Check content for safety"""
    data = request.json
    
    # Mock content check
    return jsonify({
        'safe': True,
        'score': random.randint(85, 100),
        'flags': [],
        'recommendations': []
    })

# ============================================
# API ROUTES - FILM SUBMISSION
# ============================================

@app.route('/api/submit', methods=['POST'])
def submit_film():
    """Handle film submission"""
    data = request.json
    
    # In production, save to database
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