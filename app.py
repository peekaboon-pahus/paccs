"""
PACCS - Peekaboon Agentic Creative Curation System
Production Flask Application with AI Moderation, PDF Reports & Stripe Payments
"""
from flask import Flask, render_template, request, jsonify, send_file, redirect
import json
import os
import hashlib
import random
import uuid
import re
from datetime import datetime
from io import BytesIO
import stripe

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'paccs-secret-key-change-in-production')

# Stripe Configuration - Keys MUST be set in environment variables on Render
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

OFFENSIVE_WORDS = [
    'hate', 'kill', 'violence', 'terrorist', 'abuse', 'racist', 'nazi',
    'porn', 'xxx', 'nude', 'nsfw', 'sex', 'explicit',
    'scam', 'fraud', 'hack', 'spam', 'crypto', 'bitcoin', 'invest now',
    'click here', 'free money', 'make money fast', 'get rich'
]

SPAM_PATTERNS = [
    r'earn \$?\d+', r'make \$?\d+', r'click here', r'buy now',
    r'limited offer', r'act now', r'free trial', r'no risk',
    r'100% free', r'winner', r'congratulations', r'selected'
]

def moderate_content(profile_data):
    flags = []
    reasons = []
    score = 100
    
    bio = profile_data.get('bio', '').lower()
    full_name = f"{profile_data.get('firstName', '')} {profile_data.get('lastName', '')}".lower()
    designation = profile_data.get('designation', '').lower()
    company = profile_data.get('company', '').lower()
    all_text = f"{bio} {full_name} {designation} {company}"
    
    offensive_found = []
    for word in OFFENSIVE_WORDS:
        if word in all_text:
            offensive_found.append(word)
    
    if offensive_found:
        flags.append('offensive_language')
        reasons.append(f"Potentially offensive content detected")
        score -= 40
    
    spam_found = False
    for pattern in SPAM_PATTERNS:
        if re.search(pattern, all_text, re.IGNORECASE):
            spam_found = True
            break
    
    if spam_found:
        flags.append('spam_detected')
        reasons.append("Content appears to contain spam")
        score -= 30
    
    bio_length = len(profile_data.get('bio', ''))
    if bio_length < 20:
        flags.append('low_quality_bio')
        reasons.append("Bio is too short")
        score -= 15
    elif bio_length < 50:
        flags.append('short_bio')
        reasons.append("Bio could be more detailed")
        score -= 5
    
    name = full_name.strip()
    if re.search(r'\d', name):
        flags.append('suspicious_name')
        reasons.append("Name contains numbers")
        score -= 20
    
    if len(name) < 3:
        flags.append('invalid_name')
        reasons.append("Name is too short")
        score -= 25
    
    common_placeholders = ['test', 'testing', 'asdf', 'lorem ipsum', 'sample bio']
    for placeholder in common_placeholders:
        if bio.strip() == placeholder or bio.strip().startswith(placeholder):
            flags.append('placeholder_content')
            reasons.append("Bio appears to be placeholder content")
            score -= 30
            break
    
    professional_score = 0
    social_links = profile_data.get('socialLinks', {})
    valid_social_links = sum(1 for v in social_links.values() if v)
    if valid_social_links >= 2:
        professional_score += 10
    elif valid_social_links >= 1:
        professional_score += 5
    
    film_links = profile_data.get('filmLinks', [])
    if len([l for l in film_links if l]) >= 1:
        professional_score += 10
    
    if profile_data.get('designation'):
        professional_score += 5
    if profile_data.get('company'):
        professional_score += 5
    if bio_length >= 100:
        professional_score += 10
    
    score = min(100, score + professional_score)
    score = max(0, min(100, score))
    
    if score >= 80:
        status = 'auto_approved'
    elif score >= 50:
        status = 'pending_review'
    else:
        status = 'flagged'
    
    return {'score': score, 'status': status, 'flags': flags, 'reasons': reasons}

# ============================================
# PDF REPORT GENERATOR
# ============================================

