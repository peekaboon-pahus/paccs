"""
PACCS Professional PDF Report Generator
Creates beautiful, downloadable PDF reports for filmmakers
"""
from datetime import datetime
import json
import os

class PDFReportGenerator:
    """Generates professional PDF-style reports (HTML that can be printed to PDF)"""
    
    def __init__(self):
        self.template = self._get_template()
    
    def _get_template(self):
        """HTML template for PDF report"""
        return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PACCS Film Intelligence Report - {title}</title>
    <style>
        @page {{ margin: 0.5in; }}
        @media print {{
            body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .no-print {{ display: none; }}
            .page-break {{ page-break-before: always; }}
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            color: #1a365d;
            line-height: 1.6;
            background: white;
        }}
        
        .report {{
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
        }}
        
        /* Header */
        .header {{
            text-align: center;
            border-bottom: 4px solid #2c5282;
            padding-bottom: 30px;
            margin-bottom: 30px;
        }}
        .logo {{
            font-size: 2.5em;
            font-weight: bold;
            color: #1a365d;
            margin-bottom: 5px;
        }}
        .logo-sub {{
            color: #666;
            font-size: 1em;
        }}
        .report-title {{
            font-size: 1.3em;
            color: #2c5282;
            margin-top: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        .report-date {{
            color: #888;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        /* Film Info */
        .film-info {{
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 25px;
        }}
        .film-title {{
            font-size: 1.8em;
            color: #1a365d;
            margin-bottom: 15px;
        }}
        .film-meta {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }}
        .meta-item {{
            padding: 8px 0;
            border-bottom: 1px solid #cbd5e0;
        }}
        .meta-label {{
            font-weight: bold;
            color: #2c5282;
        }}
        
        /* Score Box */
        .score-box {{
            background: linear-gradient(135deg, #276749 0%, #2f855a 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 25px;
        }}
        .main-score {{
            font-size: 4em;
            font-weight: bold;
        }}
        .score-label {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .pathway-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 10px 25px;
            border-radius: 25px;
            margin-top: 15px;
            font-size: 1.3em;
            font-weight: bold;
        }}
        
        /* Scores Grid */
        .scores-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }}
        .score-card {{
            background: #f8fafc;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 2px solid #e2e8f0;
        }}
        .score-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2c5282;
        }}
        .score-name {{
            color: #666;
            font-size: 0.9em;
        }}
        
        /* Section */
        .section {{
            margin-bottom: 25px;
            padding: 20px;
            background: #f8fafc;
            border-radius: 10px;
            border-left: 4px solid #2c5282;
        }}
        .section h2 {{
            color: #1a365d;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        /* Predictions */
        .predictions {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}
        .prediction {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e2e8f0;
        }}
        .prediction-value {{
            font-size: 2em;
            font-weight: bold;
            color: #276749;
        }}
        .prediction-label {{
            color: #666;
            font-size: 0.85em;
        }}
        
        /* Revenue */
        .revenue-box {{
            background: linear-gradient(135deg, #553c9a 0%, #6b46c1 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 25px;
        }}
        .revenue-total {{
            font-size: 2em;
            font-weight: bold;
        }}
        .revenue-breakdown {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
            text-align: left;
        }}
        .revenue-item {{
            background: rgba(255,255,255,0.1);
            padding: 10px;
            border-radius: 5px;
        }}
        
        /* Matches */
        .match-list {{
            list-style: none;
        }}
        .match-item {{
            display: flex;
            justify-content: space-between;
            padding: 12px;
            background: white;
            margin-bottom: 8px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}
        .match-name {{
            font-weight: bold;
            color: #1a365d;
        }}
        .match-score {{
            background: #48bb78;
            color: white;
            padding: 3px 12px;
            border-radius: 15px;
            font-size: 0.9em;
        }}
        
        /* Comparison */
        .comparison-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px 15px;
            background: white;
            margin-bottom: 8px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}
        .percentile {{
            background: #2c5282;
            color: white;
            padding: 3px 12px;
            border-radius: 15px;
            font-weight: bold;
        }}
        
        /* Next Steps */
        .steps-list {{
            list-style: none;
            counter-reset: steps;
        }}
        .step {{
            counter-increment: steps;
            padding: 12px 15px 12px 50px;
            background: white;
            margin-bottom: 8px;
            border-radius: 8px;
            position: relative;
            border: 1px solid #e2e8f0;
        }}
        .step:before {{
            content: counter(steps);
            position: absolute;
            left: 15px;
            background: #2c5282;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            text-align: center;
            line-height: 24px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        /* Footer */
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e2e8f0;
            text-align: center;
            color: #888;
            font-size: 0.85em;
        }}
        .footer-logo {{
            font-weight: bold;
            color: #1a365d;
            font-size: 1.1em;
        }}
        
        /* Print Button */
        .print-btn {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #2c5282;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .print-btn:hover {{
            background: #1a365d;
        }}
    </style>
