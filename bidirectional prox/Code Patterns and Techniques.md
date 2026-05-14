# Code Patterns & Techniques

## PDF Extraction Patterns

### Basic Page Extraction

```python
from pdf_utils import extract_page_content

# Extract content from specific page
content = extract_page_content("files/owner-manual.pdf", page_number=5)

# Access extracted data
text = content["text"]
tables = content["tables"]
page_num = content["page_number"]
total_pages = content["total_pages"]

print(f"Page {page_num + 1} of {total_pages}")
print(f"Text length: {len(text)} characters")
print(f"Tables found: {len(tables)}")
```

**Pattern:** Extract → Validate → Process

---

### Batch Table Extraction

```python
from pdf_utils import extract_all_tables

# Extract all tables from PDF
all_tables = extract_all_tables("files/owner-manual.pdf")

# Process each page with tables
for page_info in all_tables:
    page_num = page_info["page_number"] + 1  # Convert to 1-indexed
    tables = page_info["tables"]
    
    print(f"\nPage {page_num}: {len(tables)} tables")
    
    for i, table in enumerate(tables):
        print(f"\n  Table {i+1} ({len(table)} rows):")
        for row in table[:5]:  # Show first 5 rows
            print(f"    {row}")
```

**Pattern:** Batch → Iterate → Process

---

### Directory-Wide Search

```python
from pdf_utils import search_pdfs_for_tables

# Search all PDFs in directory
results = search_pdfs_for_tables("files/")

# Display results
for pdf_name, pages in results.items():
    if pages:
        print(f"{pdf_name}: Tables on pages {pages}")
    else:
        print(f"{pdf_name}: No tables found")
```

**Pattern:** Scan → Collect → Report

---

## Error Handling Patterns

### Safe Extraction with Try-Except

```python
from pdf_utils import extract_page_content

pdf_files = [
    "files/owner-manual.pdf",
    "files/quick-start-guide.pdf",
    "files/selection-chart.pdf"
]

for pdf_file in pdf_files:
    try:
        content = extract_page_content(pdf_file, page_number=0)
        if content:
            print(f"✓ {content['pdf_name']}: {len(content['text'])} chars")
        else:
            print(f"✗ No content from {pdf_file}")
    except FileNotFoundError:
        print(f"✗ File not found: {pdf_file}")
    except ValueError as e:
        print(f"✗ Invalid page or PDF error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
```

**Pattern:** Try → Catch specific → Catch general

---

### Validation Pattern

```python
def validate_extraction(content):
    """Validate extracted content"""
    if content is None:
        return False, "No content extracted"
    
    if "text" not in content:
        return False, "Missing text field"
    
    if "tables" not in content:
        return False, "Missing tables field"
    
    if len(content["text"]) == 0:
        return False, "Empty text"
    
    return True, "Valid"

# Usage
content = extract_page_content(pdf_file, page_num)
is_valid, message = validate_extraction(content)

if is_valid:
    process_content(content)
else:
    print(f"Invalid: {message}")
```

**Pattern:** Check → Validate → Process or Reject

---

## OCR Pattern

### Automatic OCR for Image-Heavy Pages

```python
from pdf_utils import extract_page_content

# OCR is automatically applied when:
# - Text extraction yields < 50 characters
# - Page appears to be image-based

content = extract_page_content("files/selection-chart.pdf", page_number=0)

if content:
    print(f"Text length: {len(content['text'])}")
    print(f"OCR was applied: {len(content['text']) > 1000}")
    print(f"\nExtracted text preview:")
    print(content["text"][:500])
```

**Pattern:** Extract → Detect low text → Apply OCR → Return enhanced

---

## Multimodal AI Pattern

### Image Analysis with BLIP

```python
from pdf_utils import analyze_image_content
import pdfplumber

# Analyze images in PDF page
with pdfplumber.open("files/owner-manual.pdf") as pdf:
    page = pdf.pages[5]
    
    # Check if page has images
    if len(page.images) > 0:
        print(f"Found {len(page.images)} images on page")
        
        # Analyze with multimodal AI
        analysis = analyze_image_content(page)
        
        if "error" not in analysis:
            for img_result in analysis["results"]:
                print(f"\nImage {img_result['image_index']}:")
                print(f"  Caption: {img_result['general_caption']}")
                print(f"  Description: {img_result['detailed_description'][:100]}...")
                
                # Welding-specific analysis
                for prompt, answer in img_result["welding_analysis"].items():
                    print(f"  {prompt}: {answer}")
        else:
            print(f"Analysis error: {analysis['error']}")
```

**Pattern:** Detect → Extract → Analyze → Interpret

---

### Standalone Image Analysis