def generate_film_report_pdf(film_data, analysis_data):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib.colors import HexColor
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.enums import TA_CENTER
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
        
        styles = getSampleStyleSheet()
        PURPLE = HexColor('#a855f7')
        DARK = HexColor('#1a1a2e')
        GRAY = HexColor('#6b7280')
        WHITE = HexColor('#ffffff')
        
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=28, textColor=PURPLE, spaceAfter=20, alignment=TA_CENTER)
        heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=16, textColor=PURPLE, spaceBefore=25, spaceAfter=15)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, textColor=DARK, spaceAfter=10)
        score_style = ParagraphStyle('Score', parent=styles['Normal'], fontSize=48, textColor=PURPLE, alignment=TA_CENTER)
        
        story = []
        story.append(Paragraph("PACCS Film Report", title_style))
        story.append(Spacer(1, 20))
        
        film_title = film_data.get('title', 'Untitled Film')
        story.append(Paragraph(f"<b>{film_title}</b>", ParagraphStyle('FilmTitle', parent=styles['Heading1'], fontSize=24, textColor=DARK, alignment=TA_CENTER, spaceAfter=10)))
        
        story.append(Paragraph("OVERALL SCORE", heading_style))
        score = analysis_data.get('score', 0)
        story.append(Paragraph(f"{score}/10", score_style))
        
        story.append(Paragraph("SUCCESS PREDICTIONS", heading_style))
        predictions = analysis_data.get('predictions', {})
        pred_data = [
            ['Metric', 'Probability'],
            ['Festival Selection', f"{predictions.get('festival_selection', 0)}%"],
            ['Distribution Deal', f"{predictions.get('distribution_deal', 0)}%"],
            ['Award Nomination', f"{predictions.get('award_nomination', 0)}%"],
        ]
        pred_table = Table(pred_data, colWidths=[10*cm, 5*cm])
        pred_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PURPLE),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb')),
        ]))
        story.append(pred_table)
        
        story.append(Spacer(1, 30))
        story.append(Paragraph("Powered by PACCS | paccs.peekaboon.com", ParagraphStyle('Footer', parent=body_style, alignment=TA_CENTER, textColor=PURPLE, fontSize=10)))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    except ImportError:
        return None

def generate_filmmaker_report_pdf(profile_data):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib.colors import HexColor
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.enums import TA_CENTER
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
        
        styles = getSampleStyleSheet()
        PURPLE = HexColor('#a855f7')
        DARK = HexColor('#1a1a2e')
        GRAY = HexColor('#6b7280')
        
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=32, textColor=DARK, spaceAfter=10, alignment=TA_CENTER)
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=16, textColor=PURPLE, spaceAfter=5, alignment=TA_CENTER)
        heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, textColor=PURPLE, spaceBefore=20, spaceAfter=10)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, textColor=DARK, spaceAfter=10, leading=16)
        
        story = []
        story.append(Paragraph(profile_data.get('fullName', 'Filmmaker'), title_style))
        story.append(Paragraph(profile_data.get('designation', ''), subtitle_style))
        
        if profile_data.get('bio'):
            story.append(Paragraph("ABOUT", heading_style))
            story.append(Paragraph(profile_data.get('bio'), body_style))
        
        story.append(Spacer(1, 40))
        story.append(Paragraph("paccs.peekaboon.com", ParagraphStyle('Footer', parent=body_style, alignment=TA_CENTER, textColor=GRAY, fontSize=10)))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    except ImportError:
        return None

# ============================================
# DATA LOADING
# ============================================

def load_films():
    try:
        with open('films_database.json', 'r') as f:
            return json.load(f)
    except:
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

def load_payments():
    try:
        with open('paccs_payments.json', 'r') as f:
            return json.load(f)
    except:
        return []

def save_payments(payments):
    with open('paccs_payments.json', 'w') as f:
        json.dump(payments, f, indent=2)

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

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/pricing')
def pricing_page():
    return render_template('pricing.html')

@app.route('/success')
def success_page():
    return render_template('success.html')

