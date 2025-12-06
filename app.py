"""
PACCS - Peekaboon Agentic Creative Curation System
With AI Moderation, PDF Reports, Stripe Payments & Streaming
"""
from flask import Flask, render_template, request, jsonify, send_file, redirect
import json
import os
import hashlib
import random
import uuid
import re
from datetime import datetime, timedelta
from io import BytesIO
import stripe

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'paccs-secret-key-change-in-production')

# Stripe Configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')

# Credit Packages
CREDIT_PACKAGES = {
    'starter': {'name': 'Starter', 'credits': 5, 'price': 1000, 'price_display': '£10'},
    'pro': {'name': 'Pro', 'credits': 15, 'price': 2500, 'price_display': '£25'},
    'studio': {'name': 'Studio', 'credits': 40, 'price': 5000, 'price_display': '£50'},
}

# ============================================
# AI MODERATION SYSTEM
# ============================================

OFFENSIVE_WORDS = ['hate', 'kill', 'violence', 'terrorist', 'abuse', 'racist', 'nazi', 'porn', 'xxx', 'nude', 'nsfw', 'explicit', 'scam', 'fraud']
SPAM_PATTERNS = [r'earn \$?\d+', r'make \$?\d+', r'click here', r'buy now', r'limited offer', r'100% free', r'winner']

def moderate_content(profile_data):
    flags, reasons, score = [], [], 100
    bio = profile_data.get('bio', '').lower()
    full_name = f"{profile_data.get('firstName', '')} {profile_data.get('lastName', '')}".lower()
    all_text = f"{bio} {full_name} {profile_data.get('designation', '')} {profile_data.get('company', '')}".lower()
    
    if any(word in all_text for word in OFFENSIVE_WORDS):
        flags.append('offensive_language'); reasons.append("Offensive content detected"); score -= 40
    if any(re.search(p, all_text, re.IGNORECASE) for p in SPAM_PATTERNS):
        flags.append('spam_detected'); reasons.append("Spam content detected"); score -= 30
    if len(bio) < 20: flags.append('low_quality_bio'); reasons.append("Bio too short"); score -= 15
    
    score = max(0, min(100, score + (10 if profile_data.get('designation') else 0) + (10 if len(bio) >= 100 else 0)))
    status = 'auto_approved' if score >= 80 else 'pending_review' if score >= 50 else 'flagged'
    return {'score': score, 'status': status, 'flags': flags, 'reasons': reasons}

# ============================================
# DATA LOADING
# ============================================

def load_json(filename, default):
    try:
        with open(filename, 'r') as f: return json.load(f)
    except: return default

def save_json(filename, data):
    with open(filename, 'w') as f: json.dump(data, f, indent=2)

def load_films(): return load_json('films_database.json', [])
def load_users(): return load_json('paccs_users.json', {})
def save_users(users): save_json('paccs_users.json', users)
def load_profiles(): return load_json('paccs_profiles.json', {})
def save_profiles(profiles): save_json('paccs_profiles.json', profiles)
def load_payments(): return load_json('paccs_payments.json', [])
def save_payments(payments): save_json('paccs_payments.json', payments)
def load_streaming_films(): return load_json('paccs_streaming.json', [])
def save_streaming_films(films):
    try:
        save_json('paccs_streaming.json', films)
    except Exception as e:
        print(f"Error saving streaming films: {e}")
def load_rentals(): return load_json('paccs_rentals.json', [])
def save_rentals(rentals): save_json('paccs_rentals.json', rentals)
def load_music(): return load_json('paccs_music.json', [])
def save_music(tracks): 
    try:
        save_json('paccs_music.json', tracks)
    except Exception as e:
        print(f"Error saving music: {e}")
def load_music_licenses(): return load_json('paccs_music_licenses.json', [])
def save_music_licenses(licenses): save_json('paccs_music_licenses.json', licenses)

films_data = load_films()
print(f"Loaded {len(films_data)} films")

# ============================================
# FIREBASE AUTH
# ============================================

@app.route('/auth/verify', methods=['POST'])
def verify_auth():
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        if not id_token:
            return jsonify({'error': 'No token provided'}), 400
        return jsonify({'success': True})
    except Exception as e:
        print(f"Auth error: {e}")
        return jsonify({'error': str(e)}), 401

@app.route('/auth/logout', methods=['POST'])
def logout():
    return jsonify({'success': True})

