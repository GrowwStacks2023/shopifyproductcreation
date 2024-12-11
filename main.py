import logging
import os
import argparse
from config import read_config
from shopify import process_pdfs, activate_products, delete_products
from google_drive import process_uploaded_files
from file_operations import send_csv_to_webhook

def parse_arguments():
    # Setting up command-line argument parsing
    parser = argparse.ArgumentParser(description="Shopify Product Management")
    parser.add_argument("--source_folder", help="Path to the source folder", required=True)
    parser.add_argument("--store_url", help="Your Shopify store URL", required=True)
    parser.add_argument("--access_token", help="Access token for Shopify", required=True)
    parser.add_argument("--credentials_path", help="Path to the Google Drive credentials JSON", required=True)
    parser.add_argument("--year", help="Enter the year (e.g., 2024)", required=True)
    parser.add_argument("--quarter", help="Enter the quarter (1-4)", required=True)
    parser.add_argument("--markets_to_process", type=int, help="Enter the number of markets to process", default=None)
    
    # Parsing the arguments
    return parser.parse_args()

def main():
    logging.info("Starting main program execution")
    
    # Parse command-line arguments
    args = parse_arguments()

    # Values from the command line arguments
    source_folder = args.source_folder
    store_url = args.store_url
    access_token = args.access_token
    credentials_path = args.credentials_path
    year = args.year
    quarter = args.quarter
    markets_to_process = args.markets_to_process

    logging.info(f"Using source folder: {source_folder}")
    logging.info(f"Using store URL: {store_url}")
    logging.info(f"Using Google credentials path: {credentials_path}")
    logging.info(f"Processing year: {year}, Quarter: {quarter}")
    logging.info(f"Markets to process: {'all' if markets_to_process is None else markets_to_process}")

    # Read the config file (if required for additional settings)
    config_path = os.path.join(source_folder, 'config.json')
    logging.info(f"Looking for config file at: {config_path}")
    
    if os.path.exists(config_path):
        config = read_config(config_path)
        logging.info(f"Config file loaded: {config_path}")
    else:
        logging.warning(f"Config file not found at {config_path}. Proceeding without it.")

    # Process PDFs and create products
    process_pdfs(source_folder, store_url, access_token, config, year, quarter, markets_to_process)
    
    # Process uploaded files and update with Google Drive links
    csv_file_path = os.path.join(source_folder, 'product_pdf_data.csv')
    if os.path.exists(csv_file_path):
        print("\nUploading files to Google Drive...")
        process_uploaded_files(csv_file_path, store_url, access_token, credentials_path)
    else:
        logging.error("CSV file not found!")
    
    # Send CSV to the webhook
    send_csv_to_webhook(csv_file_path, "https://hook.eu1.make.com/wdcdvyyfqli6rwhgj51jnu2d2yqrxpeg")
    
    # Handle final action (Activate/Delete/Skip)
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