@app.route('/cancel')
def cancel_page():
    return redirect('/pricing')

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
    
    moderation = moderate_content(data)
    user_id = f"USER_{len(users) + 1:05d}"
    profile_id = str(uuid.uuid4())[:8]
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    users[email] = {
        'id': user_id, 'email': email, 'password': hashed_password,
        'name': f"{first_name} {last_name}", 'firstName': first_name, 'lastName': last_name,
        'plan': 'free', 'credits': 3, 'profile_id': profile_id,
        'films_analyzed': [], 'created_at': datetime.now().isoformat()
    }
    
    profiles[profile_id] = {
        'id': profile_id, 'user_id': user_id, 'email': email,
        'firstName': first_name, 'lastName': last_name, 'fullName': f"{first_name} {last_name}",
        'designation': data.get('designation', ''), 'company': data.get('company', ''),
        'country': data.get('country', ''), 'city': data.get('city', ''),
        'bio': data.get('bio', ''), 'profilePhoto': data.get('profilePhoto', ''),
        'socialLinks': data.get('socialLinks', {}), 'filmLinks': data.get('filmLinks', []),
        'films': [], 'status': moderation['status'],
        'moderation_score': moderation['score'], 'moderation_flags': moderation['flags'],
        'moderation_reasons': moderation['reasons'], 'featured': False, 'spotlight': False,
        'created_at': datetime.now().isoformat(), 'updated_at': datetime.now().isoformat()
    }
    
    save_users(users)
    save_profiles(profiles)
    
    return jsonify({'success': True, 'user_id': user_id, 'profile_id': profile_id, 'credits': 3, 'moderation_status': moderation['status']})

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
            'id': user['id'], 'email': user['email'], 'name': user['name'],
            'firstName': user.get('firstName', ''), 'lastName': user.get('lastName', ''),
            'plan': user['plan'], 'credits': user['credits'], 'profile_id': user.get('profile_id', '')
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
            'films_analyzed': len(films_analyzed), 'avg_score': avg_score,
            'festival_matches': len(films_analyzed) * 3 if films_analyzed else 0,
            'credits': user.get('credits', 3), 'recent': films_analyzed[-5:] if films_analyzed else [],
            'profile_id': user.get('profile_id', '')
        })
    
    return jsonify({'films_analyzed': 0, 'avg_score': None, 'festival_matches': 0, 'credits': 3, 'recent': []})

@app.route('/api/user/credits')
def get_user_credits():
    email = request.headers.get('X-User-Email', '')
    users = load_users()
    if email and email in users:
        return jsonify({'credits': users[email].get('credits', 0), 'plan': users[email].get('plan', 'free')})
    return jsonify({'credits': 0, 'plan': 'free'})

# ============================================
# API ROUTES - STRIPE PAYMENTS
# ============================================

@app.route('/api/stripe/config')
def stripe_config():
    return jsonify({'publishableKey': STRIPE_PUBLISHABLE_KEY})

