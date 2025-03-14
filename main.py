import asyncio
import argparse
import sys
import signal
from stable_genius.agents.personalities import create_agent

def signal_handler(sig, frame):
    """Handle keyboard interrupt gracefully"""
    print("\n\nKeyboard interrupt detected. Shutting down gracefully...")
    print("Thank you for using the application! ₍ᐢ._.ᐢ₎♡ ༘")
    sys.exit(0)

async def simulate_conversation(turns=5):
    """Run a simulated conversation between two agents"""
    try:
        agent1 = create_agent("Alice", "friendly")
        agent2 = create_agent("Bob", "analytical")
        
        print("=== Starting Conversation ===")
        
        # Start with a greeting
        message = "Hello there!"
        
        for i in range(turns):
            print(f"\nTurn {i+1}:")
            try:
                print(f"Alice receives: {message}")
                response1 = await agent1.receive_message(message, "Bob")
                message1 = response1['speech']
                # Get current psyche state
                alice_psyche = agent1.get_psyche()
                print(f"Alice ({alice_psyche.tension_level}/100 tension): {message1}")
                
                print(f"Bob receives: {message1}")
                response2 = await agent2.receive_message(message1, "Alice")
                message = response2['speech']
                # Get current psyche state
                bob_psyche = agent2.get_psyche()
                print(f"Bob ({bob_psyche.tension_level}/100 tension): {message}")
            except Exception as e:
                print(f"Error during conversation turn {i+1}: {str(e)}")
                message = "I'm not sure I understood that. Can you try again?"
        
        print("\n=== Conversation Ended ===")
        alice_psyche = agent1.get_psyche()
        bob_psyche = agent2.get_psyche()
        print(f"Alice's final state: {alice_psyche.tension_level}/100 tension")
        print(f"Bob's final state: {bob_psyche.tension_level}/100 tension")
        print("Alice's memories:", alice_psyche.memories)
        print("Bob's memories:", bob_psyche.memories)
        
    except KeyboardInterrupt:
        print("\n\nConversation interrupted by user. Exiting gracefully...")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    # Register signal handler for CTRL+C
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(description='Run AI agent conversation')
    parser.add_argument('--turns', type=int, default=5, help='Number of conversation turns')
    
    args = parser.parse_args()
    
    try:
        # Run the conversation
        exit_code = asyncio.run(simulate_conversation(args.turns))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        # This is a fallback in case the signal handler doesn't catch it
        print("\n\nKeyboard interrupt detected. Shutting down...")
        sys.exit(0) 