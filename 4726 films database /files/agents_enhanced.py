"""
PACCS Enhanced Intelligent Agents
- Predictive scoring based on real selection patterns
- Festival matching
- Distributor matching
- Comprehensive recommendations
"""
import random
from datetime import datetime

class QualityAssessmentAgent:
    """Analyzes narrative, technical, and artistic quality with predictive intelligence"""
    
    def __init__(self):
        self.name = "Quality Assessment Agent"
        self.role = "Creative Quality Evaluator"
        
        # Learned patterns from successful films (based on real festival data)
        self.success_indicators = {
            "optimal_duration": {"short": (5, 20), "feature": (75, 120)},
            "strong_countries": ["France", "Germany", "South Korea", "Japan", "Iran", "India", "USA", "UK"],
            "trending_themes": ["Mental Health", "Climate Change", "Identity", "Social Justice", "Family"],
            "quality_genres": ["Documentary", "Drama", "Animation"]
        }
    
    def analyze(self, film):
        """Analyze film quality with predictive scoring"""
        
        # Base scores from film data
        technical = film.get('technical_quality', 5.0)
        narrative = film.get('narrative_score', 5.0)
        originality = film.get('originality_score', 5.0)
        
        # Weighted quality score
        quality_score = (technical * 0.3 + narrative * 0.4 + originality * 0.3)
        
        # Predictive adjustments based on learned patterns
        adjustments = []
        
        # Duration optimization
        duration = film.get('duration_minutes', 0)
        if 5 <= duration <= 20:
            quality_score += 0.5
            adjustments.append("Optimal short film duration")
        elif 75 <= duration <= 120:
            quality_score += 0.5
            adjustments.append("Optimal feature length")
        elif duration > 120:
            quality_score -= 0.5
            adjustments.append("Consider tighter edit - lengthy runtime")
        
        # Country of origin patterns
        country = film.get('country', '')
        if any(c in country for c in self.success_indicators['strong_countries']):
            quality_score += 0.3
            adjustments.append(f"Strong film culture origin ({country})")
        
        # Theme relevance
        themes = film.get('themes', [])
        matching_themes = [t for t in themes if t in self.success_indicators['trending_themes']]
        if matching_themes:
            quality_score += 0.4 * len(matching_themes)
            adjustments.append(f"Trending themes: {', '.join(matching_themes)}")
        
        # Genre strength
        genre = film.get('genre', '')
        if genre in self.success_indicators['quality_genres']:
            quality_score += 0.3
            adjustments.append(f"Strong festival genre ({genre})")
        
        # First-time filmmaker consideration
        if film.get('first_time_filmmaker'):
            quality_score += 0.2
            adjustments.append("First-time filmmaker (discovery potential)")
        
        # Festival track record boost
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
        
        # Ensure valid range
        quality_score = max(1.0, min(10.0, quality_score))
        
        # Calculate confidence
        confidence = 0.65
        if film.get('synopsis') and len(film.get('synopsis', '')) > 100:
            confidence += 0.1
        if film.get('screenings_awards'):
            confidence += 0.15
        if duration > 0:
            confidence += 0.05
        confidence = min(0.95, confidence)
        
        # Generate detailed reasoning
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
        if adjustments:
            reasoning += f"Predictive factors: {', '.join(adjustments[:3])}."
        
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
    """Predicts commercial viability with distributor matching"""
    
    def __init__(self):
        self.name = "Market Intelligence Agent"
        self.role = "Commercial Viability & Distribution Analyst"
        
        # Genre market performance data
        self.genre_trends = {
            "Documentary": {"score": 0.85, "trend": "rising", "platforms": ["Netflix", "HBO", "BBC"]},
            "Drama": {"score": 0.75, "trend": "stable", "platforms": ["Amazon", "MUBI", "Criterion"]},
            "Thriller": {"score": 0.85, "trend": "rising", "platforms": ["Netflix", "Hulu", "Shudder"]},
            "Horror": {"score": 0.90, "trend": "hot", "platforms": ["Shudder", "AMC+", "Netflix"]},
            "Comedy": {"score": 0.70, "trend": "stable", "platforms": ["Amazon", "Hulu", "YouTube"]},
            "Sci-Fi": {"score": 0.80, "trend": "rising", "platforms": ["Netflix", "Apple TV+", "Amazon"]},
            "Social Impact": {"score": 0.75, "trend": "rising", "platforms": ["Netflix", "PBS", "BBC"]},
            "Animation": {"score": 0.85, "trend": "hot", "platforms": ["Netflix", "Disney+", "Cartoon Network"]},
            "Romance": {"score": 0.65, "trend": "stable", "platforms": ["Netflix", "Hallmark", "Amazon"]},
            "Experimental": {"score": 0.45, "trend": "niche", "platforms": ["MUBI", "Criterion", "Vimeo"]},
            "General": {"score": 0.60, "trend": "stable", "platforms": ["Amazon", "Vimeo", "YouTube"]}
        }
        
        # Distributor database
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
        
        # Territory market data
        self.territory_potential = {
            "USA": {"market_size": 10, "accessibility": 0.9},
            "UK": {"market_size": 8, "accessibility": 0.9},
            "India": {"market_size": 9, "accessibility": 0.7},
            "Germany": {"market_size": 7, "accessibility": 0.8},
            "France": {"market_size": 7, "accessibility": 0.8},
            "Japan": {"market_size": 8, "accessibility": 0.6},
            "South Korea": {"market_size": 7, "accessibility": 0.7},
            "Brazil": {"market_size": 6, "accessibility": 0.6},
            "China": {"market_size": 10, "accessibility": 0.3},
            "Canada": {"market_size": 5, "accessibility": 0.9},
        }
    
    def get_distributor_matches(self, film, market_score, genre):
        """Find matching distributors based on film characteristics"""
        matches = []
        duration = film.get('duration_minutes', 0)
        
        # Determine film category
        if duration <= 40:
            category = "SHORT_FILM"
        elif genre == "Documentary" or "Documentary" in film.get('genres', []):
            category = "DOCUMENTARY"
        else:
            category = "FEATURE"
        
        # Check social impact themes
        themes = film.get('themes', [])
        if any(t in ['Social Justice', 'Mental Health', 'Climate Change', 'Health'] for t in themes):
            category = "BRAND_PARTNERSHIP"
        
        # Find matching distributors
        for dist in self.distributors.get(category, []):
            if market_score >= dist['min_score']:
                # Check genre match
                if "All genres" in dist['focus'] or genre in dist['focus'] or any(g in dist['focus'] for g in film.get('genres', [])):
                    match_score = min(100, int((market_score / 10) * 100))
                    matches.append({
                        "name": dist['name'],
                        "match_score": match_score,
                        "territories": dist['territories'],
                        "reason": f"Good fit for {genre} content"
                    })
        
        # Sort by match score
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches[:5]  # Top 5 matches
    
    def analyze(self, film):
        """Analyze market potential with distributor matching"""
        
        genre = film.get('genre', 'General')
        genre_data = self.genre_trends.get(genre, self.genre_trends['General'])
        base_score = genre_data['score'] * 10
        
        # Duration optimization
        duration = film.get('duration_minutes', 0)
        if 5 <= duration <= 15:
            base_score += 0.5  # Sweet spot for shorts
        elif 85 <= duration <= 110:
            base_score += 0.5  # Sweet spot for features
        elif duration > 150:
            base_score -= 1.0
        
        # Festival/award boost
        awards = film.get('screenings_awards', '')
        if 'Winner' in awards or 'Award' in awards:
            base_score += 1.5
        elif 'Official Selection' in awards:
            base_score += 0.8
        
        # Territory considerations
        country = film.get('country', '')
        territory_boost = 0
        for territory, data in self.territory_potential.items():
            if territory in country:
                territory_boost = data['accessibility'] * 0.5
                break
        base_score += territory_boost
        
        # Calculate final market score
        market_score = max(1.0, min(10.0, base_score))
        
        # Get distributor matches
        distributor_matches = self.get_distributor_matches(film, market_score, genre)
        
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
        
        # Calculate confidence
        confidence = 0.60
        if film.get('screenings_awards'):
            confidence += 0.2
        if duration > 0:
            confidence += 0.1
        confidence = min(0.95, confidence)
        
        # Generate reasoning
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
            "timestamp": datetime.now().isoformat()
        }