# ============================================
# PAGE ROUTES
# ============================================

@app.route('/')
def landing(): return render_template('landing.html')

@app.route('/browse')
def browse(): return render_template('index.html')

@app.route('/analyze')
def analyze(): return render_template('index.html')

@app.route('/signup')
def signup_page(): return render_template('signup.html')

@app.route('/login')
def login_page(): return render_template('login.html')

@app.route('/dashboard')
def dashboard_page(): return render_template('dashboard.html')

@app.route('/trailer-analysis')
def trailer_analysis_page(): return render_template('trailer-analysis.html')

@app.route('/submit')
def submit_page(): return render_template('submit.html')

@app.route('/music')
def music_page(): return render_template('music.html')

@app.route('/filmmakers')
def filmmakers_page(): return render_template('filmmakers.html')

@app.route('/filmmaker/<profile_id>')
def filmmaker_profile(profile_id): return render_template('profile.html', profile_id=profile_id)

@app.route('/spotlight')
def spotlight_page(): return render_template('spotlight.html')

@app.route('/admin')
def admin_page(): return render_template('admin.html')

@app.route('/pricing')
def pricing_page(): return render_template('pricing.html')

@app.route('/success')
def success_page(): return render_template('success.html')

@app.route('/cancel')
def cancel_page(): return redirect('/pricing')

# Streaming Pages
@app.route('/watch')
def watch_browse(): return render_template('watch.html')

@app.route('/watch/<film_id>')
def watch_film(film_id): return render_template('watch_film.html', film_id=film_id)

@app.route('/upload')
def upload_page(): return render_template('upload.html')

@app.route('/rent-success')
def rent_success(): return render_template('rent_success.html')

@app.route('/admin-streaming')
def admin_streaming_page(): return render_template('admin_streaming.html')

# Music Pages
@app.route('/music-browse')
def music_browse(): return render_template('music_browse.html')

@app.route('/music-upload')
def music_upload(): return render_template('music_upload.html')

@app.route('/music-license/<track_id>')
def music_license(track_id): return render_template('music_license.html', track_id=track_id)

@app.route('/admin-music')
def admin_music_page(): return render_template('admin_music.html')

# Festival & Competition Pages
@app.route('/festival')
def festival_page(): return render_template('festival.html')

@app.route('/piff')
def piff_redirect(): return redirect('/festival')

@app.route('/winners')
def winners_page(): return render_template('winners.html')

@app.route('/admin-judging')
def admin_judging_page(): return render_template('admin_judging.html')

@app.route('/script-analysis')
def script_analysis_page(): return render_template('script-analysis.html')

# ============================================
# API ROUTES - FILMS & ANALYSIS
# ============================================

@app.route('/api/films')
def get_films():
    return jsonify({'films': films_data[:100] if films_data else [], 'total': len(films_data), 'analyzed': len(films_data), 'avg_score': 7.2})

@app.route('/api/analyze', methods=['POST'])
def analyze_film():
    score = round(random.uniform(5.5, 8.5), 1)
    return jsonify({
        'score': score, 'pathway': 'THEATRICAL' if score > 6.5 else 'FESTIVAL',
        'predictions': {'festival_selection': random.randint(40, 85), 'distribution_deal': random.randint(30, 70), 'award_nomination': random.randint(10, 40), 'viral_potential': random.randint(5, 25)},
        'festivals': [{'name': n, 'score': random.randint(40, 90)} for n in ['Sundance', 'Toronto', 'Berlin', 'Cannes', 'Venice']],
        'distributors': [{'name': n, 'score': random.randint(35, 80)} for n in ['A24', 'Netflix', 'Amazon', 'MUBI', 'Neon']]
    })