```python
from pdf_utils import analyze_standalone_image

# Analyze product images
for img_file in ["product.webp", "product-inside.webp"]:
    result = analyze_standalone_image(img_file)
    
    if "error" not in result:
        print(f"\n{result['image_name']}:")
        print(f"  Dimensions: {result['dimensions']}")
        print(f"  Caption: {result['general_caption']}")
        print(f"  Description: {result['detailed_description'][:100]}...")
        
        # Specific analysis
        for prompt, answer in result["specific_analysis"].items():
            print(f"  {prompt}")
            print(f"    → {answer}")
    else:
        print(f"Error analyzing {img_file}: {result['error']}")
```

**Pattern:** Load → Preprocess → Generate → Interpret

---

## Building Knowledge Base

### Aggregating Multiple PDFs

```python
from pdf_utils import extract_page_content, extract_all_tables
import json

pdfs = [
    "files/owner-manual.pdf",
    "files/quick-start-guide.pdf",
    "files/selection-chart.pdf"
]

knowledge_base = {
    "pdfs": {},
    "tables": {},
    "metadata": {}
}

for pdf_path in pdfs:
    pdf_name = pdf_path.split("/")[-1]
    
    # Extract all tables
    tables = extract_all_tables(pdf_path)
    knowledge_base["tables"][pdf_name] = tables
    
    # Extract first page content
    content = extract_page_content(pdf_path, 0)
    if content:
        knowledge_base["pdfs"][pdf_name] = {
            "text_preview": content["text"][:500],
            "total_pages": content["total_pages"],
            "table_count": len(content["tables"])
        }

# Save knowledge base
with open("welding_knowledge.json", "w") as f:
    json.dump(knowledge_base, f, indent=2)

print(f"Knowledge base saved with {len(pdfs)} PDFs")
```

**Pattern:** Iterate → Extract → Aggregate → Persist

---

## Query Pattern

### Searching Extracted Content

```python
def search_content(knowledge_base, query):
    """Search knowledge base for query terms"""
    results = []
    query_lower = query.lower()
    
    for pdf_name, pdf_data in knowledge_base["pdfs"].items():
        text = pdf_data.get("text_preview", "").lower()
        if query_lower in text:
            results.append({
                "pdf": pdf_name,
                "type": "text",
                "match": True
            })
    
    for pdf_name, tables in knowledge_base["tables"].items():
        for page_info in tables:
            for table in page_info["tables"]:
                for row in table:
                    for cell in row:
                        if cell and query_lower in str(cell).lower():
                            results.append({
                                "pdf": pdf_name,
                                "type": "table",
                                "page": page_info["page_number"] + 1,
                                "match": True
                            })
    
    return results

# Usage
results = search_content(knowledge_base, "duty cycle")
for result in results:
    print(f"Found in {result['pdf']} ({result['type']})")
```

**Pattern:** Index → Query → Match → Return

---

## Type Hint Pattern

### Complete Function with Type Hints

```python
from typing import Optional, Dict, Any, List
import os

def extract_page_content(
    pdf_path: str,
    page_number: int = 0
) -> Optional[Dict[str, Any]]:
    """
    Extract text and tables from a specific PDF page.
    
    Args:
        pdf_path: Path to the PDF file
        page_number: 0-indexed page number (default: 0)
    
    Returns:
        Dictionary with extracted content or None if error
    
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If page number is invalid
    """
    # Validate input
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Process PDF
    try:
        # ... extraction logic ...
        result: Dict[str, Any] = {
            "text": extracted_text,
            "tables": extracted_tables,
            "page_number": page_number,
            "total_pages": total_pages,
            "pdf_name": os.path.basename(pdf_path)
        }
        return result
    except Exception as e:
        raise ValueError(f"Error processing PDF: {e}")
```

**Pattern:** Type → Document → Validate → Process → Return

---

## Context Manager Pattern

### Safe PDF Handling

```python
import pdfplumber

def process_pdf_safely(pdf_path: str):
    """Process PDF with proper resource management"""
    
    # Context manager ensures PDF is closed
    with pdfplumber.open(pdf_path) as pdf:
        # Process pages
        for page_num, page in enumerate(pdf.pages):
            try:
                # Extract content
                text = page.extract_text() or ""
                tables = page.extract_tables() or []
                
                # Process content
                yield {
                    "page": page_num,
                    "text": text,
                    "tables": tables
                }
            except Exception as e:
                print(f"Error on page {page_num}: {e}")
                continue

# Usage
for page_data in process_pdf_safely("files/owner-manual.pdf"):
    print(f"Page {page_data['page']}: {len(page_data['text'])} chars")
```

**Pattern:** Open → Process → Yield/Close → Cleanup

---

## Lazy Loading Pattern

### On-Demand Model Loading

```python
from transformers import BlipProcessor, BlipForConditionalGeneration

# Global cache for models
_model_cache = {}

def get_blip_model():
    """Load BLIP model once and cache"""
    if "blip" not in _model_cache:
        print("Loading BLIP model (first time only)...")
        _model_cache["blip_processor"] = BlipProcessor.from_pretrained(
            'Salesforce/blip-image-captioning-base'
        )
        _model_cache["blip_model"] = BlipForConditionalGeneration.from_pretrained(
            'Salesforce/blip-image-captioning-base'
        )
    return _model_cache["blip_processor"], _model_cache["blip_model"]

# Usage in function
def analyze_image_content(page):
    processor, model = get_blip_model()  # Loads only once
    # ... use model ...
```

