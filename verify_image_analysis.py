#!/usr/bin/env python3
"""
Quick verification script for image analysis feature.
Tests that everything is working correctly.
"""

import sys
import os

def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def test_1_imports():
    """Test that all modules can be imported"""
    print_header("Test 1: Import Verification")
    
    modules = [
        ("pdf_utils", "from pdf_utils import analyze_standalone_image"),
        ("PIL", "from PIL import Image"),
        ("transformers", "from transformers import BlipProcessor, BlipForConditionalGeneration"),
        ("torch", "import torch"),
    ]
    
    results = []
    for name, import_stmt in modules:
        try:
            exec(import_stmt)
            print(f"✓ {name}")
            results.append(True)
        except ImportError as e:
            print(f"✗ {name}: {e}")
            results.append(False)
    
    return all(results)

def test_2_image_files():
    """Check that image files exist"""
    print_header("Test 2: Image File Check")
    
    images = ["product.webp", "product-inside.webp"]
    results = []
    
    for img in images:
        exists = os.path.exists(img)
        status = "✓" if exists else "⚠"
        print(f"{status} {img}: {'Found' if exists else 'Not found (optional)'}")
        results.append(exists)
    
    return any(results)  # At least one should exist

def test_3_basic_analysis():
    """Test basic image analysis functionality"""
    print_header("Test 3: Basic Image Analysis")
    
    # Find an available image
    images = ["product.webp", "product-inside.webp"]
    available = [img for img in images if os.path.exists(img)]
    
    if not available:
        print("⚠ No images found, skipping analysis test")
        return True  # Not a failure, just nothing to test
    
    test_image = available[0]
    print(f"Testing with: {test_image}")
    
    try:
        from pdf_utils import analyze_standalone_image
        
        # This will load the model - may take a moment
        print("Loading BLIP model (this may take 30-60 seconds)...")
        result = analyze_standalone_image(test_image)
        
        if "error" in result:
            print(f"✗ Analysis failed: {result['error']}")
            return False
        
        print(f"✓ Analysis successful!")
        print(f"\nResults:")
        print(f"  Image: {result['image_name']}")
        print(f"  Size: {result['dimensions']}")
        print(f"  Format: {result['format']}")
        print(f"\n  Caption: {result['general_caption']}")
        print(f"\n  Description (first 150 chars):")
        print(f"  {result['detailed_description'][:150]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_4_pdf_extraction():
    """Test PDF extraction with OCR"""
    print_header("Test 4: PDF Extraction with OCR")
    
    pdf_file = "files/selection-chart.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"⚠ {pdf_file} not found, skipping")
        return True
    
    try:
        from pdf_utils import extract_page_content
        
        print(f"Extracting from {pdf_file}...")
        content = extract_page_content(pdf_file, page_number=0)
        
        if not content:
            print("✗ No content extracted")
            return False
        
        print(f"✓ Extraction successful!")
        print(f"  Text length: {len(content['text'])} characters")
        print(f"  Tables found: {len(content['tables'])}")
        
        # Check if OCR was used
        if len(content['text']) > 100:
            print(f"\n  OCR was successful!")
            print(f"  Sample text: {content['text'][:100]}...")
        
        # Check for image analysis
        if 'image_analysis' in content:
            print(f"\n  Image analysis was performed!")
            analysis = content['image_analysis']
            print(f"  Images analyzed: {analysis.get('images_analyzed', 0)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during PDF extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 60)
    print("Prox Welding Agent - Image Analysis Verification")
    print("=" * 60)
    
    tests = [
        ("Import Verification", test_1_imports),
        ("Image File Check", test_2_image_files),
        ("Basic Image Analysis", test_3_basic_analysis),
        ("PDF Extraction with OCR", test_4_pdf_extraction),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Test Summary")
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Image analysis is working correctly.")
    else:
        print("⚠️  Some tests failed. Review the output above.")
    print("=" * 60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)