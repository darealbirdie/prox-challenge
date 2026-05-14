#!/usr/bin/env python3
"""
Terminal Chat Interface for Claude Welding Agent
Run with: python chat_interface.py
"""

from dotenv import load_dotenv
load_dotenv()

from claude_agent import ProxWeldingAgent
from datetime import datetime
import sys

def print_header():
    print("\n" + "="*70)
    print("🤖 PROX WELDING AGENT - Interactive Chat")
    print("="*70)
    print("Type your question and press Enter")
    print("Type 'quit', 'exit', or 'q' to end")
    print("Type 'help' for suggestions")
    print("="*70 + "\n")

def print_suggestions():
    suggestions = [
        "What's the duty cycle for MIG welding at 200A on 240V?",
        "How do I set up the machine for TIG welding?",
        "What polarity should I use for different welding processes?",
        "What are the safety precautions for welding?",
        "How do I select welding parameters?"
    ]
    print("\n💡 Try asking:")
    for i, s in enumerate(suggestions, 1):
        print(f"   {i}. {s}")
    print()

def format_response(answer, sources):
    print("\n" + "─"*70)
    print("🤖 AGENT RESPONSE")
    print("─"*70)
    print(answer)
    if sources:
        print("\n📚 Sources:")
        for src in sources[:5]:
            print(f"   • {src}")
    print("─"*70 + "\n")

def main():
    print_header()
    
    # Initialize agent
    print("🚀 Initializing Prox Welding Agent...")
    try:
        agent = ProxWeldingAgent()
        stats = agent.get_knowledge_stats()
        print(f"✓ Agent ready! Knowledge base: {stats['total_notes']} notes")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        sys.exit(1)
    
    # Main chat loop
    while True:
        try:
            question = input("\nYour question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q', '/exit']:
                print("\n👋 Goodbye!")
                break
            
            if question.lower() == 'help':
                print_suggestions()
                continue
            
            if question.lower() == 'stats':
                stats = agent.get_knowledge_stats()
                print(f"\n📊 Knowledge Base Stats:")
                print(f"   Notes: {stats['total_notes']}")
                print(f"   Tags: {len(stats['tags'])}")
                continue
            
            if question.lower() == 'clear':
                print("\033[2J\033[H")  # Clear screen
                print_header()
                continue
            
            # Get response
            print("\n🤖 Thinking...")
            start_time = datetime.now()
            
            result = agent.answer_question(question)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            # Display response
            format_response(result['answer'], result.get('sources', []))
            print(f"⏱️  Response time: {elapsed:.1f}s")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    main()
