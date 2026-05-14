#!/usr/bin/env python3
"""
Interactive Prox Welding Agent REPL
Bidirectional knowledge system with live vault editing
"""

import os
import sys
import json
import re
import readline  # Enables arrow keys in input
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent import ProxWeldingAgent

# ANSI colors
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    RED = '\033[91m'

def print_header():
    print(f"""
{Colors.BOLD}{Colors.CYAN}
{'='*70}
  PROX WELDING AGENT - Interactive Bidirectional Knowledge System
{'='*70}
{Colors.RESET}

  Connected to: bidirectional prox (Obsidian vault)
  Features: Read/Write/Edit/Query/Synthesize

  Commands:
    {Colors.GREEN}ask <question>{Colors.RESET}       - Query the knowledge base
    {Colors.GREEN}new <title>{Colors.RESET}        - Create new note
    {Colors.GREEN}edit <title>{Colors.RESET}      - Edit existing note
    {Colors.GREEN}enrich <note> <pdf> [page]{Colors.RESET} - Enrich note from PDF
    {Colors.GREEN}image <path> [title]{Colors.RESET} - Analyze image & add to vault
    {Colors.GREEN}link <note1> <note2>{Colors.RESET} - Create bidirectional link
    {Colors.GREEN}search <term>{Colors.RESET}     - Keyword search vault
    {Colors.GREEN}stats{Colors.RESET}             - Show vault statistics
    {Colors.GREEN}graph{Colors.RESET}             - Export knowledge graph
    {Colors.GREEN}list{Colors.RESET}              - List all notes
    {Colors.GREEN}read <note>{Colors.RESET}       - Read a note
    {Colors.GREEN}reverse{Colors.RESET}           - Try reverse engineering Claude artifacts
    {Colors.GREEN}demo{Colors.RESET}              - Run demo scenarios
    {Colors.GREEN}help{Colors.RESET}              - Show this help
    {Colors.GREEN}quit{Colors.RESET}              - Exit

{Colors.RESET}""")

