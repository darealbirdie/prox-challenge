#!/usr/bin/env python3
"""
Prox Welding Agent - Claude Code Integration (Multimodal)
Bidirectional knowledge system for Claude to read/write/evolve Obsidian vault.
Supports text, PDF, and image analysis with BLIP multimodal AI.

Usage with Claude Code:
    from agent import get_vault, analyze_image
    vault = get_vault()  # Uses VAULT_PATH env var or defaults to 'bidirectional prox'
    results = vault.search('MIG aluminum setup')
    vault.write_note('Insight', content, tags=['insight'])
    analyze_image('product.webp', vault=vault)
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PDF extraction tools
from pdf_utils import (
    extract_page_content,
    extract_all_tables,
    search_pdfs_for_tables,
    get_pdf_info,
    analyze_standalone_image
)

# Optional: Vector search for RAG
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import faiss
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False


class ObsidianVault:
    """Obsidian vault manager for Claude Code - bidirectional knowledge"""
    
    def __init__(self, vault_path: str = None):
        """
        Connect to existing Obsidian vault.
        
        Args:
            vault_path: Path to Obsidian vault (defaults to VAULT_PATH env var or 'bidirectional prox')
        """
        # Get vault path from environment variable or use default
        if vault_path is None:
            vault_path = os.getenv('VAULT_PATH', 'bidirectional prox')
        
        self.vault_path = Path(vault_path).resolve()
        
        if not self.vault_path.exists():
            raise FileNotFoundError(
                f"Vault not found: {self.vault_path}\n"
                "Set VAULT_PATH environment variable or ensure vault exists at this path."
            )
        
        self.notes_dir = self.vault_path
        self.documents = []
        self.knowledge_graph = {}
        
        # Embedding model for semantic search (optional)
        self.embedding_model = None
        self.document_index = None
        
        if VECTOR_SEARCH_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception:
                pass
        
        # Load vault
        self._load_vault_notes()
        self._build_knowledge_graph()
        
        if self.embedding_model and self.documents:
            self._build_vector_index()
    
    def _load_vault_notes(self):
        """Load all markdown notes from vault into memory"""
        for md_file in self.notes_dir.glob("*.md"):
            try:
                content = md_file.read_text()
                note = self._parse_markdown_note(content)
                note['filename'] = md_file.name
                note['filepath'] = md_file
                note['last_modified'] = md_file.stat().st_mtime
                self.documents.append(note)
            except Exception:
                pass
        
        self.documents.sort(key=lambda x: x.get('last_modified', 0), reverse=True)
    
    def _parse_markdown_note(self, content: str) -> Dict[str, Any]:
        """Parse Obsidian markdown note"""
        note = {
            'content': content,
            'frontmatter': {},
            'body': content,
            'tags': [],
            'links': [],
            'backlinks': [],
            'references': {}
        }
        
        # Frontmatter
        fm_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            note['body'] = fm_match.group(2)
            for line in fm_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    note['frontmatter'][key.strip()] = value.strip()
        
        # Tags
        note['tags'] = re.findall(r'#([\w/-]+)', content)
        
        # Wiki links
        note['links'] = re.findall(r'\[\[([^\]]+)\]\]', content)
        
        return note
    
    def _build_knowledge_graph(self):
        """Build bidirectional link graph"""
        title_index = {}
        for doc in self.documents:
            title_match = re.search(r'^#\s+(.+)$', doc['body'], re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
                title_index[title.lower()] = doc
            stem = doc['filename'].replace('.md', '').lower()
            title_index[stem] = doc
        
        # Build backlinks
        for doc in self.documents:
            doc_title = None
            title_match = re.search(r'^#\s+(.+)$', doc['body'], re.MULTILINE)
            if title_match:
                doc_title = title_match.group(1).strip()
            
            for link in doc.get('links', []):
                linked_doc = title_index.get(link.lower().strip())
                if linked_doc and doc_title:
                    linked_doc.setdefault('backlinks', []).append(doc_title)
    
    def _build_vector_index(self):
        """Build FAISS index for semantic search"""
        if not self.documents or not self.embedding_model:
            return
        
        texts = []
        self.text_to_note = []
        
        for doc in self.documents:
            body = doc['body']
            sections = re.split(r'\n##+\s+', body)
            for section in sections:
                section = section.strip()
                if len(section) > 50:
                    texts.append(section[:1000])
                    self.text_to_note.append(doc)
        
        if not texts:
            return
        
        embeddings = self.embedding_model.encode(texts)
        faiss.normalize_L2(embeddings)
        
        dimension = embeddings.shape[1]
        self.document_index = faiss.IndexFlatIP(dimension)
        self.document_index.add(embeddings.astype('float32'))
    
    # ============ CLAUDE TOOLS: READ ============
    
    def read_note(self, title: str) -> Optional[Dict[str, Any]]:
        """Read a note from vault"""
        for doc in self.documents:
            title_match = re.search(r'^#\s+(.+)$', doc['body'], re.MULTILINE)
            if title_match and title_match.group(1).strip() == title:
                return doc
        return None
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search vault using semantic + keyword search"""
        results = []
        
        # Semantic search
        if self.document_index and self.embedding_model:
            query_emb = self.embedding_model.encode([query])
            faiss.normalize_L2(query_emb)
            scores, indices = self.document_index.search(query_emb.astype('float32'), min(k*2, 10))
            
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.text_to_note) and score > 0.15:
                    doc = self.text_to_note[idx].copy()
                    doc['similarity'] = float(score)
                    doc['excerpt'] = self._extract_chunk(doc, query)
                    results.append(doc)
        
        # Keyword fallback
        if not results:
            results = self._keyword_search(query, k)
        
        # Deduplicate
        seen = set()
        unique = []
        for r in results:
            fn = r.get('filename', '')
            if fn and fn not in seen:
                seen.add(fn)
                unique.append(r)
        
        return unique[:k]
    
    def _extract_chunk(self, doc: Dict, query: str) -> str:
        """Extract relevant text chunk"""
        body = doc.get('body', '')
        qwords = query.lower().split()
        
        for para in re.split(r'\n\n', body):
            if any(w in para.lower() for w in qwords):
                return para.strip()
        
        return body[:300]
    
    def _keyword_search(self, query: str, k: int) -> List[Dict]:
        """Keyword search fallback"""
        qwords = query.lower().split()
        scored = []
        
        for doc in self.documents:
            score = 0
            body = doc.get('body', '').lower()
            
            for word in qwords:
                score += body.count(word) * 2
            
            for tag in doc.get('tags', []):
                if tag.lower() in query.lower():
                    score += 5
            
            title_match = re.search(r'^#\s+(.+)$', doc['body'], re.MULTILINE)
            if title_match:
                title = title_match.group(1).lower()
                if any(w in title for w in qwords):
                    score += 10
            
            if score > 0:
                scored.append((score, doc))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:k]]
    
    def query_pdf(self, question: str) -> List[Dict[str, Any]]:
        """Extract direct evidence from PDFs"""
        evidence = []
        q = question.lower()
        
        # Get files directory from environment variable or use default
        files_dir = os.getenv('FILES_DIR', 'files')
        
        pdfs = {
            'owner-manual': os.path.join(files_dir, 'owner-manual.pdf'),
            'quick-start': os.path.join(files_dir, 'quick-start-guide.pdf'),
            'selection': os.path.join(files_dir, 'selection-chart.pdf')
        }
        
        # Determine relevant PDFs
        relevant = []
        if any(w in q for w in ['duty', 'mig', '200a', 'cycle']):
            relevant = ['owner-manual']
        elif any(w in q for w in ['shock', 'safety', 'ground']):
            relevant = ['owner-manual']
        elif any(w in q for w in ['aluminum', 'tig', 'spool']):
            relevant = ['owner-manual', 'selection']
        elif any(w in q for w in ['setup', 'load', 'wire']):
            relevant = ['quick-start']
        elif any(w in q for w in ['select', 'choose', 'process']):
            relevant = ['selection']
        else:
            relevant = ['owner-manual', 'quick-start']
        
        for key in relevant[:2]:
            pdf_path = pdfs[key]
            if not os.path.exists(pdf_path):
                continue
            
            try:
                info = get_pdf_info(pdf_path)
                # Search more pages - duty cycle is on page 7, 29+
                # Also search pages that are likely to contain technical specs
                pages_to_search = set()
                # Always check first few pages
                for i in range(min(5, info['total_pages'])):
                    pages_to_search.add(i)
                # For duty/cycle/mig queries, also check pages 6-10 and 28-35
                if any(w in q for w in ['duty', 'cycle', 'mig', '200a', 'specification', 'spec']):
                    for i in range(6, min(11, info['total_pages'])):
                        pages_to_search.add(i)
                    for i in range(28, min(36, info['total_pages'])):
                        pages_to_search.add(i)
                
                for page_num in sorted(pages_to_search):
                    content = extract_page_content(pdf_path, page_num)
                    if content:
                        text_lower = content['text'].lower()
                        if any(w in text_lower for w in q.split()):
                            evidence.append({
                                'type': 'pdf',
                                'source': f"{key}.pdf",
                                'page': page_num + 1,
                                'text': content['text'][:500],
                                'excerpt': content['text'][:300]
                            })
            except Exception:
                pass
        
        return evidence
    
    # ============ CLAUDE TOOLS: WRITE ============
    
    def write_note(self, title: str, content: str, 
                   tags: List[str] = None, 
                   links: List[str] = None,
                   append: bool = False) -> Path:
        """Create or update a note in vault"""
        filename = self._title_to_filename(title)
        filepath = self.notes_dir / filename
        
        frontmatter = {
            'created': datetime.now().isoformat(),
            'agent': 'claude',
            'last_sync': datetime.now().isoformat(),
            'tags': tags or [],
            'type': 'generated'
        }
        
        fm_lines = [f"{k}: {v}" if not isinstance(v, list) else f"{k}: {v}" 
                    for k, v in frontmatter.items()]
        fm_block = "---\n" + "\n".join(fm_lines) + "\n---\n"
        
        full_content = f"{fm_block}\n# {title}\n\n{content}"
        
        if links:
            full_content += "\n\n## Related\n"
            for link in links:
                full_content += f"- [[{link}]]\n"
        
        if filepath.exists() and append:
            existing = filepath.read_text()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            addition = f"\n\n## Update - {timestamp}\n\n{content}"
            filepath.write_text(existing + addition)
            print(f"  [Updated] {filepath.name}")
        else:
            filepath.write_text(full_content)
            print(f"  [Created] {filepath.name}")
        
        # Reload vault
        self._load_vault_notes()
        self._build_knowledge_graph()
        if self.embedding_model:
            self._build_vector_index()
        
        return filepath
    
    def _title_to_filename(self, title: str) -> str:
        """Convert title to filename"""
        filename = re.sub(r'[^\w\s-]', '', title.lower())
        filename = re.sub(r'[-\s]+', '_', filename)
        return f"{filename.strip('_')}.md"
    
    def enrich_note(self, note_title: str, pdf_path: str, pages: List[int] = None):
        """Enrich note with PDF extraction"""
        note = self.read_note(note_title)
        if not note:
            print(f"  [Error] Note not found: {note_title}")
            return
        
        filepath = note['filepath']
        existing = filepath.read_text()
        
        enrichment = f"\n\n## Source Evidence ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        enrichment += f"**Source:** {Path(pdf_path).name}\n\n"
        
        if pages:
            for page_num in pages:
                try:
                    content = extract_page_content(pdf_path, page_num)
                    if content:
                        enrichment += f"### Page {page_num + 1}\n\n"
                        enrichment += f"{content['text'][:500]}...\n\n"
                except Exception:
                    pass
        
        filepath.write_text(existing + enrichment)
        
        self._load_vault_notes()
        self._build_knowledge_graph()
        if self.embedding_model:
            self._build_vector_index()
        
        print(f"  [Enriched] {note_title}")
    
    def link_notes(self, note1: str, note2: str, relation: str = "related"):
        """Create bidirectional link between notes"""
        n1 = self.read_note(note1)
        n2 = self.read_note(note2)
        
        if not n1 or not n2:
            print(f"  [Error] Note(s) not found")
            return
        
        # Update note1
        p1 = n1['filepath']
        c1 = p1.read_text()
        if "## Related" in c1:
            if f"[[{note2}]]" not in c1:
                c1 = c1.replace("## Related", f"## Related\n- [[{note2}]]")
        else:
            c1 += f"\n## Related\n- [[{note2}]]\n"
        p1.write_text(c1)
        
        # Update note2
        p2 = n2['filepath']
        c2 = p2.read_text()
        if "## Related" in c2:
            if f"[[{note1}]]" not in c2:
                c2 = c2.replace("## Related", f"## Related\n- [[{note1}]]")
        else:
            c2 += f"\n## Related\n- [[{note1}]]\n"
        p2.write_text(c2)
        
        self._load_vault_notes()
        self._build_knowledge_graph()
        if self.embedding_model:
            self._build_vector_index()
        
        print(f"  [Linked] {note1} <-> {note2}")
    
    # ============ CLAUDE TOOLS: MULTIMODAL ============
    
    def analyze_image(self, image_path: str, note_title: str = None, tags: List[str] = None):
        """
        Analyze image with multimodal AI and add to vault.
        
        Claude uses this to extract knowledge from images.
        
        Args:
            image_path: Path to image file
            note_title: Optional note title (auto-generated if None)
            tags: Optional tags
        """
        print(f"  Analyzing image: {image_path}")
        
        result = analyze_standalone_image(image_path)
        
        if "error" in result:
            print(f"  [Error] Analysis failed: {result['error']}")
            return
        
        img_name = Path(image_path).stem
        title = note_title or f"Image: {img_name.replace('-', ' ').title()}"
        
        content_parts = [
            f"**Source:** `{Path(image_path).name}`",
            f"**Dimensions:** {result.get('dimensions', 'N/A')}",
            f"**Format:** {result.get('format', 'N/A')}",
            "",
            "## AI Analysis",
            "",
            f"**Caption:** {result.get('general_caption', 'N/A')}",
            "",
            f"**Description:** {result.get('detailed_description', 'N/A')}",
            "",
            "## Specific Analysis"
        ]
        
        for prompt, answer in result.get('specific_analysis', {}).items():
            content_parts.append(f"\n**{prompt}**\n\n> {answer}")
        
        # Auto-link based on content
        auto_links = []
        caption = result.get('general_caption', '').lower()
        if 'welding' in caption:
            auto_links = ['Safety Warnings and Symbols']
        elif 'machine' in caption or 'equipment' in caption:
            auto_links = ['Controls and Interior Components']
        
        all_links = (auto_links or []) + (tags or [])
        
        self.write_note(
            title=title,
            content="\n".join(content_parts),
            tags=['image-analysis', 'ai-generated'] + (tags or []),
            links=auto_links
        )
    
    def analyze_image_and_link(self, image_path: str, link_to: List[str]):
        """Analyze image and link to existing notes"""
        self.analyze_image(image_path)
        
        # Get the note we just created (most recent)
        img_notes = [d for d in self.documents if 'image-analysis' in d.get('tags', [])]
        if img_notes:
            img_title_match = re.search(r'^#\s+(.+)$', img_notes[0]['body'], re.MULTILINE)
            if img_title_match:
                img_title = img_title_match.group(1).strip()
                for target in link_to:
                    self.link_notes(img_title, target)
    
    # ============ CLAUDE TOOLS: UTILITY ============
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vault statistics"""
        stats = {
            'total_notes': len(self.documents),
            'tags': {},
            'recent': []
        }
        
        for doc in self.documents:
            for tag in doc.get('tags', []):
                stats['tags'][tag] = stats['tags'].get(tag, 0) + 1
        
        recent = sorted(self.documents, 
                       key=lambda x: x.get('last_modified', 0), 
                       reverse=True)[:5]
        stats['recent'] = [d['filename'] for d in recent]
        
        return stats
    
    def export_graph(self, output: str = "knowledge_graph.json"):
        """Export knowledge graph"""
        graph = {
            'nodes': [],
            'edges': [],
            'metadata': {
                'vault': str(self.vault_path),
                'generated': datetime.now().isoformat(),
                'total_notes': len(self.documents)
            }
        }
        
        title_index = {}
        for doc in self.documents:
            title_match = re.search(r'^#\s+(.+)$', doc['body'], re.MULTILINE)
            title = title_match.group(1).strip() if title_match else doc['filename']
            title_index[title.lower()] = title
            
            graph['nodes'].append({
                'id': title,
                'filename': doc['filename'],
                'tags': doc.get('tags', [])
            })
        
        for node in graph['nodes']:
            doc = next(d for d in self.documents if d['filename'] == node['filename'])
            for link in doc.get('links', []):
                graph['edges'].append({
                    'source': node['id'],
                    'target': link,
                    'type': 'wiki_link'
                })
        
        Path(output).write_text(json.dumps(graph, indent=2))
        print(f"  → Exported: {output}")
        return graph


# ============ CLAUDE INTERFACE ============

def get_vault(vault_path: str = "bidirectional prox") -> ObsidianVault:
    """Get connected vault instance"""
    return ObsidianVault(vault_path)


def search_knowledge(query: str, vault_path: str = "bidirectional prox", k: int = 5):
    """Quick search of vault knowledge"""
    vault = ObsidianVault(vault_path)
    return vault.search(query, k)


def extract_pdf_evidence(question: str, vault_path: str = "bidirectional prox"):
    """Extract evidence from PDFs"""
    vault = ObsidianVault(vault_path)
    return vault.query_pdf(question)


def analyze_image(image_path: str, note_title: str = None, vault_path: str = "bidirectional prox", tags: List[str] = None):
    """
    Analyze image with multimodal AI.
    
    This is the key multimodal function for Claude!
    
    Args:
        image_path: Path to image file
        note_title: Optional note title
        vault_path: Path to vault
        tags: Optional tags
    """
    vault = ObsidianVault(vault_path)
    vault.analyze_image(image_path, note_title, tags)
    return vault


if __name__ == "__main__":
    print("Prox Welding Agent - Claude Code Integration (Multimodal)")
    print("="*60)
    
    vault = ObsidianVault("bidirectional prox")
    stats = vault.get_stats()
    
    print(f"\n📚 Vault: {stats['total_notes']} notes")
    print(f"🏷️  Tags: {len(stats['tags'])} categories")
    print(f"\nRecent notes:")
    for note in stats['recent'][:5]:
        print(f"  • {note}")
    
    print("\n✅ Ready for Claude Code integration!")
    print("\nMultimodal capabilities:")
    print("  ✓ Text search & retrieval")
    print("  ✓ PDF extraction")
    print("  ✓ Image analysis (BLIP AI)")
    print("  ✓ Knowledge graph")
    print("  ✓ Bidirectional links")
