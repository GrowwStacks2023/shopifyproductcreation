import os
import json
import requests
from pathlib import Path
import logging
import re
from typing import Optional
import base64
import csv
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Enhanced logging configuration
logging.basicConfig(
    filename="CreateProducts.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def read_config(config_path: str):
    logging.info(f"Attempting to read config file from: {config_path}")
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            logging.info(f"Successfully loaded config with keys: {list(config_data.keys())}")
            return config_data
    except Exception as e:
        logging.error(f"Failed to read config file: {e}")
        raise

def create_product(store_url: str, product_data: dict, access_token: str):
    logging.info(f"Attempting to create product: {product_data['product']['title']}")
    logging.info(f"Product data being sent: {json.dumps(product_data, indent=2)}")
    
    shopify_url = f"https://{store_url}/admin/api/2024-01/products.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }

    try:
        logging.info(f"Sending POST request to Shopify API: {shopify_url}")
        response = requests.post(shopify_url, json=product_data, headers=headers)
        
        if response.status_code == 201:
            product_title = product_data['product']['title']
            product_id = response.json()['product']['id']
            logging.info(f"Successfully created product: {product_title} (ID: {product_id})")
            return response.json()
        else:
            logging.error(f"Failed to create product: {product_data['product']['title']}")
            logging.error(f"Response status code: {response.status_code}")
            logging.error(f"Response body: {response.text}")
            raise Exception(f"Failed to create product: {response.status_code} {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error while creating product: {e}")
        raise

def attach_image_to_product(store_url: str, product_id: int, image_path: str, access_token: str):
    logging.info(f"Attempting to attach image to product {product_id}")
    logging.info(f"Image path: {image_path}")
    
    upload_url = f"https://{store_url}/admin/api/2024-01/products/{product_id}/images.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }

    try:
        logging.info(f"Reading image file: {image_path}")
        with open(image_path, "rb") as image_file:
            # Encode the image to base64
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            logging.info(f"Image successfully encoded to base64.")
            
            # Create the data payload for the image upload
            image_data = {
                "image": {
                    "attachment": encoded_image,
                    "filename": os.path.basename(image_path)
                }
            }

            logging.info(f"Sending image upload request to: {upload_url}")
            response = requests.post(upload_url, headers=headers, json=image_data)
        
        if response.status_code == 201:
            logging.info(f"Successfully uploaded image for product {product_id}")
            logging.info(f"Image response: {response.json()}")
        else:
            logging.error(f"Failed to upload image for product {product_id}")
            logging.error(f"Response status code: {response.status_code}")
            logging.error(f"Response body: {response.text}")
            raise Exception(f"Failed to upload image: {response.status_code} {response.text}")

    except Exception as e:
        logging.error(f"Error during image upload for product {product_id}: {e}")
        raise

def clean_string(input_string: str) -> str:
    logging.info(f"Cleaning string: '{input_string}'")
    
    # Convert to lowercase
    cleaned_string = input_string.lower()
    logging.info(f"After lowercase: '{cleaned_string}'")
    
    # Remove file extensions
    cleaned_string = re.sub(r'\.jpe?g$', '', cleaned_string)
    logging.info(f"After removing extensions: '{cleaned_string}'")
    
    # Replace special characters with spaces
    cleaned_string = re.sub(r'[^a-z0-9]', ' ', cleaned_string)
    logging.info(f"After removing special characters: '{cleaned_string}'")
    
    # Remove extra spaces and join with single spaces
    cleaned_string = ' '.join(cleaned_string.split())
    logging.info(f"Final cleaned string: '{cleaned_string}'")
    
    return cleaned_string

def generate_csv_header(csv_file_path):
    """Generate the CSV file header if it doesn't exist."""
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, 'w', newline='') as csvfile:
            fieldnames = ['Product ID', 'PDF Path', 'Drive URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
def update_csv_with_drive_url(csv_file_path: str, product_id: str, drive_url: str):
    """Update the CSV file with the Google Drive URL for a specific product."""
    logging.info(f"Updating CSV with Drive URL for product {product_id}")
    
    try:
        # Read existing CSV into DataFrame with explicit column names
        df = pd.read_csv(csv_file_path, names=['Product ID', 'PDF Path', 'Drive URL'], skiprows=1)
        
        # Update Drive URL for matching Product ID
        df.loc[df['Product ID'] == product_id, 'Drive URL'] = drive_url
        
        # Write updated DataFrame back to CSV
        df.to_csv(csv_file_path, index=False, columns=['Product ID', 'PDF Path', 'Drive URL'])
        logging.info(f"Successfully updated CSV with Drive URL for product {product_id}")
    except Exception as e:
        logging.error(f"Error updating CSV with Drive URL: {e}")
        raise
def insert_data_to_csv(csv_file_path, product_id, pdf_path):
    """Insert product data into CSV after product creation."""
    try:
        with open(csv_file_path, 'a', newline='') as csvfile:
            fieldnames = ['Product ID', 'PDF Path', 'Drive URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({
                'Product ID': product_id,
                'PDF Path': pdf_path,
                'Drive URL': ''
            })
        logging.info(f"Inserted data into CSV: Product ID = {product_id}, PDF Path = {pdf_path}")
    except Exception as e:
        logging.error(f"Error inserting data into CSV: {e}")
        raise

