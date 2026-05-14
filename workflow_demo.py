#!/usr/bin/env python3
"""
Complete workflow demonstration for the Prox welding agent.
Shows how to use all features together.
"""

from pdf_utils import (
    extract_page_content,
    extract_all_tables,
    search_pdfs_for_tables,
    get_pdf_info,
    analyze_standalone_image
)
import json
import os

def main():
    print("\n" + "=" * 70)
    print("Prox Welding Agent - Complete Workflow Demonstration")
    print("=" * 70)
    
    # Step 1: Analyze standalone product images
    print("\n[Step 1] Analyzing Standalone Product Images")
    print("-" * 70)
    
    product_images = ["product.webp", "product-inside.webp"]
    image_results = {}
    
    for img_file in product_images:
        if os.path.exists(img_file):
            print(f"\nAnalyzing: {img_file}")
            result = analyze_standalone_image(img_file)
            
            if "error" not in result:
                print(f"  ✓ Caption: {result['general_caption']}")
                print(f"  ✓ Description: {result['detailed_description'][:100]}...")
                image_results[img_file] = result
            else:
                print(f"  ✗ Error: {result['error']}")
        else:
            print(f"\n⚠ {img_file} not found (optional)")
    
    # Step 2: Extract information from PDF manuals
    print("\n[Step 2] Extracting Information from PDF Manuals")
    print("-" * 70)
    
    pdfs = ["files/owner-manual.pdf", "files/quick-start-guide.pdf", "files/selection-chart.pdf"]
    pdf_results = {}
    
    for pdf_path in pdfs:
        pdf_name = os.path.basename(pdf_path)
        print(f"\nProcessing: {pdf_name}")
        
        # Get PDF info
        info = get_pdf_info(pdf_path)
        print(f"  Pages: {info['total_pages']}, Size: {info['file_size']:,} bytes")
        
        # Extract from first page
        content = extract_page_content(pdf_path, page_number=0)
        if content:
            print(f"  Text extracted: {len(content['text'])} characters")
            print(f"  Tables found: {len(content['tables'])}")
            
            # Check for image analysis
            if 'image_analysis' in content:
                print(f"  Image analysis: {content['image_analysis'].get('images_analyzed', 0)} images")
        
        pdf_results[pdf_name] = content
    
    # Step 3: Search for tables across all PDFs
    print("\n[Step 3] Searching for Tables Across All Manuals")
    print("-" * 70)
    
    table_locations = search_pdfs_for_tables("files/")
    for pdf_name, pages in table_locations.items():
        if pages:
            print(f"  • {pdf_name}: Tables on pages {pages}")
        else:
            print(f"  • {pdf_name}: No tables found")
    
    # Step 4: Extract all tables
    print("\n[Step 4] Extracting All Tables for Knowledge Base")
    print("-" * 70)
    
    all_tables = {}
    total_tables = 0
    
    for pdf_path in pdfs:
        pdf_name = os.path.basename(pdf_path)
        tables_info = extract_all_tables(pdf_path)
        
        table_count = sum(len(info['tables']) for info in tables_info)
        all_tables[pdf_name] = {
            "pages_with_tables": len(tables_info),
            "total_tables": table_count
        }
        total_tables += table_count
        
        print(f"  • {pdf_name}: {len(tables_info)} pages, {table_count} tables")
    
    # Step 5: Build comprehensive knowledge base
    print("\n[Step 5] Building Comprehensive Knowledge Base")
    print("-" * 70)
    
    knowledge_base = {
        "metadata": {
            "total_pdfs": len(pdfs),
            "total_pages": sum(info['total_pages'] for info in [
                get_pdf_info(p) for p in pdfs
            ]),
            "total_tables": total_tables,
            "images_analyzed": len(image_results)
        },
        "product_images": {
            name: {
                "caption": result['general_caption'],
                "description": result['detailed_description'][:200],
                "analysis": result['specific_analysis']
            }
            for name, result in image_results.items()
        },
        "pdf_documents": {
            name: {
                "pages": info['total_pages'],
                "tables": all_tables.get(name, {}).get('total_tables', 0),
                "first_page_text": content['text'][:200] if content else ""
            }
            for name, info in [
                (os.path.basename(p), get_pdf_info(p)) for p in pdfs
            ]
            for content in [pdf_results.get(name)]
        },
        "table_locations": table_locations
    }
    
    # Save knowledge base
    output_file = "complete_knowledge_base.json"
    with open(output_file, "w") as f:
        json.dump(knowledge_base, f, indent=2)
    
    print(f"✓ Knowledge base saved to {output_file}")
    
    # Step 6: Demonstrate agent usage
    print("\n[Step 6] Agent Usage Examples")
    print("-" * 70)
    
    examples = [
        "What welding equipment is shown in product.webp?",
        "What materials can be welded with 120V input?",
        "What is the duty cycle for MIG welding at 200A?",
        "Show me the welding process selection chart",
        "What safety equipment is required for TIG welding?"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    
    # Summary
    print("\n" + "=" * 70)
    print("Workflow Complete!")
    print("=" * 70)
    
    print(f"\nSummary:")
    print(f"  • Analyzed {len(image_results)} product images")
    print(f"  • Processed {len(pdf_results)} PDF documents")
    print(f"  • Extracted {total_tables} tables")
    print(f"  • Built comprehensive knowledge base")
    print(f"\nThe agent can now answer technical questions about:")
    print(f"  • Welding equipment and processes")
    print(f"  • Material specifications and requirements")
    print(f"  • Safety procedures and guidelines")
    print(f"  • Technical diagrams and charts")
    print()

if __name__ == "__main__":
    main()