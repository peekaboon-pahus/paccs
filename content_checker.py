"""
PACCS Content Safety & Originality Checker
Ensures all submitted content meets platform standards
"""
import re
from datetime import datetime


class ContentChecker:
    """Checks films for offensive content, originality, and compliance"""
    
    def __init__(self):
        self.name = "Content Safety Agent"
        
        # Offensive words/phrases to flag
        self.offensive_terms = [
            'hate', 'nazi', 'terrorist', 'kill all', 'death to',
            'racial slur', 'ethnic slur'  # Add more as needed
        ]
        
        # Suspicious patterns
        self.spam_patterns = [
            r'(.)\1{5,}',  # Repeated characters (aaaaaaaa)
            r'(buy now|click here|free money|act now)',
            r'[A-Z]{10,}',  # ALL CAPS spam
        ]
        
        # Copyright red flags
        self.copyright_flags = [
            'remake of', 'based on marvel', 'based on disney',
            'star wars', 'harry potter', 'lord of the rings',
            'copied from', 'stolen from'
        ]
        
        # Required fields
        self.required_fields = ['title', 'duration', 'country', 'genre']
    
    def check_film(self, film_data):
        """
        Full safety check on film submission
        
        Returns:
            dict with 'approved', 'score', 'issues', 'warnings'
        """
        issues = []
        warnings = []
        
        # 1. Check required fields
        for field in self.required_fields:
            if not film_data.get(field):
                issues.append(f"Missing required field: {field}")
        
        # 2. Check title
        title = film_data.get('title', '')
        title_check = self._check_text(title, 'Title')
        issues.extend(title_check['issues'])
        warnings.extend(title_check['warnings'])
        
        # 3. Check synopsis
        synopsis = film_data.get('synopsis', '')
        if synopsis:
            synopsis_check = self._check_text(synopsis, 'Synopsis')
            issues.extend(synopsis_check['issues'])
            warnings.extend(synopsis_check['warnings'])
        
        # 4. Check themes
        themes = film_data.get('themes', '')
        if themes:
            themes_check = self._check_text(themes, 'Themes')
            issues.extend(themes_check['issues'])
            warnings.extend(themes_check['warnings'])
        
        # 5. Check duration validity
        duration = film_data.get('duration', 0)
        try:
            duration = int(duration)
            if duration < 1:
                issues.append("Duration must be at least 1 minute")
            elif duration > 600:
                warnings.append("Duration over 10 hours - please verify")
        except:
            issues.append("Invalid duration format")
        
        # 6. Check for copyright concerns
        copyright_check = self._check_copyright(film_data)
        warnings.extend(copyright_check)
        
        # 7. Check for spam/bot submission
        spam_check = self._check_spam(film_data)
        issues.extend(spam_check['issues'])
        warnings.extend(spam_check['warnings'])
        
        # 8. Check originality (basic)
        originality = self._check_originality(title)
        warnings.extend(originality)
        
        # Calculate safety score
        safety_score = 100
        safety_score -= len(issues) * 20
        safety_score -= len(warnings) * 5
        safety_score = max(0, min(100, safety_score))
        
        # Determine approval
        approved = len(issues) == 0 and safety_score >= 50
        
        return {
            'approved': approved,
            'safety_score': safety_score,
            'status': 'approved' if approved else 'rejected',
            'issues': issues,
            'warnings': warnings,
            'checked_at': datetime.now().isoformat(),
            'checker': self.name,
            'recommendation': self._get_recommendation(approved, issues, warnings)
        }
    
    def _check_text(self, text, field_name):
        """Check text for offensive content"""
        issues = []
        warnings = []
        text_lower = text.lower()
        
        # Check offensive terms
        for term in self.offensive_terms:
            if term in text_lower:
                issues.append(f"{field_name} contains potentially offensive content: '{term}'")
        
        # Check for excessive caps (shouting)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.7 and len(text) > 10:
            warnings.append(f"{field_name} has excessive capitals - may appear as spam")
        
        # Check for very short content
        if len(text.strip()) < 2:
            issues.append(f"{field_name} is too short")
        
        return {'issues': issues, 'warnings': warnings}
    
    def _check_copyright(self, film_data):
        """Check for potential copyright issues"""
        warnings = []
        
        text_to_check = ' '.join([
            str(film_data.get('title', '')),
            str(film_data.get('synopsis', '')),
            str(film_data.get('themes', ''))
        ]).lower()
        
        for flag in self.copyright_flags:
            if flag in text_to_check:
                warnings.append(f"Potential copyright concern: content mentions '{flag}'")
        
        return warnings
    
    def _check_spam(self, film_data):
        """Check for spam patterns"""
        issues = []
        warnings = []
        
        text = str(film_data.get('title', '')) + str(film_data.get('synopsis', ''))
        
        for pattern in self.spam_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                warnings.append("Content matches spam patterns")
                break
        
        # Check for suspicious URLs
        if re.search(r'https?://', text):
            warnings.append("Content contains URLs - will be reviewed")
        
        # Check for email addresses
        if re.search(r'\S+@\S+\.\S+', text):
            warnings.append("Content contains email addresses - will be reviewed")
        
        return {'issues': issues, 'warnings': warnings}
    
    def _check_originality(self, title):
        """Basic originality check"""
        warnings = []
        
        # Common generic titles
        generic_titles = [
            'untitled', 'test', 'my film', 'movie', 'short film',
            'the movie', 'film project', 'demo'
        ]
        
        if title.lower().strip() in generic_titles:
            warnings.append("Title appears generic - consider a more unique title")
        
        return warnings
    
    def _get_recommendation(self, approved, issues, warnings):
        """Generate recommendation based on check results"""
        if approved and not warnings:
            return "Content approved - ready for analysis"
        elif approved and warnings:
            return "Content approved with minor concerns - review warnings"
        elif issues:
            return "Content rejected - please address issues and resubmit"
        else:
            return "Content needs review - please check warnings"
    
    def quick_check(self, title, synopsis=""):
        """Quick check for real-time validation"""
        text = f"{title} {synopsis}".lower()
        
        for term in self.offensive_terms:
            if term in text:
                return {'valid': False, 'reason': 'Contains inappropriate content'}
        
        if len(title.strip()) < 2:
            return {'valid': False, 'reason': 'Title too short'}
        
        return {'valid': True, 'reason': 'Passed quick check'}


# Test
if __name__ == "__main__":
    checker = ContentChecker()
    
    # Test good film
    good_film = {
        'title': 'The Journey Home',
        'duration': 95,
        'country': 'UK',
        'genre': 'Drama',
        'synopsis': 'A heartwarming story about family reunion.',
        'themes': 'family, love, hope'
    }
    
    result = checker.check_film(good_film)
    print("Good Film Check:")
    print(f"  Approved: {result['approved']}")
    print(f"  Score: {result['safety_score']}")
    print(f"  Issues: {result['issues']}")
    print(f"  Warnings: {result['warnings']}")
    
    # Test problematic film
    bad_film = {
        'title': 'AAAAAAA TEST',
        'duration': 0,
        'synopsis': 'Buy now click here free money!'
    }
    
    result = checker.check_film(bad_film)
    print("\nBad Film Check:")
    print(f"  Approved: {result['approved']}")
    print(f"  Score: {result['safety_score']}")
    print(f"  Issues: {result['issues']}")
    print(f"  Warnings: {result['warnings']}")
    
    print("\nContent checker ready!")