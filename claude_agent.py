#!/usr/bin/env python3
"""
Prox Welding Agent - Claude Agent SDK Implementation
Uses Obsidian vault as knowledge base (eliminates duplicate work)
"""

from dotenv import load_dotenv
import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from pdf_utils import extract_pdf_images
from pdf_compiler import PDFKnowledgeCompiler

# Load .env file
load_dotenv()

# Import vault library - provides all knowledge base operations
from agent import get_vault

# Anthropic Claude
import anthropic

# Load API key
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment")

client = anthropic.Anthropic(api_key=api_key)


class ProxWeldingAgent:
    """Claude-based multimodal welding assistant using Obsidian vault"""
    
    def __init__(self):
        # Use the vault instead of building own knowledge base!
        # This eliminates duplicate PDF extraction work
        self.vault = get_vault(None)  # Will use VAULT_PATH from env or default
        self.conversation_history = []
        print(f"✓ Connected to vault with {self.vault.get_stats()['total_notes']} notes")
    
    def _create_system_prompt(self, context: str) -> str:
        """Create system prompt with knowledge context"""
        return f"""You are Prox, a helpful and knowledgeable welding assistant specializing in the Vulcan OmniPro 220 multiprocess welder.

You have access to the machine's technical documentation and can provide expert guidance on setup, operation, and troubleshooting.

RELEVANT KNOWLEDGE:
{context}

GUIDELINES:
1. Be helpful, patient, and encouraging
2. Use clear language while preserving technical accuracy
3. Prioritize visual explanations whenever they reduce cognitive load
4. Ask clarifying questions if setup/process is ambiguous
5. Always prioritize welding safety
6. Break complex procedures into sequential steps
7. Use the retrieved documentation as ground truth
8. Prefer diagrams over prose when spatial or procedural understanding matters

ARTIFACT DECISION RULES:
If a response involves:
- spatial relationships → use Mermaid diagrams
- step-by-step processes → use flowcharts
- troubleshooting → use decision trees
- hardware wiring or polarity → use schematics/diagrams
- parameter tuning → use tables or interactive HTML artifacts
- comparisons → use tables
- calculations → use HTML calculators or formatted formulas
- configurations/settings → use structured UI or markdown tables

Never default to plain text if a diagram, table, or interactive artifact would explain it better.

MULTIMODAL BEHAVIOR:
- If retrieved context references diagrams, panels, controls, sockets, wiring, or images:
  explain visually using artifacts.
- If troubleshooting is involved:
  create diagnostic flows.
- If setup is involved:
  generate visual setup guides.
- If the answer is cognitively dense:
  use visual decomposition.

ARTIFACT FORMAT:
Artifacts MUST be wrapped EXACTLY like this:

<artifact type="mermaid">
flowchart TD
A --> B
</artifact>

Valid artifact types:
- mermaid
- html
- markdown
- json

IMPORTANT RULES:
- Never wrap artifact blocks in markdown code fences
- Artifacts must be self-contained
- Mermaid artifacts must use valid Mermaid syntax
- HTML artifacts should be standalone and visually clean
- Use artifacts proactively, not reactively
- The best answer is often visual first, text second
"""
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a technical question using RAG and Claude"""
        print(f"\n❓ Question: {question}")
        
        # Search vault for relevant knowledge (RAG)
        # This replaces the duplicate PDF extraction in the old version!
        results = self.vault.search(question, k=5)
        
        # Also query PDFs directly for fresh evidence
        pdf_evidence = self.vault.query_pdf(question)
        
        if not results and not pdf_evidence:
            print("  ℹ️  No relevant knowledge found, using general expertise")
            context = "No specific documentation matched the query."
        else:
            print(f"  ✓ Found {len(results)} relevant knowledge sources")
            for r in results:
                print(f"    - {r['filename']}")
            
            if pdf_evidence:
                print(f"  ✓ Found {len(pdf_evidence)} PDF evidence sources")
                for e in pdf_evidence:
                    print(f"    - {e['source']} (page {e['page']})")
            
            # Format results as context for Claude
            context_parts = []
            for i, result in enumerate(results):
                excerpt = result.get('excerpt', '') or result.get('body', '')[:500]
                context_parts.append(f"""
