#!/usr/bin/env python3
"""Upload all PDFs to the second brain with full extraction"""

from dotenv import load_dotenv
load_dotenv()

from claude_agent import ProxWeldingAgent
import os

print("="*70)
print("📁 PDF Upload to Second Brain")
print("="*70)

agent = ProxWeldingAgent()

# Find all PDFs
pdf_dir = "files/"
pdfs = [
    os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir)
    if f.lower().endswith('.pdf')
]

print(f"\nFound {len(pdfs)} PDFs to upload:\n")

results = []
for pdf_path in pdfs:
    print(f"\n{'='*70}")
    filename = os.path.basename(pdf_path)
    
    # Upload with full extraction
    result = agent.upload_pdf(
        pdf_path=pdf_path,
        note_title=f"PDF: {filename.replace('.pdf', '')}",
        extract_pages=None,  # All pages
        create_summary=True
    )
    results.append(result)

print(f"\n{'='*70}")
print("✓ ALL PDFs UPLOADED SUCCESSFULLY!")
print(f"{'='*70}")
print(f"\nSummary:")
print(f"  PDFs uploaded: {len(results)}")
for r in results:
    info = r['pdf']
    print(f"  • {info['filename']}: {info['total_pages']} pages")

# Show vault stats
stats = agent.get_knowledge_stats()
print(f"\n📊 Vault Stats:")
print(f"  Total notes: {stats['total_notes']}")
print(f"  Total tags: {len(stats['tags'])}")

print(f"\n✨ All content now searchable in your second brain!")
