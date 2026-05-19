#!/usr/bin/env python3
"""
PDF → Autonomous Knowledge Compiler

This is the core pipeline that transforms PDFs into structured knowledge:

PDF → extract pages →
    ├── text → vault note
    ├── images → extracted files + image analysis note
    ├── tables → structured blocks
    └── links between them

The result is a true engineering knowledge graph, not just markdown.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import the two layers
from pdf_image_extractor import extract_pdf_images, extract_pdf_structure, extract_text_blocks
from pdf_utils import extract_page_content, get_pdf_info, extract_all_tables


class PDFKnowledgeCompiler:
    """
    Compiles PDFs into structured knowledge for the vault.
    
    Each PDF becomes:
    - A main note with text content
    - Individual image notes with AI analysis
    - Table extraction notes
    - A JSON manifest for the knowledge graph
    """
    
    def __init__(self, vault=None, image_output_dir: str = "extracted_images"):
        """
        Initialize the compiler.
        
        Args:
            vault: ObsidianVault instance for writing notes
            image_output_dir: Directory to store extracted images
        """
        self.vault = vault
        self.image_output_dir = Path(image_output_dir)
        self.image_output_dir.mkdir(parents=True, exist_ok=True)
        
    def compile_pdf(
        self,
        pdf_path: str,
        title: str = None,
        extract_pages: List[int] = None,
        analyze_images: bool = True,
        create_summary: bool = True
    ) -> Dict[str, Any]:
        """
        Full pipeline: PDF → structured knowledge.
        
        Args:
            pdf_path: Path to PDF file
            title: Optional title (defaults to PDF filename)
            extract_pages: Specific pages to extract (None = all)
            analyze_images: Whether to run AI analysis on extracted images
            create_summary: Whether to generate AI summary
            
        Returns:
            Compilation results with all extracted data
        """
        print(f"\n[Compiling PDF] {pdf_path}")
        
        # Get PDF info
        info = get_pdf_info(pdf_path)
        print(f"  Pages: {info['total_pages']}, Size: {info['file_size']} bytes")
        
        # Extract structure
        structure = extract_pdf_structure(pdf_path)
        print(f"  Structure: {structure['total_pages']} pages, TOC: {structure['has_toc']}")
        
        # Create title
        if title is None:
            title = Path(pdf_path).stem.replace('-', ' ').replace('_', ' ').title()
        
        # Extract images first (before text, as they're independent)
        image_dir = self.image_output_dir / title.replace(' ', '_')
        images = extract_pdf_images(pdf_path, str(image_dir), prefix=title.replace(' ', '_'))
        print(f"  [OK] Extracted {len(images)} images")
        
        # Analyze images if requested
        image_notes = []
        if analyze_images and self.vault and images:
            for img in images:
                try:
                    result = self.vault.analyze_image(
                        img["path"],
                        note_title=f"PDF Image - {title} - Page {img['page'] + 1}"
                    )
                    if result:
                        image_notes.append({
                            "image": img,
                            "analysis": result
                        })
                except Exception as e:
                    print(f"  [WARN] Image analysis failed: {e}")
        
        # Extract text and tables from pages
        pages_data = []
        page_range = extract_pages if extract_pages else range(info['total_pages'])
        
        for page_num in page_range:
            try:
                page_data = extract_page_content(pdf_path, page_num)
                if page_data:
                    pages_data.append(page_data)
                    print(f"  [OK] Extracted page {page_num + 1}/{info['total_pages']}")
            except Exception as e:
                print(f"  [WARN] Page {page_num + 1} error: {e}")
        
        # Extract all tables
        tables_data = extract_all_tables(pdf_path)
        print(f"  [OK] Found {len(tables_data)} pages with tables")
        
        # Create the main note
        main_note = self._create_main_note(title, info, pages_data, images, tables_data)
        
        # Write to vault if available
        note_path = None
        if self.vault:
            note_path = self.vault.write_note(
                title=title,
                content=main_note,
                tags=['pdf', 'compiled', 'knowledge-graph']
            )
            print(f"  [OK] Created note: {note_path.name}")
        
        # Create JSON manifest for knowledge graph
        manifest = self._create_manifest(
            title=title,
            pdf_path=pdf_path,
            info=info,
            structure=structure,
            images=images,
            pages_data=pages_data,
            tables_data=tables_data,
            image_notes=image_notes
        )
        
        # Save manifest
        manifest_path = self.image_output_dir / f"{title.replace(' ', '_')}_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"  [OK] Created manifest: {manifest_path.name}")
        
        return {
            'title': title,
            'pdf': info,
            'structure': structure,
            'images': images,
            'image_notes': image_notes,
            'pages_extracted': len(pages_data),
            'tables_found': len(tables_data),
            'note_path': str(note_path) if note_path else None,
            'manifest_path': str(manifest_path)
        }
    
    def _create_main_note(
        self,
        title: str,
        info: Dict,
        pages_data: List[Dict],
        images: List[Dict],
        tables_data: List[Dict]
    ) -> str:
        """Create the main note content."""
        content_parts = [
            f"# {title}",
            "",
            f"**Source:** `{Path(info.get('filename', 'unknown')).name}`",
            f"**Pages:** {info['total_pages']}",
            f"**File Size:** {info['file_size']} bytes",
            f"**Compiled:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Images Extracted:** {len(images)}",
            "",
            "---",
            ""
        ]
        
        # Add page content
        for page in pages_data:
            page_num = page.get('page_number', 0) + 1
            content_parts.append(f"## Page {page_num}")
            
            if page.get('text'):
                # Truncate long text
                text = page['text']
                if len(text) > 1500:
                    text = text[:1500] + "..."
                content_parts.append(f"\n{text}\n")
            
            if page.get('tables'):
                content_parts.append(f"\n**Tables:** {len(page['tables'])} found\n")
            
            if page.get('image_analysis'):
                caption = page['image_analysis'].get('general_caption', 'N/A')
                content_parts.append(f"\n**Image Analysis:** {caption}\n")
            
            content_parts.append("\n---\n")
        
        # Add image references
        if images:
            content_parts.append("## Extracted Images")
            content_parts.append("")
            for img in images:
                content_parts.append(f"- ![[{img['filename']}|200]] (Page {img['page'] + 1})")
            content_parts.append("")
        
        return "\n".join(content_parts)
    
    def _create_manifest(
        self,
        title: str,
        pdf_path: str,
        info: Dict,
        structure: Dict,
        images: List[Dict],
        pages_data: List[Dict],
        tables_data: List[Dict],
        image_notes: List[Dict]
    ) -> Dict[str, Any]:
        """Create the JSON manifest for the knowledge graph."""
        return {
            "title": title,
            "pdf": {
                "path": pdf_path,
                "filename": info.get('filename', 'unknown'),
                "total_pages": info['total_pages'],
                "file_size": info['file_size']
            },
            "structure": {
                "total_pages": structure['total_pages'],
                "has_toc": structure['has_toc'],
                "page_sizes": structure['page_sizes']
            },
            "pages": [
                {
                    "page_number": p.get('page_number', 0),
                    "text_length": len(p.get('text', '')),
                    "has_tables": len(p.get('tables', [])) > 0,
                    "has_image_analysis": 'image_analysis' in p
                }
                for p in pages_data
            ],
            "images": [
                {
                    "page": img['page'],
                    "filename": img['filename'],
                    "dimensions": f"{img['width']}x{img['height']}",
                    "ext": img['ext']
                }
                for img in images
            ],
            "tables": [
                {
                    "page": t['page_number'],
                    "table_count": len(t.get('tables', []))
                }
                for t in tables_data
            ],
            "image_notes": len(image_notes),
            "compiled_at": datetime.now().isoformat()
        }


def compile_pdf_to_knowledge(
    pdf_path: str,
    vault=None,
    title: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to compile a PDF to knowledge.
    
    Args:
        pdf_path: Path to PDF file
        vault: ObsidianVault instance
        title: Optional title
        **kwargs: Additional arguments for compiler
        
    Returns:
        Compilation results
    """
    compiler = PDFKnowledgeCompiler(vault=vault)
    return compiler.compile_pdf(pdf_path, title=title, **kwargs)


if __name__ == "__main__":
    # Example usage
    from agent import get_vault
    
    vault = get_vault()
    compiler = PDFKnowledgeCompiler(vault=vault)
    
    # Compile the owner manual
    result = compiler.compile_pdf(
        "files/owner-manual.pdf",
        title="Owner Manual",
        analyze_images=True
    )
    
    print(f"\n[OK] Compilation complete!")
    print(f"  Pages: {result['pages_extracted']}")
    print(f"  Images: {len(result['images'])}")
    print(f"  Image notes: {len(result['image_notes'])}")