</head>
<body>
    <button class="print-btn no-print" onclick="window.print()">📄 Download PDF</button>
    
    <div class="report">
        <div class="header">
            <div class="logo">🎬 PACCS</div>
            <div class="logo-sub">Peekaboon Agentic Creative Curation System</div>
            <div class="report-title">Film Intelligence Report</div>
            <div class="report-date">Generated: {date}</div>
        </div>
        
        <div class="film-info">
            <div class="film-title">{title}</div>
            <div class="film-meta">
                <div class="meta-item"><span class="meta-label">Director:</span> {director}</div>
                <div class="meta-item"><span class="meta-label">Country:</span> {country}</div>
                <div class="meta-item"><span class="meta-label">Duration:</span> {duration} minutes</div>
                <div class="meta-item"><span class="meta-label">Genre:</span> {genre}</div>
                <div class="meta-item"><span class="meta-label">Themes:</span> {themes}</div>
                <div class="meta-item"><span class="meta-label">Report ID:</span> {report_id}</div>
            </div>
        </div>
        
        <div class="score-box">
            <div class="main-score">{final_score}/10</div>
            <div class="score-label">PACCS Score</div>
            <div class="pathway-badge">{pathway}</div>
        </div>
        
        <div class="scores-grid">
            <div class="score-card">
                <div class="score-value">{quality_score}/10</div>
                <div class="score-name">Quality Score</div>
            </div>
            <div class="score-card">
                <div class="score-value">{market_score}/10</div>
                <div class="score-name">Market Score</div>
            </div>
            <div class="score-card">
                <div class="score-value">{confidence}%</div>
                <div class="score-name">Confidence Level</div>
            </div>
            <div class="score-card">
                <div class="score-value">Top {overall_percentile}%</div>
                <div class="score-name">Overall Ranking</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Success Predictions</h2>
            <div class="predictions">
                <div class="prediction">
                    <div class="prediction-value">{festival_prob}%</div>
                    <div class="prediction-label">Festival Selection</div>
                </div>
                <div class="prediction">
                    <div class="prediction-value">{distribution_prob}%</div>
                    <div class="prediction-label">Distribution Deal</div>
                </div>
                <div class="prediction">
                    <div class="prediction-value">{award_prob}%</div>
                    <div class="prediction-label">Award Nomination</div>
                </div>
                <div class="prediction">
                    <div class="prediction-value">{viral_prob}%</div>
                    <div class="prediction-label">Viral Potential</div>
                </div>
            </div>
        </div>
        
        <div class="revenue-box">
            <div>💰 Estimated Market Value</div>
            <div class="revenue-total">£{revenue_low:,} - £{revenue_high:,}</div>
            <div class="revenue-breakdown">
                <div class="revenue-item">🎬 Festival Circuit: £{rev_festival:,}</div>
                <div class="revenue-item">📺 Streaming Rights: £{rev_streaming:,}</div>
                <div class="revenue-item">📚 Educational: £{rev_educational:,}</div>
                <div class="revenue-item">📦 Other: £{rev_other:,}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Competitive Ranking</h2>
            <div class="comparison-item">
                <span>Overall (All Films)</span>
                <span class="percentile">Top {overall_percentile}%</span>
            </div>
            <div class="comparison-item">
                <span>In {genre} Genre</span>
                <span class="percentile">Top {genre_percentile}%</span>
            </div>
            <div class="comparison-item">
                <span>By Duration Category</span>
                <span class="percentile">Top {duration_percentile}%</span>
            </div>
        </div>
        
        <div class="section">
            <h2>🏆 Top Festival Matches</h2>
            <ul class="match-list">
                {festival_matches_html}
            </ul>
        </div>
        
        <div class="section">
            <h2>📺 Top Distributor Matches</h2>
            <ul class="match-list">
                {distributor_matches_html}
            </ul>
        </div>
        
        <div class="section">
            <h2>📋 Recommended Next Steps</h2>
            <ul class="steps-list">
                {next_steps_html}
            </ul>
        </div>
        
        <div class="section">
            <h2>💪 Strengths</h2>
            <ul class="match-list">
                {strengths_html}
            </ul>
        </div>
        
        <div class="section">
            <h2>🎯 Areas for Development</h2>
            <ul class="match-list">
                {improvements_html}
            </ul>
        </div>
        
        <div class="footer">
            <div class="footer-logo">🎬 PACCS by PAHUS Studios Limited</div>
            <p>Peekaboon Agentic Creative Curation System</p>
            <p>www.peekaboon.com | © {year} All Rights Reserved</p>
            <p style="margin-top: 15px; font-style: italic;">
                This report is generated by AI-powered multi-agent analysis. 
                Scores and recommendations are based on pattern recognition from historical data 
                and should be used as guidance only.
            </p>
        </div>
    </div>
