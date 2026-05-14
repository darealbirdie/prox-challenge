#!/usr/bin/env python3
"""
Autonomous Agent Demo - Shows the agent operating on its own
"""

from dotenv import load_dotenv
load_dotenv()

from claude_agent import ProxWeldingAgent
from pathlib import Path
import time
import random

print("="*70)
print("🤖 AUTONOMOUS AGENTIC AI DEMO")
print("="*70)

agent = ProxWeldingAgent()

# Start autonomous mode in background thread
import threading

def run_autonomous():
    """Run autonomous mode with short polling for demo"""
    agent.start_autonomous_mode(
        watch_dirs=['.', 'files/', 'images/'],
        poll_interval=10,      # Check every 10 seconds
        auto_upload_images=True,
        auto_upload_pdfs=True
    )

# Start autonomous agent in background thread
print("\n🚀 Starting autonomous agent in background...\n")
auto_thread = threading.Thread(target=run_autonomous, daemon=True)
auto_thread.start()

time.sleep(2)

print("\n" + "="*70)
print("AUTONOMOUS AGENT IS NOW ACTIVE!")
print("="*70)

# Simulate dropping files into watched directories
print("\n📂 Simulating: Adding new image file...")
time.sleep(1)

# Create a dummy file path (in real use, actual file would appear)
dummy_image = Path("test_welding_diagram.png")

print(f"\n🖼️  [AUTO] Agent detected: {dummy_image.name}")
print("   → Would auto-analyze with BLIP AI")
print("   → Would create knowledge base entry")
print("   → Would auto-link to related welding notes")

print("\n📂 Simulating: Dropping new welding photo...")
time.sleep(1)

dummy_photo = Path("welding_setup.jpg")
print(f"\n🖼️  [AUTO] Agent detected: {dummy_photo.name}")
print("   → Analyzing visual content...")
print("   → Extracting equipment details...")
print("   → Creating catalog entry...")

print("\n📂 Simulating: New PDF manual appears...")
time.sleep(1)

dummy_pdf = Path("new_process_manual.pdf")
print(f"\n📄 [AUTO] Agent detected: {dummy_pdf.name}")
print("   → Extracting all 42 pages...")
print("   → Applying OCR to diagrams...")
print("   → Indexing content for search...")
print("   → Creating searchable note with AI summary...")

print("\n" + "="*70)
print("AUTONOMOUS CYCLE RUNNING")
print("="*70)

# Show what happens during autonomous cycles
for i in range(3):
    time.sleep(2)
    stats = agent.get_knowledge_stats()
    print(f"\n[Cycle {i+1}] Autonomous Agent Status:")
    print(f"   • Knowledge base: {stats['total_notes']} notes")
    print(f"   • Watched files:  {len(agent._processed_files) if hasattr(agent, '_processed_files') else 0}")
    print(f"   • Status: 🟢 Active & monitoring")

print("\n" + "="*70)
print("KEY CAPABILITIES: AUTONOMOUS vs MANUAL")
print("="*70)

print("\n✅ MANUAL MODE (original):")
print("   • YOU: 'agent.analyze_image(file)'  ")
print("   • YOU: 'agent.upload_pdf(file)'")
print("   • YOU: Must explicitly call each method")

print("\n🤖 AUTONOMOUS MODE (NEW):")
print("   • Auto-detects NEW files in watched folders")
print("   • Auto-uploads images → BLIP analysis → vault")
print("   • Auto-extracts PDFs → OCR → searchable notes")
print("   • Runs continuously in background")
print("   • Zero human intervention needed")

print("\n" + "="*70)

# Stop autonomous mode
agent.stop_autonomous_mode()

time.sleep(1)

print("\n📊 FINAL STATE:")
stats = agent.get_knowledge_stats()
print(f"   • Total notes: {stats['total_notes']}")
print(f"   • Tags: {len(stats['tags'])}")
print(f"   • All content: RAG-searchable via Claude")

print("\n" + "="*70)
print("✓ DEMO COMPLETE")
print("="*70)
print("\nYour agent now has BOTH modes:")
print("   1. Manual: agent.analyze_image(), agent.upload_pdf()")
print("   2. Autonomous: agent.start_autonomous_mode()")
print("\nThe agent can work WITHOUT you telling it what to do!")
print("="*70)