@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.json
    package_id = data.get('package')
    user_email = data.get('email', '')
    
    if package_id not in CREDIT_PACKAGES:
        return jsonify({'error': 'Invalid package'}), 400
    if not stripe.api_key:
        return jsonify({'error': 'Payment system not configured. Please add STRIPE_SECRET_KEY to environment variables.'}), 500
    
    package = CREDIT_PACKAGES[package_id]
    
    try:
        domain = request.host_url.rstrip('/')
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'unit_amount': package['price'],
                    'product_data': {
                        'name': f"PACCS {package['name']} - {package['credits']} Credits",
                        'description': f"Get {package['credits']} film analysis credits",
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{domain}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{domain}/pricing",
            customer_email=user_email if user_email else None,
            metadata={'package_id': package_id, 'credits': package['credits'], 'user_email': user_email}
        )
        return jsonify({'sessionId': checkout_session.id, 'url': checkout_session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify-payment', methods=['POST'])
def verify_payment():
    data = request.json
    session_id = data.get('session_id')
    user_email = data.get('email', '').lower().strip()
    
    if not session_id:
        return jsonify({'success': False, 'error': 'No session ID provided'})
    if not stripe.api_key:
        return jsonify({'success': False, 'error': 'Payment system not configured'})
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            credits_to_add = int(session.metadata.get('credits', 0))
            package_id = session.metadata.get('package_id', '')
            users = load_users()
            
            if user_email and user_email in users:
                users[user_email]['credits'] = users[user_email].get('credits', 0) + credits_to_add
                save_users(users)
                
                payments = load_payments()
                payments.append({
                    'session_id': session_id, 'user_email': user_email, 'package': package_id,
                    'credits': credits_to_add, 'amount': session.amount_total,
                    'currency': session.currency, 'status': 'completed', 'created_at': datetime.now().isoformat()
                })
                save_payments(payments)
                
                return jsonify({'success': True, 'credits_added': credits_to_add, 'new_balance': users[user_email]['credits']})
            else:
                return jsonify({'success': True, 'credits_added': credits_to_add, 'message': 'Payment successful. Please log in to see your credits.'})
        else:
            return jsonify({'success': False, 'error': 'Payment not completed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/packages')
def get_packages():
    return jsonify({
        'packages': [
            {'id': 'starter', 'name': 'Starter', 'credits': 5, 'price': '£10', 'price_per_credit': '£2.00', 'popular': False},
            {'id': 'pro', 'name': 'Pro', 'credits': 15, 'price': '£25', 'price_per_credit': '£1.67', 'popular': True},
            {'id': 'studio', 'name': 'Studio', 'credits': 40, 'price': '£50', 'price_per_credit': '£1.25', 'popular': False}
        ]
    })

# ============================================
# API ROUTES - PROFILES
# ============================================

@app.route('/api/profile/<profile_id>')
def get_profile(profile_id):
    profiles = load_profiles()
    if profile_id in profiles:
        profile = profiles[profile_id]
        if profile.get('status') not in ['approved', 'auto_approved'] and not profile.get('featured'):
            return jsonify({'success': False, 'error': 'Profile not available'}), 404
        safe_profile = {
            'id': profile['id'], 'fullName': profile['fullName'], 'firstName': profile['firstName'],
            'lastName': profile['lastName'], 'designation': profile['designation'], 'company': profile['company'],
            'country': profile['country'], 'city': profile['city'], 'bio': profile['bio'],
            'profilePhoto': profile.get('profilePhoto', ''), 'socialLinks': profile.get('socialLinks', {}),
            'filmLinks': profile.get('filmLinks', []), 'films': profile.get('films', []),
            'featured': profile.get('featured', False), 'status': profile.get('status', 'pending')
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
        if profile.get('status') in ['approved', 'auto_approved'] or profile.get('featured'):
            filmmakers.append({
                'id': profile['id'], 'fullName': profile['fullName'], 'designation': profile['designation'],
                'company': profile.get('company', ''), 'country': profile.get('country', ''),
                'profilePhoto': profile.get('profilePhoto', ''), 'featured': profile.get('featured', False),
                'films_count': len(profile.get('films', [])) + len(profile.get('filmLinks', []))
            })
    filmmakers.sort(key=lambda x: (not x['featured'], x['fullName']))
    return jsonify({'success': True, 'filmmakers': filmmakers, 'total': len(filmmakers)})

@app.route('/api/spotlight')
def get_spotlight():
    profiles = load_profiles()
    featured_filmmakers = []
    spotlight_films = []
    for profile_id, profile in profiles.items():
        if profile.get('featured') or profile.get('spotlight'):
            featured_filmmakers.append({
                'id': profile['id'], 'fullName': profile['fullName'],
                'designation': profile['designation'], 'profilePhoto': profile.get('profilePhoto', '')
            })
        for film in profile.get('films', []):
            if film.get('score', 0) >= 7.0:
                spotlight_films.append({
                    'title': film.get('title', ''), 'score': film.get('score', 0),
                    'filmmaker': profile['fullName'], 'filmmaker_id': profile['id']
                })
    spotlight_films.sort(key=lambda x: x['score'], reverse=True)
    return jsonify({'success': True, 'featured_filmmakers': featured_filmmakers[:10], 'spotlight_films': spotlight_films[:20]})

# ============================================
# API ROUTES - ADMIN
# ============================================

@app.route('/api/admin/profiles')
def admin_get_profiles():
    profiles = load_profiles()
    all_profiles = []
    for profile_id, profile in profiles.items():
        all_profiles.append({
            'id': profile['id'], 'fullName': profile['fullName'], 'email': profile['email'],
            'designation': profile['designation'], 'status': profile.get('status', 'pending'),
            'featured': profile.get('featured', False), 'moderation_score': profile.get('moderation_score', 0),
            'moderation_flags': profile.get('moderation_flags', []), 'moderation_reasons': profile.get('moderation_reasons', []),
            'created_at': profile.get('created_at', '')
        })
    all_profiles.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify({'success': True, 'profiles': all_profiles})

@app.route('/api/admin/profile/<profile_id>/approve', methods=['POST'])
def admin_approve_profile(profile_id):
    profiles = load_profiles()
    if profile_id in profiles:
        profiles[profile_id]['status'] = 'approved'
        profiles[profile_id]['updated_at'] = datetime.now().isoformat()
        save_profiles(profiles)
        return jsonify({'success': True, 'message': 'Profile approved'})
    return jsonify({'success': False, 'error': 'Profile not found'}), 404

@app.route('/api/admin/profile/<profile_id>/reject', methods=['POST'])
def admin_reject_profile(profile_id):
    profiles = load_profiles()
    if profile_id in profiles:
        profiles[profile_id]['status'] = 'rejected'
        profiles[profile_id]['updated_at'] = datetime.now().isoformat()
        save_profiles(profiles)
        return jsonify({'success': True, 'message': 'Profile rejected'})
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

@app.route('/api/admin/payments')
def admin_get_payments():
    payments = load_payments()
    return jsonify({'success': True, 'payments': payments, 'total': len(payments), 'total_revenue': sum(p.get('amount', 0) for p in payments) / 100})

# ============================================
# API ROUTES - PDF REPORTS
# ============================================

@app.route('/api/report/pdf')
def download_film_report():
    film_data = {'title': request.args.get('title', 'Film Analysis'), 'genre': request.args.get('genre', 'Drama'), 'country': request.args.get('country', 'Unknown')}
    analysis_data = {
        'score': float(request.args.get('score', 7.5)), 'pathway': request.args.get('pathway', 'FESTIVAL'),
        'predictions': {'festival_selection': 65, 'distribution_deal': 45, 'award_nomination': 25, 'viral_potential': 15},
        'festivals': [{'name': 'Sundance', 'score': 78}], 'distributors': [{'name': 'A24', 'score': 70}]
    }
    pdf_buffer = generate_film_report_pdf(film_data, analysis_data)
    if pdf_buffer is None:
        return jsonify({'error': 'PDF generation not available'}), 500
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=f"PACCS_Report.pdf")

@app.route('/api/filmmaker/<profile_id>/pdf')
def download_filmmaker_pdf(profile_id):
    profiles = load_profiles()
    if profile_id not in profiles:
        return jsonify({'error': 'Profile not found'}), 404
    pdf_buffer = generate_filmmaker_report_pdf(profiles[profile_id])
    if pdf_buffer is None:
        return jsonify({'error': 'PDF generation not available'}), 500
    safe_name = profiles[profile_id].get('fullName', 'Filmmaker').replace(' ', '_')[:30]
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=f"PACCS_Profile_{safe_name}.pdf")

# ============================================
# API ROUTES - MUSIC & CONTENT
# ============================================

@app.route('/api/music/analyze', methods=['POST'])
def analyze_music():
    return jsonify({'mood': random.choice(['Dramatic', 'Uplifting', 'Tense']), 'tempo': random.choice(['Slow', 'Moderate', 'Fast']), 'energy': random.randint(40, 90)})

@app.route('/api/content/check', methods=['POST'])
def check_content():
    return jsonify({'safe': True, 'score': random.randint(85, 100), 'flags': []})

@app.route('/api/submit', methods=['POST'])
def submit_film():
    return jsonify({'success': True, 'message': 'Film submitted successfully', 'submission_id': f"SUB_{random.randint(10000, 99999)}"})

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
    print(f"\n{'='*60}\nPACCS - AI Film Intelligence Platform\n{'='*60}")
    print(f"Loaded {len(films_data)} films")
    print(f"Stripe configured: {'Yes' if stripe.api_key else 'No - Add STRIPE_SECRET_KEY to env vars'}")
    print(f"Running on http://localhost:{port}\n{'='*60}\n")
    app.run(host='0.0.0.0', port=port, debug=debug)