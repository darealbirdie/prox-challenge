#!/usr/bin/env python3
"""
PDF Image Extractor - Raw media extraction layer
Extracts images from PDFs using PyMuPDF (fitz) for the knowledge compiler pipeline.

This is a separate layer from pdf_utils.py:
- pdf_utils = text + OCR + multimodal analysis
- pdf_image_extractor = raw media extraction (images, vectors, structure)
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Optional
import os


def extract_pdf_images(
    pdf_path: str,
    output_dir: str = "extracted_images",
    prefix: str = ""
) -> List[Dict[str, Any]]:
    """
    Extract all embedded images from a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save extracted images
        prefix: Optional prefix for image filenames
        
    Returns:
        List of image metadata dictionaries with:
        - page: 0-indexed page number
        - path: Full path to extracted image
        - filename: Image filename
        - ext: Image extension (png, jpg, etc.)
        - width, height: Image dimensions
        - xref: PDF cross-reference number
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extracted_images = []
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_index in range(len(doc)):
            page = doc[page_index]
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    image_width = base_image.get("width", 0)
                    image_height = base_image.get("height", 0)
                    
                    # Create filename with prefix if provided
                    base_name = Path(pdf_path).stem
                    if prefix:
                        filename = f"{prefix}_page_{page_index}_img_{img_index}.{image_ext}"
                    else:
                        filename = f"{base_name}_page_{page_index}_img_{img_index}.{image_ext}"
                    
                    image_path = output_dir / filename
                    
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)
                    
                    extracted_images.append({
                        "page": page_index,
                        "path": str(image_path),
                        "filename": filename,
                        "ext": image_ext,
                        "width": image_width,
                        "height": image_height,
                        "xref": xref,
                        "pdf": os.path.basename(pdf_path)
                    })
                    
                except Exception as e:
                    print(f"Warning: Failed to extract image {img_index} from page {page_index}: {e}")
                    continue
        
        doc.close()
        return extracted_images
        
    except Exception as e:
        print(f"PDF image extraction failed: {e}")
        return []


def extract_pdf_structure(pdf_path: str) -> Dict[str, Any]:
    """
    Extract structural information from a PDF.
    
    Returns:
        Dictionary with:
        - total_pages: Number of pages
        - page_sizes: List of page dimensions
        - has_toc: Whether PDF has table of contents
        - metadata: PDF metadata
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    try:
        doc = fitz.open(pdf_path)
        
        page_sizes = []
        for page in doc:
            rect = page.rect
            page_sizes.append({
                "width": rect.width,
                "height": rect.height
            })
        
        # Get table of contents
        toc = doc.get_toc()
        
        result = {
            "total_pages": len(doc),
            "page_sizes": page_sizes,
            "has_toc": len(toc) > 0,
            "toc": toc[:20] if toc else [],  # First 20 entries
            "metadata": dict(doc.metadata) if doc.metadata else {}
        }
        
        doc.close()
        return result
        
    except Exception as e:
        print(f"PDF structure extraction failed: {e}")
        return {
            "total_pages": 0,
            "page_sizes": [],
            "has_toc": False,
            "toc": [],
            "metadata": {}
        }


def extract_text_blocks(pdf_path: str, page_number: int = 0) -> List[Dict[str, Any]]:
    """
    Extract text blocks with positioning information from a PDF page.
    
    Args:
        pdf_path: Path to PDF file
        page_number: 0-indexed page number
        
    Returns:
        List of text blocks with position and content
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    try:
        doc = fitz.open(pdf_path)
        if page_number >= len(doc):
            return []
        
        page = doc[page_number]
        blocks = page.get_text("dict")["blocks"]
        
        text_blocks = []
        for block in blocks:
            if block["type"] == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text_blocks.append({
                            "text": span["text"],
                            "bbox": span["bbox"],  # [x0, y0, x1, y1]
                            "font": span.get("font", ""),
                            "size": span.get("size", 0),
                            "page": page_number
                        })
        
        doc.close()
        return text_blocks
        
    except Exception as e:
        print(f"Text block extraction failed: {e}")
        return []


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = "files/owner-manual.pdf"
    
    print(f"Extracting images from: {pdf_path}")
    images = extract_pdf_images(pdf_path, output_dir="extracted_images")
    print(f"Extracted {len(images)} images")
    
    for img in images[:5]:
        print(f"  - {img['filename']} (page {img['page']}, {img['width']}x{img['height']})")