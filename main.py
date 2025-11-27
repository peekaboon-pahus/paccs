"""
PACCS Main Program
Command-line interface for the system
"""
from database import FilmDatabase
from consensus import ConsensusProtocol

def print_menu():
    """Display main menu"""
    print("\n" + "="*50)
    print("PACCS - Peekaboon Agentic Creative Curation System")
    print("="*50)
    print("1. View database statistics")
    print("2. Process single film")
    print("3. Process batch (5 films)")
    print("4. View all decisions")
    print("5. Export decisions to JSON")
    print("6. Exit")
    print("-"*50)

def main():
    """Main program loop"""
    db = FilmDatabase()
    consensus = ConsensusProtocol()
    
    while True:
        print_menu()
        choice = input("Select option (1-6): ").strip()
        
        if choice == "1":
            stats = db.get_statistics()
            print(f"\n--- Database Statistics ---")
            print(f"Total films: {stats['total_films']}")
            print(f"Pending review: {stats['pending']}")
            print(f"Reviewed: {stats['reviewed']}")
            print(f"Genres: {stats['genres']}")
        
        elif choice == "2":
            pending = db.get_pending_films()
            if not pending:
                print("\nNo pending films to process!")
                continue
            
            print(f"\nPending films ({len(pending)}):")
            for i, film in enumerate(pending[:10], 1):
                print(f"  {i}. {film['title']} ({film['genre']})")
            
            try:
                idx = int(input("\nSelect film number: ")) - 1
                if 0 <= idx < len(pending):
                    film = pending[idx]
                    decision = consensus.process_film(film)
                    db.update_film_status(film['id'], 'reviewed')
                else:
                    print("Invalid selection")
            except ValueError:
                print("Please enter a number")
        
        elif choice == "3":
            pending = db.get_pending_films()
            if not pending:
                print("\nNo pending films to process!")
                continue
            
            batch = pending[:5]
            print(f"\nProcessing {len(batch)} films...")
            
            for film in batch:
                consensus.process_film(film)
                db.update_film_status(film['id'], 'reviewed')
            
            print(f"\nBatch complete! Processed {len(batch)} films.")
            
            stats = consensus.get_statistics()
            print(f"Average confidence: {stats['avg_confidence']}")
            print(f"Pathways: {stats['pathways']}")
        
        elif choice == "4":
            if not consensus.decisions:
                print("\nNo decisions yet. Process some films first!")
                continue
            
            print(f"\n--- All Decisions ({len(consensus.decisions)}) ---")
            for d in consensus.decisions:
                flag = " [ESCALATE]" if d['needs_escalation'] else ""
                print(f"  {d['film_title']}: {d['pathway']} (Score: {d['final_score']}){flag}")
        
        elif choice == "5":
            if not consensus.decisions:
                print("\nNo decisions to export!")
                continue
            
            consensus.save_decisions()
            print("Decisions exported to paccs_decisions.json")
        
        elif choice == "6":
            print("\nThank you for using PACCS!")
            break
        
        else:
            print("\nInvalid option. Please select 1-6.")


if __name__ == "__main__":
    main()