def main():
    print_header()
    
    # Initialize agent
    try:
        agent = ProxWeldingAgent(vault_path="bidirectional prox")
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        return
    
    print(f"{Colors.GREEN}✓ Agent ready! Type 'help' for commands{Colors.RESET}\n")
    
    while True:
        try:
            cmd = input(f"{Colors.BLUE}prox> {Colors.RESET}").strip()
            
            if not cmd:
                continue
            
            parts = cmd.split(maxsplit=1)
            action = parts[0].lower()
            
            if action in ['quit', 'exit', 'q']:
                print(f"{Colors.YELLOW}Goodbye!{Colors.RESET}")
                break
            
            # ============ ASK ============
            elif action == 'ask':
                if len(parts) < 2:
                    print(f"{Colors.YELLOW}Usage: ask <question>{Colors.RESET}")
                    continue
                
                question = parts[1]
                result = agent.query(question, context_notes=3)
                
                print(f"\n{Colors.CYAN}{'='*60}")
                print(f"ANSWER")
                print(f"{'='*60}{Colors.RESET}")
                print(result['answer'])
                print(f"\n{Colors.MAGENTA}Sources: {', '.join(result['sources'][:3])}{Colors.RESET}")
                print()
            
            # ============ NEW ============
            elif action == 'new':
                if len(parts) < 2:
                    print(f"{Colors.YELLOW}Usage: new <title>{Colors.RESET}")
                    continue
                
                title = parts[1]
                print(f"{Colors.YELLOW}Enter note content (end with empty line):{Colors.RESET}")
                lines = []
                while True:
                    line = input()
                    if line == '':
                        break
                    lines.append(line)
                
                content = '\n'.join(lines)
                tags_input = input(f"{Colors.YELLOW}Tags (comma-separated): {Colors.RESET}")
                tags = [t.strip() for t in tags_input.split(',') if t.strip()]
                
                agent.create_or_update_note(title, content, tags=tags)
            
            # ============ EDIT ============
            elif action == 'edit':
                if len(parts) < 2:
                    print(f"{Colors.YELLOW}Usage: edit <title>{Colors.RESET}")
                    continue
                
                title = parts[1]
                note = agent._find_note(title)
                
                if not note:
                    print(f"{Colors.RED}Note not found: {title}{Colors.RESET}")
                    continue
                
                print(f"\n{Colors.CYAN}Current content:{Colors.RESET}")
                print(note['body'][:500])
                print(f"\n{Colors.YELLOW}Enter new content to append (empty line to finish):{Colors.RESET}")
                
                lines = []
                while True:
                    line = input()
                    if line == '':
                        break
                    lines.append(line)
                
                addition = '\n'.join(lines)
                agent.create_or_update_note(title, addition, append=True)
            
            # ============ ENRICH ============
            elif action == 'enrich':
                args = parts[1].split() if len(parts) > 1 else []
                
                if len(args) < 2:
                    print(f"{Colors.YELLOW}Usage: enrich <note_title> <pdf> [page_num]{Colors.RESET}")
                    continue
                
                note_title = args[0]
                pdf_path = args[1]
                pages = [int(args[2]) - 1] if len(args) > 2 else None
                
                agent.enrich_note_from_pdf(note_title, pdf_path, pages)
            
            # ============ IMAGE ============
            elif action == 'image':
                args = parts[1].split() if len(parts) > 1 else []
                
                if len(args) < 1:
                    print(f"{Colors.YELLOW}Usage: image <path> [title]{Colors.RESET}")
                    continue
                
                img_path = args[0]
                title = args[1] if len(args) > 1 else None
                
                agent.add_image_analysis(img_path, title)
            
            # ============ LINK ============
            elif action == 'link':
                args = parts[1].split() if len(parts) > 1 else []
                
                if len(args) < 2:
                    print(f"{Colors.YELLOW}Usage: link <note1> <note2>{Colors.RESET}")
                    continue
                
                agent.create_cross_reference(args[0], args[1])
            
            # ============ SEARCH ============
            elif action == 'search':
                if len(parts) < 2:
                    print(f"{Colors.YELLOW}Usage: search <term>{Colors.RESET}")
                    continue
                
                term = parts[1]
                results = agent._keyword_search(term, k=10)
                
                print(f"\n{Colors.CYAN}Found {len(results)} results:{Colors.RESET}\n")
                for doc in results:
                    title_match = re.search(r'^#\s+(.+)$', doc['body'], re.MULTILINE)
                    title = title_match.group(1) if title_match else doc['filename']
                    print(f"  {Colors.GREEN}• {title}{Colors.RESET}")
                    excerpt = doc['body'][:100].replace('\n', ' ')
                    print(f"    {excerpt}...")
                    print()
            
            # ============ STATS ============
            elif action == 'stats':
                stats = agent.get_stats()
                print(f"\n{Colors.CYAN}Vault Statistics:{Colors.RESET}")
                print(f"  Total notes: {stats['total_notes']}")
                print(f"\n  Tags:")
                for tag, count in sorted(stats['tags'].items(), key=lambda x: -x[1]):
                    print(f"    {tag}: {count}")
                print()
            
            # ============ GRAPH ============
            elif action == 'graph':
                agent.export_graph()
            
            # ============ LIST ============
            elif action == 'list':
                print(f"\n{Colors.CYAN}Notes in vault:{Colors.RESET}\n")
                for doc in agent.documents:
                    title_match = re.search(r'^#\s+(.+)$', doc['body'], re.MULTILINE)
                    title = title_match.group(1) if title_match else doc['filename']
                    tags = doc.get('tags', [])
                    print(f"  {Colors.GREEN}• {title}{Colors.RESET}")
                    if tags:
                        print(f"    Tags: {', '.join(tags[:5])}")
                    print()
            
            # ============ READ ============
            elif action == 'read':
                if len(parts) < 2:
                    print(f"{Colors.YELLOW}Usage: read <note_title>{Colors.RESET}")
                    continue
                
                title = parts[1]
                note = agent._find_note(title)
                
                if not note:
                    print(f"{Colors.RED}Note not found: {title}{Colors.RESET}")
                    continue
                
                print(f"\n{Colors.CYAN}{'='*60}")
                print(f"{note['filename']}")
                print(f"{'='*60}{Colors.RESET}")
                print(note['body'])
                print(f"\n{Colors.MAGENTA}Tags: {', '.join(note.get('tags', []))}{Colors.RESET}")
                if note.get('links'):
                    print(f"{Colors.MAGENTA}Links: {', '.join(note['links'])}{Colors.RESET}")
                print()
            
            # ============ REVERSE ENGINEERING ============
            elif action == 'reverse':
                print(f"\n{Colors.MAGENTA}{'='*60}")
                print(f"REVERSE ENGINEERING CLAUDE ARTIFACTS")
                print(f"{'='*60}{Colors.RESET}\n")
                
                print("""
Claude Artifacts Analysis - What we know:

1. Structure:
   - Frontmatter (YAML) with metadata
   - Markdown body with headings
   - Wiki-style links [[Note Name]]
   - Tags #like-this

2. Bidirectional Links:
   - When Note A links to Note B
   - Note B automatically gets a backlink to Note A
   - Creates a knowledge graph

3. RAG (Retrieval-Augmented Generation):
   - Vector embeddings for semantic search
   - FAISS index for fast similarity search
   - Combines with keyword search

4. Knowledge Synthesis:
   - Agent reads from vault
   - Processes with LLM
   - Writes new insights back
   - Creates cross-references

5. Key Patterns in This Vault:
   - Flashcard-style notes (concise, focused)
   - Heavy use of tables for technical data
   - Cross-references between related concepts
   - Tags for categorization
   - Source attribution (PDF, page numbers)

What we can reverse engineer:
   ✓ Note structure and metadata format
   ✓ Linking patterns (wiki-style)
   ✓ Tag taxonomy and organization
   ✓ Content types (reference, guide, index)
   ✓ Integration points (PDF extraction, image analysis)
   ✓ Query patterns (semantic + keyword)

The "secret sauce":
   - Bidirectional updates (vault ↔ agent)
   - Real-time knowledge graph
   - Semantic search over structured notes
   - Automated cross-referencing
   - Progressive enrichment (add data to existing notes)

Try: ask "How does MIG compare to TIG for aluminum?"
     link "Safety Warnings" "MIG Flux-Cored Welding"
     enrich "Owners Manual - Technical Specifications" "files/owner-manual.pdf" 7
        """)
            
                input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
            
            # ============ DEMO ============
            elif action == 'demo':
                print(f"\n{Colors.CYAN}Running demo scenarios...{Colors.RESET}\n")
                
                scenarios = [
                    ("ask", "What is the duty cycle for MIG at 200A 240V?"),
                    ("ask", "How do I prevent electric shock when welding?"),
                    ("ask", "What materials can be welded with TIG?"),
                    ("search", "welding"),
                    ("stats", ""),
                ]
                
                for action_type, arg in scenarios:
                    if action_type == 'ask':
                        print(f"{Colors.BLUE}Q: {arg}{Colors.RESET}")
                        result = agent.query(arg, context_notes=2)
                        print(f"{Colors.GREEN}A: {result['answer'][:200]}...{Colors.RESET}\n")
                    elif action_type == 'search':
                        print(f"{Colors.BLUE}Search: {arg}{Colors.RESET}")
                        results = agent._keyword_search(arg, k=3)
                        for doc in results[:2]:
                            title_match = re.search(r'^#\s+(.+)$', doc['body'], re.MULTILINE)
                            title = title_match.group(1) if title_match else doc['filename']
                            print(f"  • {title}")
                        print()
                    elif action_type == 'stats':
                        stats = agent.get_stats()
                        print(f"{Colors.BLUE}Stats:{Colors.RESET} {stats['total_notes']} notes, {len(stats['tags'])} tags\n")
            
            # ============ HELP ============
            elif action == 'help':
                print_header()
            
            else:
                print(f"{Colors.RED}Unknown command: {action}. Type 'help' for commands.{Colors.RESET}")
        
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Use 'quit' to exit{Colors.RESET}")
        except EOFError:
            print(f"\n{Colors.YELLOW}Goodbye!{Colors.RESET}")
            break
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
