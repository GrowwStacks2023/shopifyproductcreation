import json
import requests
import logging
from typing import Optional
from file_operations import generate_csv_header, insert_data_to_csv, update_csv_with_drive_url
from google_drive import upload_to_drive

def create_product(store_url: str, product_data: dict, access_token: str):
    logging.info(f"Attempting to create product: {product_data['product']['title']}")
    shopify_url = f"https://{store_url}/admin/api/2024-01/products.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(shopify_url, json=product_data, headers=headers)
        if response.status_code == 201:
            product_title = product_data['product']['title']
            product_id = response.json()['product']['id']
            logging.info(f"Successfully created product: {product_title} (ID: {product_id})")
            return response.json()
        else:
            logging.error(f"Failed to create product: {product_data['product']['title']}")
            raise Exception(f"Failed to create product: {response.status_code} {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error while creating product: {e}")
        raise

def process_pdfs(source_folder: str, store_url: str, access_token: str, config: dict, year: str, quarter: str, markets_to_process: Optional[int] = None):
    logging.info(f"Starting PDF processing in folder: {source_folder}")
    pdf_files = [f for f in Path(source_folder).rglob('*.pdf')]
    if markets_to_process:
        pdf_files = pdf_files[:markets_to_process]

    image_folder = Path(source_folder) / 'images'
    image_files = list(image_folder.glob('*.jp*g'))
    
    csv_file_path = os.path.join(source_folder, 'product_pdf_data.csv')
    generate_csv_header(csv_file_path)

    for pdf_file in pdf_files:
        title = pdf_file.stem.split('-', 2)[-1].strip()
        cleaned_title = clean_string(title)
        
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
            product_response = create_product(store_url, product_data, access_token)
            product_id = product_response.get('product', {}).get('id')

            if product_id:
                insert_data_to_csv(csv_file_path, product_id, str(pdf_file))

                matching_image = None
                for image_path in image_files:
                    cleaned_image_name = clean_string(image_path.stem)
                    if cleaned_title in cleaned_image_name or cleaned_image_name in cleaned_title:
                        matching_image = image_path
                        break

                if matching_image:
                    attach_image_to_product(store_url, product_id, str(matching_image), access_token)
        except Exception as e:
            logging.error(f"Error processing {pdf_file.name}: {e}")
            continue

def activate_products(store_url: str, access_token: str, csv_file_path: str):
    logging.info("Activating products...")
    df = pd.read_csv(csv_file_path)
    for _, row in df.iterrows():
        product_id = row['Product ID']
        update_url = f"https://{store_url}/admin/api/2024-01/products/{product_id}.json"
        headers = {"X-Shopify-Access-Token": access_token, "Content-Type": "application/json"}
        update_data = {"product": {"id": product_id, "status": "active"}}

        try:
            response = requests.put(update_url, json=update_data, headers=headers)
            if response.status_code == 200:
                logging.info(f"Successfully activated product {product_id}")
            else:
                logging.error(f"Failed to activate product {product_id}")
        except Exception as e:
            logging.error(f"Error activating product {product_id}: {e}")
