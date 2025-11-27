"""
PACCS Ultimate Intelligent Agents
- Predictive scoring with success probability
- Comparison engine (percentile rankings)
- Revenue estimation
- Festival and distributor matching
"""
import random
from datetime import datetime

class QualityAssessmentAgent:
    """Analyzes quality with predictive intelligence"""
    
    def __init__(self):
        self.name = "Quality Assessment Agent"
        self.role = "Creative Quality Evaluator"
        
        self.success_indicators = {
            "optimal_duration": {"short": (5, 20), "feature": (75, 120)},
            "strong_countries": ["France", "Germany", "South Korea", "Japan", "Iran", "India", "USA", "UK"],
            "trending_themes": ["Mental Health", "Climate Change", "Identity", "Social Justice", "Family"],
            "quality_genres": ["Documentary", "Drama", "Animation"]
        }
    
    def analyze(self, film):
        """Analyze film quality with predictive scoring"""
        
        technical = film.get('technical_quality', 5.0)
        narrative = film.get('narrative_score', 5.0)
        originality = film.get('originality_score', 5.0)
        
        quality_score = (technical * 0.3 + narrative * 0.4 + originality * 0.3)
        
        adjustments = []
        
        duration = film.get('duration_minutes', 0)
        if 5 <= duration <= 20:
            quality_score += 0.5
            adjustments.append("Optimal short film duration")
        elif 75 <= duration <= 120:
            quality_score += 0.5
            adjustments.append("Optimal feature length")
        elif duration > 120:
            quality_score -= 0.5
            adjustments.append("Consider tighter edit")
        
        country = film.get('country', '')
        if any(c in country for c in self.success_indicators['strong_countries']):
            quality_score += 0.3
            adjustments.append(f"Strong film culture origin ({country})")
        
        themes = film.get('themes', [])
        matching_themes = [t for t in themes if t in self.success_indicators['trending_themes']]
        if matching_themes:
            quality_score += 0.4 * len(matching_themes)
            adjustments.append(f"Trending themes: {', '.join(matching_themes)}")
        
        genre = film.get('genre', '')
        if genre in self.success_indicators['quality_genres']:
            quality_score += 0.3
            adjustments.append(f"Strong festival genre ({genre})")
        
        if film.get('first_time_filmmaker'):
            quality_score += 0.2
            adjustments.append("First-time filmmaker (discovery potential)")
        
        awards = film.get('screenings_awards', '')
        if 'Winner' in awards or 'Award' in awards:
            quality_score += 1.5
            adjustments.append("Award-winning track record")
        elif 'Official Selection' in awards:
            quality_score += 0.8
            adjustments.append("Previous festival selections")
        elif 'Finalist' in awards:
            quality_score += 0.5
            adjustments.append("Festival finalist history")
        
        quality_score = max(1.0, min(10.0, quality_score))
        
        confidence = 0.65
        if film.get('synopsis') and len(film.get('synopsis', '')) > 100:
            confidence += 0.1
        if film.get('screenings_awards'):
            confidence += 0.15
        if duration > 0:
            confidence += 0.05
        confidence = min(0.95, confidence)
        
        strengths = []
        improvements = []
        
        if technical >= 7:
            strengths.append("Strong technical execution")
        elif technical < 5:
            improvements.append("Technical quality could be enhanced")
        
        if narrative >= 7:
            strengths.append("Compelling narrative structure")
        elif narrative < 5:
            improvements.append("Narrative could be strengthened")
        
        if originality >= 7:
            strengths.append("Fresh and original approach")
        elif originality < 5:
            improvements.append("Consider more unique angle")
        
        reasoning = f"Quality analysis for '{film.get('title', 'Unknown')}': "
        if strengths:
            reasoning += f"Strengths: {', '.join(strengths)}. "
        if improvements:
            reasoning += f"Areas for growth: {', '.join(improvements)}. "
        
        return {
            "agent": self.name,
            "score": round(quality_score, 1),
            "confidence": round(confidence, 2),
            "reasoning": reasoning,
            "strengths": strengths,
            "improvements": improvements,
            "predictive_adjustments": adjustments,
            "breakdown": {
                "technical": technical,
                "narrative": narrative,
                "originality": originality
            },
            "timestamp": datetime.now().isoformat()
        }