**Pattern:** Check → Load → Cache → Reuse

---

## Batch Processing Pattern

### Efficient Multi-PDF Processing

```python
from pdf_utils import extract_all_tables
import time

def process_pdfs_batch(pdf_paths: List[str], batch_size: int = 5):
    """Process PDFs in batches"""
    results = {}
    
    for i in range(0, len(pdf_paths), batch_size):
        batch = pdf_paths[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        print(f"\nProcessing batch {batch_num}...")
        batch_start = time.time()
        
        for pdf_path in batch:
            try:
                start = time.time()
                tables = extract_all_tables(pdf_path)
                elapsed = time.time() - start
                
                results[pdf_path] = {
                    "tables": tables,
                    "processing_time": elapsed,
                    "success": True
                }
                
                print(f"  ✓ {pdf_path} ({elapsed:.1f}s)")
            except Exception as e:
                results[pdf_path] = {
                    "error": str(e),
                    "success": False
                }
                print(f"  ✗ {pdf_path}: {e}")
        
        batch_elapsed = time.time() - batch_start
        print(f"  Batch {batch_num} completed in {batch_elapsed:.1f}s")
    
    return results

# Usage
pdfs = ["files/owner-manual.pdf", "files/quick-start-guide.pdf"]
results = process_pdfs_batch(pdfs, batch_size=2)
```

**Pattern:** Chunk → Process → Track → Report

---

## Performance Optimization

### Caching Expensive Operations

```python
from functools import lru_cache

@lru_cache(maxsize=32)
def get_pdf_info_cached(pdf_path: str):
    """Cache PDF info to avoid repeated file reads"""
    return get_pdf_info(pdf_path)

# Usage - subsequent calls are fast
info1 = get_pdf_info_cached("files/owner-manual.pdf")  # Reads file
info2 = get_pdf_info_cached("files/owner-manual.pdf")  # Uses cache
```

**Pattern:** Decorate → Cache → Reuse

---

## Logging Pattern

### Structured Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_with_logging(pdf_path: str, page_num: int):
    """Extract with detailed logging"""
    logger.info(f"Starting extraction: {pdf_path}, page {page_num}")
    
    try:
        start_time = time.time()
        content = extract_page_content(pdf_path, page_num)
        elapsed = time.time() - start_time
        
        if content:
            logger.info(
                f"Extraction successful: {len(content['text'])} chars, "
                f"{len(content['tables'])} tables ({elapsed:.2f}s)"
            )
        else:
            logger.warning(f"No content extracted from {pdf_path}")
        
        return content
    except FileNotFoundError:
        logger.error(f"File not found: {pdf_path}")
        raise
    except Exception as e:
        logger.exception(f"Extraction failed: {e}")
        raise
```

**Pattern:** Log → Try → Process → Log → Return

---

## Testing Pattern

### Parameterized Testing

```python
import pytest
from pdf_utils import extract_page_content

@pytest.mark.parametrize("pdf_file,page_num,expect_tables", [
    ("files/owner-manual.pdf", 5, True),
    ("files/quick-start-guide.pdf", 0, True),
    ("files/selection-chart.pdf", 0, False),
])
def test_extract_page_content(pdf_file, page_num, expect_tables):
    """Test extraction with multiple inputs"""
    if not os.path.exists(pdf_file):
        pytest.skip(f"File not found: {pdf_file}")
    
    content = extract_page_content(pdf_file, page_num)
    
    assert content is not None
    assert "text" in content
    assert "tables" in content
    
    has_tables = len(content["tables"]) > 0
    assert has_tables == expect_tables, \
        f"Expected tables={expect_tables}, got {has_tables}"
```

**Pattern:** Parameterize → Test → Assert → Report

---

## Best Practices Summary

### DO:
- ✓ Use type hints for all functions
- ✓ Wrap in try-except for error handling
- ✓ Use context managers for file/PDF handling
- ✓ Cache expensive operations (model loading)
- ✓ Validate inputs before processing
- ✓ Log important operations
- ✓ Write tests for critical paths
- ✓ Document with docstrings

### DON'T:
- ✗ Don't ignore exceptions
- ✗ Don't process without validation
- ✗ Don't load models repeatedly
- ✗ Don't leave files open
- ✗ Don't assume PDF structure
- ✗ Don't skip error handling
- ✗ Don't process without logging

---
**Source:** Code analysis from pdf_utils.py, test_pdf_utils.py, demo_pdf_extraction.py
**Category:** Code Patterns
**Tags:** #code-patterns #python #best-practices #error-handling #ocr #multimodal-ai