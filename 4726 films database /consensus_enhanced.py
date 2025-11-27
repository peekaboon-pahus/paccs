"""
PACCS Enhanced Consensus Protocol
- Multi-agent negotiation with predictive intelligence
- Festival and distributor matching
- Report generation
"""
import json
from datetime import datetime
from agents import QualityAssessmentAgent, MarketIntelligenceAgent, OpportunityRoutingAgent
from report_generator import FilmReportGenerator

class ConsensusProtocol:
    """Enhanced consensus with full matching capabilities"""
    
    def __init__(self):
        print("Initializing PACCS Enhanced Consensus Protocol...")
        self.quality_agent = QualityAssessmentAgent()
        self.market_agent = MarketIntelligenceAgent()
        self.routing_agent = OpportunityRoutingAgent()
        self.report_generator = FilmReportGenerator()
        self.negotiation_log = []
        self.decisions = []
    
    def log_event(self, event_type, message, agent=None):
        """Log negotiation events for audit trail"""
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
        """Process a single film with full analysis"""
        self.negotiation_log = []
        
        print(f"\n{'='*60}")
        print(f"PACCS CONSENSUS: {film.get('title', 'Unknown')}")
        print(f"{'='*60}")
        
        # Phase 1: Quality Assessment
        self.log_event("PHASE", "Phase 1 - Quality Assessment with Predictive Intelligence")
        quality_result = self.quality_agent.analyze(film)
        self.log_event("RESULT", f"Quality: {quality_result['score']}/10 (conf: {quality_result['confidence']})", "Quality Agent")
        
        if quality_result.get('predictive_adjustments'):
            for adj in quality_result['predictive_adjustments'][:2]:
                self.log_event("INSIGHT", adj, "Quality Agent")
        
        # Phase 2: Market Analysis with Distributor Matching
        self.log_event("PHASE", "Phase 2 - Market Analysis & Distributor Matching")
        market_result = self.market_agent.analyze(film)
        self.log_event("RESULT", f"Market: {market_result['score']}/10 (trend: {market_result.get('genre_trend', 'stable')})", "Market Agent")
        
        if market_result.get('distributor_matches'):
            top_dist = market_result['distributor_matches'][0]
            self.log_event("MATCH", f"Top distributor: {top_dist['name']} ({top_dist['match_score']}% match)", "Market Agent")
        
        # Phase 3: Negotiation (if needed)
        score_diff = abs(quality_result['score'] - market_result['score'])
        
        if score_diff > 2.0:
            self.log_event("PHASE", "Phase 3 - Agent Negotiation Required")
            self.log_event("CONFLICT", f"Score divergence: {score_diff:.1f} points")
            
            if quality_result['confidence'] > market_result['confidence']:
                self.log_event("NEGOTIATION", "Quality assessment weighted higher (higher confidence)", "Quality Agent")
            else:
                self.log_event("NEGOTIATION", "Market assessment weighted higher (higher confidence)", "Market Agent")
        else:
            self.log_event("PHASE", "Phase 3 - Agents in Agreement")
            self.log_event("CONSENSUS", f"Score alignment within range ({score_diff:.1f} points)")
        
        # Phase 4: Routing with Festival Matching
        self.log_event("PHASE", "Phase 4 - Pathway Routing & Festival Matching")
        routing_result = self.routing_agent.route(quality_result, market_result, film)
        self.log_event("ROUTING", f"Pathway: {routing_result['primary_pathway']}", "Routing Agent")
        
        if routing_result.get('festival_matches'):
            top_fest = routing_result['festival_matches'][0]
            self.log_event("MATCH", f"Top festival: {top_fest['name']} ({top_fest['match_score']}% match)", "Routing Agent")
        
        # Phase 5: Final Consensus
        self.log_event("PHASE", "Phase 5 - Final Consensus")
        
        final_score = (quality_result['score'] + market_result['score']) / 2
        final_confidence = min(quality_result['confidence'], market_result['confidence'], routing_result['confidence'])
        
        needs_escalation = final_confidence < 0.6
        
        if needs_escalation:
            self.log_event("ESCALATION", "Low confidence - flagging for human review")
        else:
            self.log_event("CONSENSUS", f"CONSENSUS REACHED: {routing_result['primary_pathway']} ({final_score:.1f}/10)")
        
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
        
        self.decisions.append(decision)
        
        # Generate report if requested
        report_text = None
        if generate_report:
            report_text = self.report_generator.generate_report(
                film, quality_result, market_result, routing_result
            )
            decision['report'] = report_text
        
        print(f"\n{'='*60}")
        print(f"DECISION: {routing_result['primary_pathway']}")
        print(f"Score: {final_score:.1f}/10 | Confidence: {int(final_confidence*100)}%")
        if routing_result.get('festival_matches'):
            print(f"Top Festival: {routing_result['festival_matches'][0]['name']}")
        if market_result.get('distributor_matches'):
            print(f"Top Distributor: {market_result['distributor_matches'][0]['name']}")
        print(f"{'='*60}")
        
        return decision
    
    def save_decisions(self, filename="paccs_decisions.json"):
        """Save all decisions to file"""
        # Remove report text for JSON (too long)
        decisions_to_save = []
        for d in self.decisions:
            d_copy = d.copy()
            d_copy.pop('report', None)  # Remove report text
            decisions_to_save.append(d_copy)
        
        with open(filename, 'w') as f:
            json.dump(decisions_to_save, f, indent=2)
        print(f"\nDecisions saved to {filename}")
    
    def generate_film_report(self, film_id):
        """Generate a report for a specific film from decisions"""
        for d in self.decisions:
            if d['film_id'] == film_id:
                return d.get('report', "Report not generated")
        return None
    
    def get_statistics(self):
        """Get enhanced consensus statistics"""
        if not self.decisions:
            return {"total": 0}
        
        pathways = {}
        festivals_matched = 0
        distributors_matched = 0
        escalations = 0
        total_confidence = 0
        total_score = 0
        
        for d in self.decisions:
            p = d['pathway']
            pathways[p] = pathways.get(p, 0) + 1
            
            if d.get('festival_matches'):
                festivals_matched += len(d['festival_matches'])
            if d.get('distributor_matches'):
                distributors_matched += len(d['distributor_matches'])
            if d['needs_escalation']:
                escalations += 1
            
            total_confidence += d['final_confidence']
            total_score += d['final_score']
        
        return {
            'total_processed': len(self.decisions),
            'pathways': pathways,
            'avg_score': round(total_score / len(self.decisions), 2),
            'avg_confidence': round(total_confidence / len(self.decisions), 2),
            'escalations': escalations,
            'escalation_rate': round(escalations / len(self.decisions) * 100, 1),
            'total_festival_matches': festivals_matched,
            'total_distributor_matches': distributors_matched,
            'avg_festivals_per_film': round(festivals_matched / len(self.decisions), 1),
            'avg_distributors_per_film': round(distributors_matched / len(self.decisions), 1)
        }