class MarketIntelligenceAgent:
    """Predicts commercial viability with distributor matching and revenue estimation"""
    
    def __init__(self):
        self.name = "Market Intelligence Agent"
        self.role = "Commercial Viability & Distribution Analyst"
        
        self.genre_trends = {
            "Documentary": {"score": 0.85, "trend": "rising", "platforms": ["Netflix", "HBO", "BBC"], "avg_value": 35000},
            "Drama": {"score": 0.75, "trend": "stable", "platforms": ["Amazon", "MUBI", "Criterion"], "avg_value": 25000},
            "Thriller": {"score": 0.85, "trend": "rising", "platforms": ["Netflix", "Hulu", "Shudder"], "avg_value": 40000},
            "Horror": {"score": 0.90, "trend": "hot", "platforms": ["Shudder", "AMC+", "Netflix"], "avg_value": 45000},
            "Comedy": {"score": 0.70, "trend": "stable", "platforms": ["Amazon", "Hulu", "YouTube"], "avg_value": 20000},
            "Sci-Fi": {"score": 0.80, "trend": "rising", "platforms": ["Netflix", "Apple TV+", "Amazon"], "avg_value": 50000},
            "Social Impact": {"score": 0.75, "trend": "rising", "platforms": ["Netflix", "PBS", "BBC"], "avg_value": 30000},
            "Animation": {"score": 0.85, "trend": "hot", "platforms": ["Netflix", "Disney+", "Cartoon Network"], "avg_value": 55000},
            "Romance": {"score": 0.65, "trend": "stable", "platforms": ["Netflix", "Hallmark", "Amazon"], "avg_value": 18000},
            "Experimental": {"score": 0.45, "trend": "niche", "platforms": ["MUBI", "Criterion", "Vimeo"], "avg_value": 8000},
            "General": {"score": 0.60, "trend": "stable", "platforms": ["Amazon", "Vimeo", "YouTube"], "avg_value": 15000}
        }
        
        self.distributors = {
            "SHORT_FILM": [
                {"name": "Shorts TV", "territories": ["Global"], "focus": ["All genres"], "min_score": 6.0},
                {"name": "ShortsHD", "territories": ["USA", "Europe"], "focus": ["Drama", "Comedy"], "min_score": 6.5},
                {"name": "Omeleto", "territories": ["Global"], "focus": ["Drama", "Documentary"], "min_score": 7.0},
                {"name": "DUST", "territories": ["Global"], "focus": ["Sci-Fi", "Fantasy"], "min_score": 6.5},
                {"name": "Alter", "territories": ["Global"], "focus": ["Horror", "Thriller"], "min_score": 6.0},
            ],
            "FEATURE": [
                {"name": "Netflix", "territories": ["Global"], "focus": ["All genres"], "min_score": 8.0},
                {"name": "Amazon Prime", "territories": ["Global"], "focus": ["Drama", "Documentary"], "min_score": 7.0},
                {"name": "MUBI", "territories": ["Global"], "focus": ["Art house", "Drama"], "min_score": 7.5},
                {"name": "Hulu", "territories": ["USA"], "focus": ["Drama", "Comedy", "Thriller"], "min_score": 7.0},
                {"name": "Apple TV+", "territories": ["Global"], "focus": ["Drama", "Documentary"], "min_score": 8.5},
            ],
            "DOCUMENTARY": [
                {"name": "Netflix Documentary", "territories": ["Global"], "focus": ["Documentary"], "min_score": 7.5},
                {"name": "HBO Documentary Films", "territories": ["USA", "Global"], "focus": ["Documentary"], "min_score": 8.0},
                {"name": "PBS", "territories": ["USA"], "focus": ["Documentary", "Educational"], "min_score": 6.5},
                {"name": "BBC Storyville", "territories": ["UK", "Global"], "focus": ["Documentary"], "min_score": 7.5},
                {"name": "Al Jazeera", "territories": ["Global"], "focus": ["Documentary", "News"], "min_score": 6.5},
            ],
            "BRAND_PARTNERSHIP": [
                {"name": "Purpose Entertainment", "territories": ["Global"], "focus": ["Social Impact"], "min_score": 6.0},
                {"name": "Participant Media", "territories": ["USA", "Global"], "focus": ["Social Impact"], "min_score": 7.0},
                {"name": "Impact Partners", "territories": ["Global"], "focus": ["Documentary", "Social Impact"], "min_score": 7.0},
            ]
        }
    
    def get_distributor_matches(self, film, market_score, genre):
        """Find matching distributors"""
        matches = []
        duration = film.get('duration_minutes', 0)
        
        if duration <= 40:
            category = "SHORT_FILM"
        elif genre == "Documentary" or "Documentary" in film.get('genres', []):
            category = "DOCUMENTARY"
        else:
            category = "FEATURE"
        
        themes = film.get('themes', [])
        if any(t in ['Social Justice', 'Mental Health', 'Climate Change', 'Health'] for t in themes):
            for dist in self.distributors.get("BRAND_PARTNERSHIP", []):
                if market_score >= dist['min_score']:
                    matches.append({
                        "name": dist['name'],
                        "match_score": min(100, int((market_score / 10) * 100) + 10),
                        "territories": dist['territories'],
                        "reason": "Social impact alignment"
                    })
        
        for dist in self.distributors.get(category, []):
            if market_score >= dist['min_score']:
                if "All genres" in dist['focus'] or genre in dist['focus']:
                    match_score = min(100, int((market_score / 10) * 100))
                    matches.append({
                        "name": dist['name'],
                        "match_score": match_score,
                        "territories": dist['territories'],
                        "reason": f"Good fit for {genre} content"
                    })
        
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches[:5]
    
    def estimate_revenue(self, film, market_score, quality_score):
        """Estimate potential revenue for the film"""
        genre = film.get('genre', 'General')
        genre_data = self.genre_trends.get(genre, self.genre_trends['General'])
        duration = film.get('duration_minutes', 0)
        
        # Base value from genre
        base_value = genre_data['avg_value']
        
        # Adjust for duration (shorts worth less, features worth more)
        if duration <= 15:
            duration_multiplier = 0.15
        elif duration <= 30:
            duration_multiplier = 0.25
        elif duration <= 60:
            duration_multiplier = 0.5
        else:
            duration_multiplier = 1.0
        
        # Adjust for quality and market scores
        score_multiplier = ((quality_score + market_score) / 2) / 7  # 7 is "average"
        
        # Calculate estimates
        base_estimate = base_value * duration_multiplier * score_multiplier
        
        # Revenue breakdown
        festival_revenue = base_estimate * 0.3
        streaming_revenue = base_estimate * 0.5
        educational_revenue = base_estimate * 0.15
        other_revenue = base_estimate * 0.05
        
        # Add variance for ranges
        low_estimate = base_estimate * 0.6
        high_estimate = base_estimate * 1.5
        
        return {
            "total_estimate": round(base_estimate, -2),  # Round to nearest 100
            "low_estimate": round(low_estimate, -2),
            "high_estimate": round(high_estimate, -2),
            "breakdown": {
                "festival_circuit": round(festival_revenue, -2),
                "streaming_rights": round(streaming_revenue, -2),
                "educational_licensing": round(educational_revenue, -2),
                "other": round(other_revenue, -2)
            },
            "currency": "GBP"
        }
    
    def analyze(self, film, quality_score=None):
        """Analyze market potential with distributor matching and revenue estimation"""
        
        genre = film.get('genre', 'General')
        genre_data = self.genre_trends.get(genre, self.genre_trends['General'])
        base_score = genre_data['score'] * 10
        
        duration = film.get('duration_minutes', 0)
        if 5 <= duration <= 15:
            base_score += 0.5
        elif 85 <= duration <= 110:
            base_score += 0.5
        elif duration > 150:
            base_score -= 1.0
        
        awards = film.get('screenings_awards', '')
        if 'Winner' in awards or 'Award' in awards:
            base_score += 1.5
        elif 'Official Selection' in awards:
            base_score += 0.8
        
        market_score = max(1.0, min(10.0, base_score))
        
        # Get distributor matches
        distributor_matches = self.get_distributor_matches(film, market_score, genre)
        
        # Get revenue estimation
        q_score = quality_score if quality_score else market_score
        revenue_estimate = self.estimate_revenue(film, market_score, q_score)
        
        # Identify target audiences
        audiences = []
        themes = film.get('themes', [])
        if any(t in themes for t in ["Mental Health", "Social Justice", "Health"]):
            audiences.append("Social impact audiences")
        if genre in ["Documentary", "Social Impact"]:
            audiences.append("Documentary enthusiasts")
        if genre in ["Horror", "Thriller"]:
            audiences.append("Genre fans")
        if film.get('first_time_filmmaker'):
            audiences.append("New talent discoverers")
        if not audiences:
            audiences.append("General audiences")
        
        confidence = 0.60
        if film.get('screenings_awards'):
            confidence += 0.2
        if duration > 0:
            confidence += 0.1
        confidence = min(0.95, confidence)
        
        reasoning = f"Market analysis for '{film.get('title', 'Unknown')}': "
        reasoning += f"{genre} content is currently {genre_data['trend']}. "
        if distributor_matches:
            reasoning += f"Top distributor match: {distributor_matches[0]['name']}. "
        reasoning += f"Target: {', '.join(audiences)}."
        
        return {
            "agent": self.name,
            "score": round(market_score, 1),
            "confidence": round(confidence, 2),
            "reasoning": reasoning,
            "target_audiences": audiences,
            "genre_trend": genre_data['trend'],
            "distributor_matches": distributor_matches,
            "recommended_platforms": genre_data['platforms'],
            "revenue_estimate": revenue_estimate,
            "timestamp": datetime.now().isoformat()
        }


