# PDF Functions Reference

## Core Extraction Functions

### `extract_page_content(pdf_path, page_number=0)`

Extract text, tables, and analyze images from a specific PDF page.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `page_number` (int): 0-indexed page number (default: 0)

**Returns:**
```python
{
    "text": str,              # Extracted text content
    "tables": list,           # List of tables (each is list of rows)
    "page_number": int,       # Current page number (0-indexed)
    "total_pages": int,       # Total pages in PDF
    "pdf_name": str,          # Filename
    "image_analysis": dict,   # Optional: AI analysis of images
    "image_analysis_error": str  # Optional: Error message
}
```

**Example:**
```python
content = extract_page_content("files/owner-manual.pdf", page_number=5)
print(f"Text: {content['text'][:200]}")
print(f"Tables: {len(content['tables'])}")
if content['tables']:
    for row in content['tables'][0]:
        print(row)
```

**Error Handling:**
- Raises `FileNotFoundError` if PDF doesn't exist
- Raises `ValueError` if page number is out of range
- Raises `ValueError` for general processing errors

---

### `extract_text_from_images(page)`

Extract text from a PDF page using OCR (Tesseract).

**Parameters:**
- `page`: pdfplumber page object

**Returns:**
- `str`: Extracted text (empty string if OCR fails)

**Use Case:**
Automatically called when text extraction yields < 50 characters, indicating a potentially image-based page.

**Example:**
```python
import pdfplumber
with pdfplumber.open("files/selection-chart.pdf") as pdf:
    page = pdf.pages[0]
    text = extract_text_from_images(page)
    print(text)
```

---

### `extract_all_tables(pdf_path)`

Extract all tables from all pages in a PDF.

**Parameters:**
- `pdf_path` (str): Path to the PDF file

**Returns:**
```python
[
    {
        "page_number": int,      # 0-indexed page number
        "tables": list,          # List of tables on this page
        "text": str,             # Text from the page
        "pdf_name": str          # Filename
    },
    ...
]
```

**Example:**
```python
tables_info = extract_all_tables("files/owner-manual.pdf")
for page_info in tables_info:
    print(f"Page {page_info['page_number'] + 1}: {len(page_info['tables'])} tables")
    for table in page_info['tables']:
        for row in table:
            print(row)
```

**Error Handling:**
- Raises `FileNotFoundError` if PDF doesn't exist
- Skips problematic pages with warning (continues processing)

---

### `analyze_image_content(page)`

Analyze images in a PDF page using multimodal AI (BLIP model).

**Parameters:**
- `page`: pdfplumber page object

**Returns:**
```python
{
    "images_analyzed": int,
    "results": [
        {
            "image_index": int,
            "dimensions": str,          # "width x height"
            "mode": str,                # Image mode (RGB, etc.)
            "general_caption": str,     # AI-generated caption
            "detailed_description": str, # Detailed analysis
            "welding_analysis": {       # Welding-specific prompts
                "prompt": "answer",
                ...
            },
            "image_name": str
        },
        ...
    ]
}
# OR (if error)
{"error": "error message"}
```

**When Called:**
- Automatically when text < 100 characters after OCR
- When page has images and text < 300 characters

**AI Prompts Used:**
1. General caption generation
2. Detailed technical description
3. Welding process identification (MIG, TIG, Stick, Flux-core)
4. Materials being welded
5. Equipment settings/parameters
6. Safety equipment/precautions

**Example:**
```python
import pdfplumber
with pdfplumber.open("files/owner-manual.pdf") as pdf:
    page = pdf.pages[5]
    analysis = analyze_image_content(page)
    if "error" not in analysis:
        for img_result in analysis["results"]:
            print(f"Caption: {img_result['general_caption']}")
            print(f"Welding process: {img_result['welding_analysis']['prompt1']}")
```

**Dependencies:**
- `transformers` and `torch` must be installed
- Returns error dict if not available

---

### `analyze_standalone_image(image_path)`

Analyze a standalone image file (not from PDF) using multimodal AI.

**Parameters:**
- `image_path` (str): Path to image file (PNG, JPG, WEBP, etc.)

**Returns:**
```python
{
    "image_path": str,
    "image_name": str,
    "dimensions": str,          # "width x height"
    "format": str,              # Image format
    "mode": str,                # Image mode
    "general_caption": str,     # AI-generated caption
    "detailed_description": str, # Detailed technical description
    "specific_analysis": {      # Answers to specific prompts
        "prompt": "answer",
        ...
    }
}
# OR (if error)
{"error": "error message"}
```

**AI Prompts Used:**
1. General identification
2. Key components/features
3. Materials/construction methods
4. Purpose/function
5. Safety features/design elements

**Example:**
```python
result = analyze_standalone_image("product.webp")
if "error" not in result:
    print(f"Caption: {result['general_caption']}")
    print(f"Description: {result['detailed_description']}")
    for prompt, answer in result['specific_analysis'].items():
        print(f"{prompt}: {answer}")
```

---

### `get_pdf_info(pdf_path)`

Get basic metadata about a PDF file.

**Parameters:**
- `pdf_path` (str): Path to the PDF file

**Returns:**
```python
{
    "filename": str,
    "total_pages": int,
    "file_size": int           # Size in bytes
}
```

**Example:**
```python
info = get_pdf_info("files/owner-manual.pdf")
print(f"{info['filename']}: {info['total_pages']} pages")
```

**Error Handling:**
- Raises `FileNotFoundError` if PDF doesn't exist

---

### `search_pdfs_for_tables(pdf_dir="files/")`

Search all PDFs in a directory for tables.

**Parameters:**
- `pdf_dir` (str): Directory containing PDF files

**Returns:**
```python
{
    "filename.pdf": [1, 3, 5],  # Page numbers (1-indexed) with tables
    ...
}
```

**Example:**
```python
results = search_pdfs_for_tables("files/")
for pdf_name, pages in results.items():
    if pages:
        print(f"{pdf_name}: tables on pages {pages}")
```

**Error Handling:**
- Raises `FileNotFoundError` if directory doesn't exist
- Skips problematic PDFs with warning

---

## Function Call Hierarchy

```
User Code
    ↓
extract_page_content()       # Main entry point
    ├─ extract_text_from_images()  # If low text
    ├─ analyze_image_content()     # If image-heavy
    └─ Returns combined result

extract_all_tables()          # Batch table extraction
    └─ Calls extract_page_content() per page

analyze_standalone_image()    # Direct image analysis
    └─ Uses BLIP model directly
```

## Type Hints

All functions use Python type hints:
```python
from typing import Optional, Dict, Any, List, Union

def extract_page_content(
    pdf_path: str,
    page_number: int = 0
) -> Optional[Dict[str, Any]]:
    ...
```

## Best Practices

1. **Always wrap in try-except**: Functions raise exceptions for errors
2. **Check return values**: Some functions return `None` or error dicts
3. **Lazy loading**: BLIP model loads once and caches
4. **Resource management**: Use context managers (`with pdfplumber.open()`)
5. **Page indexing**: Remember pages are 0-indexed in code, 1-indexed for users

## Performance Notes

- **OCR**: Slower (~1-2 sec/page), use only when needed
- **BLIP**: Slowest (~5-10 sec/image), requires GPU for speed
- **Text extraction**: Fast (~0.1 sec/page)
- **Table extraction**: Fast (~0.1 sec/page)

## See Also
- [[PDF Extraction System]] - Overview and architecture
- [[Testing Patterns]] - How to test these functions
- [[Demo Usage]] - Complete working examples
