"""
PACCS Film Database - REAL DATA VERSION
Loads actual films from FilmFreeway export
"""
import csv
import json
import random
from datetime import datetime

class FilmDatabase:
    """Manages the film database with REAL FilmFreeway data"""
    
    def __init__(self, csv_file="FilmFreeway-Submissions-2025-11-25-09-41-21.csv", db_file="films_database.json"):
        self.csv_file = csv_file
        self.db_file = db_file
        self.films = []
        self.load_or_create()
    
    def load_or_create(self):
        """Load from JSON cache or import from CSV"""
        try:
            with open(self.db_file, 'r') as f:
                self.films = json.load(f)
            print(f"Loaded {len(self.films)} films from database")
        except FileNotFoundError:
            print("Importing films from FilmFreeway CSV...")
            self.import_from_csv()
            self.save()
            print(f"Database initialized with {len(self.films)} REAL films!")
    
    def parse_duration(self, duration_str):
        """Convert duration string to minutes"""
        if not duration_str:
            return 0
        try:
            # Format: "00:04:59" or "01:29:50"
            parts = duration_str.split(':')
            if len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                return hours * 60 + minutes + (1 if seconds > 30 else 0)
            elif len(parts) == 2:
                return int(parts[0])
        except:
            return 0
        return 0
    
    def extract_genres(self, genre_str):
        """Extract genres from string"""
        if not genre_str:
            return ["General"]
        # Clean up and split
        genres = [g.strip() for g in genre_str.split(',') if g.strip()]
        return genres if genres else ["General"]
    
    def determine_themes(self, synopsis, categories):
        """Determine themes from synopsis and categories"""
        themes = []
        text = (synopsis + " " + categories).lower()
        
        theme_keywords = {
            "Mental Health": ["mental", "depression", "anxiety", "suicide", "therapy", "psychological"],
            "Social Justice": ["justice", "equality", "rights", "discrimination", "activism"],
            "Climate Change": ["climate", "environment", "nature", "pollution", "sustainability"],
            "Health": ["health", "medical", "disease", "hospital", "doctor", "patient", "public health"],
            "Family": ["family", "mother", "father", "parent", "child", "son", "daughter"],
            "Identity": ["identity", "self", "who am i", "culture", "heritage"],
            "Love": ["love", "romance", "relationship", "heart", "passion"],
            "War": ["war", "soldier", "military", "conflict", "battle"],
            "Technology": ["technology", "ai", "computer", "digital", "internet"],
            "Education": ["education", "school", "student", "learn", "teacher"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(kw in text for kw in keywords):
                themes.append(theme)
        
        return themes if themes else ["General"]
    
    def calculate_quality_score(self, film_data):
        """Calculate quality score based on available data"""
        score = 5.0  # Base score
        
        # Has synopsis (shows effort)
        if film_data.get('synopsis') and len(film_data['synopsis']) > 100:
            score += 1.0
        
        # Has awards/selections
        awards_text = film_data.get('screenings_awards', '').lower()
        if 'winner' in awards_text or 'award' in awards_text:
            score += 2.0
        elif 'finalist' in awards_text:
            score += 1.5
        elif 'official selection' in awards_text or 'semi-finalist' in awards_text:
            score += 1.0
        
        # Judging status
        status = film_data.get('judging_status', '').lower()
        if 'award winner' in status:
            score += 2.0
        elif 'selected' in status and 'not' not in status:
            score += 1.5
        elif 'finalist' in status:
            score += 1.0
        
        # Duration (feature length gets slight boost)
        duration = film_data.get('duration_minutes', 0)
        if duration >= 60:
            score += 0.5
        
        # Add some variance
        score += random.uniform(-0.5, 0.5)
        
        return max(1.0, min(10.0, round(score, 1)))
    
    def calculate_market_score(self, film_data):
        """Calculate market score based on available data"""
        score = 5.0  # Base score
        
        # Genre appeal
        genres = film_data.get('genres', [])
        high_market_genres = ['documentary', 'drama', 'thriller', 'comedy', 'horror']
        if any(g.lower() in high_market_genres for g in genres):
            score += 1.0
        
        # International appeal (different country)
        country = film_data.get('country', '').lower()
        if country and country not in ['', 'uk', 'united kingdom']:
            score += 0.5  # International content
        
        # Festival track record
        awards_text = film_data.get('screenings_awards', '')
        festival_count = awards_text.count('Official Selection') + awards_text.count('Finalist')
        score += min(festival_count * 0.3, 2.0)
        
        # Add some variance
        score += random.uniform(-0.5, 0.5)
        
        return max(1.0, min(10.0, round(score, 1)))
    
    def import_from_csv(self):
        """Import films from FilmFreeway CSV export"""
        self.films = []
        seen_titles = set()
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                
                for i, row in enumerate(reader):
                    # Skip empty rows or duplicates
                    title = row.get('Project Title', '').strip()
                    if not title or title in seen_titles:
                        continue
                    
                    seen_titles.add(title)
                    
                    # Parse the data
                    duration_minutes = self.parse_duration(row.get('Duration', ''))
                    genres = self.extract_genres(row.get('Genres', ''))
                    categories = row.get('Submission Categories', '')
                    synopsis = row.get('Synopsis', '')
                    themes = self.determine_themes(synopsis, categories)
                    
                    film = {
                        "id": f"FILM_{len(self.films)+1:04d}",
                        "tracking_number": row.get('Tracking Number', ''),
                        "title": title,
                        "director": row.get('Directors', f"{row.get('First Name', '')} {row.get('Last Name', '')}").strip(),
                        "genre": genres[0] if genres else "General",
                        "genres": genres,
                        "duration_minutes": duration_minutes,
                        "country": row.get('Country of Origin', row.get('Country', '')),
                        "language": row.get('Language', 'Unknown'),
                        "synopsis": synopsis[:500] if synopsis else "",
                        "themes": themes,
                        "categories": categories,
                        "project_type": row.get('Project Type', 'Short'),
                        "production_budget": row.get('Production Budget', ''),
                        "completion_date": row.get('Completion Date', ''),
                        "first_time_filmmaker": row.get('First-time Filmmaker', '').lower() == 'yes',
                        "submission_date": row.get('Submission Date', ''),
                        "submission_status": row.get('Submission Status', ''),
                        "judging_status": row.get('Judging Status', 'Undecided'),
                        "screenings_awards": row.get('Screenings / Awards', ''),
                        "director_email": row.get('Email', ''),
                        "submission_link": row.get('Submission Link', ''),
                        # Calculated scores
                        "technical_quality": self.calculate_quality_score(row),
                        "narrative_score": round(random.uniform(5.0, 9.0), 1),
                        "originality_score": round(random.uniform(4.0, 9.0), 1),
                        # Status for PACCS processing
                        "status": "pending",
                        "paccs_processed": False
                    }
                    
                    # Recalculate with full film data
                    film["technical_quality"] = self.calculate_quality_score(film)
                    film["market_score"] = self.calculate_market_score(film)
                    
                    self.films.append(film)
                    
                    # Progress indicator
                    if len(self.films) % 500 == 0:
                        print(f"  Imported {len(self.films)} films...")
        
        except FileNotFoundError:
            print(f"CSV file not found: {self.csv_file}")
            print("Falling back to sample data...")
            self.generate_sample_films()
    
    def generate_sample_films(self):
        """Fallback: Generate sample films if CSV not found"""
        genres = ["Drama", "Documentary", "Comedy", "Thriller", "Horror", 
                  "Sci-Fi", "Romance", "Animation", "Experimental", "Social Impact"]
        countries = ["UK", "USA", "India", "Japan", "France", "Germany", 
                    "South Korea", "Brazil", "Nigeria", "Thailand"]
        
        self.films = []
        for i in range(50):
            self.films.append({
                "id": f"FILM_{i+1:04d}",
                "title": f"Sample Film {i+1}",
                "genre": random.choice(genres),
                "duration_minutes": random.randint(5, 120),
                "country": random.choice(countries),
                "technical_quality": round(random.uniform(5.0, 10.0), 1),
                "narrative_score": round(random.uniform(4.0, 10.0), 1),
                "originality_score": round(random.uniform(3.0, 10.0), 1),
                "status": "pending"
            })
    
    def save(self):
        """Save database to file"""
        with open(self.db_file, 'w') as f:
            json.dump(self.films, f, indent=2)
    
    def get_film(self, film_id):
        """Get a specific film by ID"""
        for film in self.films:
            if film['id'] == film_id:
                return film
        return None
    
    def get_pending_films(self):
        """Get all films awaiting PACCS review"""
        return [f for f in self.films if f['status'] == 'pending']
    
    def get_reviewed_films(self):
        """Get all PACCS reviewed films"""
        return [f for f in self.films if f['status'] == 'reviewed']
    
    def update_film_status(self, film_id, status):
        """Update a film's status"""
        for film in self.films:
            if film['id'] == film_id:
                film['status'] = status
                self.save()
                return True
        return False
    
    def get_statistics(self):
        """Get database statistics"""
        total = len(self.films)
        pending = len(self.get_pending_films())
        reviewed = len(self.get_reviewed_films())
        
        genres = {}
        countries = {}
        for film in self.films:
            g = film.get('genre', 'Unknown')
            genres[g] = genres.get(g, 0) + 1
            c = film.get('country', 'Unknown')
            countries[c] = countries.get(c, 0) + 1
        
        return {
            "total_films": total,
            "pending": pending,
            "reviewed": reviewed,
            "genres": genres,
            "countries": countries,
            "top_countries": sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]
        }


# Test the database
if __name__ == "__main__":
    print("="*60)
    print("PACCS Film Database - REAL DATA")
    print("="*60)
    
    db = FilmDatabase()
    
    stats = db.get_statistics()
    print(f"\nTotal films: {stats['total_films']}")
    print(f"Pending: {stats['pending']}")
    print(f"Reviewed: {stats['reviewed']}")
    
    print(f"\nTop 10 Countries:")
    for country, count in stats['top_countries']:
        print(f"  {country}: {count} films")
    
    print(f"\nGenres:")
    for genre, count in sorted(stats['genres'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {genre}: {count} films")
    
    print("\nSample film:")
    if db.films:
        sample = db.films[0]
        print(f"  Title: {sample.get('title')}")
        print(f"  Director: {sample.get('director')}")
        print(f"  Country: {sample.get('country')}")
        print(f"  Duration: {sample.get('duration_minutes')} min")
        print(f"  Genre: {sample.get('genre')}")
        print(f"  Themes: {sample.get('themes')}")
        print(f"  Quality Score: {sample.get('technical_quality')}")
    
    print("\n" + "="*60)
    print("Database ready for PACCS processing!")
    print("="*60)