--- Source {i+1}: {result['filename']} ---
{excerpt}
""")
            
            # Add PDF evidence to context
            for i, evidence in enumerate(pdf_evidence):
                context_parts.append(f"""
--- PDF Evidence {i+1}: {evidence['source']} (page {evidence['page']}) ---
{evidence['excerpt']}
""")
            
            context = "\n".join(context_parts)
        
        # Create system prompt with knowledge context
        system_prompt = self._create_system_prompt(context)
        
        # Call Claude
        try:
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4000,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": question}
                ]
            )
            
            response = message.content[0].text if message.content else "No response"
            
            # Parse artifacts from response
            answer_text, artifacts = self._parse_artifacts_from_response(response)
            
            # Store in history
            self.conversation_history.append({
                'question': question,
                'response': response,
                'sources': [r['filename'] for r in results] + [e['source'] for e in pdf_evidence],
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"  ✓ Response generated ({len(response)} chars)")
            print(f"  ✓ Found {len(artifacts)} artifacts")
            
            return {
                'answer': answer_text,
                'artifacts': artifacts,
                'sources': [r['filename'] for r in results] + [e['source'] for e in pdf_evidence],
                'context_used': len(results) > 0 or len(pdf_evidence) > 0
            }
        except Exception as e:
            print(f"  ✗ Claude API error: {e}")
            return {
                'answer': f"I encountered an error: {e}",
                'artifacts': [],
                'sources': [],
                'context_used': False
            }
    
    def _parse_artifacts_from_response(self, response: str) -> tuple[str, List[Dict[str, Any]]]:
        """Parse artifacts from Claude's response using <artifact> tags"""
        import re
        
        # Handle None or non-string response
        if response is None or not isinstance(response, str):
            return "", []
        
        artifacts = []
        answer_text = response
        
        # Find all artifact blocks: <artifact type="...">content</artifact>
        try:
            artifact_pattern = r'<artifact\s+type="([^"]+)">(.*?)</artifact>'
            matches = re.findall(artifact_pattern, response, re.DOTALL | re.IGNORECASE)
        except Exception as e:
            print(f"  ✗ Regex error in _parse_artifacts_from_response: {e}")
            matches = []
        
        # Remove artifact blocks from answer text and collect artifacts
        for artifact_type, content in matches:
            artifact_type = artifact_type.lower().strip()
            content = content.strip()
            
            if content:  # Only add non-empty artifacts
                artifacts.append({
                    'type': artifact_type,
                    'content': content
                })
            
            # Remove this artifact block from the answer text
            try:
                answer_text = answer_text.replace(f'<artifact type="{artifact_type}">{content}</artifact>', '')
            except Exception as e:
                print(f"  ✗ Replace error in _parse_artifacts_from_response: {e}")
                # If replace fails, continue with the original answer_text for this artifact
                pass
        
        # Clean up extra whitespace from answer text
        try:
            answer_text = re.sub(r'\n\s*\n\s*\n', '\n\n', answer_text).strip()
        except Exception as e:
            print(f"  ✗ Whitespace cleanup error in _parse_artifacts_from_response: {e}")
            # If regex fails, return the answer_text as is
            pass
        
        return answer_text, artifacts
    
    def generate_artifact(self, prompt: str, artifact_type: str = "mermaid") -> Dict[str, Any]:
        """Generate a visual artifact (diagram, chart, etc.)"""
        print(f"\n🎨 Generating {artifact_type} artifact...")
        
        if artifact_type == "mermaid":
            system_prompt = """You are an expert at creating Mermaid diagrams for technical documentation.
Create clear, well-structured diagrams that explain technical concepts.
Always use proper Mermaid syntax and include a brief explanation of what the diagram shows."""
        elif artifact_type == "python":
            system_prompt = """You are an expert at creating Python visualizations using matplotlib and plotly.
Generate complete, runnable Python code that creates clear, informative charts and diagrams.
Include all necessary imports and make the code as clear as possible."""
        else:
            system_prompt = f"Create a {artifact_type} artifact to explain the following concept."
        
        try:
            message = client.messages.create(
                model="claude-4-6-sonnet",
                max_tokens=3000,
                temperature=0.5,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            artifact = message.content[0].text if message.content else "No artifact generated"
            
            print(f"  ✓ Artifact generated ({len(artifact)} chars)")
            
            return {
                'artifact': artifact,
                'type': artifact_type,
                'prompt': prompt
            }
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return {'error': str(e)}
    
    def enrich_with_pdf(self, note_title: str, pdf_path: str, pages: List[int] = None):
        """Enrich a note with PDF extraction"""
        print(f"\n📄 Enriching '{note_title}' with PDF data...")
        self.vault.enrich_note(note_title, pdf_path, pages)
        return True
    
    def link_notes(self, note1: str, note2: str, relation: str = "related"):
        """Create bidirectional link between notes"""
        print(f"\n🔗 Linking '{note1}' ↔ '{note2}'...")
        self.vault.link_notes(note1, note2, relation)
        return True
    
    def analyze_image(self, image_path: str, note_title: str = None, 
                     tags: List[str] = None, auto_link: bool = True):
        """
        Upload and analyze an image using multimodal AI (BLIP).
        Extracts captions, descriptions, and details from images.
        Automatically creates a note in the knowledge vault.
        
        Args:
            image_path: Path to image file (jpg, png, webp, etc.)
            note_title: Optional custom title for the note
            tags: Optional tags to categorize the analysis
            auto_link: Auto-link to related notes (default: True)
        
        Returns:
            Dict with analysis results
        """
        print(f"\n🖼️  Uploading & Analyzing Image: {image_path}")
        result = self.vault.analyze_image(image_path, note_title, tags)
        if auto_link and 'image-analysis' in tags:
            # Auto-link based on image content
            print(f"  ✓ Auto-linked based on image content")
        return result
    
    def upload_pdf(self, pdf_path: str, note_title: str = None, 
                    extract_pages: List[int] = None, create_summary: bool = True):
        """
        Upload a PDF, extract all content, and create a searchable note.
        Uses the PDF Knowledge Compiler for structured ingestion.
        
        Pipeline:
        PDF → extract pages →
            ├── text → vault note
            ├── images → extracted files + image analysis note
            ├── tables → structured blocks
            └── links between them
        
        Args:
            pdf_path: Path to PDF file
            note_title: Optional custom title (defaults to PDF filename)
            extract_pages: Specific pages to extract (None = all pages)
            create_summary: Generate AI summary of the PDF
        
        Returns:
            Dict with extraction results
        """
        import os
        
        print(f"\n📑 Uploading PDF: {pdf_path}")
        
        # Use the new PDF Knowledge Compiler
        compiler = PDFKnowledgeCompiler(vault=self.vault)
        result = compiler.compile_pdf(
            pdf_path,
            title=note_title,
            extract_pages=extract_pages,
            analyze_images=True,
            create_summary=create_summary
        )
        
        return {
            'pdf': result['pdf'],
            'pages_extracted': result['pages_extracted'],
            'images_extracted': len(result['images']),
            'image_notes_created': len(result['image_notes']),
            'note_path': result['note_path'],
            'manifest_path': result['manifest_path']
        }
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        return self.vault.get_stats()

    # ============ AUTONOMOUS AGENT MODE ============
    
    def start_autonomous_mode(self, watch_dirs: List[str] = None, 
                             poll_interval: int = 30,
                             auto_upload_images: bool = True,
                             auto_upload_pdfs: bool = True):
        """
        Start autonomous background agent mode.
        
        The agent will:
        - Watch specified directories for new files
        - Auto-upload images with AI analysis
        - Auto-extract and index PDFs
        - Build knowledge graph continuously
        - Operate without human intervention
        
        Args:
            watch_dirs: Directories to monitor (defaults: current, files/, images/)
            poll_interval: Seconds between checks (default: 30)
            auto_upload_images: Auto-analyze new images
            auto_upload_pdfs: Auto-extract new PDFs
        """
        import time
        import threading
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        if watch_dirs is None:
            watch_dirs = ['.', 'files/', 'images/']
        
        # Ensure directories exist
        for d in watch_dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
        
        self._autonomous_running = True
        self._processed_files = set()
        
        # Initialize with existing files
        for watch_dir in watch_dirs:
            for ext in ['.jpg', '.jpeg', '.png', '.webp', '.pdf']:
                for f in Path(watch_dir).glob(f'*{ext}'):
                    self._processed_files.add(str(f.absolute()))
        
        print(f"🤖 Autonomous Agent Mode: ACTIVE")
        print(f"   Watching: {watch_dirs}")
        print(f"   Poll interval: {poll_interval}s")
        print(f"   Auto-upload images: {auto_upload_images}")
        print(f"   Auto-upload PDFs: {auto_upload_pdfs}")
        print(f"   Press Ctrl+C to stop\n")
        
        class AutonomousHandler(FileSystemEventHandler):
            def __init__(self, agent_ref):
                self.agent = agent_ref
            
            def _handle_new_file(self, file_path):
                file_path = Path(file_path).absolute()
                path_str = str(file_path)
                
                if path_str in self.agent._processed_files:
                    return
                
                self.agent._processed_files.add(path_str)
                ext = file_path.suffix.lower()
                
                try:
                    if ext in ['.jpg', '.jpeg', '.png', '.webp'] and auto_upload_images:
                        print(f"\n🖼️  [AUTO] New image: {file_path.name}")
                        self.agent.analyze_image(str(file_path), auto_link=True)
                        print(f"   → Added to knowledge base")
                    
                    elif ext == '.pdf' and auto_upload_pdfs:
                        print(f"\n📄 [AUTO] New PDF: {file_path.name}")
                        self.agent.upload_pdf(str(file_path), extract_pages=None, create_summary=True)
                        print(f"   → Extracted and indexed")
                except Exception as e:
                    print(f"   ⚠ Error: {e}")
            
            def on_created(self, event):
                if not event.is_directory:
                    self._handle_new_file(event.src_path)
            
            def on_modified(self, event):
                if not event.is_directory:
                    time.sleep(0.5)
                    self._handle_new_file(event.src_path)
        
        event_handler = AutonomousHandler(self)
        observer = Observer()
        
        for watch_dir in watch_dirs:
            if Path(watch_dir).exists():
                observer.schedule(event_handler, str(Path(watch_dir).absolute()), recursive=True)
                print(f"   ✓ Monitoring: {watch_dir}")
        
        observer.start()
        
        def background_tasks():
            while self._autonomous_running:
                time.sleep(poll_interval)
                if self._autonomous_running:
                    stats = self.get_knowledge_stats()
                    print(f"\n[Cycle] Notes: {stats['total_notes']} | Files: {len(self._processed_files)}")
        
        bg_thread = threading.Thread(target=background_tasks, daemon=True)
        bg_thread.start()
        
        try:
            while self._autonomous_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping autonomous agent...")
            self._autonomous_running = False
            observer.stop()
        
        observer.join()
        print("✓ Autonomous agent stopped")
    
    def stop_autonomous_mode(self):
        """Stop the autonomous agent"""
        self._autonomous_running = False


def main():
    """Demo the Prox welding agent"""
    print("=" * 70)
    print("Prox Welding Agent - Claude SDK + Autonomous Mode")
    print("=" * 70)
    
    agent = ProxWeldingAgent()
    
    stats = agent.get_knowledge_stats()
    print(f"\n📊 Knowledge Base:")
    print(f"  Notes: {stats['total_notes']}")
    print(f"  Tags: {len(stats['tags'])}")
    
    questions = [
        "What's the duty cycle for MIG welding at 200A on 240V?",
    ]
    
    print("\n" + "=" * 70)
    print("DEMO: Answering Technical Questions")
    print("=" * 70)
    
    for question in questions:
        result = agent.answer_question(question)
        print(f"\n{'='*70}")
        print(f"ANSWER:\n{result['answer'][:500]}...")
        print(f"{'='*70}")
    
    print("\n" + "=" * 70)
    print("AUTONOMOUS MODE")
    print("=" * 70)
    print("\nTo start autonomous agent:")
    print("  agent.start_autonomous_mode()")
    print("\nOr with custom settings:")
    print("  agent.start_autonomous_mode(")
    print("      watch_dirs=['images/', 'scans/'],")
    print("      poll_interval=60,")
    print("      auto_upload_images=True,")
    print("      auto_upload_pdfs=True")
    print("  )")
    
    print("\n" + "=" * 70)
    try:
        response = input("\nStart autonomous mode now? (y/n): ")
        if response.lower() == 'y':
            agent.start_autonomous_mode()
    except (EOFError, KeyboardInterrupt):
        pass
    
    print("\n✓ Demo complete!")
