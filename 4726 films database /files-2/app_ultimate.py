"""
PACCS Ultimate Web Application
Flask-based web interface with full feature support
"""
from flask import Flask, render_template, jsonify, request
from database import FilmDatabase
from consensus import ConsensusProtocol

app = Flask(__name__)
db = FilmDatabase()
consensus = ConsensusProtocol()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/films')
def get_films():
    pending = db.get_pending_films()
    reviewed = db.get_reviewed_films()
    stats = db.get_statistics()
    return jsonify({
        'pending': pending[:20],
        'reviewed': reviewed[:20],
        'stats': stats
    })

@app.route('/api/process', methods=['POST'])
def process_film():
    data = request.json
    film_id = data.get('film_id')
    
    film = db.get_film(film_id)
    if not film:
        return jsonify({'error': 'Film not found'}), 404
    
    decision = consensus.process_film(film, generate_report=True)
    db.update_film_status(film_id, 'reviewed')
    consensus.save_decisions()
    
    return jsonify(decision)

@app.route('/api/batch', methods=['POST'])
def batch_process():
    pending = db.get_pending_films()[:5]
    processed = 0
    
    for film in pending:
        consensus.process_film(film)
        db.update_film_status(film['id'], 'reviewed')
        processed += 1
    
    consensus.save_decisions()
    
    return jsonify({
        'processed': processed,
        'stats': consensus.get_statistics()
    })

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'database': db.get_statistics(),
        'consensus': consensus.get_statistics()
    })

@app.route('/api/report/<film_id>')
def get_report(film_id):
    """Get full report for a specific film"""
    for d in consensus.decisions:
        if d['film_id'] == film_id:
            return jsonify(d)
    return jsonify({'error': 'Report not found'}), 404

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎬 PACCS Ultimate Web Interface")
    print("="*60)
    print("\n✨ Features:")
    print("   • Success Prediction")
    print("   • Comparison Engine")
    print("   • Revenue Estimation")
    print("   • Festival Matching")
    print("   • Distributor Matching")
    print("   • Full Report Generation")
    print("\n🌐 Open your browser and go to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server\n")
    app.run(debug=True, port=5000)
