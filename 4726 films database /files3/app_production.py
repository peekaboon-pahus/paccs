"""
PACCS Production Web Application
Complete system with authentication, PDF reports, and payment ready
"""
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, make_response
from database import FilmDatabase
from consensus import ConsensusProtocol
from auth import UserManager, login_required
from pdf_generator import PDFReportGenerator
import os
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Initialize systems
db = FilmDatabase()
consensus = ConsensusProtocol()
user_manager = UserManager()
pdf_generator = PDFReportGenerator()

# ============================================
# PUBLIC PAGES
# ============================================

@app.route('/')
def home():
    """Landing page"""
    if 'user_email' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/app')
def app_home():
    """Main application - redirect to dashboard or login"""
    if 'user_email' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

# ============================================
# AUTHENTICATION
# ============================================

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    """Signup page"""
    if request.method == 'GET':
        return render_template('signup.html')
    
    # Handle signup
    data = request.json or request.form
    result = user_manager.signup(
        email=data.get('email'),
        password=data.get('password'),
        name=data.get('name'),
        company=data.get('company', '')
    )
    
    if result['success']:
        session['user_email'] = data.get('email').lower()
        if request.is_json:
            return jsonify(result)
        return redirect(url_for('dashboard'))
    
    if request.is_json:
        return jsonify(result), 400
    return render_template('signup.html', error=result['error'])

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Login page"""
    if request.method == 'GET':
        return render_template('login.html')
    
    # Handle login
    data = request.json or request.form
    result = user_manager.login(
        email=data.get('email'),
        password=data.get('password')
    )
    
    if result['success']:
        session['user_email'] = data.get('email').lower()
        if request.is_json:
            return jsonify(result)
        return redirect(url_for('dashboard'))
    
    if request.is_json:
        return jsonify(result), 401
    return render_template('login.html', error=result['error'])

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('user_email', None)
    return redirect(url_for('home'))

# ============================================
# DASHBOARD (Protected)
# ============================================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user = user_manager.get_user(session['user_email'])
    return render_template('dashboard.html', user=user)

@app.route('/analyze')
@login_required
def analyze_page():
    """Film analysis page"""
    user = user_manager.get_user(session['user_email'])
    return render_template('index.html', user=user)

@app.route('/my-films')
@login_required
def my_films():
    """User's analyzed films"""
    user = user_manager.get_user(session['user_email'])
    films = user_manager.get_user_films(session['user_email'])
    return render_template('my_films.html', user=user, films=films)

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/films')
def get_films():
    """Get films for analysis"""
    pending = db.get_pending_films()
    reviewed = db.get_reviewed_films()
    stats = db.get_statistics()
    return jsonify({
        'pending': pending[:20],
        'reviewed': reviewed[:20],
        'stats': stats
    })

@app.route('/api/process', methods=['POST'])
def process_film():
    """Process a single film"""
    data = request.json
    film_id = data.get('film_id')
    
    film = db.get_film(film_id)
    if not film:
        return jsonify({'error': 'Film not found'}), 404
    
    # Check credits if user is logged in
    if 'user_email' in session:
        credit_result = user_manager.use_credit(session['user_email'])
        if not credit_result['success']:
            return jsonify(credit_result), 403
    
    # Process film
    decision = consensus.process_film(film, generate_report=True)
    db.update_film_status(film_id, 'reviewed')
    consensus.save_decisions()
    
    # Add to user history
    if 'user_email' in session:
        user_manager.add_film_to_history(session['user_email'], decision)
    
    return jsonify(decision)

@app.route('/api/batch', methods=['POST'])
def batch_process():
    """Process batch of films"""
    pending = db.get_pending_films()[:5]
    processed = 0
    
    for film in pending:
        consensus.process_film(film)
        db.update_film_status(film['id'], 'reviewed')
        processed += 1
    
    consensus.save_decisions()
    
    return jsonify({
        'processed': processed,
        'stats': consensus.get_statistics()
    })

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    return jsonify({
        'database': db.get_statistics(),
        'consensus': consensus.get_statistics(),
        'users': user_manager.get_stats()
    })