def setup_google_drive(credentials_path: str):
    """Setup Google Drive API client."""
    logging.info(f"Setting up Google Drive client with credentials from: {credentials_path}")
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        service = build('drive', 'v3', credentials=credentials)
        logging.info("Successfully set up Google Drive client")
        return service
    except Exception as e:
        logging.error(f"Failed to setup Google Drive client: {e}")
        raise

def upload_to_drive(service, file_path: str, folder_id: Optional[str] = None) -> str:
    """Upload a file to Google Drive and return its shareable link."""
    logging.info(f"Uploading file to Google Drive: {file_path}")
    try:
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id] if folder_id else []
        }
        
        media = MediaFileUpload(
            file_path,
            mimetype='application/pdf',
            resumable=True
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        # Set file to be accessible via link
        service.permissions().create(
            fileId=file['id'],
            body={'type': 'anyone', 'role': 'reader'},
            fields='id'
        ).execute()
        
        logging.info(f"Successfully uploaded file. File ID: {file['id']}")
        return file['webViewLink']
    except Exception as e:
        logging.error(f"Failed to upload file to Google Drive: {e}")
        raise

def update_product_with_file(store_url: str, product_id: int, file_url: str, access_token: str):
    """Update Shopify product with digital download URL."""
    logging.info(f"Updating product {product_id} with file URL")
    
    update_url = f"https://{store_url}/admin/api/2024-01/products/{product_id}.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    update_data = {
        "product": {
            "id": product_id,
            "variants": [{
                "id": product_id,
                "metafields": [{
                    "key": "digital_download",
                    "value": file_url,
                    "type": "single_line_text_field",
                    "namespace": "custom"
                }]
            }]
        }
    }
    
    try:
        response = requests.put(update_url, json=update_data, headers=headers)
        if response.status_code == 200:
            logging.info(f"Successfully updated product {product_id} with file URL")
        else:
            logging.error(f"Failed to update product: {response.status_code} {response.text}")
            raise Exception(f"Failed to update product: {response.status_code}")
    except Exception as e:
        logging.error(f"Error updating product with file URL: {e}")
        raise

def process_uploaded_files(csv_path: str, store_url: str, access_token: str, credentials_path: str):
    """Process uploaded files from CSV and upload them to Google Drive."""
    logging.info(f"Processing uploaded files from CSV: {csv_path}")
    
    try:
        # Setup Google Drive service
        drive_service = setup_google_drive(credentials_path)
        
        # Read CSV file with explicit column names
        df = pd.read_csv(csv_path, names=['Product ID', 'PDF Path', 'Drive URL'], skiprows=1)
        logging.info(f"Found {len(df)} entries in CSV")
        
        # Process each row
        for index, row in df.iterrows():
            product_id = row['Product ID']
            pdf_path = row['PDF Path']
            
            # Skip if already has Drive URL
            if pd.notna(row['Drive URL']):
                logging.info(f"Skipping product {product_id} - already has Drive URL")
                continue
                
            logging.info(f"Processing product {product_id} with PDF: {pdf_path}")
            
            try:
                # Upload file to Google Drive
                file_url = upload_to_drive(drive_service, pdf_path)
                
                # Update CSV with Drive URL
                update_csv_with_drive_url(csv_path, product_id, file_url)
                
                # Update product with file URL
                update_product_with_file(store_url, product_id, file_url, access_token)
                
                logging.info(f"Successfully processed product {product_id}")
            except Exception as e:
                logging.error(f"Error processing product {product_id}: {e}")
                continue
                
        logging.info("Completed processing all files")
    except Exception as e:
        logging.error(f"Error in process_uploaded_files: {e}")
        raise


