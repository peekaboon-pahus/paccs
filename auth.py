"""
PACCS User Authentication System
"""
import json
import hashlib
import os
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for

USERS_FILE = 'paccs_users.json'

class UserManager:
    def __init__(self):
        self.users = self._load_users()
    
    def _load_users(self):
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_users(self):
        with open(USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def signup(self, email, password, name, company=""):
        email = email.lower().strip()
        
        if email in self.users:
            return {"success": False, "error": "Email already registered"}
        
        if '@' not in email or '.' not in email:
            return {"success": False, "error": "Invalid email address"}
        
        if len(password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters"}
        
        user_id = f"USER_{len(self.users) + 1:05d}"
        self.users[email] = {
            "id": user_id,
            "email": email,
            "password": self._hash_password(password),
            "name": name,
            "company": company,
            "plan": "free",
            "credits": 3,
            "films_analyzed": [],
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        self._save_users()
        return {"success": True, "user_id": user_id, "message": "Account created! You have 3 free analyses."}
    
    def login(self, email, password):
        email = email.lower().strip()
        
        if email not in self.users:
            return {"success": False, "error": "Email not found"}
        
        user = self.users[email]
        
        if user['password'] != self._hash_password(password):
            return {"success": False, "error": "Incorrect password"}
        
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
        email = email.lower().strip()
        if email in self.users:
            user = self.users[email].copy()
            del user['password']
            return user
        return None
    
    def use_credit(self, email):
        email = email.lower().strip()
        if email in self.users:
            if self.users[email]['credits'] > 0:
                self.users[email]['credits'] -= 1
                self._save_users()
                return {"success": True, "credits_remaining": self.users[email]['credits']}
            return {"success": False, "error": "No credits remaining. Please upgrade."}
        return {"success": False, "error": "User not found"}
    
    def add_credits(self, email, amount):
        email = email.lower().strip()
        if email in self.users:
            self.users[email]['credits'] += amount
            self._save_users()
            return {"success": True, "credits": self.users[email]['credits']}
        return {"success": False, "error": "User not found"}
    
    def add_film_to_history(self, email, film_data):
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
        email = email.lower().strip()
        if email in self.users:
            return self.users[email].get('films_analyzed', [])
        return []
    
    def get_all_users_count(self):
        return len(self.users)
    
    def get_stats(self):
        total = len(self.users)
        plans = {}
        total_films = 0
        for user in self.users.values():
            plan = user.get('plan', 'free')
            plans[plan] = plans.get(plan, 0) + 1
            total_films += len(user.get('films_analyzed', []))
        return {"total_users": total, "plans": plans, "total_films_analyzed": total_films}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


if __name__ == "__main__":
    print("Auth system ready!")
    manager = UserManager()
    print(f"Total users: {manager.get_all_users_count()}")