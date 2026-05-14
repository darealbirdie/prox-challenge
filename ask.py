#!/usr/bin/env python3
"""
One-liner chat interface: python ask.py "your question"
"""

from dotenv import load_dotenv
load_dotenv()

from claude_agent import ProxWeldingAgent
from sys import argv

agent = ProxWeldingAgent()

if len(argv) < 2:
    print("Usage: python ask.py \"Your question about welding\"")
    print("\nExamples:")
    print('  python ask.py "What is the duty cycle at 200A?"')
    print('  python ask.py "How do I set up TIG welding?"')
    print('  python ask.py "What are the safety precautions?"')
    exit(1)

question = " ".join(argv[1:])
result = agent.answer_question(question)

print("\n" + "="*70)
print("🤖 AGENT RESPONSE")
print("="*70)
print(result['answer'])
if result.get('sources'):
    print(f"\n📚 Sources: {', '.join(result['sources'][:5])}")
print("="*70 + "\n")