class FestivalMatchingAgent:
    """Matches films to optimal festivals worldwide"""
    
    def __init__(self):
        self.name = "Festival Matching Agent"
        self.role = "Festival Strategy Specialist"
        
        # Comprehensive festival database
        self.festivals = [
            # Tier 1 - Major Festivals
            {"name": "Sundance Film Festival", "country": "USA", "tier": 1, "genres": ["Drama", "Documentary", "Indie"], "duration_pref": "feature", "min_score": 8.5, "deadline_month": 9, "prestige": 10},
            {"name": "Cannes Film Festival", "country": "France", "tier": 1, "genres": ["Drama", "Art House"], "duration_pref": "feature", "min_score": 9.0, "deadline_month": 3, "prestige": 10},
            {"name": "Berlin International Film Festival", "country": "Germany", "tier": 1, "genres": ["Drama", "Documentary", "Political"], "duration_pref": "feature", "min_score": 8.5, "deadline_month": 10, "prestige": 10},
            {"name": "Venice Film Festival", "country": "Italy", "tier": 1, "genres": ["Drama", "Art House"], "duration_pref": "feature", "min_score": 8.5, "deadline_month": 5, "prestige": 10},
            {"name": "Toronto International Film Festival", "country": "Canada", "tier": 1, "genres": ["All"], "duration_pref": "feature", "min_score": 8.0, "deadline_month": 6, "prestige": 9},
            
            # Tier 2 - Major Regional
            {"name": "Tribeca Film Festival", "country": "USA", "tier": 2, "genres": ["Drama", "Documentary", "Indie"], "duration_pref": "both", "min_score": 7.5, "deadline_month": 12, "prestige": 8},
            {"name": "SXSW Film Festival", "country": "USA", "tier": 2, "genres": ["Indie", "Tech", "Documentary"], "duration_pref": "both", "min_score": 7.0, "deadline_month": 10, "prestige": 8},
            {"name": "BFI London Film Festival", "country": "UK", "tier": 2, "genres": ["All"], "duration_pref": "feature", "min_score": 7.5, "deadline_month": 6, "prestige": 8},
            {"name": "Rotterdam International Film Festival", "country": "Netherlands", "tier": 2, "genres": ["Experimental", "Indie"], "duration_pref": "feature", "min_score": 7.0, "deadline_month": 9, "prestige": 8},
            {"name": "Busan International Film Festival", "country": "South Korea", "tier": 2, "genres": ["Asian", "Drama"], "duration_pref": "feature", "min_score": 7.0, "deadline_month": 7, "prestige": 8},
            
            # Documentary Focused
            {"name": "IDFA Amsterdam", "country": "Netherlands", "tier": 1, "genres": ["Documentary"], "duration_pref": "both", "min_score": 7.5, "deadline_month": 7, "prestige": 9},
            {"name": "Hot Docs", "country": "Canada", "tier": 2, "genres": ["Documentary"], "duration_pref": "both", "min_score": 7.0, "deadline_month": 12, "prestige": 8},
            {"name": "Sheffield DocFest", "country": "UK", "tier": 2, "genres": ["Documentary"], "duration_pref": "both", "min_score": 6.5, "deadline_month": 2, "prestige": 7},
            {"name": "DOC NYC", "country": "USA", "tier": 2, "genres": ["Documentary"], "duration_pref": "both", "min_score": 6.5, "deadline_month": 7, "prestige": 7},
            
            # Short Film Focused
            {"name": "Clermont-Ferrand Short Film Festival", "country": "France", "tier": 1, "genres": ["All"], "duration_pref": "short", "min_score": 7.0, "deadline_month": 9, "prestige": 9},
            {"name": "Palm Springs ShortFest", "country": "USA", "tier": 2, "genres": ["All"], "duration_pref": "short", "min_score": 6.5, "deadline_month": 2, "prestige": 8},
            {"name": "Tampere Film Festival", "country": "Finland", "tier": 2, "genres": ["All"], "duration_pref": "short", "min_score": 6.0, "deadline_month": 11, "prestige": 7},
            {"name": "Oberhausen Short Film Festival", "country": "Germany", "tier": 2, "genres": ["Experimental", "Art"], "duration_pref": "short", "min_score": 6.5, "deadline_month": 1, "prestige": 8},
            
            # Genre Specific
            {"name": "Fantastic Fest", "country": "USA", "tier": 2, "genres": ["Horror", "Sci-Fi", "Fantasy"], "duration_pref": "both", "min_score": 6.5, "deadline_month": 6, "prestige": 7},
            {"name": "Sitges Film Festival", "country": "Spain", "tier": 2, "genres": ["Horror", "Fantasy", "Thriller"], "duration_pref": "feature", "min_score": 6.5, "deadline_month": 6, "prestige": 7},
            {"name": "Annecy Animation Festival", "country": "France", "tier": 1, "genres": ["Animation"], "duration_pref": "both", "min_score": 7.0, "deadline_month": 2, "prestige": 9},
            {"name": "Ottawa International Animation Festival", "country": "Canada", "tier": 2, "genres": ["Animation"], "duration_pref": "both", "min_score": 6.0, "deadline_month": 5, "prestige": 7},
            
            # Regional/Emerging
            {"name": "Mumbai Film Festival", "country": "India", "tier": 2, "genres": ["All"], "duration_pref": "both", "min_score": 6.0, "deadline_month": 7, "prestige": 7},
            {"name": "Cairo International Film Festival", "country": "Egypt", "tier": 2, "genres": ["All"], "duration_pref": "feature", "min_score": 6.0, "deadline_month": 9, "prestige": 6},
            {"name": "Durban International Film Festival", "country": "South Africa", "tier": 3, "genres": ["African", "Documentary"], "duration_pref": "both", "min_score": 5.5, "deadline_month": 4, "prestige": 6},
            {"name": "BAFICI Buenos Aires", "country": "Argentina", "tier": 2, "genres": ["Indie", "Latin"], "duration_pref": "both", "min_score": 6.0, "deadline_month": 12, "prestige": 7},
            
            # Health/Social Impact Focused
            {"name": "Global Health Film Festival", "country": "UK", "tier": 3, "genres": ["Health", "Documentary", "Social Impact"], "duration_pref": "both", "min_score": 5.0, "deadline_month": 8, "prestige": 6},
            {"name": "Social Impact Media Awards", "country": "USA", "tier": 3, "genres": ["Social Impact", "Documentary"], "duration_pref": "both", "min_score": 5.5, "deadline_month": 10, "prestige": 6},
            {"name": "Peekaboon International Film Festival", "country": "UK", "tier": 3, "genres": ["Health", "Documentary", "Social Impact"], "duration_pref": "both", "min_score": 4.0, "deadline_month": 6, "prestige": 6},
        ]
    
    def match_festivals(self, film, quality_score):
        """Find matching festivals for a film"""
        matches = []
        duration = film.get('duration_minutes', 0)
        genre = film.get('genre', 'General')
        genres = film.get('genres', [genre])
        country = film.get('country', '')
        themes = film.get('themes', [])
        
        # Determine duration preference
        if duration <= 40:
            duration_type = "short"
        else:
            duration_type = "feature"
        
        for festival in self.festivals:
            match_score = 0
            reasons = []
            
            # Check minimum score requirement
            if quality_score < festival['min_score']:
                continue
            
            # Duration match
            if festival['duration_pref'] == "both" or festival['duration_pref'] == duration_type:
                match_score += 20
            else:
                continue  # Skip if duration doesn't match
            
            # Genre match
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
                continue  # Skip if genre doesn't match at all
            
            # Prestige/quality alignment
            if quality_score >= 8 and festival['prestige'] >= 8:
                match_score += 20
                reasons.append("Quality matches prestige level")
            elif quality_score >= 6 and festival['prestige'] <= 7:
                match_score += 15
                reasons.append("Realistic tier target")
            
            # Country/regional advantage
            if festival['country'] in country:
                match_score += 10
                reasons.append("Home country advantage")
            
            # Add to matches if reasonable score
            if match_score >= 30:
                matches.append({
                    "name": festival['name'],
                    "country": festival['country'],
                    "tier": festival['tier'],
                    "match_score": min(100, match_score + int(quality_score * 3)),
                    "prestige": festival['prestige'],
                    "deadline_month": festival['deadline_month'],
                    "reasons": reasons
                })
        
        # Sort by match score
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches[:10]  # Top 10 matches
    
    def analyze(self, film, quality_score):
        """Generate festival strategy recommendations"""
        
        matches = self.match_festivals(film, quality_score)
        
        # Categorize by tier
        tier_1 = [m for m in matches if m['tier'] == 1]
        tier_2 = [m for m in matches if m['tier'] == 2]
        tier_3 = [m for m in matches if m['tier'] == 3]
        
        # Generate strategy
        strategy = []
        if tier_1:
            strategy.append(f"Aim high: Submit to {tier_1[0]['name']} first")
        if tier_2:
            strategy.append(f"Strong backup: {tier_2[0]['name']}")
        if tier_3:
            strategy.append(f"Guaranteed exposure: {tier_3[0]['name']}")
        
        # Calculate confidence
        confidence = 0.6
        if len(matches) >= 5:
            confidence += 0.2
        if tier_1:
            confidence += 0.1
        confidence = min(0.95, confidence)
        
        return {
            "agent": self.name,
            "matches": matches,
            "top_recommendation": matches[0] if matches else None,
            "tier_1_options": tier_1,
            "tier_2_options": tier_2,
            "tier_3_options": tier_3,
            "strategy": strategy,
            "total_matches": len(matches),
            "confidence": round(confidence, 2),
            "timestamp": datetime.now().isoformat()
        }


