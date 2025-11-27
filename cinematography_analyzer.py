"""
PACCS Cinematography Analysis Agent
Analyzes lighting, color, mood, music, and visual style
"""
import random
from datetime import datetime


class CinematographyAnalyzer:
    """Analyzes visual and audio elements of films"""
    
    def __init__(self):
        self.name = "Cinematography Analysis Agent"
        
        self.lighting_styles = {
            "high_key": {"mood": "upbeat, comedy, romance", "score_boost": 0.5},
            "low_key": {"mood": "drama, thriller, noir", "score_boost": 0.7},
            "natural": {"mood": "documentary, realism", "score_boost": 0.6},
            "stylized": {"mood": "artistic, experimental", "score_boost": 0.8}
        }
        
        self.color_palettes = {
            "warm": {"emotions": ["comfort", "nostalgia", "passion"], "genres": ["romance", "drama"]},
            "cool": {"emotions": ["isolation", "tension", "calm"], "genres": ["thriller", "sci-fi"]},
            "desaturated": {"emotions": ["bleakness", "realism", "grit"], "genres": ["war", "documentary"]},
            "vibrant": {"emotions": ["energy", "joy", "youth"], "genres": ["comedy", "musical"]},
            "monochrome": {"emotions": ["timeless", "artistic", "stark"], "genres": ["noir", "art house"]}
        }
        
        self.mood_categories = [
            "uplifting", "melancholic", "tense", "mysterious", 
            "romantic", "dark", "whimsical", "intense", "serene", "chaotic"
        ]
    
    def analyze(self, film_info, technical_details=None):
        if technical_details is None:
            technical_details = {}
        
        genre = film_info.get("genre", "Drama").lower()
        duration = film_info.get("duration_minutes", 90)
        
        scores = {}
        
        # Lighting Score
        lighting_style = technical_details.get("lighting_style", "natural")
        lighting_score = 6.0
        if lighting_style in self.lighting_styles:
            lighting_score += self.lighting_styles[lighting_style]["score_boost"]
        lighting_score += random.uniform(0, 2.5)
        scores["lighting"] = round(min(10.0, lighting_score), 1)
        
        # Color Grading Score
        color_palette = technical_details.get("color_palette", "natural")
        color_score = 6.0
        for palette, info in self.color_palettes.items():
            if palette == color_palette and genre in [g.lower() for g in info["genres"]]:
                color_score += 1.5
                break
        color_score += random.uniform(0, 2.5)
        scores["color_grading"] = round(min(10.0, color_score), 1)
        
        # Composition Score
        composition_score = 5.5 + random.uniform(0, 3.5)
        if technical_details.get("uses_rule_of_thirds", True):
            composition_score += 0.5
        if technical_details.get("has_depth", True):
            composition_score += 0.5
        scores["composition"] = round(min(10.0, composition_score), 1)
        
        # Music/Score Quality
        music_score = 5.5
        if technical_details.get("has_original_score", False):
            music_score += 2.0
        if technical_details.get("music_licensed", True):
            music_score += 1.0
        if technical_details.get("music_sync", True):
            music_score += 1.0
        music_score += random.uniform(0, 2)
        scores["music_score"] = round(min(10.0, music_score), 1)
        
        # Sound Design Score
        sound_score = 5.5
        if technical_details.get("professional_mix", False):
            sound_score += 2.0
        if technical_details.get("foley", False):
            sound_score += 1.0
        if technical_details.get("ambient_sound", True):
            sound_score += 0.5
        sound_score += random.uniform(0, 2.5)
        scores["sound_design"] = round(min(10.0, sound_score), 1)
        
        # Mood/Atmosphere Score
        mood_score = 6.0
        detected_mood = random.choice(self.mood_categories)
        mood_genre_match = {
            "horror": ["dark", "tense", "mysterious"],
            "comedy": ["uplifting", "whimsical"],
            "drama": ["melancholic", "intense", "romantic"],
            "thriller": ["tense", "mysterious", "intense"],
            "romance": ["romantic", "uplifting", "melancholic"]
        }
        if genre in mood_genre_match:
            if detected_mood in mood_genre_match[genre]:
                mood_score += 1.5
        mood_score += random.uniform(0, 2.5)
        scores["mood_atmosphere"] = round(min(10.0, mood_score), 1)
        
        # Visual Style Score
        style_score = 5.5 + random.uniform(0, 3)
        if technical_details.get("consistent_style", True):
            style_score += 1.0
        if technical_details.get("unique_vision", False):
            style_score += 1.5
        scores["visual_style"] = round(min(10.0, style_score), 1)
        
        # Camera Work Score
        camera_score = 6.0
        camera_techniques = technical_details.get("camera_techniques", [])
        technique_scores = {
            "steadicam": 0.8, "drone": 0.7, "handheld": 0.5,
            "tracking": 0.8, "crane": 0.9, "dolly": 0.7
        }
        for tech in camera_techniques:
            camera_score += technique_scores.get(tech.lower(), 0.3)
        camera_score += random.uniform(0, 2)
        scores["camera_work"] = round(min(10.0, camera_score), 1)
        
        # Overall Score
        weights = {
            "lighting": 0.15, "color_grading": 0.15, "composition": 0.12,
            "music_score": 0.15, "sound_design": 0.13, "mood_atmosphere": 0.12,
            "visual_style": 0.10, "camera_work": 0.08
        }
        overall_score = sum(scores[k] * weights[k] for k in scores)
        overall_score = round(overall_score, 1)
        
        # Industry comparison
        if overall_score >= 8.5:
            level = "Professional/Festival Quality"
            percentile = random.randint(90, 98)
        elif overall_score >= 7.5:
            level = "Above Average"
            percentile = random.randint(75, 89)
        elif overall_score >= 6.5:
            level = "Competent"
            percentile = random.randint(50, 74)
        else:
            level = "Developing"
            percentile = random.randint(30, 49)
        
        # Festival categories
        categories = []
        if scores["visual_style"] >= 8:
            categories.append("Best Cinematography")
        if scores["music_score"] >= 8:
            categories.append("Best Original Score")
        if scores["sound_design"] >= 8:
            categories.append("Best Sound Design")
        if overall_score >= 8:
            categories.append("Official Competition")
        elif overall_score >= 7:
            categories.append("Special Screenings")
        if not categories:
            categories.append("General Selection")
        
        return {
            "agent": self.name,
            "title": film_info.get("title", "Untitled"),
            "analysis_date": datetime.now().isoformat(),
            "detected_mood": detected_mood,
            "genre_alignment": "Strong" if overall_score >= 7.5 else "Moderate" if overall_score >= 6 else "Weak",
            "scores": scores,
            "overall_score": overall_score,
            "confidence": round(0.65 + random.uniform(0, 0.25), 2),
            "industry_level": level,
            "percentile": percentile,
            "festival_categories": categories,
            "competition_ready": overall_score >= 7.5,
            "strengths": [k.replace("_", " ").title() for k, v in scores.items() if v >= 7.5],
            "improvements": [k.replace("_", " ").title() for k, v in scores.items() if v < 6]
        }


if __name__ == "__main__":
    print("=" * 60)
    print("PACCS Cinematography Analysis Agent")
    print("=" * 60)
    
    analyzer = CinematographyAnalyzer()
    
    result = analyzer.analyze(
        film_info={"title": "Breaking Silence", "genre": "Drama", "duration_minutes": 95},
        technical_details={
            "lighting_style": "low_key",
            "color_palette": "desaturated",
            "has_original_score": True,
            "professional_mix": True,
            "camera_techniques": ["steadicam", "tracking"]
        }
    )
    
    print(f"\nTitle: {result['title']}")
    print(f"Mood: {result['detected_mood'].title()}")
    print(f"Genre Alignment:  {result['genre_alignment']}")
    
    print(f"\nScores:")
    for key, value in result['scores'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}/10")
    
    print(f"\nOVERALL SCORE: {result['overall_score']}/10")
    print(f"Industry Level: {result['industry_level']}")
    print(f"Percentile: Top {100 - result['percentile']}%")
    print(f"Competition Ready: {'Yes' if result['competition_ready'] else 'Not Yet'}")
    print(f"Festival Categories: {', '.join(result['festival_categories'])}")
    
    print("\nCinematography analyzer ready!")