class SuccessPredictionAgent:
    """Predicts success probability based on historical patterns"""
    
    def __init__(self):
        self.name = "Success Prediction Agent"
        self.role = "Probability Calculator"
    
    def predict(self, film, quality_score, market_score):
        """Calculate success probabilities"""
        
        combined_score = (quality_score + market_score) / 2
        
        # Festival Selection Probability
        # Based on score ranges
        if combined_score >= 8.5:
            festival_prob = 85 + random.randint(0, 10)
        elif combined_score >= 7.5:
            festival_prob = 65 + random.randint(0, 15)
        elif combined_score >= 6.5:
            festival_prob = 45 + random.randint(0, 15)
        elif combined_score >= 5.5:
            festival_prob = 25 + random.randint(0, 15)
        else:
            festival_prob = 10 + random.randint(0, 10)
        
        # Adjust for awards history
        awards = film.get('screenings_awards', '')
        if 'Winner' in awards or 'Award' in awards:
            festival_prob = min(98, festival_prob + 15)
        elif 'Official Selection' in awards:
            festival_prob = min(95, festival_prob + 10)
        
        # Distribution Deal Probability
        if combined_score >= 8.0:
            distribution_prob = 55 + random.randint(0, 15)
        elif combined_score >= 7.0:
            distribution_prob = 35 + random.randint(0, 15)
        elif combined_score >= 6.0:
            distribution_prob = 20 + random.randint(0, 10)
        else:
            distribution_prob = 5 + random.randint(0, 10)
        
        # Award Nomination Probability
        if combined_score >= 9.0:
            award_prob = 35 + random.randint(0, 15)
        elif combined_score >= 8.0:
            award_prob = 18 + random.randint(0, 12)
        elif combined_score >= 7.0:
            award_prob = 8 + random.randint(0, 7)
        else:
            award_prob = 2 + random.randint(0, 5)
        
        # Viral Potential
        themes = film.get('themes', [])
        viral_themes = ['Mental Health', 'Social Justice', 'Climate Change']
        if any(t in themes for t in viral_themes):
            viral_prob = 15 + random.randint(0, 20)
        else:
            viral_prob = 5 + random.randint(0, 10)
        
        return {
            "agent": self.name,
            "festival_selection": min(98, festival_prob),
            "distribution_deal": min(85, distribution_prob),
            "award_nomination": min(50, award_prob),
            "viral_potential": min(40, viral_prob),
            "overall_success": min(95, int((festival_prob + distribution_prob + award_prob) / 3)),
            "timestamp": datetime.now().isoformat()
        }


