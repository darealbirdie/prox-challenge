# Testing Patterns

## Test Suite Overview

Comprehensive test suite for `pdf_utils` module covering imports, PDF info, content extraction, table extraction, and specific page tests.

## Test Structure

```
test_pdf_utils.py
├── test_imports()          # Verify library imports
├── test_pdf_info()         # Test metadata extraction
├── test_extract_page_content()  # Test page-level extraction
├── test_extract_all_tables()    # Test batch table extraction
├── test_search_pdfs_for_tables() # Test directory search
└── test_specific_pages()   # Test known content pages
```

## Import Test Pattern

**Purpose:** Verify dependencies are correctly installed

```python
def test_imports():
    """Test that pdfplumber imports correctly"""
    try:
        import pdfplumber
        print("✓ pdfplumber imported successfully")
        return True
    except ImportError as e:
        print(f"✗ pdfplumber import failed: {e}")
        return False
```

**Best Practice:**
- Test critical imports first
- Provide clear error messages
- Return boolean for test aggregation

---

## PDF Info Test Pattern

**Purpose:** Verify PDF metadata extraction

```python
def test_pdf_info():
    """Test getting PDF information for all files"""
    print("Testing PDF info extraction:")
    all_passed = True

    for pdf_file in PDF_FILES:
        if not os.path.exists(pdf_file):
            print(f"✗ PDF file not found: {pdf_file}")
            all_passed = False
            continue

        try:
            info = get_pdf_info(pdf_file)
            print(f"✓ {info['filename']}: {info['total_pages']} pages, {info['file_size']} bytes")
        except Exception as e:
            print(f"✗ Error getting info for {pdf_file}: {e}")
            all_passed = False

    return all_passed
```