# ============================================
# API ROUTES - AUTHENTICATION
# ============================================

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    users, profiles = load_users(), load_profiles()
    email = data.get('email', '').lower().strip()
    
    if email in users: return jsonify({'success': False, 'error': 'Email already exists'})
    if len(data.get('password', '')) < 6: return jsonify({'success': False, 'error': 'Password must be at least 6 characters'})
    
    moderation = moderate_content(data)
    user_id, profile_id = f"USER_{len(users) + 1:05d}", str(uuid.uuid4())[:8]
    
    users[email] = {
        'id': user_id, 'email': email, 'password': hashlib.sha256(data['password'].encode()).hexdigest(),
        'name': f"{data.get('firstName', '')} {data.get('lastName', '')}", 'plan': 'free', 'credits': 3,
        'profile_id': profile_id, 'films_analyzed': [], 'created_at': datetime.now().isoformat()
    }
    
    profiles[profile_id] = {
        'id': profile_id, 'user_id': user_id, 'email': email,
        'firstName': data.get('firstName', ''), 'lastName': data.get('lastName', ''),
        'fullName': f"{data.get('firstName', '')} {data.get('lastName', '')}",
        'designation': data.get('designation', ''), 'company': data.get('company', ''),
        'country': data.get('country', ''), 'city': data.get('city', ''), 'bio': data.get('bio', ''),
        'profilePhoto': data.get('profilePhoto', ''), 'socialLinks': data.get('socialLinks', {}),
        'filmLinks': data.get('filmLinks', []), 'films': [], 'status': moderation['status'],
        'moderation_score': moderation['score'], 'moderation_flags': moderation['flags'],
        'featured': False, 'created_at': datetime.now().isoformat()
    }
    
    save_users(users); save_profiles(profiles)
    return jsonify({'success': True, 'user_id': user_id, 'profile_id': profile_id, 'credits': 3})

@app.route('/api/login', methods=['POST'])
def api_login():
    data, users = request.json, load_users()
    email = data.get('email', '').lower().strip()
    if email not in users: return jsonify({'success': False, 'error': 'Email not found'})
    if users[email]['password'] != hashlib.sha256(data.get('password', '').encode()).hexdigest():
        return jsonify({'success': False, 'error': 'Invalid password'})
    user = users[email]
    return jsonify({'success': True, 'user': {'id': user['id'], 'email': email, 'name': user['name'], 'plan': user['plan'], 'credits': user['credits'], 'profile_id': user.get('profile_id', '')}})

@app.route('/api/user/credits')
def get_user_credits():
    email, users = request.headers.get('X-User-Email', ''), load_users()
    if email and email in users:
        return jsonify({'credits': users[email].get('credits', 0), 'plan': users[email].get('plan', 'free')})
    return jsonify({'credits': 0, 'plan': 'free'})

# ============================================
# API ROUTES - STRIPE PAYMENTS
# ============================================

@app.route('/api/stripe/config')
def stripe_config(): return jsonify({'publishableKey': STRIPE_PUBLISHABLE_KEY})

@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.json
    package_id = data.get('package')
    if package_id not in CREDIT_PACKAGES: return jsonify({'error': 'Invalid package'}), 400
    if not stripe.api_key: return jsonify({'error': 'Payment not configured'}), 500
    
    package = CREDIT_PACKAGES[package_id]
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price_data': {'currency': 'gbp', 'unit_amount': package['price'],
                'product_data': {'name': f"PACCS {package['name']} - {package['credits']} Credits"}}, 'quantity': 1}],
            mode='payment', success_url=f"{request.host_url}success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.host_url}pricing", customer_email=data.get('email'),
            metadata={'package_id': package_id, 'credits': package['credits'], 'user_email': data.get('email', '')}
        )
        return jsonify({'sessionId': session.id, 'url': session.url})
    except Exception as e: return jsonify({'error': str(e)}), 500

@app.route('/api/verify-payment', methods=['POST'])
def verify_payment():
    data = request.json
    if not data.get('session_id') or not stripe.api_key: return jsonify({'success': False, 'error': 'Invalid request'})
    try:
        session = stripe.checkout.Session.retrieve(data['session_id'])
        if session.payment_status == 'paid':
            credits = int(session.metadata.get('credits', 0))
            email = data.get('email', '').lower().strip()
            users = load_users()
            if email in users:
                users[email]['credits'] = users[email].get('credits', 0) + credits
                save_users(users)
            return jsonify({'success': True, 'credits_added': credits, 'new_balance': users.get(email, {}).get('credits', credits)})
        return jsonify({'success': False, 'error': 'Payment not completed'})
    except Exception as e: return jsonify({'success': False, 'error': str(e)})

# ============================================
# API ROUTES - STREAMING
# ============================================

@app.route('/api/streaming/films')
def get_streaming_films():
    films = load_streaming_films()
    approved = [f for f in films if f.get('status') == 'approved']
    featured = next((f for f in approved if f.get('featured')), approved[0] if approved else None)
    return jsonify({'success': True, 'films': approved, 'featured': featured, 'total': len(approved)})

