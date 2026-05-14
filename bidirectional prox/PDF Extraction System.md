# PDF Extraction System

## Overview
Comprehensive PDF processing system for the Prox welding agent, featuring text extraction, table parsing, OCR for image-based content, and multimodal AI for image analysis.

## System Capabilities

### Core Features
- **Text Extraction**: Extract text from PDF pages using pdfplumber
- **Table Extraction**: Parse structured table data from PDFs
- **OCR Processing**: Tesseract OCR for image-heavy/scanned pages
- **Image Analysis**: Multimodal AI (BLIP) for understanding diagrams and images
- **Standalone Image Analysis**: Process product images separately

### Key Libraries
- `pdfplumber` - PDF text and table extraction
- `pytesseract` - OCR engine
- `PIL` (Pillow) - Image processing
- `transformers` + `torch` - Multimodal AI (BLIP model)

## File Structure

```
pdf_utils.py              # Core extraction functions
test_pdf_utils.py         # Test suite
demo_pdf_extraction.py    # Full demo with knowledge base generation
files/                    # PDF documents
  - owner-manual.pdf
  - quick-start-guide.pdf
  - selection-chart.pdf
```

## Quick Start

```python
from pdf_utils import extract_page_content, extract_all_tables

# Extract content from a specific page
content = extract_page_content("files/owner-manual.pdf", page_number=5)
print(content["text"])
print(f"Tables: {len(content['tables'])}")

# Extract all tables from a PDF
all_tables = extract_all_tables("files/owner-manual.pdf")
```

## Processing Flow

```
PDF Input
    ↓
[pdfplumber] → Text & Table Extraction
    ↓
Low Text Detected? ──Yes──→ [OCR] → Enhanced Text
    ↓ No
    ↓
Image-Heavy Page? ──Yes──→ [Multimodal AI] → Image Analysis
    ↓ No
    ↓
Output: {text, tables, image_analysis}
```

## Use Cases

### For the Prox Welding Agent
- Extract technical specifications from manuals
- Parse welding parameter tables
- Read selection charts (OCR-enabled)
- Analyze product diagrams with AI
- Build searchable knowledge base

### Example Queries
- "What's the duty cycle for MIG welding at 200A?"
- "How do I set up polarity for TIG welding?"
- "What wire feed speed should I use?"
- "Show me the welding process selection chart"

## Related Notes
- [[PDF Functions Reference]] - Detailed function documentation
- [[Testing Patterns]] - Test suite and patterns
- [[Demo Usage]] - Full demo walkthrough
- [[Code Patterns]] - Techniques and best practices
