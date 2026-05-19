import pdfplumber
import os
from typing import Optional, Dict, Any, List, Union
import pytesseract
from PIL import Image
import io
import fitz
from pathlib import Path
# Multimodal image analysis imports
try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    import torch
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False
    print("Warning: Multimodal dependencies not available. Install transformers and torch for image analysis.")


def extract_page_content(
    pdf_path: str,
    page_number: int = 0
) -> Optional[Dict[str, Any]]:
    """
    Extract text and tables from a specific PDF page.
    Also attempts OCR if little text is found or for image-heavy pages.
    Includes multimodal image analysis for diagram understanding.

    Args:
        pdf_path: Path to the PDF file
        page_number: 0-indexed page number (default: first page)

    Returns:
        Dictionary containing 'text' and 'tables', or None if page doesn't exist

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If page_number is invalid
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_number < 0 or page_number >= len(pdf.pages):
                raise ValueError(
                    f"Page {page_number} out of range. PDF has {len(pdf.pages)} pages."
                )

            page = pdf.pages[page_number]

            # Extract text
            text = page.extract_text() or ""

            # Extract tables
            tables = page.extract_tables() or []

            # If very little text found, try OCR on the rendered page
            if len(text.strip()) < 50:  # Arbitrary threshold for "little text"
                ocr_text = extract_text_from_images(page)
                if ocr_text and len(ocr_text.strip()) > len(text.strip()):
                    text = ocr_text

            # Perform multimodal image analysis for image-heavy pages or diagrams
            image_analysis = None
            if len(text.strip()) < 100:  # If we still have very little text after OCR, try image analysis
                image_analysis = analyze_image_content(page)
            elif len(page.images) > 0 and len(text.strip()) < 300:  # Image-heavy page with limited text
                image_analysis = analyze_image_content(page)

            result = {
                "text": text,
                "tables": tables,
                "page_number": page_number,
                "total_pages": len(pdf.pages),
                "pdf_name": os.path.basename(pdf_path)
            }
            
            # Add image analysis if available
            if image_analysis and "error" not in image_analysis:
                result["image_analysis"] = image_analysis
            elif image_analysis and "error" in image_analysis:
                result["image_analysis_error"] = image_analysis["error"]

            return result
    except Exception as e:
        raise ValueError(f"Error processing PDF: {e}")


def extract_text_from_images(page) -> str:
    """
    Extract text from a PDF page using OCR on the rendered page image.

    Args:
        page: A pdfplumber page object

    Returns:
        Extracted text from the page via OCR
    """
    try:
        # Render the page to an image and OCR it
        pil_image = page.to_image(resolution=300).original
        text = pytesseract.image_to_string(pil_image)
        return text.strip()
    except Exception as e:
        print(f"Warning: OCR failed: {e}")
        return ""


def extract_all_tables(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract all tables from all pages in a PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of dictionaries with page content containing tables
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    results = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            try:
                tables = page.extract_tables() or []
                if tables:
                    results.append({
                        "page_number": page_num,
                        "tables": tables,
                        "text": page.extract_text() or "",
                        "pdf_name": os.path.basename(pdf_path)
                    })
            except Exception as e:
                # Skip problematic pages but continue processing
                print(f"Warning: Skipping page {page_num + 1} due to error: {e}")
                continue

    return results

def extract_pdf_images(
    pdf_path: str,
    output_dir: str = "extracted_images"
) -> List[Dict[str, Any]]:
    """
    Extract all embedded images from a PDF.

    Returns:
        List of image metadata dictionaries
    """

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

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

                    filename = (
                        f"{Path(pdf_path).stem}"
                        f"_page_{page_index+1}"
                        f"_img_{img_index+1}.{image_ext}"
                    )

                    image_path = os.path.join(
                        output_dir,
                        filename
                    )

                    with open(image_path, "wb") as f:
                        f.write(image_bytes)

                    extracted_images.append({
                        "page": page_index + 1,
                        "path": image_path,
                        "filename": filename,
                        "pdf": os.path.basename(pdf_path)
                    })

                except Exception as e:
                    print(f"Warning: Failed image extraction: {e}")

        return extracted_images

    except Exception as e:
        print(f"PDF image extraction failed: {e}")
        return []

def analyze_image_content(page) -> Dict[str, Any]:
    """
    Analyze image content in a PDF page using multimodal AI.
    
    Args:
        page: A pdfplumber page object
        
    Returns:
        Dictionary containing image analysis results
    """
    if not MULTIMODAL_AVAILABLE:
        return {"error": "Multimodal dependencies not available"}
    
    try:
        # Extract images from the page
        images = page.images
        if not images:
            return {"error": "No images found on page"}
        
        results = []
        
        for img_obj in images:
            if 'stream' not in img_obj:
                continue
                
            try:
                # Extract image data
                image_data = img_obj['stream'].get_data()
                pil_image = Image.open(io.BytesIO(image_data))
                
                # Convert to RGB if needed
                if pil_image.mode != 'RGB':
                    if pil_image.mode == 'CMYK':
                        pil_image = pil_image.convert('RGB')
                    elif pil_image.mode in ('L', 'P'):
                        pil_image = pil_image.convert('RGB')
                
                # Initialize model and processor if not already done
                if not hasattr(analyze_image_content, 'processor'):
                    analyze_image_content.processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base')
                    analyze_image_content.model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')
                
                # Generate general caption
                inputs = analyze_image_content.processor(pil_image, return_tensors='pt')
                out = analyze_image_content.model.generate(**inputs, max_length=50)
                caption = analyze_image_content.processor.decode(out[0], skip_special_tokens=True)
                
                # Generate more specific welding-related description
                text_input = "Describe any welding equipment, symbols, or technical details visible in this image:"
                inputs = analyze_image_content.processor(pil_image, text=text_input, return_tensors='pt')
                out = analyze_image_content.model.generate(**inputs, max_length=100)
                detailed_description = analyze_image_content.processor.decode(out[0], skip_special_tokens=True)
                
                # Try to extract specific welding information
                welding_prompts = [
                    "What welding process is shown (MIG, TIG, Stick, Flux-core)?",
                    "What materials are being welded?",
                    "What equipment settings or parameters are visible?",
                    "What safety equipment or precautions are shown?"
                ]
                
                welding_info = {}
                for prompt in welding_prompts:
                    try:
                        inputs = analyze_image_content.processor(pil_image, text=prompt, return_tensors='pt')
                        out = analyze_image_content.model.generate(**inputs, max_length=50)
                        answer = analyze_image_content.processor.decode(out[0], skip_special_tokens=True)
                        welding_info[prompt] = answer
                    except:
                        welding_info[prompt] = "Unable to determine"
                
                results.append({
                    "image_index": len(results),
                    "dimensions": f"{pil_image.width}x{pil_image.height}",
                    "mode": pil_image.mode,
                    "general_caption": caption,
                    "detailed_description": detailed_description,
                    "welding_analysis": welding_info,
                    "image_name": img_obj.get('name', 'Unknown')
                })
                
            except Exception as e:
                print(f"Warning: Could not analyze image: {e}")
                results.append({
                    "image_index": len(results),
                    "error": str(e)
                })
                continue
        
        if results:
            return {
                "images_analyzed": len(results),
                "results": results
            }
        else:
            return {"error": "No images could be analyzed"}
            
    except Exception as e:
        return {"error": f"Image analysis failed: {e}"}


def analyze_standalone_image(image_path: str) -> Dict[str, Any]:
    """
    Analyze a standalone image file (not from a PDF) using multimodal AI.
    Useful for analyzing product images, diagrams, and other standalone images.
    
    Args:
        image_path: Path to the image file (PNG, JPG, WEBP, etc.)
        
    Returns:
        Dictionary containing image analysis results
    """
    if not MULTIMODAL_AVAILABLE:
        return {"error": "Multimodal dependencies not available. Install transformers and torch."}
    
    try:
        if not os.path.exists(image_path):
            return {"error": f"Image file not found: {image_path}"}
        
        # Load and prepare image
        pil_image = Image.open(image_path)
        
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            if pil_image.mode == 'CMYK':
                pil_image = pil_image.convert('RGB')
            elif pil_image.mode in ('L', 'P'):
                pil_image = pil_image.convert('RGB')
        
        # Initialize model and processor if not already done
        if not hasattr(analyze_standalone_image, 'processor'):
            analyze_standalone_image.processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base')
            analyze_standalone_image.model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')
        
        # Generate general caption
        inputs = analyze_standalone_image.processor(pil_image, return_tensors='pt')
        out = analyze_standalone_image.model.generate(**inputs, max_length=50)
        caption = analyze_standalone_image.processor.decode(out[0], skip_special_tokens=True)
        
        # Generate detailed description
        text_input = "Provide a detailed technical description of this image, including any equipment, components, or features visible:"
        inputs = analyze_standalone_image.processor(pil_image, text=text_input, return_tensors='pt')
        out = analyze_standalone_image.model.generate(**inputs, max_length=150)
        detailed_description = analyze_standalone_image.processor.decode(out[0], skip_special_tokens=True)
        
        # Generate specific analysis prompts
        analysis_prompts = [
            "What type of welding equipment or product is shown?",
            "What are the key components or features visible?",
            "What materials or construction methods are apparent?",
            "What is the likely purpose or function of this equipment?",
            "Are there any safety features or design elements visible?"
        ]
        
        specific_analysis = {}
        for prompt in analysis_prompts:
            try:
                inputs = analyze_standalone_image.processor(pil_image, text=prompt, return_tensors='pt')
                out = analyze_standalone_image.model.generate(**inputs, max_length=80)
                answer = analyze_standalone_image.processor.decode(out[0], skip_special_tokens=True)
                specific_analysis[prompt] = answer
            except Exception as e:
                specific_analysis[prompt] = f"Unable to analyze: {e}"
        
        return {
            "image_path": image_path,
            "image_name": os.path.basename(image_path),
            "dimensions": f"{pil_image.width}x{pil_image.height}",
            "format": pil_image.format,
            "mode": pil_image.mode,
            "general_caption": caption,
            "detailed_description": detailed_description,
            "specific_analysis": specific_analysis
        }
        
    except Exception as e:
        return {"error": f"Image analysis failed: {e}"}


def get_pdf_info(pdf_path: str) -> Dict[str, Any]:
    """
    Get basic information about a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary with PDF metadata
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        return {
            "filename": os.path.basename(pdf_path),
            "total_pages": len(pdf.pages),
            "file_size": os.path.getsize(pdf_path)
        }