@app.route('/api/streaming/film/<film_id>')
def get_streaming_film(film_id):
    films = load_streaming_films()
    film = next((f for f in films if f['id'] == film_id), None)
    if film: return jsonify({'success': True, 'film': film})
    return jsonify({'success': False, 'error': 'Film not found'}), 404

@app.route('/api/streaming/upload', methods=['POST'])
def upload_streaming_film():
    try:
        data = request.json
        films = load_streaming_films()
        
        film_id = str(uuid.uuid4())[:8]
        new_film = {
            'id': film_id,
            'title': data.get('title', 'Untitled'),
            'genre': data.get('genre', ''),
            'duration': data.get('duration', ''),
            'year': data.get('year', '2024'),
            'country': data.get('country', ''),
            'description': data.get('description', ''),
            'tags': data.get('tags', []),
            'video_url': data.get('video_url', ''),
            'thumbnail': data.get('thumbnail', ''),
            'price': data.get('price', 5),
            'filmmaker': data.get('filmmaker', ''),
            'filmmaker_id': data.get('filmmaker_id', ''),
            'filmmaker_email': data.get('filmmaker_email', ''),
            'status': 'pending_review',
            'featured': False,
            'views': 0,
            'rentals': 0,
            'earnings': 0,
            'created_at': datetime.now().isoformat()
        }
        
        films.append(new_film)
        save_streaming_films(films)
        print(f"Film uploaded: {film_id} - {new_film['title']}")
        return jsonify({'success': True, 'film_id': film_id, 'message': 'Film submitted for review'})
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/streaming/check-access/<film_id>')
def check_film_access(film_id):
    email = request.headers.get('X-User-Email', '').lower()
    if not email: return jsonify({'hasAccess': False})
    
    rentals = load_rentals()
    now = datetime.now()
    
    for rental in rentals:
        if rental['film_id'] == film_id and rental['user_email'] == email:
            expires = datetime.fromisoformat(rental['expires_at'])
            if now < expires:
                return jsonify({'hasAccess': True, 'expires_at': rental['expires_at']})
    
    return jsonify({'hasAccess': False})

@app.route('/api/streaming/rent', methods=['POST'])
def rent_film():
    data = request.json
    film_id, email = data.get('film_id'), data.get('email', '').lower()
    
    if not stripe.api_key: return jsonify({'error': 'Payment not configured'}), 500
    
    films = load_streaming_films()
    film = next((f for f in films if f['id'] == film_id), None)
    if not film: return jsonify({'error': 'Film not found'}), 404
    
    if film['price'] == 0:
        rentals = load_rentals()
        rentals.append({
            'id': str(uuid.uuid4())[:8], 'film_id': film_id, 'user_email': email,
            'price': 0, 'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=365)).isoformat()
        })
        save_rentals(rentals)
        return jsonify({'success': True, 'message': 'Access granted'})
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price_data': {'currency': 'gbp', 'unit_amount': int(film['price'] * 100),
                'product_data': {'name': f"Rent: {film['title']}", 'description': '48-hour rental access'}}, 'quantity': 1}],
            mode='payment', success_url=f"{request.host_url}rent-success?session_id={{CHECKOUT_SESSION_ID}}&film_id={film_id}",
            cancel_url=f"{request.host_url}watch/{film_id}", customer_email=email,
            metadata={'film_id': film_id, 'user_email': email, 'type': 'rental', 'price': film['price']}
        )
        return jsonify({'sessionId': session.id, 'url': session.url})
    except Exception as e: return jsonify({'error': str(e)}), 500

@app.route('/api/streaming/verify-rental', methods=['POST'])
def verify_rental():
    data = request.json
    session_id, film_id = data.get('session_id'), data.get('film_id')
    
    if not session_id or not stripe.api_key: return jsonify({'success': False})
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            email = session.metadata.get('user_email', '')
            price = float(session.metadata.get('price', 0))
            
            rentals = load_rentals()
            rentals.append({
                'id': str(uuid.uuid4())[:8], 'film_id': film_id, 'user_email': email,
                'session_id': session_id, 'price': price,
                'filmmaker_share': price * 0.7, 'platform_share': price * 0.3,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=48)).isoformat()
            })
            save_rentals(rentals)
            
            films = load_streaming_films()
            for f in films:
                if f['id'] == film_id:
                    f['rentals'] = f.get('rentals', 0) + 1
                    f['earnings'] = f.get('earnings', 0) + price * 0.7
                    break
            save_streaming_films(films)
            
            return jsonify({'success': True, 'message': 'Rental confirmed'})
        return jsonify({'success': False, 'error': 'Payment not completed'})
    except Exception as e: return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/streaming')
