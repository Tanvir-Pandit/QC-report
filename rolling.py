import fitz
import os
import tempfile
import easyocr

# Create a temporary directory to store images
with tempfile.TemporaryDirectory() as temp_dir:
    pdf_path = 'roling/null (2).pdf'
    pdf_document = fitz.open(pdf_path)

    # Save images in the temporary folder
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        image = page.get_pixmap()
        image.save(os.path.join(temp_dir, f'page_{page_num}.png'))

    # Initialize the EasyOCR reader with the desired language(s)
    reader = easyocr.Reader(['en'])  # You can specify the language(s) you want to recognize

    # List of image file paths from the temporary folder
    image_paths = [os.path.join(temp_dir, f'page_{page_num}.png') for page_num in range(pdf_document.page_count)]

    for image_path in image_paths:
        # Perform OCR on the image
        result = reader.readtext(image_path)

        # Print the recognized text for each image
        print(f"OCR result for {image_path}:")
        for detection in result:
            text = detection[1]
            print(text)