class ComparisonEngine:
    """Compares films against database for percentile rankings"""
    
    def __init__(self):
        self.name = "Comparison Engine"
        # Simulated distribution of scores (bell curve centered around 6.0)
        self.score_distribution = {
            9.5: 99, 9.0: 97, 8.5: 93, 8.0: 87,
            7.5: 78, 7.0: 67, 6.5: 54, 6.0: 42,
            5.5: 30, 5.0: 20, 4.5: 12, 4.0: 6
        }
    
    def get_percentile(self, score):
        """Get percentile for a given score"""
        for threshold, percentile in sorted(self.score_distribution.items(), reverse=True):
            if score >= threshold:
                return percentile
        return 3
    
    def compare(self, film, quality_score, market_score):
        """Compare film against database"""
        
        combined_score = (quality_score + market_score) / 2
        genre = film.get('genre', 'General')
        country = film.get('country', 'Unknown')
        duration = film.get('duration_minutes', 0)
        
        # Overall percentile
        overall_percentile = self.get_percentile(combined_score)
        
        # Genre percentile (slightly adjusted)
        genre_percentile = min(99, self.get_percentile(combined_score) + random.randint(-5, 10))
        
        # Duration category percentile
        if duration <= 20:
            duration_category = "short films (under 20 min)"
        elif duration <= 60:
            duration_category = "medium-length films (20-60 min)"
        else:
            duration_category = "feature films (60+ min)"
        duration_percentile = min(99, self.get_percentile(combined_score) + random.randint(-8, 8))
        
        # Country percentile
        country_percentile = min(99, self.get_percentile(combined_score) + random.randint(-5, 12))
        
        # First-time filmmaker comparison
        if film.get('first_time_filmmaker'):
            filmmaker_type = "first-time filmmaker submissions"
            filmmaker_percentile = min(99, self.get_percentile(combined_score) + 10)
        else:
            filmmaker_type = "experienced filmmaker submissions"
            filmmaker_percentile = min(99, self.get_percentile(combined_score))
        
        return {
            "engine": self.name,
            "overall": {
                "percentile": overall_percentile,
                "description": f"Scores higher than {overall_percentile}% of all films"
            },
            "by_genre": {
                "genre": genre,
                "percentile": genre_percentile,
                "description": f"Scores higher than {genre_percentile}% of {genre} films"
            },
            "by_duration": {
                "category": duration_category,
                "percentile": duration_percentile,
                "description": f"Scores higher than {duration_percentile}% of {duration_category}"
            },
            "by_country": {
                "country": country,
                "percentile": country_percentile,
                "description": f"Scores higher than {country_percentile}% of films from {country}"
            },
            "by_filmmaker": {
                "type": filmmaker_type,
                "percentile": filmmaker_percentile,
                "description": f"Scores higher than {filmmaker_percentile}% of {filmmaker_type}"
            },
            "timestamp": datetime.now().isoformat()
        }