</body>
</html>
'''
    
    def generate_report(self, decision):
        """Generate HTML report from decision data"""
        
        # Extract data with defaults
        film_data = decision.get('film_data', {})
        quality = decision.get('quality_assessment', {})
        market = decision.get('market_assessment', {})
        prediction = decision.get('success_prediction', {})
        comparison = decision.get('comparison', {})
        revenue = decision.get('revenue_estimate', {})
        
        # Generate festival matches HTML
        festival_matches = decision.get('festival_matches', [])
        festival_html = ""
        for f in festival_matches[:5]:
            festival_html += f'''
                <li class="match-item">
                    <span class="match-name">{f.get('name', 'Unknown')} ({f.get('country', '')})</span>
                    <span class="match-score">{f.get('match_score', 0)}% match</span>
                </li>
            '''
        if not festival_html:
            festival_html = '<li class="match-item"><span>No matches found - build festival presence first</span></li>'
        
        # Generate distributor matches HTML
        distributor_matches = decision.get('distributor_matches', [])
        distributor_html = ""
        for d in distributor_matches[:5]:
            territories = ", ".join(d.get('territories', []))
            distributor_html += f'''
                <li class="match-item">
                    <span class="match-name">{d.get('name', 'Unknown')} ({territories})</span>
                    <span class="match-score">{d.get('match_score', 0)}% match</span>
                </li>
            '''
        if not distributor_html:
            distributor_html = '<li class="match-item"><span>Continue building to unlock distributor matches</span></li>'
        
        # Generate next steps HTML
        next_steps = decision.get('next_steps', ['Continue building festival presence'])
        steps_html = "".join([f'<li class="step">{step}</li>' for step in next_steps])
        
        # Generate strengths HTML
        strengths = quality.get('strengths', ['Analysis in progress'])
        strengths_html = "".join([f'<li class="match-item"><span>✓ {s}</span></li>' for s in strengths])
        if not strengths_html:
            strengths_html = '<li class="match-item"><span>Analysis in progress</span></li>'
        
        # Generate improvements HTML
        improvements = quality.get('improvements', [])
        improvements_html = "".join([f'<li class="match-item"><span>→ {i}</span></li>' for i in improvements])
        if not improvements_html:
            improvements_html = '<li class="match-item"><span>No major areas identified</span></li>'
        
        # Calculate percentiles
        overall_pct = comparison.get('overall', {}).get('percentile', 50)
        genre_pct = comparison.get('by_genre', {}).get('percentile', 50)
        duration_pct = comparison.get('by_duration', {}).get('percentile', 50)
        
        # Fill template
        html = self.template.format(
            title=decision.get('film_title', 'Unknown Film'),
            date=datetime.now().strftime('%B %d, %Y at %H:%M'),
            director=film_data.get('director', 'Unknown'),
            country=film_data.get('country', 'Unknown'),
            duration=film_data.get('duration', 'N/A'),
            genre=film_data.get('genre', 'General'),
            themes=", ".join(film_data.get('themes', ['General'])),
            report_id=f"PACCS-{decision.get('film_id', 'XXX')[:10]}-{datetime.now().strftime('%Y%m%d')}",
            final_score=decision.get('final_score', 'N/A'),
            pathway=decision.get('pathway', 'FESTIVAL'),
            quality_score=quality.get('score', 'N/A'),
            market_score=market.get('score', 'N/A'),
            confidence=int(decision.get('final_confidence', 0.5) * 100),
            overall_percentile=100 - overall_pct,
            genre_percentile=100 - genre_pct,
            duration_percentile=100 - duration_pct,
            festival_prob=prediction.get('festival_selection', '?'),
            distribution_prob=prediction.get('distribution_deal', '?'),
            award_prob=prediction.get('award_nomination', '?'),
            viral_prob=prediction.get('viral_potential', '?'),
            revenue_low=revenue.get('low_estimate', 0),
            revenue_high=revenue.get('high_estimate', 0),
            rev_festival=revenue.get('breakdown', {}).get('festival_circuit', 0),
            rev_streaming=revenue.get('breakdown', {}).get('streaming_rights', 0),
            rev_educational=revenue.get('breakdown', {}).get('educational_licensing', 0),
            rev_other=revenue.get('breakdown', {}).get('other', 0),
            festival_matches_html=festival_html,
            distributor_matches_html=distributor_html,
            next_steps_html=steps_html,
            strengths_html=strengths_html,
            improvements_html=improvements_html,
            year=datetime.now().year
        )
        
        return html
    
    def save_report(self, html, filename):
        """Save HTML report to file"""
        with open(filename, 'w') as f:
            f.write(html)
        return filename


# Test
if __name__ == "__main__":
    print("="*60)
    print("PDF Report Generator Test")
    print("="*60)
    
    # Sample decision data
    test_decision = {
        "film_id": "TEST_001",
        "film_title": "Breaking Silence",
        "film_data": {
            "director": "Priya Sharma",
            "country": "India",
            "duration": 52,
            "genre": "Documentary",
            "themes": ["Mental Health", "Social Justice"]
        },
        "final_score": 8.2,
        "final_confidence": 0.85,
        "pathway": "FESTIVAL",
        "quality_assessment": {
            "score": 8.5,
            "strengths": ["Strong technical execution", "Compelling narrative"],
            "improvements": ["Consider international co-production"]
        },
        "market_assessment": {
            "score": 7.9
        },
        "success_prediction": {
            "festival_selection": 87,
            "distribution_deal": 65,
            "award_nomination": 28,
            "viral_potential": 35
        },
        "comparison": {
            "overall": {"percentile": 15},
            "by_genre": {"percentile": 12},
            "by_duration": {"percentile": 18}
        },
        "revenue_estimate": {
            "low_estimate": 15000,
            "high_estimate": 45000,
            "breakdown": {
                "festival_circuit": 8000,
                "streaming_rights": 20000,
                "educational_licensing": 5000,
                "other": 2000
            }
        },
        "festival_matches": [
            {"name": "IDFA Amsterdam", "country": "Netherlands", "match_score": 88},
            {"name": "Hot Docs", "country": "Canada", "match_score": 82},
            {"name": "Sheffield DocFest", "country": "UK", "match_score": 75}
        ],
        "distributor_matches": [
            {"name": "Netflix Documentary", "territories": ["Global"], "match_score": 78},
            {"name": "BBC Storyville", "territories": ["UK", "Global"], "match_score": 72}
        ],
        "next_steps": [
            "Submit to IDFA Amsterdam",
            "Prepare press kit and stills",
            "Contact impact distribution partners",
            "Create 2-minute festival trailer"
        ]
    }
    
    generator = PDFReportGenerator()
    html = generator.generate_report(test_decision)
    
    # Save to file
    generator.save_report(html, "test_report.html")
    print("\nReport saved to: test_report.html")
    print("Open in browser and click 'Download PDF' to save as PDF")
    
    print("\n" + "="*60)
    print("PDF report generator test complete!")