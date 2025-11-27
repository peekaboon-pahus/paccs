"""
PACCS Ultimate Consensus Protocol
- Multi-agent negotiation
- Success prediction
- Comparison engine
- Revenue estimation
- Festival and distributor matching
- Report generation
"""
import json
from datetime import datetime
from agents import (
    QualityAssessmentAgent, 
    MarketIntelligenceAgent, 
    OpportunityRoutingAgent,
    SuccessPredictionAgent,
    ComparisonEngine
)
from report_generator import FilmReportGenerator

class ConsensusProtocol:
    """Ultimate consensus with all features"""
    
    def __init__(self):
        print("Initializing PACCS Ultimate Consensus Protocol...")
        self.quality_agent = QualityAssessmentAgent()
        self.market_agent = MarketIntelligenceAgent()
        self.routing_agent = OpportunityRoutingAgent()
        self.success_agent = SuccessPredictionAgent()
        self.comparison_engine = ComparisonEngine()
        self.report_generator = FilmReportGenerator()
        self.negotiation_log = []
        self.decisions = []
        
        # Try to load existing decisions
        try:
            with open('paccs_decisions.json', 'r') as f:
                self.decisions = json.load(f)
                print(f"Loaded {len(self.decisions)} existing decisions")
        except:
            pass
    
    def log_event(self, event_type, message, agent=None):
        """Log negotiation events"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        log_entry = {
            'timestamp': timestamp,
            'type': event_type,
            'agent': agent,
            'message': message
        }
        self.negotiation_log.append(log_entry)
        
        if agent:
            print(f"  [{timestamp}] {agent}: {message}")
        else:
            print(f"  [{timestamp}] SYSTEM: {message}")
    
    def process_film(self, film, generate_report=False):
        """Process a film with full analysis"""
        self.negotiation_log = []
        
        print(f"\n{'='*60}")
        print(f"🎬 PACCS CONSENSUS: {film.get('title', 'Unknown')}")
        print(f"{'='*60}")
        
        # Phase 1: Quality Assessment
        self.log_event("PHASE", "Phase 1 - Quality Assessment")
        quality_result = self.quality_agent.analyze(film)
        self.log_event("RESULT", f"Quality: {quality_result['score']}/10", "Quality Agent")
        
        # Phase 2: Market Analysis
        self.log_event("PHASE", "Phase 2 - Market Analysis & Revenue Estimation")
        market_result = self.market_agent.analyze(film, quality_result['score'])
        self.log_event("RESULT", f"Market: {market_result['score']}/10 (trend: {market_result.get('genre_trend', 'stable')})", "Market Agent")
        
        if market_result.get('distributor_matches'):
            self.log_event("MATCH", f"Top distributor: {market_result['distributor_matches'][0]['name']}", "Market Agent")
        
        if market_result.get('revenue_estimate'):
            rev = market_result['revenue_estimate']
            self.log_event("REVENUE", f"Estimated value: £{rev['low_estimate']:,} - £{rev['high_estimate']:,}", "Market Agent")
        
        # Phase 3: Negotiation
        score_diff = abs(quality_result['score'] - market_result['score'])
        if score_diff > 2.0:
            self.log_event("PHASE", "Phase 3 - Agent Negotiation")
            self.log_event("CONFLICT", f"Score divergence: {score_diff:.1f} points")
        else:
            self.log_event("PHASE", "Phase 3 - Agents in Agreement")
        
        # Phase 4: Routing & Festival Matching
        self.log_event("PHASE", "Phase 4 - Pathway Routing & Matching")
        routing_result = self.routing_agent.route(quality_result, market_result, film)
        self.log_event("ROUTING", f"Pathway: {routing_result['primary_pathway']}", "Routing Agent")
        
        if routing_result.get('festival_matches'):
            self.log_event("MATCH", f"Top festival: {routing_result['festival_matches'][0]['name']}", "Routing Agent")
        
        # Phase 5: Success Prediction
        self.log_event("PHASE", "Phase 5 - Success Prediction")
        success_prediction = routing_result.get('success_prediction', 
            self.success_agent.predict(film, quality_result['score'], market_result['score']))
        self.log_event("PREDICTION", f"Festival selection: {success_prediction['festival_selection']}%", "Prediction Agent")
        
        # Phase 6: Comparison
        comparison = routing_result.get('comparison',
            self.comparison_engine.compare(film, quality_result['score'], market_result['score']))
        self.log_event("COMPARE", f"Overall ranking: Top {100 - comparison['overall']['percentile']}%", "Comparison Engine")
        
        # Final Consensus
        self.log_event("PHASE", "Phase 6 - Final Consensus")
        
        final_score = (quality_result['score'] + market_result['score']) / 2
        final_confidence = min(quality_result['confidence'], market_result['confidence'], routing_result['confidence'])
        needs_escalation = final_confidence < 0.6
        
        if needs_escalation:
            self.log_event("ESCALATION", "Low confidence - flagging for human review")
        else:
            self.log_event("CONSENSUS", f"CONSENSUS REACHED: {routing_result['primary_pathway']}")
        
        # Build decision record
        decision = {
            'film_id': film.get('id'),
            'film_title': film.get('title'),
            'film_data': {
                'director': film.get('director'),
                'country': film.get('country'),
                'duration': film.get('duration_minutes'),
                'genre': film.get('genre'),
                'themes': film.get('themes', [])
            },
            'quality_assessment': quality_result,
            'market_assessment': market_result,
            'routing_decision': routing_result,
            'success_prediction': success_prediction,
            'comparison': comparison,
            'revenue_estimate': market_result.get('revenue_estimate', {}),
            'final_score': round(final_score, 1),
            'final_confidence': round(final_confidence, 2),
            'pathway': routing_result['primary_pathway'],
            'festival_matches': routing_result.get('festival_matches', [])[:5],
            'distributor_matches': market_result.get('distributor_matches', [])[:5],
            'next_steps': routing_result.get('next_steps', []),
            'needs_escalation': needs_escalation,
            'audit_log': self.negotiation_log.copy(),
            'processed_at': datetime.now().isoformat()
        }
        
        # Generate report if requested
        if generate_report:
            try:
                report = self.report_generator.generate_report(
                    film, quality_result, market_result, routing_result
                )
                decision['report'] = report
            except:
                pass
        
        self.decisions.append(decision)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"✅ DECISION: {routing_result['primary_pathway']}")
        print(f"📊 Score: {final_score:.1f}/10 | Confidence: {int(final_confidence*100)}%")
        print(f"🎯 Festival Selection Probability: {success_prediction['festival_selection']}%")
        print(f"📈 Ranking: Top {100 - comparison['overall']['percentile']}% overall")
        if market_result.get('revenue_estimate'):
            rev = market_result['revenue_estimate']
            print(f"💰 Estimated Value: £{rev['low_estimate']:,} - £{rev['high_estimate']:,}")
        print(f"{'='*60}")
        
        return decision
    
    def save_decisions(self, filename="paccs_decisions.json"):
        """Save decisions to file"""
        decisions_to_save = []
        for d in self.decisions:
            d_copy = d.copy()
            d_copy.pop('report', None)
            decisions_to_save.append(d_copy)
        
        with open(filename, 'w') as f:
            json.dump(decisions_to_save, f, indent=2)
        print(f"\n💾 Decisions saved to {filename}")
    
    def get_statistics(self):
        """Get comprehensive statistics"""
        if not self.decisions:
            return {"total": 0}
        
        pathways = {}
        festivals_matched = 0
        distributors_matched = 0
        escalations = 0
        total_confidence = 0
        total_score = 0
        total_festival_prob = 0
        total_revenue = 0
        
        for d in self.decisions:
            p = d['pathway']
            pathways[p] = pathways.get(p, 0) + 1
            
            if d.get('festival_matches'):
                festivals_matched += len(d['festival_matches'])
            if d.get('distributor_matches'):
                distributors_matched += len(d['distributor_matches'])
            if d.get('needs_escalation'):
                escalations += 1
            
            total_confidence += d.get('final_confidence', 0.5)
            total_score += d.get('final_score', 5)
            
            if d.get('success_prediction'):
                total_festival_prob += d['success_prediction'].get('festival_selection', 50)
            
            if d.get('revenue_estimate'):
                total_revenue += d['revenue_estimate'].get('total_estimate', 0)
        
        count = len(self.decisions)
        
        return {
            'total_processed': count,
            'pathways': pathways,
            'avg_score': round(total_score / count, 2),
            'avg_confidence': round(total_confidence / count, 2),
            'avg_festival_probability': round(total_festival_prob / count, 1),
            'total_estimated_value': total_revenue,
            'escalations': escalations,
            'escalation_rate': round(escalations / count * 100, 1),
            'total_festival_matches': festivals_matched,
            'total_distributor_matches': distributors_matched,
            'avg_festivals_per_film': round(festivals_matched / count, 1),
            'avg_distributors_per_film': round(distributors_matched / count, 1)
        }


# Test
if __name__ == "__main__":
    from database import FilmDatabase
    
    print("="*60)
    print("🎬 PACCS Ultimate Consensus Test")
    print("="*60)
    
    db = FilmDatabase()
    consensus = ConsensusProtocol()
    
    # Process 3 films
    for film in db.films[:3]:
        decision = consensus.process_film(film, generate_report=True)
    
    consensus.save_decisions()
    
    # Show statistics
    stats = consensus.get_statistics()
    print(f"\n{'='*60}")
    print("📊 ULTIMATE STATISTICS")
    print(f"{'='*60}")
    print(f"Total processed: {stats['total_processed']}")
    print(f"Average score: {stats['avg_score']}/10")
    print(f"Average confidence: {stats['avg_confidence']*100:.0f}%")
    print(f"Avg festival probability: {stats['avg_festival_probability']}%")
    print(f"Total estimated value: £{stats['total_estimated_value']:,}")
    print(f"Pathways: {stats['pathways']}")
    print(f"Festival matches: {stats['total_festival_matches']}")
    print(f"Distributor matches: {stats['total_distributor_matches']}")
    
    print("\n✅ Ultimate consensus test complete!")