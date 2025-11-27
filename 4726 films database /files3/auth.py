"""
PACCS User Authentication System
- Filmmaker signup/login
- Session management
- User dashboard
"""
import json
import hashlib
import os
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, flash

# User database file
USERS_FILE = 'paccs_users.json'

class UserManager:
    """Manages filmmaker accounts"""
    
    def __init__(self):
        self.users = self._load_users()
    
    def _load_users(self):
        """Load users from file"""
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_users(self):
        """Save users to file"""
        with open(USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def _hash_password(self, password):
        """Hash password for security"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def signup(self, email, password, name, company=""):
        """Create new user account"""
        email = email.lower().strip()
        
        # Check if user exists
        if email in self.users:
            return {"success": False, "error": "Email already registered"}
        
        # Validate email
        if '@' not in email or '.' not in email:
            return {"success": False, "error": "Invalid email address"}
        
        # Validate password
        if len(password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters"}
        
        # Create user
        user_id = f"USER_{len(self.users) + 1:05d}"
        self.users[email] = {
            "id": user_id,
            "email": email,
            "password": self._hash_password(password),
            "name": name,
            "company": company,
            "plan": "free",  # free, basic, pro, enterprise
            "credits": 3,  # Free users get 3 free analyses
            "films_analyzed": [],
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        self._save_users()
        
        return {
            "success": True, 
            "user_id": user_id,
            "message": "Account created successfully! You have 3 free film analyses."
        }
    
    def login(self, email, password):
        """Authenticate user"""
        email = email.lower().strip()
        
        if email not in self.users:
            return {"success": False, "error": "Email not found"}
        
        user = self.users[email]
        
        if user['password'] != self._hash_password(password):
            return {"success": False, "error": "Incorrect password"}
        
        # Update last login
        user['last_login'] = datetime.now().isoformat()
        self._save_users()
        
        return {
            "success": True,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "name": user['name'],
                "company": user['company'],
                "plan": user['plan'],
                "credits": user['credits']
            }
        }
    
    def get_user(self, email):
        """Get user data"""
        email = email.lower().strip()
        if email in self.users:
            user = self.users[email].copy()
            del user['password']  # Don't expose password
            return user
        return None
    
    def use_credit(self, email):
        """Use one analysis credit"""
        email = email.lower().strip()
        if email in self.users:
            if self.users[email]['credits'] > 0:
                self.users[email]['credits'] -= 1
                self._save_users()
                return {"success": True, "credits_remaining": self.users[email]['credits']}
            else:
                return {"success": False, "error": "No credits remaining. Please upgrade your plan."}
        return {"success": False, "error": "User not found"}
    
    def add_credits(self, email, amount):
        """Add credits to user account (after payment)"""
        email = email.lower().strip()
        if email in self.users:
            self.users[email]['credits'] += amount
            self._save_users()
            return {"success": True, "credits": self.users[email]['credits']}
        return {"success": False, "error": "User not found"}
    
    def add_film_to_history(self, email, film_data):
        """Add analyzed film to user's history"""
        email = email.lower().strip()
        if email in self.users:
            self.users[email]['films_analyzed'].append({
                "film_id": film_data.get('film_id'),
                "film_title": film_data.get('film_title'),
                "score": film_data.get('final_score'),
                "pathway": film_data.get('pathway'),
                "analyzed_at": datetime.now().isoformat()
            })
            self._save_users()
            return True
        return False
    
    def get_user_films(self, email):
        """Get user's analyzed films"""
        email = email.lower().strip()
        if email in self.users:
            return self.users[email].get('films_analyzed', [])
        return []
    
    def upgrade_plan(self, email, plan, credits):
        """Upgrade user plan"""
        email = email.lower().strip()
        if email in self.users:
            self.users[email]['plan'] = plan
            self.users[email]['credits'] += credits
            self._save_users()
            return {"success": True, "plan": plan, "credits": self.users[email]['credits']}
        return {"success": False, "error": "User not found"}
    
    def get_all_users_count(self):
        """Get total user count"""
        return len(self.users)
    
    def get_stats(self):
        """Get user statistics"""
        total = len(self.users)
        plans = {}
        total_films = 0
        
        for user in self.users.values():
            plan = user.get('plan', 'free')
            plans[plan] = plans.get(plan, 0) + 1
            total_films += len(user.get('films_analyzed', []))
        
        return {
            "total_users": total,
            "plans": plans,
            "total_films_analyzed": total_films
        }


# Flask decorator for requiring login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


# Test
if __name__ == "__main__":
    print("="*60)
    print("PACCS User Manager Test")
    print("="*60)
    
    manager = UserManager()
    
    # Test signup
    result = manager.signup(
        email="filmmaker@example.com",
        password="test123",
        name="John Filmmaker",
        company="Indie Films Ltd"
    )
    print(f"\nSignup: {result}")
    
    # Test login
    result = manager.login("filmmaker@example.com", "test123")
    print(f"Login: {result}")
    
    # Test get user
    user = manager.get_user("filmmaker@example.com")
    print(f"User: {user}")
    
    # Test stats
    stats = manager.get_stats()
    print(f"Stats: {stats}")
    
    print("\n" + "="*60)
    print("User manager test complete!")
