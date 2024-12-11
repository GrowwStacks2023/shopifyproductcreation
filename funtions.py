import os
import json
import requests
import base64
import re
import csv
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from typing import Optional

# Enhanced logging configuration
import logging
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
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            logging.info(f"Image successfully encoded to base64.")
            
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
    
    cleaned_string = input_string.lower()
    cleaned_string = re.sub(r'\.jpe?g$', '', cleaned_string)
    cleaned_string = re.sub(r'[^a-z0-9]', ' ', cleaned_string)
    cleaned_string = ' '.join(cleaned_string.split())
    
    logging.info(f"Final cleaned string: '{cleaned_string}'")
    
    return cleaned_string

def generate_csv_header(csv_file_path):
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, 'w', newline='') as csvfile:
            fieldnames = ['Product ID', 'PDF Path', 'Drive URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

def update_csv_with_drive_url(csv_file_path: str, product_id: str, drive_url: str):
    logging.info(f"Updating CSV with Drive URL for product {product_id}")
    
    try:
        df = pd.read_csv(csv_file_path, names=['Product ID', 'PDF Path', 'Drive URL'], skiprows=1)
        df.loc[df['Product ID'] == product_id, 'Drive URL'] = drive_url
        df.to_csv(csv_file_path, index=False, columns=['Product ID', 'PDF Path', 'Drive URL'])
        logging.info(f"Successfully updated CSV with Drive URL for product {product_id}")
    except Exception as e:
        logging.error(f"Error updating CSV with Drive URL: {e}")
        raise

def insert_data_to_csv(csv_file_path, product_id, pdf_path):
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
    logging.info(f"Processing uploaded files from CSV: {csv_path}")
    
    try:
        drive_service = setup_google_drive(credentials_path)
        df = pd.read_csv(csv_path, names=['Product ID', 'PDF Path', 'Drive URL'], skiprows=1)
        logging.info(f"Found {len(df)} entries in CSV")
        
        for index, row in df.iterrows():
            product_id = row['Product ID']
            pdf_path = row['PDF Path']
            
            if pd.notna(row['Drive URL']):
                logging.info(f"Skipping product {product_id} - already has Drive URL")
                continue
                
            logging.info(f"Processing product {product_id} with PDF: {pdf_path}")
            
            try:
                file_url = upload_to_drive(drive_service, pdf_path)
                update_csv_with_drive_url(csv_path, product_id, file_url)
                update_product_with_file(store_url, product_id, file_url, access_token)
                
                logging.info(f"Successfully processed product {product_id}")
            except Exception as e:
                logging.error(f"Error processing product {product_id}: {e}")
                continue
                
        logging.info("Completed processing all files")
    except Exception as e:
        logging.error(f"Error in process_uploaded_files: {e}")
        raise
