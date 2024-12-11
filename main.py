from config import read_config
from shopify import process_pdfs, activate_products, delete_products
from google_drive import process_uploaded_files
from file_operations import send_csv_to_webhook
import logging
import os

def main():
    logging.info("Starting main program execution")
    
    # Hardcoded values (you can modify these as needed)
    source_folder = "/home/vyavasthapak/Desktop/Store/2024Q3"
    store_url = "project-digital-shop.myshopify.com"
    access_token = "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"
    credentials_path = "/home/vyavasthapak/Desktop/Bradely/python-444308-6e5be7255eac.json"
    
    logging.info(f"Using source folder: {source_folder}")
    logging.info(f"Using store URL: {store_url}")
    
    # Get user inputs
    year = input("Enter the year (e.g., 2024): ")
    logging.info(f"User entered year: {year}")
    
    quarter = input("Enter the quarter (1-4): ")
    logging.info(f"User entered quarter: {quarter}")
    
    markets_to_process = input("Enter markets to process (leave empty for all): ")
    logging.info(f"User entered markets to process: {markets_to_process or 'all'}")
    
    if markets_to_process:
        markets_to_process = int(markets_to_process)
    
    # Read config
    config_path = os.path.join(source_folder, 'config.json')
    logging.info(f"Looking for config file at: {config_path}")
    
    if not os.path.exists(config_path):
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
    
    send_csv_to_webhook(csv_file_path, "https://hook.eu1.make.com/wdcdvyyfqli6rwhgj51jnu2d2yqrxpeg")
    
    # Handle final action
    while True:
        action = input("Do you want to Activate or Delete the products? (Activate/Delete/Skip): ").strip().lower()
        logging.info(f"User selected action: {action}")
        
        if action in ['activate', 'delete', 'skip']:
            if action == 'activate':
                activate_products(store_url, access_token, csv_file_path)
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