def process_pdfs(source_folder: str, store_url: str, access_token: str, config: dict, year: str, quarter: str, markets_to_process: Optional[int] = None):
    logging.info(f"Starting PDF processing in folder: {source_folder}")
    logging.info(f"Processing for Year: {year}, Quarter: {quarter}")
    
    # Get PDF files
    pdf_files = [f for f in Path(source_folder).rglob('*.pdf')]
    logging.info(f"Found {len(pdf_files)} PDF files")
    
    if markets_to_process:
        logging.info(f"Limiting processing to {markets_to_process} markets")
        pdf_files = pdf_files[:markets_to_process]
    
    # Get image files
    image_folder = Path(source_folder) / 'images'
    image_files = list(image_folder.glob('*.jp*g'))
    logging.info(f"Found {len(image_files)} image files in {image_folder}")
    
    # Define the CSV file path
    csv_file_path = os.path.join(source_folder, 'product_pdf_data.csv')
    generate_csv_header(csv_file_path)  # Create header if CSV doesn't exist

    for pdf_file in pdf_files:
        logging.info(f"\n{'='*50}")
        logging.info(f"Processing PDF: {pdf_file.name}")
        
        # Extract title from PDF file
        title = pdf_file.stem.split('-', 2)[-1].strip()
        logging.info(f"Extracted title: '{title}'")
        
        # Clean title for comparison
        cleaned_title = clean_string(title)
        logging.info(f"Cleaned title for matching: '{cleaned_title}'")
        
        # Prepare product data
        product_data = {
            "product": {
                "title": title,
                "body_html": config["Description"],
                "vendor": "Your Vendor",
                "product_type": "Digital Product",
                "status": "draft",
                "price": config["Price"],
                "compare_at_price": config["CompareToPrice"],
                "collections": config["Collections"],
                "search_engine_description": config["SearchEngineDescription"]
            }
        }
        
        try:
            # Create product in Shopify
            logging.info("Creating product in Shopify...")
            product_response = create_product(store_url, product_data, access_token)
            product_id = product_response.get('product', {}).get('id')

            if product_id:
                logging.info(f"Product created successfully: Product ID {product_id}")

                # Insert product ID and PDF file path into CSV immediately after creation
                insert_data_to_csv(csv_file_path, product_id, str(pdf_file))

                # Start image matching process
                matching_image = None
                for image_path in image_files:
                    cleaned_image_name = clean_string(image_path.stem)
                    logging.info(f"Comparing with image: '{image_path.name}'")
                    logging.info(f"Cleaned image name: '{cleaned_image_name}'")
                    
                    if cleaned_title in cleaned_image_name or cleaned_image_name in cleaned_title:
                        logging.info(f"Found matching image: {image_path.name}")
                        matching_image = image_path
                        break
                    else:
                        logging.info("No match, continuing to next image")
                
                if matching_image:
                    logging.info(f"Attaching image to product: {matching_image}")
                    attach_image_to_product(store_url, product_id, str(matching_image), access_token)
                else:
                    logging.warning(f"No matching image found for product {product_id} (Title: {title})")
                    
        except Exception as e:
            logging.error(f"Error processing {pdf_file.name}: {e}")
            continue

def activate_products(store_url: str, access_token: str, csv_file_path: str):
    logging.info("Starting product activation process...")
    
    # Read the CSV file to get the product IDs
    try:
        # Read the CSV file with pandas to get product IDs
        df = pd.read_csv(csv_file_path, names=['Product ID', 'PDF Path', 'Drive URL'], skiprows=1)
        logging.info(f"Found {len(df)} products in the CSV file")
        
        # Loop through each row and update the product status
        for index, row in df.iterrows():
            product_id = row['Product ID']
            logging.info(f"Activating product ID: {product_id}")
            
            update_url = f"https://{store_url}/admin/api/2024-01/products/{product_id}.json"
            headers = {
                "X-Shopify-Access-Token": access_token,
                "Content-Type": "application/json"
            }
            
            update_data = {
                "product": {
                    "id": product_id,
                    "status": "active"
                }
            }
            
            try:
                response = requests.put(update_url, json=update_data, headers=headers)
                if response.status_code == 200:
                    logging.info(f"Successfully activated product {product_id}")
                else:
                    logging.error(f"Failed to activate product {product_id}. Status code: {response.status_code}, Response: {response.text}")
            except Exception as e:
                logging.error(f"Error activating product {product_id}: {e}")
    
    except Exception as e:
        logging.error(f"Error reading CSV or updating products: {e}")
        raise

