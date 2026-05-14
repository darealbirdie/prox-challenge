#!/usr/bin/env python3
"""
Quick test to verify image analysis setup without running full model.
"""

import sys
import os

def main():
    print("\n" + "=" * 60)
    print("Image Analysis Setup Verification")
    print("=" * 60)
    
    # Check 1: Verify files exist
    print("\n1. Checking for required files...")
    files = [
        "pdf_utils.py",
        "demo_pdf_extraction.py",
        "test_image_analysis.py",
        "verify_image_analysis.py",
        "workflow_demo.py",
        "IMAGE_ANALYSIS_README.md"
    ]
    
    for f in files:
        exists = os.path.exists(f)
        status = "✓" if exists else "✗"
        print(f"   {status} {f}")
    
    # Check 2: Verify image files
    print("\n2. Checking for product images...")
    images = ["product.webp", "product-inside.webp"]
    for img in images:
        exists = os.path.exists(img)
        status = "✓" if exists else "⚠"
        print(f"   {status} {img}: {'Found' if exists else 'Optional'}")
    
    # Check 3: Verify imports
    print("\n3. Checking Python imports...")
    try:
        import pdfplumber
        print("   ✓ pdfplumber")
    except ImportError:
        print("   ✗ pdfplumber")
    
    try:
        import pytesseract
        print("   ✓ pytesseract")
    except ImportError:
        print("   ✗ pytesseract")
    
    try:
        from PIL import Image
        print("   ✓ PIL/Pillow")
    except ImportError:
        print("   ✗ PIL/Pillow")
    
    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        print("   ✓ transformers (BLIP model)")
    except ImportError:
        print("   ✗ transformers (install with: pip install transformers)")
    
    try:
        import torch
        print("   ✓ torch")
    except ImportError:
        print("   ✗ torch (install with: pip install torch)")
    
    # Check 4: Verify pdf_utils has the new functions
    print("\n4. Checking pdf_utils for new functions...")
    try:
        from pdf_utils import analyze_standalone_image
        print("   ✓ analyze_standalone_image function")
    except ImportError:
        print("   ✗ analyze_standalone_image function")
    
    try:
        from pdf_utils import extract_page_content
        print("   ✓ extract_page_content function (with OCR)")
    except ImportError:
        print("   ✗ extract_page_content function")
    
    # Check 5: Test OCR on selection chart
    print("\n5. Testing OCR on selection chart...")
    try:
        from pdf_utils import extract_page_content
        content = extract_page_content("files/selection-chart.pdf", page_number=0)
        if content and len(content['text']) > 100:
            print(f"   ✓ OCR working: {len(content['text'])} characters extracted")
            print(f"   Sample: {content['text'][:80]}...")
        else:
            print(f"   ✗ OCR not working properly")
    except Exception as e:
        print(f"   ✗ OCR test failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Setup Verification Complete")
    print("=" * 60)
    
    print("\nNext Steps:")
    print("  1. Run: python3 verify_image_analysis.py")
    print("     (Tests the full image analysis pipeline)")
    print("\n  2. Run: python3 test_image_analysis.py")
    print("     (Tests image analysis on product images)")
    print("\n  3. Run: python3 demo_pdf_extraction.py")
    print("     (Runs the full demo with all features)")
    print("\n  4. Run: python3 workflow_demo.py")
    print("     (Demonstrates complete workflow)")
    print()

if __name__ == "__main__":
    main()