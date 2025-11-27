"""
PACCS Dashboard
Generates metrics and visualizations
"""
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from datetime import datetime

class Dashboard:
    """Generates PACCS metrics dashboard"""
    
    def __init__(self):
        self.decisions = []
        self.load_decisions()
    
    def load_decisions(self):
        """Load decisions from file"""
        try:
            with open('paccs_decisions.json', 'r') as f:
                self.decisions = json.load(f)
            print(f"Loaded {len(self.decisions)} decisions")
        except FileNotFoundError:
            print("No decisions file found. Run consensus.py first.")
            self.decisions = []
    
    def generate_metrics(self):
        """Calculate system metrics"""
        if not self.decisions:
            return None
        
        pathways = {}
        for d in self.decisions:
            p = d['pathway']
            pathways[p] = pathways.get(p, 0) + 1
        
        scores = [d['final_score'] for d in self.decisions]
        avg_score = sum(scores) / len(scores)
        
        confidences = [d['final_confidence'] for d in self.decisions]
        avg_confidence = sum(confidences) / len(confidences)
        
        escalations = sum(1 for d in self.decisions if d['needs_escalation'])
        escalation_rate = escalations / len(self.decisions) * 100
        
        return {
            'total_processed': len(self.decisions),
            'pathways': pathways,
            'avg_score': round(avg_score, 2),
            'avg_confidence': round(avg_confidence, 2),
            'escalation_rate': round(escalation_rate, 1),
            'score_range': {
                'min': round(min(scores), 1),
                'max': round(max(scores), 1)
            }
        }
    
    def generate_chart(self, filename='metrics_dashboard.png'):
        """Generate visualization dashboard"""
        if not self.decisions:
            print("No decisions to visualize")
            return
        
        metrics = self.generate_metrics()
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('PACCS Performance Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Pathway Distribution (Pie Chart)
        ax1 = axes[0, 0]
        pathways = metrics['pathways']
        colors = ['#2c5282', '#4299e1', '#63b3ed', '#90cdf4', '#bee3f8']
        ax1.pie(pathways.values(), labels=pathways.keys(), autopct='%1.1f%%', 
                colors=colors[:len(pathways)])
        ax1.set_title('Pathway Distribution')
        
        # 2. Score Distribution (Histogram)
        ax2 = axes[0, 1]
        scores = [d['final_score'] for d in self.decisions]
        ax2.hist(scores, bins=10, color='#2c5282', edgecolor='white')
        ax2.axvline(metrics['avg_score'], color='#c53030', linestyle='--', 
                   label=f'Average: {metrics["avg_score"]}')
        ax2.set_xlabel('Score')
        ax2.set_ylabel('Count')
        ax2.set_title('Score Distribution')
        ax2.legend()
        
        # 3. Quality vs Market Scores (Scatter)
        ax3 = axes[1, 0]
        quality_scores = [d['quality_assessment']['score'] for d in self.decisions]
        market_scores = [d['market_assessment']['score'] for d in self.decisions]
        colors_scatter = ['#c53030' if d['needs_escalation'] else '#2c5282' 
                         for d in self.decisions]
        ax3.scatter(quality_scores, market_scores, c=colors_scatter, alpha=0.7)
        ax3.plot([0, 10], [0, 10], 'k--', alpha=0.3, label='Agreement line')
        ax3.set_xlabel('Quality Score')
        ax3.set_ylabel('Market Score')
        ax3.set_title('Quality vs Market Assessment')
        ax3.set_xlim(0, 10)
        ax3.set_ylim(0, 10)
        ax3.legend()
        
        # 4. Key Metrics Summary
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        summary_text = f"""
        PACCS Performance Summary
        -------------------------
        
        Total Films Processed: {metrics['total_processed']}
        
        Average Score: {metrics['avg_score']}/10
        Score Range: {metrics['score_range']['min']} - {metrics['score_range']['max']}
        
        Average Confidence: {metrics['avg_confidence']*100:.1f}%
        
        Escalation Rate: {metrics['escalation_rate']:.1f}%
        (Films flagged for human review)
        
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """
        
        ax4.text(0.1, 0.5, summary_text, transform=ax4.transAxes, 
                fontsize=11, verticalalignment='center', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='#f7fafc', edgecolor='#e2e8f0'))
        
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"Dashboard saved to {filename}")
        return filename


if __name__ == "__main__":
    print("="*60)
    print("PACCS Dashboard Generator")
    print("="*60)
    
    dashboard = Dashboard()
    
    if dashboard.decisions:
        metrics = dashboard.generate_metrics()
        print(f"\nMetrics Summary:")
        print(f"  Total processed: {metrics['total_processed']}")
        print(f"  Average score: {metrics['avg_score']}/10")
        print(f"  Average confidence: {metrics['avg_confidence']*100:.1f}%")
        print(f"  Escalation rate: {metrics['escalation_rate']:.1f}%")
        print(f"  Pathways: {metrics['pathways']}")
        
        dashboard.generate_chart()
    else:
        print("\nNo decisions found. Run this command first:")
        print("  python3 consensus.py")
    
    print("\nDashboard generation complete!")