def admin_streaming():
    films = load_streaming_films()
    return jsonify({'success': True, 'films': films, 'total': len(films)})

@app.route('/api/admin/streaming/<film_id>/approve', methods=['POST'])
def approve_streaming_film(film_id):
    films = load_streaming_films()
    for f in films:
        if f['id'] == film_id:
            f['status'] = 'approved'
            save_streaming_films(films)
            return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/api/admin/streaming/<film_id>/feature', methods=['POST'])
def feature_streaming_film(film_id):
    films = load_streaming_films()
    for f in films:
        f['featured'] = (f['id'] == film_id)
        if f['id'] == film_id: f['status'] = 'approved'
    save_streaming_films(films)
    return jsonify({'success': True})

# ============================================
# API ROUTES - MUSIC MARKETPLACE
# ============================================

@app.route('/api/music/tracks')
def get_music_tracks():
    tracks = load_music()
    approved = [t for t in tracks if t.get('status') == 'approved']
    return jsonify({'success': True, 'tracks': approved, 'total': len(approved)})

@app.route('/api/music/track/<track_id>')
def get_music_track(track_id):
    tracks = load_music()
    track = next((t for t in tracks if t['id'] == track_id), None)
    if track: return jsonify({'success': True, 'track': track})
    return jsonify({'success': False, 'error': 'Track not found'}), 404

@app.route('/api/music/upload', methods=['POST'])
def upload_music():
    try:
        data = request.json
        tracks = load_music()
        
        track_id = str(uuid.uuid4())[:8]
        new_track = {
            'id': track_id,
            'title': data.get('title', 'Untitled'),
            'genre': data.get('genre', ''),
            'duration': data.get('duration', ''),
            'description': data.get('description', ''),
            'audio_url': data.get('audio_url', ''),
            'moods': data.get('moods', []),
            'artist': data.get('artist', ''),
            'artist_id': data.get('artist_id', ''),
            'artist_email': data.get('artist_email', ''),
            'price_short': data.get('price_short', 15),
            'price_feature': data.get('price_feature', 50),
            'price_commercial': data.get('price_commercial', 100),
            'status': 'pending_review',
            'licenses': 0,
            'earnings': 0,
            'created_at': datetime.now().isoformat()
        }
        
        tracks.append(new_track)
        save_music(tracks)
        print(f"Music track uploaded: {track_id} - {new_track['title']}")
        return jsonify({'success': True, 'track_id': track_id, 'message': 'Track submitted for review'})
    except Exception as e:
        print(f"Music upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/music/license', methods=['POST'])
def license_music():
    data = request.json
    track_id = data.get('track_id')
    license_type = data.get('license_type', 'short')
    price = data.get('price', 15)
    email = data.get('email', '')
    
    if not stripe.api_key: return jsonify({'error': 'Payment not configured'}), 500
    
    tracks = load_music()
    track = next((t for t in tracks if t['id'] == track_id), None)
    if not track: return jsonify({'error': 'Track not found'}), 404
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price_data': {'currency': 'gbp', 'unit_amount': int(price * 100),
                'product_data': {'name': f"License: {track['title']}", 'description': f'{license_type.title()} film license'}}, 'quantity': 1}],
            mode='payment', 
            success_url=f"{request.host_url}music-browse?licensed=true&track={track_id}",
            cancel_url=f"{request.host_url}music-license/{track_id}", 
            customer_email=email,
            metadata={'track_id': track_id, 'license_type': license_type, 'user_email': email, 'type': 'music_license', 'price': price, 'artist_email': track.get('artist_email', '')}
        )
        return jsonify({'sessionId': session.id, 'url': session.url})
    except Exception as e: return jsonify({'error': str(e)}), 500

@app.route('/api/admin/music')
def admin_music():
    tracks = load_music()
    return jsonify({'success': True, 'tracks': tracks, 'total': len(tracks)})

