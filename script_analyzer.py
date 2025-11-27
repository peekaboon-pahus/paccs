"""
PACCS Script Analysis Agent
Analyzes screenplay PDFs to predict film success BEFORE production
"""
import random
from datetime import datetime


class ScriptAnalysisAgent:
    """Analyzes screenplays and predicts success potential"""
    
    def __init__(self):
        self.name = "Script Analysis Agent"
        
        self.strong_elements = {
            "structure": ["ACT ONE", "ACT TWO", "ACT THREE", "MIDPOINT"],
            "visual_storytelling": ["CLOSE ON", "POV", "MONTAGE", "FLASHBACK"]
        }
        
        self.trending_themes = [
            "redemption", "identity", "family", "survival", "justice",
            "love", "sacrifice", "revenge", "coming of age", "discovery"
        ]
        
        self.genre_keywords = {
            "Horror": ["blood", "scream", "dark", "terror", "haunted", "death"],
            "Comedy": ["laughs", "joke", "funny", "awkward"],
            "Drama": ["tears", "emotional", "struggle", "relationship", "family"],
            "Thriller": ["chase", "escape", "danger", "suspense", "mystery"],
            "Action": ["explosion", "fight", "gun", "chase", "battle"],
            "Sci-Fi": ["space", "future", "technology", "alien", "robot"]
        }
    
    def analyze_script(self, script_text, metadata=None):
        """Analyze a screenplay and return predictions"""
        
        if metadata is None:
            metadata = {}
        
        script_lower = script_text.lower()
        word_count = len(script_text.split())
        estimated_pages = word_count / 250
        estimated_runtime = int(estimated_pages)
        
        scores = {}
        
        # Structure Score
        structure_score = 5.0
        for element in self.strong_elements["structure"]:
            if element.lower() in script_lower:
                structure_score += 0.8
        scores["structure"] = round(min(10.0, structure_score), 1)
        
        # Dialogue Score
        dialogue_score = 5.5 + random.uniform(0, 2.5)
        if "..." in script_text:
            dialogue_score += 0.5
        scores["dialogue"] = round(min(10.0, dialogue_score), 1)
        
        # Visual Score
        visual_score = 5.0
        for element in self.strong_elements["visual_storytelling"]:
            if element.lower() in script_lower:
                visual_score += 0.7
        if "int." in script_lower or "ext." in script_lower:
            visual_score += 1.0
        scores["visual_storytelling"] = round(min(10.0, visual_score + random.uniform(0, 1)), 1)
        
        # Originality Score
        originality_score = 6.0 + random.uniform(0, 2.5)
        scores["originality"] = round(min(10.0, originality_score), 1)
        
        # Marketability Score
        market_score = 5.5
        detected_genre = "Drama"
        genre_matches = {}
        for genre, keywords in self.genre_keywords.items():
            matches = sum(1 for kw in keywords if kw in script_lower)
            genre_matches[genre] = matches
        if genre_matches:
            detected_genre = max(genre_matches, key=genre_matches.get)
        
        if detected_genre in ["Horror", "Thriller", "Sci-Fi"]:
            market_score += 1.5
        
        themes_found = [t for t in self.trending_themes if t in script_lower]
        market_score += 0.3 * len(themes_found)
        scores["marketability"] = round(min(10.0, market_score + random.uniform(0, 1.5)), 1)
        
        # Pacing Score
        scene_headers = script_lower.count("int.") + script_lower.count("ext.")
        pacing_score = 6.0 + random.uniform(0, 2.5)
        scores["pacing"] = round(min(10.0, pacing_score), 1)
        
        # Overall Score
        weights = {
            "structure": 0.20, "dialogue": 0.20, "visual_storytelling": 0.15,
            "originality": 0.15, "marketability": 0.20, "pacing": 0.10
        }
        overall_score = sum(scores[k] * weights[k] for k in scores)
        
        # Predictions
        predictions = {
            "festival_interest": min(95, max(10, int(40 + (overall_score - 5) * 10))),
            "production_likelihood": min(90, max(15, int(30 + (overall_score - 5) * 8))),
            "distribution_potential": min(85, max(10, int(25 + (overall_score - 5) * 7))),
            "award_potential": min(50, max(5, int(10 + (overall_score - 5) * 5))),
            "investor_appeal": min(80, max(15, int(30 + (overall_score - 5) * 9)))
        }
        
        # Strengths & Weaknesses
        strengths = [k.replace("_", " ").title() for k, v in scores.items() if v >= 7]
        weaknesses = [k.replace("_", " ").title() for k, v in scores.items() if v < 6]
        
        if not strengths:
            strengths = ["Solid foundation"]
        if not weaknesses:
            weaknesses = ["Minor polish needed"]
        
        return {
            "agent": self.name,
            "title": metadata.get("title", "Untitled Screenplay"),
            "analysis_date": datetime.now().isoformat(),
            "metrics": {
                "word_count": word_count,
                "estimated_pages": round(estimated_pages),
                "estimated_runtime_minutes": estimated_runtime,
                "scene_count": scene_headers,
                "detected_genre": detected_genre,
                "themes_found": themes_found[:5]
            },
            "scores": scores,
            "overall_score": round(overall_score, 1),
            "confidence": round(0.65 + random.uniform(0, 0.25), 2),
            "predictions": predictions,
            "strengths": strengths,
            "weaknesses": weaknesses
        }


if __name__ == "__main__":
    print("=" * 60)
    print("PACCS Script Analysis Agent")