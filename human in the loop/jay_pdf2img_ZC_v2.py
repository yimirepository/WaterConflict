import os
import fitz  # PyMuPDF
from PIL import Image
import io
from tqdm import tqdm
import concurrent.futures

# Define the folder containing PDF files
pdf_folder = 'reference'  # Update this path to the folder containing the literatures
output_folder = 'img2'  # Update this path to the output folder

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

def convert_doc_to_images_and_extract_text(pdf_path, output_folder):

    #Extract text from the PDF document and save any images found.
    #Returns the extracted text and a list of image file paths.

    try:
        print(f"Processing file: {pdf_path}")
        doc = fitz.open(pdf_path)
        extracted_text = ""
        image_files = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Extract text from the page
            extracted_text += page.get_text("text")

            # Extract images from the page
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # Save the image to the output folder
                image_filename = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page_{page_num+1}_img_{img_index+1}.{image_ext}"
                image_path = os.path.join(output_folder, image_filename)

                # Use PIL to save the image
                image = Image.open(io.BytesIO(image_bytes))

                #UNCOMMENT TO GET IMAGES SAVED

                #image.save(image_path)
                #image_files.append(image_path)
                #print(f"Saved image: {image_path}")

        return image_files, extracted_text

    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        return [], ""

# Process all PDFs in the folder
def process_pdfs(pdf_folder, output_folder):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for pdf_file in os.listdir(pdf_folder):
            if pdf_file.endswith('.pdf'):
                pdf_path = os.path.join(pdf_folder, pdf_file)
                futures.append(executor.submit(process_single_pdf, pdf_path, output_folder))

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            images, text = future.result()
            print(f"Processed {len(images)} images for a file.")

def process_single_pdf(pdf_path, output_folder):
    # Convert to images and extract text
    images, text = convert_doc_to_images_and_extract_text(pdf_path, output_folder)

    # Create a text file name based on the PDF file name
    text_file_name = os.path.splitext(os.path.basename(pdf_path))[0] + ".txt"
    text_file_path = os.path.join(output_folder, text_file_name)

    # Save the extracted text to a text file
    with open(text_file_path, 'w', encoding='utf-8') as text_file:
        text_file.write(text)

    print(f"Extracted text saved to: {text_file_path}")

    return images, text

# Start processing
process_pdfs(pdf_folder, output_folder)