# Test the enhanced consensus
if __name__ == "__main__":
    from database import FilmDatabase
    
    print("="*60)
    print("PACCS Enhanced Consensus Protocol Test")
    print("="*60)
    
    # Load database
    db = FilmDatabase()
    
    # Create consensus protocol
    consensus = ConsensusProtocol()
    
    # Process first 3 films with reports
    for film in db.films[:3]:
        decision = consensus.process_film(film, generate_report=True)
        
        # Print top matches
        print(f"\n📋 Summary for: {film.get('title')}")
        print(f"   Festival matches: {len(decision.get('festival_matches', []))}")
        print(f"   Distributor matches: {len(decision.get('distributor_matches', []))}")
    
    # Save decisions
    consensus.save_decisions()
    
    # Show statistics
    stats = consensus.get_statistics()
    print(f"\n{'='*60}")
    print("ENHANCED CONSENSUS STATISTICS")
    print(f"{'='*60}")
    print(f"Total processed: {stats['total_processed']}")
    print(f"Average score: {stats['avg_score']}/10")
    print(f"Average confidence: {stats['avg_confidence']*100:.0f}%")
    print(f"Pathways: {stats['pathways']}")
    print(f"Total festival matches: {stats['total_festival_matches']}")
    print(f"Total distributor matches: {stats['total_distributor_matches']}")
    print(f"Avg festivals per film: {stats['avg_festivals_per_film']}")
    print(f"Avg distributors per film: {stats['avg_distributors_per_film']}")
    
    # Show sample report
    if consensus.decisions and consensus.decisions[0].get('report'):
        print(f"\n{'='*60}")
        print("SAMPLE REPORT")
        print(f"{'='*60}")
        print(consensus.decisions[0]['report'][:2000] + "...")
    
    print("\nEnhanced consensus test complete!")