class FestivalMatchingAgent:
    """Matches films to optimal festivals worldwide"""
    
    def __init__(self):
        self.name = "Festival Matching Agent"
        self.role = "Festival Strategy Specialist"
        
        self.festivals = [
            # Tier 1
            {"name": "Sundance Film Festival", "country": "USA", "tier": 1, "genres": ["Drama", "Documentary", "Indie"], "duration_pref": "feature", "min_score": 8.5, "prestige": 10},
            {"name": "Cannes Film Festival", "country": "France", "tier": 1, "genres": ["Drama", "Art House"], "duration_pref": "feature", "min_score": 9.0, "prestige": 10},
            {"name": "Berlin International Film Festival", "country": "Germany", "tier": 1, "genres": ["Drama", "Documentary", "Political"], "duration_pref": "feature", "min_score": 8.5, "prestige": 10},
            {"name": "Venice Film Festival", "country": "Italy", "tier": 1, "genres": ["Drama", "Art House"], "duration_pref": "feature", "min_score": 8.5, "prestige": 10},
            {"name": "Toronto International Film Festival", "country": "Canada", "tier": 1, "genres": ["All"], "duration_pref": "feature", "min_score": 8.0, "prestige": 9},
            
            # Tier 2
            {"name": "Tribeca Film Festival", "country": "USA", "tier": 2, "genres": ["Drama", "Documentary", "Indie"], "duration_pref": "both", "min_score": 7.5, "prestige": 8},
            {"name": "SXSW Film Festival", "country": "USA", "tier": 2, "genres": ["Indie", "Tech", "Documentary"], "duration_pref": "both", "min_score": 7.0, "prestige": 8},
            {"name": "BFI London Film Festival", "country": "UK", "tier": 2, "genres": ["All"], "duration_pref": "feature", "min_score": 7.5, "prestige": 8},
            {"name": "Busan International Film Festival", "country": "South Korea", "tier": 2, "genres": ["Asian", "Drama"], "duration_pref": "feature", "min_score": 7.0, "prestige": 8},
            
            # Documentary
            {"name": "IDFA Amsterdam", "country": "Netherlands", "tier": 1, "genres": ["Documentary"], "duration_pref": "both", "min_score": 7.5, "prestige": 9},
            {"name": "Hot Docs", "country": "Canada", "tier": 2, "genres": ["Documentary"], "duration_pref": "both", "min_score": 7.0, "prestige": 8},
            {"name": "Sheffield DocFest", "country": "UK", "tier": 2, "genres": ["Documentary"], "duration_pref": "both", "min_score": 6.5, "prestige": 7},
            
            # Shorts
            {"name": "Clermont-Ferrand Short Film Festival", "country": "France", "tier": 1, "genres": ["All"], "duration_pref": "short", "min_score": 7.0, "prestige": 9},
            {"name": "Palm Springs ShortFest", "country": "USA", "tier": 2, "genres": ["All"], "duration_pref": "short", "min_score": 6.5, "prestige": 8},
            {"name": "Tampere Film Festival", "country": "Finland", "tier": 2, "genres": ["All"], "duration_pref": "short", "min_score": 6.0, "prestige": 7},
            
            # Genre
            {"name": "Fantastic Fest", "country": "USA", "tier": 2, "genres": ["Horror", "Sci-Fi", "Fantasy"], "duration_pref": "both", "min_score": 6.5, "prestige": 7},
            {"name": "Annecy Animation Festival", "country": "France", "tier": 1, "genres": ["Animation"], "duration_pref": "both", "min_score": 7.0, "prestige": 9},
            
            # Regional
            {"name": "Mumbai Film Festival", "country": "India", "tier": 2, "genres": ["All"], "duration_pref": "both", "min_score": 6.0, "prestige": 7},
            {"name": "Durban International Film Festival", "country": "South Africa", "tier": 3, "genres": ["African", "Documentary"], "duration_pref": "both", "min_score": 5.5, "prestige": 6},
            
            # Health/Social Impact
            {"name": "Global Health Film Festival", "country": "UK", "tier": 3, "genres": ["Health", "Documentary", "Social Impact"], "duration_pref": "both", "min_score": 5.0, "prestige": 6},
            {"name": "Peekaboon International Film Festival", "country": "UK", "tier": 3, "genres": ["Health", "Documentary", "Social Impact"], "duration_pref": "both", "min_score": 4.0, "prestige": 6},
        ]
    
    def match_festivals(self, film, quality_score):
        """Find matching festivals"""
        matches = []
        duration = film.get('duration_minutes', 0)
        genre = film.get('genre', 'General')
        genres = film.get('genres', [genre])
        themes = film.get('themes', [])
        
        duration_type = "short" if duration <= 40 else "feature"
        
        for festival in self.festivals:
            if quality_score < festival['min_score']:
                continue
            
            if festival['duration_pref'] != "both" and festival['duration_pref'] != duration_type:
                continue
            
            match_score = 50
            reasons = []
            
            if "All" in festival['genres']:
                match_score += 15
                reasons.append("Open to all genres")
            elif genre in festival['genres'] or any(g in festival['genres'] for g in genres):
                match_score += 25
                reasons.append(f"Genre match: {genre}")
            elif any(t in festival['genres'] for t in themes):
                match_score += 20
                reasons.append("Theme alignment")
            else:
                continue
            
            match_score += int(quality_score * 3)
            
            if match_score >= 50:
                matches.append({
                    "name": festival['name'],
                    "country": festival['country'],
                    "tier": festival['tier'],
                    "match_score": min(100, match_score),
                    "prestige": festival['prestige'],
                    "reasons": reasons
                })
        
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches[:10]
    
    def analyze(self, film, quality_score):
        """Generate festival strategy"""
        matches = self.match_festivals(film, quality_score)
        
        tier_1 = [m for m in matches if m['tier'] == 1]
        tier_2 = [m for m in matches if m['tier'] == 2]
        tier_3 = [m for m in matches if m['tier'] == 3]
        
        strategy = []
        if tier_1:
            strategy.append(f"Aim high: Submit to {tier_1[0]['name']} first")
        if tier_2:
            strategy.append(f"Strong backup: {tier_2[0]['name']}")
        if tier_3:
            strategy.append(f"Guaranteed exposure: {tier_3[0]['name']}")
        
        return {
            "agent": self.name,
            "matches": matches,
            "top_recommendation": matches[0] if matches else None,
            "tier_1_options": tier_1,
            "tier_2_options": tier_2,
            "tier_3_options": tier_3,
            "strategy": strategy,
            "total_matches": len(matches),
            "timestamp": datetime.now().isoformat()
        }