class OpportunityRoutingAgent:
    """Routes films to optimal distribution pathways with comprehensive matching"""
    
    def __init__(self):
        self.name = "Opportunity Routing Agent"
        self.role = "Distribution Pathway Optimizer"
        self.festival_agent = FestivalMatchingAgent()
    
    def route(self, quality_result, market_result, film):
        """Determine optimal pathway with full matching"""
        
        quality_score = quality_result['score']
        market_score = market_result['score']
        themes = film.get('themes', [])
        genre = film.get('genre', '')
        duration = film.get('duration_minutes', 0)
        
        # Get festival matches
        festival_result = self.festival_agent.analyze(film, quality_score)
        
        # Calculate pathway scores
        pathway_scores = {}
        
        # Festival pathway
        festival_score = 0
        if quality_score >= 6.5:
            festival_score = quality_score * 0.7 + market_score * 0.3
        if festival_result['total_matches'] >= 5:
            festival_score += 1
        pathway_scores['FESTIVAL'] = festival_score
        
        # Streaming pathway
        streaming_score = market_score * 0.6 + quality_score * 0.4
        pathway_scores['STREAMING'] = streaming_score
        
        # Theatrical
        theatrical_score = 0
        if quality_score >= 8.0 and market_score >= 7.5 and duration >= 70:
            theatrical_score = (quality_score + market_score) / 2
        pathway_scores['THEATRICAL'] = theatrical_score
        
        # Brand partnership
        brand_score = 0
        impact_themes = ["Social Impact", "Climate Change", "Mental Health", "Social Justice", "Health"]
        if any(t in themes for t in impact_themes):
            brand_score = quality_score * 0.5 + market_score * 0.5 + 2
        pathway_scores['BRAND_PARTNERSHIP'] = brand_score
        
        # Educational
        edu_score = 0
        edu_themes = ["History", "Nature", "Cultural Heritage", "Health", "Education"]
        if genre == "Documentary" or any(t in themes for t in edu_themes):
            edu_score = quality_score * 0.6 + market_score * 0.4 + 1
        pathway_scores['EDUCATIONAL'] = edu_score
        
        # Determine best pathway
        best_pathway = max(pathway_scores, key=pathway_scores.get)
        
        # Calculate confidence
        confidence = 0.6
        score_diff = abs(quality_score - market_score)
        if score_diff < 1.5:
            confidence += 0.2
        if pathway_scores[best_pathway] > 7:
            confidence += 0.1
        confidence = min(0.95, confidence)
        
        # Generate next steps based on pathway
        next_steps = self._generate_next_steps(best_pathway, film, festival_result, market_result)
        
        # Generate reasoning
        reasoning = f"Routing '{film.get('title', 'Unknown')}': "
        reasoning += f"Quality ({quality_score}) + Market ({market_score}) = {best_pathway}. "
        if festival_result['top_recommendation']:
            reasoning += f"Top festival: {festival_result['top_recommendation']['name']}."
        
        return {
            "agent": self.name,
            "primary_pathway": best_pathway,
            "pathway_scores": pathway_scores,
            "confidence": round(confidence, 2),
            "reasoning": reasoning,
            "next_steps": next_steps,
            "festival_matches": festival_result['matches'][:5],
            "distributor_matches": market_result.get('distributor_matches', []),
            "festival_strategy": festival_result['strategy'],
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_next_steps(self, pathway, film, festival_result, market_result):
        """Generate actionable next steps"""
        steps = []
        
        if pathway == "FESTIVAL":
            if festival_result['tier_1_options']:
                steps.append(f"Submit to {festival_result['tier_1_options'][0]['name']}")
            if festival_result['tier_2_options']:
                steps.append(f"Backup: Apply to {festival_result['tier_2_options'][0]['name']}")
            steps.append("Prepare press kit and stills")
            steps.append("Create festival trailer (2-3 min)")
        
        elif pathway == "STREAMING":
            if market_result.get('distributor_matches'):
                steps.append(f"Contact {market_result['distributor_matches'][0]['name']}")
            steps.append("Prepare platform-specific deliverables")
            steps.append("Create social media marketing pack")
        
        elif pathway == "THEATRICAL":
            steps.append("Engage theatrical sales agent")
            steps.append("Prepare DCP deliverables")
            steps.append("Plan premiere strategy")
            steps.append("Create theatrical poster and trailer")
        
        elif pathway == "BRAND_PARTNERSHIP":
            steps.append("Identify aligned CSR brands")
            steps.append("Prepare impact metrics document")
            steps.append("Create partnership pitch deck")
            steps.append("Contact brand agencies")
        
        elif pathway == "EDUCATIONAL":
            steps.append("Contact educational distributors")
            steps.append("Prepare study guide")
            steps.append("Research library licensing options")
            steps.append("Apply for educational grants")
        
        return steps


# Test the enhanced agents
if __name__ == "__main__":
    print("="*60)
    print("PACCS Enhanced Agents Test")
    print("="*60)
    
    # Test with a real-style film
    test_film = {
        "id": "TEST_001",
        "title": "Breaking Silence",
        "director": "Test Director",
        "genre": "Documentary",
        "genres": ["Documentary", "Drama"],
        "duration_minutes": 52,
        "country": "India",
        "language": "Hindi",
        "synopsis": "A powerful documentary exploring mental health stigma in rural communities.",
        "themes": ["Mental Health", "Social Justice", "Family"],
        "first_time_filmmaker": True,
        "screenings_awards": "Official Selection - Mumbai Film Festival",
        "technical_quality": 7.5,
        "narrative_score": 8.0,
        "originality_score": 7.5,
    }
    
    print(f"\nTesting with: {test_film['title']}")
    print("-" * 40)
    
    # Test agents
    quality_agent = QualityAssessmentAgent()
    market_agent = MarketIntelligenceAgent()
    routing_agent = OpportunityRoutingAgent()
    
    quality_result = quality_agent.analyze(test_film)
    print(f"\n📊 QUALITY ASSESSMENT")
    print(f"   Score: {quality_result['score']}/10")
    print(f"   Confidence: {quality_result['confidence']}")
    print(f"   Strengths: {quality_result['strengths']}")
    print(f"   Predictive factors: {quality_result['predictive_adjustments'][:3]}")
    
    market_result = market_agent.analyze(test_film)
    print(f"\n📈 MARKET ANALYSIS")
    print(f"   Score: {market_result['score']}/10")
    print(f"   Genre trend: {market_result['genre_trend']}")
    print(f"   Top distributors:")
    for d in market_result['distributor_matches'][:3]:
        print(f"      • {d['name']} ({d['match_score']}% match)")
    
    routing_result = routing_agent.route(quality_result, market_result, test_film)
    print(f"\n🎯 ROUTING DECISION")
    print(f"   Pathway: {routing_result['primary_pathway']}")
    print(f"   Confidence: {routing_result['confidence']}")
    print(f"\n   Festival matches:")
    for f in routing_result['festival_matches'][:3]:
        print(f"      • {f['name']} ({f['match_score']}% match)")
    print(f"\n   Next steps:")
    for step in routing_result['next_steps'][:3]:
        print(f"      → {step}")
    
    print("\n" + "="*60)
    print("Enhanced agents test complete!")