**Key Patterns:**
- Check file existence before testing
- Use try-except for error handling
- Continue on failure (don't stop entire suite)
- Aggregate results with boolean flag

---

## Page Content Extraction Test

**Purpose:** Verify text and table extraction from pages

```python
def test_extract_page_content():
    """Test extracting content from first page of each PDF"""
    print("Testing page content extraction:")
    all_passed = True

    for pdf_file in PDF_FILES:
        if not os.path.exists(pdf_file):
            continue

        try:
            content = extract_page_content(pdf_file, page_number=0)
            if content:
                print(f"✓ {content['pdf_name']} page 1: {len(content['text'])} chars, {len(content['tables'])} tables")
            else:
                print(f"✗ No content from {pdf_file}")
                all_passed = False
        except Exception as e:
            print(f"✗ Error extracting from {pdf_file}: {e}")
            all_passed = False

    return all_passed
```

**Validation Checks:**
- Content is not `None`
- Text length is reasonable
- Table count is reported
- Errors are caught and reported

---

## Table Extraction Test

**Purpose:** Verify batch table extraction across all pages

```python
def test_extract_all_tables():
    """Test extracting all tables from each PDF"""
    print("Testing table extraction from all PDFs:")
    all_passed = True

    for pdf_file in PDF_FILES:
        if not os.path.exists(pdf_file):
            continue

        try:
            results = extract_all_tables(pdf_file)
            filename = os.path.basename(pdf_file)
            print(f"✓ {filename}: tables found on {len(results)} page(s)")

            if results:
                # Show details for first page with tables
                first_result = results[0]
                print(f"  - First page with tables (page {first_result['page_number'] + 1}): {len(first_result['tables'])} table(s)")
                if first_result['tables']:
                    first_table = first_result['tables'][0]
                    print(f"  - Sample table: {len(first_table)} rows")
                    # Show first row if it has content
                    for row in first_table[:1]:
                        if any(cell for cell in row if cell):
                            print(f"    First row: {row}")
                            break

        except Exception as e:
            print(f"✗ Error extracting tables from {pdf_file}: {e}")
            all_passed = False

    return all_passed
```

**Key Patterns:**
- Iterate through all results
- Show hierarchical details (pages → tables → rows)
- Sample data for verification
- Handle empty results gracefully

---

## Directory Search Test

**Purpose:** Verify PDF directory scanning

```python
def test_search_pdfs_for_tables():
    """Test searching all PDFs for tables"""
    print("Testing PDF directory search:")
    try:
        results = search_pdfs_for_tables("files/")
        print("✓ PDF table search results:")
        for pdf_name, pages in results.items():
            if pages:
                print(f"  - {pdf_name}: tables on pages {pages}")
            else:
                print(f"  - {pdf_name}: no tables found")
        return True
    except Exception as e:
        print(f"✗ Error searching PDFs: {e}")
        return False
```

**Key Patterns:**
- Single try-except for entire operation
- Iterate through dictionary results
- Distinguish between "no tables" and "error"

---

## Specific Page Test Pattern

**Purpose:** Test known pages with expected content

```python
def test_specific_pages():
    """Test extracting from specific pages known to have content"""
    print("Testing specific page extractions:")
    all_passed = True

    # Test cases: (pdf_file, page_number, expected_has_tables)
    test_cases = [
        ("files/owner-manual.pdf", 5, True),   # Page 6 has tables
        ("files/quick-start-guide.pdf", 0, True),  # First page has tables
        ("files/selection-chart.pdf", 0, True),  # Should have chart data
    ]

    for pdf_file, page_num, expect_tables in test_cases:
        if not os.path.exists(pdf_file):
            continue

        try:
            content = extract_page_content(pdf_file, page_num)
            if content:
                has_tables = len(content['tables']) > 0
                status = "✓" if has_tables == expect_tables else "⚠"
                print(f"{status} {content['pdf_name']} page {page_num + 1}: {len(content['tables'])} tables")
                if content['tables']:
                    print(f"  - First table has {len(content['tables'][0])} rows")
            else:
                print(f"✗ No content from {pdf_file} page {page_num + 1}")
                all_passed = False
        except Exception as e:
            print(f"✗ Error extracting page {page_num + 1} from {pdf_file}: {e}")
            all_passed = False

    return all_passed
```

**Key Patterns:**
- Define test cases as data (easy to extend)
- Expected vs actual comparison
- Warning (⚠) for unexpected but not failed results
- Detailed error reporting with page numbers

---

## Test Suite Runner Pattern

**Purpose:** Aggregate and report all test results

```python
if __name__ == "__main__":
    print("Testing pdf_utils module with all PDFs...\n")

    tests = [
        ("Import Test", test_imports),
        ("PDF Info Test", test_pdf_info),
        ("Page Content Test", test_extract_page_content),
        ("All Tables Test", test_extract_all_tables),
        ("PDF Search Test", test_search_pdfs_for_tables),
        ("Specific Pages Test", test_specific_pages),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        results.append(test_func())

    print(f"\n{'='*50}")
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your PDF utilities are ready.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
```

**Key Patterns:**
- Test registry as list of tuples
- Iterate and collect results
- Summary report with pass/fail count
- Emoji for visual feedback

---

## Assertion-Based Testing (Alternative)

For unit test frameworks (pytest, unittest):

```python
import pytest
from pdf_utils import extract_page_content, get_pdf_info

class TestPDFUtils:
    def test_pdf_info(self):
        info = get_pdf_info("files/owner-manual.pdf")
        assert info["total_pages"] > 0
        assert info["file_size"] > 0
        assert ".pdf" in info["filename"]

    def test_extract_content(self):
        content = extract_page_content("files/owner-manual.pdf", 0)
        assert content is not None
        assert "text" in content
        assert "tables" in content
        assert isinstance(content["tables"], list)

    def test_page_range_error(self):
        with pytest.raises(ValueError):
            extract_page_content("files/owner-manual.pdf", 999)

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            extract_page_content("nonexistent.pdf")
```

---

## Mock Testing Pattern

For testing without actual PDF files:

```python
from unittest.mock import Mock, patch

def test_extract_with_mock():
    with patch('pdfplumber.open') as mock_open:
        # Setup mock
        mock_pdf = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample text"
        mock_page.extract_tables.return_value = [[['A', 'B'], ['1', '2']]]
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_open.return_value = mock_pdf

        # Test
        content = extract_page_content("dummy.pdf", 0)
        assert content["text"] == "Sample text"
        assert len(content["tables"]) == 1
```

---

## Test Data Management

**PDF Test Files:**
```python
PDF_FILES = [
    "files/owner-manual.pdf",
    "files/quick-start-guide.pdf",
    "files/selection-chart.pdf"
]
```

**Best Practices:**
- Use relative paths from project root
- Check existence before testing
- Document expected content for each file
- Keep test files small and focused

---

## Continuous Integration Pattern

**.github/workflows/test.yml:**
```yaml
name: Test PDF Utils

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install pdfplumber pytesseract pillow
          pip install transformers torch
      
      - name: Run tests
        run: python test_pdf_utils.py
```

---

## Performance Testing

```python
import time

def test_performance():
    """Measure extraction performance"""
    start = time.time()
    content = extract_page_content("files/owner-manual.pdf", 0)
    elapsed = time.time() - start
    
    print(f"Extraction took {elapsed:.2f} seconds")
    assert elapsed < 5.0, "Extraction too slow"
```

---

## Common Test Scenarios

| Scenario | Test Approach | Expected Result |
|----------|--------------|-----------------|
| Valid PDF | Normal extraction | Content returned |
| Missing PDF | File not found | FileNotFoundError |
| Invalid page | Out of range | ValueError |
| Image-only page | OCR enabled | Text extracted |
| No tables | Table extraction | Empty list |
| Corrupted PDF | Error handling | Exception raised |
| Large PDF | Performance | Within time limit |
| Encrypted PDF | Error handling | Exception raised |

---

## Test Coverage Checklist

- [ ] All functions have tests
- [ ] Error conditions tested
- [ ] Edge cases covered (empty, large, etc.)
- [ ] Integration tests (multiple PDFs)
- [ ] Performance benchmarks
- [ ] Mock tests for external deps
- [ ] CI/CD pipeline configured
- [ ] Test data documented

---

## See Also
- [[PDF Functions Reference]] - Functions being tested
- [[Demo Usage]] - Real-world usage patterns
- [[PDF Extraction System]] - System overview