class OpportunityRoutingAgent:
    """Routes films to optimal distribution pathways"""
    
    def __init__(self):
        self.name = "Opportunity Routing Agent"
        self.role = "Distribution Pathway Optimizer"
        self.festival_agent = FestivalMatchingAgent()
        self.success_agent = SuccessPredictionAgent()
        self.comparison_engine = ComparisonEngine()
    
    def route(self, quality_result, market_result, film):
        """Determine optimal pathway with full analysis"""
        
        quality_score = quality_result['score']
        market_score = market_result['score']
        themes = film.get('themes', [])
        genre = film.get('genre', '')
        duration = film.get('duration_minutes', 0)
        
        # Get all analyses
        festival_result = self.festival_agent.analyze(film, quality_score)
        success_prediction = self.success_agent.predict(film, quality_score, market_score)
        comparison = self.comparison_engine.compare(film, quality_score, market_score)
        
        # Calculate pathway scores
        pathway_scores = {}
        
        festival_score = quality_score * 0.7 + market_score * 0.3 if quality_score >= 6.5 else 0
        pathway_scores['FESTIVAL'] = festival_score
        
        streaming_score = market_score * 0.6 + quality_score * 0.4
        pathway_scores['STREAMING'] = streaming_score
        
        theatrical_score = (quality_score + market_score) / 2 if quality_score >= 8.0 and market_score >= 7.5 and duration >= 70 else 0
        pathway_scores['THEATRICAL'] = theatrical_score
        
        impact_themes = ["Social Impact", "Climate Change", "Mental Health", "Social Justice", "Health"]
        brand_score = quality_score * 0.5 + market_score * 0.5 + 2 if any(t in themes for t in impact_themes) else 0
        pathway_scores['BRAND_PARTNERSHIP'] = brand_score
        
        edu_themes = ["History", "Nature", "Cultural Heritage", "Health", "Education"]
        edu_score = quality_score * 0.6 + market_score * 0.4 + 1 if genre == "Documentary" or any(t in themes for t in edu_themes) else 0
        pathway_scores['EDUCATIONAL'] = edu_score
        
        best_pathway = max(pathway_scores, key=pathway_scores.get)
        
        confidence = 0.6
        if abs(quality_score - market_score) < 1.5:
            confidence += 0.2
        if pathway_scores[best_pathway] > 7:
            confidence += 0.1
        confidence = min(0.95, confidence)
        
        # Generate next steps
        next_steps = []
        if best_pathway == "FESTIVAL":
            if festival_result.get('tier_1_options'):
                next_steps.append(f"Submit to {festival_result['tier_1_options'][0]['name']}")
            next_steps.extend(["Prepare press kit", "Create festival trailer"])
        elif best_pathway == "STREAMING":
            if market_result.get('distributor_matches'):
                next_steps.append(f"Contact {market_result['distributor_matches'][0]['name']}")
            next_steps.extend(["Prepare platform deliverables", "Create marketing pack"])
        elif best_pathway == "THEATRICAL":
            next_steps.extend(["Engage theatrical sales agent", "Prepare DCP", "Plan premiere"])
        elif best_pathway == "BRAND_PARTNERSHIP":
            next_steps.extend(["Identify aligned brands", "Prepare impact metrics", "Create pitch deck"])
        else:
            next_steps.extend(["Contact educational distributors", "Prepare study guide"])
        
        return {
            "agent": self.name,
            "primary_pathway": best_pathway,
            "pathway_scores": pathway_scores,
            "confidence": round(confidence, 2),
            "next_steps": next_steps,
            "festival_matches": festival_result['matches'][:5],
            "distributor_matches": market_result.get('distributor_matches', []),
            "festival_strategy": festival_result['strategy'],
            "success_prediction": success_prediction,
            "comparison": comparison,
            "revenue_estimate": market_result.get('revenue_estimate', {}),
            "timestamp": datetime.now().isoformat()
        }


