#!/usr/bin/env python3
"""
Full-featured demo script showing how to extract information from PDF manuals 
and analyze images for the Prox welding agent challenge, including OCR for 
image-based content and multimodal AI for image understanding.
"""

from pdf_utils import extract_page_content, extract_all_tables, search_pdfs_for_tables, get_pdf_info, analyze_standalone_image
import json
import os
import base64
from io import BytesIO


def demo_full_information_extraction():
    """Demonstrate comprehensive PDF information extraction for agent knowledge base"""
    
    print("🔧 Prox Welding Agent - FULL Information Extraction Demo")
    print("=" * 70)
    
    pdfs = ["files/owner-manual.pdf", "files/quick-start-guide.pdf", "files/selection-chart.pdf"]
    
    # 1. Get overview of all PDFs
    print("\n📚 PDF Overview:")
    pdf_details = []
    for pdf_path in pdfs:
        try:
            info = get_pdf_info(pdf_path)
            pdf_details.append(info)
            print(f"  • {info['filename']}: {info['total_pages']} pages, {info['file_size']:,} bytes")
        except Exception as e:
            print(f"  • Error reading {pdf_path}: {e}")
    
    # 2. Search for tables across all PDFs
    print("\n📊 Table Locations Across All Manuals:")
    table_locations = search_pdfs_for_tables("files/")
    for pdf_name, pages in table_locations.items():
        if pages:
            print(f"  • {pdf_name}: Tables on pages {pages}")
        else:
            print(f"  • {pdf_name}: No tables found")
    
    # 3. Extract specific technical content with focus on image-heavy pages
    print("\n🔍 Extracting Technical Content (Including OCR for Images):")
    
    # Owner manual - page 6 (welding setup info) - text-based
    print("\n  📋 Owner Manual - Page 6 (Setup Instructions):")
    try:
        content = extract_page_content("files/owner-manual.pdf", page_number=5)
        if content:
            print(f"    Text length: {len(content['text'])} characters")
            if content['tables']:
                print(f"    Found {len(content['tables'])} table(s)")
                table = content['tables'][0]
                print(f"    First table has {len(table)} rows")
                for i, row in enumerate(table[:3]):  # Show first 3 rows
                    print(f"      Row {i+1}: {[cell[:50] + '...' if cell and len(str(cell)) > 50 else cell for cell in row]}")
            else:
                print(f"    Text preview: {content['text'][:150]}...")
        else:
            print("    No content extracted")
    except Exception as e:
        print(f"    Error: {e}")
    
    # Selection chart - page 1 (image-based) - OCR extraction
    print("\n  🖼️  Selection Chart - Page 1 (Image/OCR Extraction):")
    try:
        content = extract_page_content("files/selection-chart.pdf", page_number=0)
        if content:
            print(f"    Text length: {len(content['text'])} characters")
            print(f"    Tables found: {len(content['tables'])}")
            print(f"    OCR Preview: {content['text'][:200]}...")
            
            # Show more of the extracted content
            lines = content['text'].split('\n')
            meaningful_lines = [line.strip() for line in lines if line.strip() and len(line.strip()) > 10]
            if meaningful_lines:
                print(f"    Key extracted information:")
                for line in meaningful_lines[:5]:  # Show first 5 meaningful lines
                    print(f"      • {line}")
        else:
            print("    No content extracted")
    except Exception as e:
        print(f"    Error: {e}")
    
    # Quick start guide - page 1 (mixed content)
    print("\n  🚀 Quick Start Guide - Page 1 (Basic Setup):")
    try:
        content = extract_page_content("files/quick-start-guide.pdf", page_number=0)
        if content:
            print(f"    Text length: {len(content['text'])} characters")
            if content['tables']:
                print(f"    Found {len(content['tables'])} table(s)")
                print(f"    Text preview: {content['text'][:100]}...")
            else:
                print(f"    Text preview: {content['text'][:150]}...")
        else:
            print("    No content extracted")
    except Exception as e:
        print(f"    Error: {e}")
    
    # 4. Extract all tables for comprehensive knowledge base
    print("\n🗂️  Building Knowledge Base from All Tables:")
    
    all_tables_data = {}
    total_tables = 0
    for pdf_path in pdfs:
        try:
            tables_info = extract_all_tables(pdf_path)
            pdf_name = os.path.basename(pdf_path)
            all_tables_data[pdf_name] = {
                "total_pages_with_tables": len(tables_info),
                "table_pages": [info['page_number'] + 1 for info in tables_info],
                "total_tables_found": sum(len(info['tables']) for info in tables_info)
            }
            total_tables += sum(len(info['tables']) for info in tables_info)
            print(f"  • {pdf_name}: {len(tables_info)} pages with tables, {sum(len(info['tables']) for info in tables_info)} total tables")
        except Exception as e:
            print(f"  • Error processing {pdf_path}: {e}")
    
    # 5. Image/Diagram Analysis Capabilities
    print("\n🖼️  Image & Diagram Analysis Capabilities:")
    print("  ✓ Image Detection: pdf_utils can detect embedded images in PDFs")
    print("  ✓ OCR Processing: Tesseract OCR extracts text from image content")
    print("  ✓ Selection Chart Processing: Image-only pages now yield searchable text")
    print("  ✓ Mixed Content Handling: Text + image pages processed appropriately")
    print("  ✓ Standalone Image Analysis: product.webp and product-inside.webp")
    
    # Show what we can extract from images specifically
    print("\n  🔬 Image Analysis Example (Selection Chart):")
    try:
        import pdfplumber
        with pdfplumber.open("files/selection-chart.pdf") as pdf:
            page = pdf.pages[0]
            image_count = len(page.images)
            print(f"    Images detected: {image_count}")
            if image_count > 0:
                img = page.images[0]
                print(f"    Image dimensions: {img['width']} x {img['height']} pixels")
                print(f"    Image format: {img.get('ImageName', 'Unknown')}")
                
                # Try to get OCR stats
                content = extract_page_content("files/selection-chart.pdf", page_number=0)
                if content:
                    print(f"    OCR extracted: {len(content['text'])} characters")
                    print(f"    OCR effectiveness: {'High' if len(content['text']) > 1000 else 'Medium' if len(content['text']) > 100 else 'Low'}")
    except Exception as e:
        print(f"    Image analysis error: {e}")
    
    # 6. Analyze standalone product images
    print("\n📸 Standalone Product Image Analysis:")
    product_images = ["product.webp", "product-inside.webp"]
    for img_file in product_images:
        if os.path.exists(img_file):
            print(f"\n  Analyzing: {img_file}")
            try:
                result = analyze_standalone_image(img_file)
                if "error" not in result:
                    print(f"    Caption: {result['general_caption']}")
                    print(f"    Description: {result['detailed_description'][:100]}...")
                    print(f"    Analysis available: {len(result['specific_analysis'])} categories")
                else:
                    print(f"    Error: {result['error']}")
            except Exception as e:
                print(f"    Failed: {e}")
        else:
            print(f"\n  ⚠️  {img_file} not found (optional)")
    
    # 7. Show how agent could use this enhanced data
    print("\n🤖 Enhanced Agent Usage Examples:")
    print("  • 'What's the duty cycle for MIG welding at 200A?' → Search owner-manual.pdf tables")
    print("  • 'How do I set up polarity for TIG welding?' → Extract from page 6 tables")
    print("  • 'What wire feed speed should I use?' → Cross-reference quick-start-guide.pdf")
    print("  • 'Show me the welding process selection chart' → OCR extracted text from selection-chart.pdf")
    print("  • 'What materials can I weld with 120V input?' → Search OCR text from selection chart")
    print("  • 'What thickness of aluminum can I weld?' → Parse selection chart OCR data")
    print("  • 'Explain the setup diagram' → Reference extracted image text and tables")
    print("  • 'Describe this product image' → Multimodal AI analysis of product.webp")
    
    # 8. Save comprehensive data for agent
    print("\n💾 Saving Enhanced Knowledge Base:")
    
    # Enhanced knowledge base with OCR content
    enhanced_kb = {
        "pdf_summary": all_tables_data,
        "table_locations": table_locations,
        "ocr_extracted_content": {},
        "extraction_metadata": {
            "total_pdfs": len(pdfs),
            "total_pages": sum(info['total_pages'] for info in pdf_details),
            "total_size_bytes": sum(info['file_size'] for info in pdf_details),
            "extraction_timestamp": "2024-01-01T00:00:00Z",
            "ocr_enabled": True
        }
    }
    
    # Add OCR extracted content for image-heavy pages
    for pdf_path in pdfs:
        pdf_name = os.path.basename(pdf_path)
        try:
            # Check if this page benefits from OCR (selection chart)
            content = extract_page_content(pdf_path, page_number=0)
            if content and len(content['text']) > 100:  # Significant OCR content
                enhanced_kb["ocr_extracted_content"][pdf_name] = {
                    "page_1_text_length": len(content['text']),
                    "page_1_text_preview": content['text'][:500],
                    "has_tables": len(content['tables']) > 0,
                    "table_count": len(content['tables'])
                }
        except Exception as e:
            enhanced_kb["ocr_extracted_content"][pdf_name] = {"error": str(e)}
    
    # Save enhanced knowledge base
    with open("enhanced_pdf_knowledge.json", "w") as f:
        json.dump(enhanced_kb, f, indent=2)
    
    # Also save the original format for backward compatibility
    sample_data = {
        "pdf_summary": all_tables_data,
        "table_locations": table_locations,
        "extraction_timestamp": "2024-01-01T00:00:00Z"
    }
    
    with open("pdf_knowledge_summary.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print("  ✓ Saved enhanced knowledge to enhanced_pdf_knowledge.json")
    print("  ✓ Saved backward-compatible summary to pdf_knowledge_summary.json")
    
    # 9. Statistics
    print("\n📈 Extraction Statistics:")
    print(f"  • Total PDFs processed: {len(pdfs)}")
    print(f"  • Total pages: {sum(info['total_pages'] for info in pdf_details)}")
    print(f"  • Total size: {sum(info['file_size'] for info in pdf_details):,} bytes")
    print(f"  • Tables found: {total_tables}")
    ocr_pages = sum(1 for kb in enhanced_kb["ocr_extracted_content"].values() 
                   if isinstance(kb, dict) and kb.get("page_1_text_length", 0) > 100)
    print(f"  • OCR-enhanced pages: {ocr_pages}")
    
    print("\n✅ Demo complete! Your agent now has FULL information extraction capabilities:")
    print("   - Standard text/table extraction")
    print("   - OCR for image/scanned content")
    print("   - Image metadata and diagram analysis")
    print("   - Standalone image analysis (product images)")
    print("   - Enhanced knowledge base for welding agent")


if __name__ == "__main__":
    demo_full_information_extraction()