def delete_products(store_url: str, access_token: str):
    logging.info("Starting product deletion process...")
    # Add implementation here
    pass

import requests
import io

def send_csv_to_webhook(csv_file_path: str, webhook_url: str):
    """Send the CSV file as buffer data to the provided webhook URL."""
    logging.info(f"Sending CSV file to webhook: {webhook_url}")
    
    try:
        # Read the CSV file as binary (buffer)
        with open(csv_file_path, 'rb') as f:
            csv_data = io.BytesIO(f.read())
        
        # Prepare the payload for the webhook
        files = {'file': (csv_file_path, csv_data, 'text/csv')}
        
        # Send POST request to the webhook URL
        response = requests.post(webhook_url, files=files)
        
        if response.status_code == 200:
            logging.info("Successfully sent CSV to the webhook")
        else:
            logging.error(f"Failed to send CSV to webhook. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        logging.error(f"Error sending CSV to webhook: {e}")
        raise

def main():
    logging.info("Starting main program execution")
    
    # Prompt user for dynamic values
    source_folder = input("Enter the source folder path (e.g., /home/user/Store/2024Q3): ").strip()
    logging.info(f"User entered source folder: {source_folder}")
    
    store_url = input("Enter the Shopify store URL (e.g., project-digital-shop.myshopify.com): ").strip()
    logging.info(f"User entered store URL: {store_url}")
    
    access_token = input("Enter the Shopify access token: ").strip()
    logging.info(f"User entered access token.")

    # Get user inputs for year and quarter
    year = input("Enter the year (e.g., 2024): ")
    logging.info(f"User entered year: {year}")
    
    quarter = input("Enter the quarter (1-4): ")
    logging.info(f"User entered quarter: {quarter}")
    
    markets_to_process = input("Enter markets to process (leave empty for all): ")
    logging.info(f"User entered markets to process: {markets_to_process or 'all'}")
    
    if markets_to_process:
        markets_to_process = int(markets_to_process)
    
    # Read config
    config_path = Path(source_folder) / 'config.json'
    logging.info(f"Looking for config file at: {config_path}")
    
    if not config_path.exists():
        logging.error("config.json file not found!")
        return
    
    config = read_config(config_path)
    
    # Process PDFs and create products
    process_pdfs(source_folder, store_url, access_token, config, year, quarter, markets_to_process)

    # Process uploaded files and update with Google Drive links
    csv_file_path = os.path.join(source_folder, 'product_pdf_data.csv')
    if os.path.exists(csv_file_path):
        print("\nUploading files to Google Drive...")
        process_uploaded_files(csv_file_path, store_url, access_token, credentials_path)
    else:
        logging.error("CSV file not found!")
    
    # Send the CSV to the webhook
    send_csv_to_webhook(csv_file_path, "https://hook.eu1.make.com/wdcdvyyfqli6rwhgj51jnu2d2yqrxpeg")
    
    # Handle final action
    while True:
        action = input("Do you want to Activate or Delete the products? (Activate/Delete/Skip): ").strip().lower()
        logging.info(f"User selected action: {action}")
        
        if action in ['activate', 'delete', 'skip']:
            if action == 'activate':
                activate_products(store_url, access_token, csv_file_path)  # Pass the CSV path to the activation function
            elif action == 'delete':
                delete_products(store_url, access_token)
            else:
                logging.info("Skipping product activation/deletion")
            break
        else:
            logging.warning(f"Invalid action entered: {action}")
            print("Invalid input. Please enter 'Activate', 'Delete', or 'Skip'.")

    logging.info("Program execution completed")


if __name__ == "__main__":
    logging.info("="*50)
    logging.info("Starting new program execution")
    main()