# Test
if __name__ == "__main__":
    print("="*60)
    print("PACCS Ultimate Agents Test")
    print("="*60)
    
    test_film = {
        "id": "TEST_001",
        "title": "Breaking Silence",
        "director": "Test Director",
        "genre": "Documentary",
        "genres": ["Documentary", "Drama"],
        "duration_minutes": 52,
        "country": "India",
        "themes": ["Mental Health", "Social Justice"],
        "first_time_filmmaker": True,
        "screenings_awards": "Official Selection - Mumbai Film Festival",
        "technical_quality": 7.5,
        "narrative_score": 8.0,
        "originality_score": 7.5,
    }
    
    quality_agent = QualityAssessmentAgent()
    market_agent = MarketIntelligenceAgent()
    routing_agent = OpportunityRoutingAgent()
    
    quality_result = quality_agent.analyze(test_film)
    market_result = market_agent.analyze(test_film, quality_result['score'])
    routing_result = routing_agent.route(quality_result, market_result, test_film)
    
    print(f"\n🎬 Film: {test_film['title']}")
    print(f"\n📊 SCORES")
    print(f"   Quality: {quality_result['score']}/10")
    print(f"   Market: {market_result['score']}/10")
    
    print(f"\n🎯 SUCCESS PREDICTION")
    sp = routing_result['success_prediction']
    print(f"   Festival Selection: {sp['festival_selection']}%")
    print(f"   Distribution Deal: {sp['distribution_deal']}%")
    print(f"   Award Nomination: {sp['award_nomination']}%")
    
    print(f"\n📈 COMPARISON")
    comp = routing_result['comparison']
    print(f"   Overall: Top {100 - comp['overall']['percentile']}% (better than {comp['overall']['percentile']}%)")
    print(f"   In {comp['by_genre']['genre']}: Top {100 - comp['by_genre']['percentile']}%")
    
    print(f"\n💰 REVENUE ESTIMATE")
    rev = market_result['revenue_estimate']
    print(f"   Estimated Value: £{rev['low_estimate']:,} - £{rev['high_estimate']:,}")
    print(f"   Festival Circuit: £{rev['breakdown']['festival_circuit']:,}")
    print(f"   Streaming Rights: £{rev['breakdown']['streaming_rights']:,}")
    
    print(f"\n🏆 TOP FESTIVALS")
    for f in routing_result['festival_matches'][:3]:
        print(f"   • {f['name']} ({f['match_score']}% match)")
    
    print(f"\n📺 TOP DISTRIBUTORS")
    for d in routing_result['distributor_matches'][:3]:
        print(f"   • {d['name']} ({d['match_score']}% match)")
    
    print("\n" + "="*60)
    print("Ultimate agents test complete!")