def search_pdfs_for_tables(pdf_dir: str = "files/") -> Dict[str, List[int]]:
    """
    Search all PDFs in a directory and return which pages contain tables.

    Args:
        pdf_dir: Directory containing PDF files (default: "files/")

    Returns:
        Dictionary mapping PDF filenames to lists of page numbers with tables
    """
    if not os.path.exists(pdf_dir):
        raise FileNotFoundError(f"Directory not found: {pdf_dir}")

    results = {}

    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            try:
                tables_info = extract_all_tables(pdf_path)
                page_numbers = [info['page_number'] + 1 for info in tables_info]  # Convert to 1-indexed
                results[filename] = page_numbers
            except Exception as e:
                print(f"Warning: Could not process {filename}: {e}")
                results[filename] = []

    return results


if __name__ == "__main__":
    # Example usage
    pdf_file = "owner_manual.pdf"
    
    # Extract from page 14 (index 13)
    try:
        content = extract_page_content(pdf_file, page_number=13)
        if content and content["tables"]:
            print(f"Page {content['page_number'] + 1} of {content['total_pages']}")
            print(f"Text preview: {content['text'][:200]}...")
            print(f"\nFound {len(content['tables'])} table(s)")
            print("\nFirst table:")
            for row in content["tables"][0]:
                print(row)
        else:
            print(f"No tables found on page 14")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")