@app.route('/api/report/<film_id>')
def get_report(film_id):
    """Get report for a specific film"""
    for d in consensus.decisions:
        if d['film_id'] == film_id:
            return jsonify(d)
    return jsonify({'error': 'Report not found'}), 404

@app.route('/api/report/<film_id>/pdf')
def get_pdf_report(film_id):
    """Generate PDF report for a film"""
    for d in consensus.decisions:
        if d['film_id'] == film_id:
            html = pdf_generator.generate_report(d)
            response = make_response(html)
            response.headers['Content-Type'] = 'text/html'
            return response
    return jsonify({'error': 'Report not found'}), 404

@app.route('/api/user')
def get_user():
    """Get current user data"""
    if 'user_email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = user_manager.get_user(session['user_email'])
    return jsonify(user)

@app.route('/api/user/films')
def get_user_films():
    """Get user's analyzed films"""
    if 'user_email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    films = user_manager.get_user_films(session['user_email'])
    return jsonify(films)

# ============================================
# PAYMENT (Stripe Integration Ready)
# ============================================

@app.route('/api/purchase', methods=['POST'])
def purchase_credits():
    """Purchase credits (Stripe integration ready)"""
    if 'user_email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    plan = data.get('plan', 'basic')
    
    # Credit packages
    packages = {
        'basic': {'credits': 5, 'price': 15},
        'pro': {'credits': 15, 'price': 35},
        'unlimited': {'credits': 100, 'price': 99}
    }
    
    if plan not in packages:
        return jsonify({'error': 'Invalid plan'}), 400
    
    # TODO: Integrate Stripe payment here
    # For now, just add credits (for testing)
    result = user_manager.add_credits(
        session['user_email'], 
        packages[plan]['credits']
    )
    
    return jsonify({
        'success': True,
        'plan': plan,
        'credits_added': packages[plan]['credits'],
        'total_credits': result.get('credits', 0)
    })

# ============================================
# SUBMIT NEW FILM (User-submitted)
# ============================================

@app.route('/api/submit-film', methods=['POST'])
def submit_film():
    """Submit a new film for analysis"""
    if 'user_email' not in session:
        return jsonify({'error': 'Please login to submit a film'}), 401
    
    data = request.json
    
    # Create film entry
    film = {
        'id': f"USER_{secrets.token_hex(8)}",
        'title': data.get('title'),
        'director': data.get('director'),
        'country': data.get('country'),
        'duration_minutes': int(data.get('duration', 0)),
        'genre': data.get('genre'),
        'genres': [data.get('genre')],
        'themes': data.get('themes', []),
        'synopsis': data.get('synopsis', ''),
        'year': data.get('year'),
        'language': data.get('language'),
        'submitted_by': session['user_email'],
        'status': 'pending',
        'technical_quality': 6.5,  # Default
        'narrative_score': 6.5,
        'originality_score': 6.5
    }
    
    # Add to database
    db.films.append(film)
    db.save()
    
    return jsonify({
        'success': True,
        'film_id': film['id'],
        'message': 'Film submitted successfully!'
    })

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎬 PACCS Production Server")
    print("="*60)
    print("\n✨ Features Enabled:")
    print("   • User Authentication (Signup/Login)")
    print("   • Film Analysis with AI Agents")
    print("   • Success Predictions")
    print("   • Festival & Distributor Matching")
    print("   • Revenue Estimation")
    print("   • PDF Report Generation")
    print("   • User Dashboard")
    print("   • Credit System")
    print("\n📊 Statistics:")
    print(f"   • Total Films: {len(db.films)}")
    print(f"   • Total Users: {user_manager.get_all_users_count()}")
    print("\n🌐 Server running at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop\n")
    
    # Use port from environment (for hosting) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