@app.route('/api/admin/music/<track_id>/approve', methods=['POST'])
def approve_music(track_id):
    tracks = load_music()
    for t in tracks:
        if t['id'] == track_id:
            t['status'] = 'approved'
            save_music(tracks)
            return jsonify({'success': True})
    return jsonify({'success': False}), 404

# ============================================
# API ROUTES - FESTIVAL ENTRIES & WINNERS
# ============================================

def load_entries(): return load_json('paccs_entries.json', [])
def save_entries(entries): save_json('paccs_entries.json', entries)
def load_winners(): return load_json('paccs_winners.json', [])
def save_winners(winners): save_json('paccs_winners.json', winners)

@app.route('/api/winners')
def get_winners():
    winners = load_winners()
    return jsonify({'success': True, 'winners': winners, 'total': len(winners)})

@app.route('/api/admin/entries')
def admin_get_entries():
    entries = load_entries()
    return jsonify({'success': True, 'entries': entries, 'total': len(entries)})

@app.route('/api/admin/entries/add', methods=['POST'])
def admin_add_entry():
    try:
        data = request.json
        entries = load_entries()
        
        entry_id = str(uuid.uuid4())[:8]
        new_entry = {
            'id': entry_id,
            'title': data.get('title', 'Untitled'),
            'director': data.get('director', ''),
            'country': data.get('country', ''),
            'duration': data.get('duration', ''),
            'category': data.get('category', 'Cinema Excellence'),
            'video_url': data.get('video_url', ''),
            'thumbnail': data.get('thumbnail', ''),
            'filmmaker_email': data.get('filmmaker_email', ''),
            'filmmaker_id': data.get('filmmaker_id', ''),
            'status': 'pending',
            'paccs_score': None,
            'score_artistic': None,
            'score_market': None,
            'score_technical': None,
            'score_impact': None,
            'judge_notes': '',
            'streaming_id': None,
            'created_at': datetime.now().isoformat()
        }
        
        entries.append(new_entry)
        save_entries(entries)
        return jsonify({'success': True, 'entry_id': entry_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/entries/<entry_id>/score', methods=['POST'])
def score_entry(entry_id):
    try:
        data = request.json
        entries = load_entries()
        
        for e in entries:
            if e['id'] == entry_id:
                e['score_artistic'] = data.get('score_artistic')
                e['score_market'] = data.get('score_market')
                e['score_technical'] = data.get('score_technical')
                e['score_impact'] = data.get('score_impact')
                e['judge_notes'] = data.get('judge_notes', '')
                e['status'] = data.get('status', 'reviewed')
                
                scores = [e['score_artistic'], e['score_market'], e['score_technical'], e['score_impact']]
                e['paccs_score'] = round(sum(s for s in scores if s) / len([s for s in scores if s]))
                
                save_entries(entries)
                return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Entry not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/entries/<entry_id>/winner', methods=['POST'])
def make_winner(entry_id):
    try:
        entries = load_entries()
        winners = load_winners()
        
        for e in entries:
            if e['id'] == entry_id:
                e['status'] = 'winner'
                save_entries(entries)
                
                winner = {
                    'id': e['id'],
                    'title': e['title'],
                    'director': e['director'],
                    'country': e['country'],
                    'duration': e['duration'],
                    'category': e['category'],
                    'thumbnail': e['thumbnail'],
                    'streaming_id': e.get('streaming_id'),
                    'filmmaker_id': e.get('filmmaker_id'),
                    'tier': 'gold',
                    'year': '2026',
                    'awarded_at': datetime.now().isoformat()
                }
                winners.append(winner)
                save_winners(winners)
                
                return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Entry not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/entries/<entry_id>/onboard', methods=['POST'])
def onboard_to_streaming(entry_id):
    try:
        entries = load_entries()
        films = load_streaming_films()
        
        for e in entries:
            if e['id'] == entry_id:
                film_id = str(uuid.uuid4())[:8]
                new_film = {
                    'id': film_id,
                    'title': e['title'],
                    'genre': e['category'],
                    'duration': e['duration'],
                    'year': '2026',
                    'country': e['country'],
                    'description': f"PIFF 2026 {e['status'].title()} - {e['category']}",
                    'video_url': e.get('video_url', ''),
                    'thumbnail': e.get('thumbnail', ''),
                    'tags': ['PIFF 2026', e['category']],
                    'filmmaker': e['director'],
                    'filmmaker_email': e.get('filmmaker_email', ''),
                    'filmmaker_id': e.get('filmmaker_id', ''),
                    'price': 5,
                    'status': 'approved',
                    'featured': e['status'] == 'winner',
                    'views': 0,
                    'rentals': 0,
                    'earnings': 0,
                    'created_at': datetime.now().isoformat()
                }
                
                films.append(new_film)
                save_streaming_films(films)
                
                e['streaming_id'] = film_id
                save_entries(entries)
                
                winners = load_winners()
                for w in winners:
                    if w['id'] == entry_id:
                        w['streaming_id'] = film_id
                save_winners(winners)
                
                return jsonify({'success': True, 'streaming_id': film_id})
        
        return jsonify({'success': False, 'error': 'Entry not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profile/<profile_id>')
def get_profile(profile_id):
    profiles = load_profiles()
    if profile_id in profiles:
        p = profiles[profile_id]
        if p.get('status') in ['approved', 'auto_approved'] or p.get('featured'):
            return jsonify({'success': True, 'profile': {k: v for k, v in p.items() if k not in ['password', 'moderation_flags']}})
    return jsonify({'success': False, 'error': 'Profile not found'}), 404

@app.route('/api/filmmakers')
def get_filmmakers():
    profiles = load_profiles()
    filmmakers = [{'id': p['id'], 'fullName': p['fullName'], 'designation': p['designation'], 'company': p.get('company', ''),
        'country': p.get('country', ''), 'profilePhoto': p.get('profilePhoto', ''), 'featured': p.get('featured', False)}
        for p in profiles.values() if p.get('status') in ['approved', 'auto_approved'] or p.get('featured')]
    return jsonify({'success': True, 'filmmakers': sorted(filmmakers, key=lambda x: (not x['featured'], x['fullName']))})

# ============================================
# API ROUTES - ADMIN
# ============================================

@app.route('/my-films')
def my_films_page(): return render_template('my-films.html')

@app.route('/festivals')
def festivals_page(): return render_template('festivals.html')

@app.route('/distributors')
def distributors_page(): return render_template('distributors.html')

@app.route('/api/admin/profiles')
def admin_get_profiles():
    profiles = load_profiles()
    return jsonify({'success': True, 'profiles': [{'id': p['id'], 'fullName': p['fullName'], 'email': p['email'],
        'designation': p['designation'], 'status': p.get('status', 'pending'), 'featured': p.get('featured', False),
        'moderation_score': p.get('moderation_score', 0), 'created_at': p.get('created_at', '')} for p in profiles.values()]})

@app.route('/api/admin/profile/<profile_id>/approve', methods=['POST'])
def admin_approve(profile_id):
    profiles = load_profiles()
    if profile_id in profiles:
        profiles[profile_id]['status'] = 'approved'
        save_profiles(profiles)
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/api/admin/profile/<profile_id>/feature', methods=['POST'])
def admin_feature(profile_id):
    profiles = load_profiles()
    if profile_id in profiles:
        profiles[profile_id]['featured'] = True
        profiles[profile_id]['status'] = 'approved'
        save_profiles(profiles)
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

# ============================================
# API ROUTES - PDF
# ============================================

@app.route('/api/filmmaker/<profile_id>/pdf')
def download_filmmaker_pdf(profile_id):
    profiles = load_profiles()
    if profile_id not in profiles: return jsonify({'error': 'Not found'}), 404
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        p = profiles[profile_id]
        story = [Paragraph(p.get('fullName', ''), styles['Title']), Paragraph(p.get('designation', ''), styles['Normal']),
            Spacer(1, 20), Paragraph(p.get('bio', ''), styles['Normal'])]
        doc.build(story)
        buffer.seek(0)
        return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f"PACCS_{p.get('fullName', 'Profile')}.pdf")
    except: return jsonify({'error': 'PDF generation failed'}), 500

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(e): return render_template('landing.html'), 404

@app.errorhandler(500)
def server_error(e): return jsonify({'error': 'Internal server error'}), 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n{'='*50}\nPACCS with Streaming\n{'='*50}")
    print(f"Films: {len(films_data)} | Stripe: {'Yes' if stripe.api_key else 'No'}")
    print(f"http://localhost:{port}\n{'='*50}\n")
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')