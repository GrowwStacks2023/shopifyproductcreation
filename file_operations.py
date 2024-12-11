import logging
import os
import csv
import pandas as pd

def generate_csv_header(csv_file_path):
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, 'w', newline='') as csvfile:
            fieldnames = ['Product ID', 'PDF Path', 'Drive URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

def insert_data_to_csv(csv_file_path, product_id, pdf_path):
    try:
        with open(csv_file_path, 'a', newline='') as csvfile:
            fieldnames = ['Product ID', 'PDF Path', 'Drive URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'Product ID': product_id, 'PDF Path': pdf_path, 'Drive URL': ''})
        logging.info(f"Inserted data into CSV: Product ID = {product_id}, PDF Path = {pdf_path}")
    except Exception as e:
        logging.error(f"Error inserting data into CSV: {e}")

def update_csv_with_drive_url(csv_file_path, product_id, drive_url):
    try:
        df = pd.read_csv(csv_file_path)
        df.loc[df['Product ID'] == product_id, 'Drive URL'] = drive_url
        df.to_csv(csv_file_path, index=False)
        logging.info(f"Updated CSV with Drive URL for Product ID = {product_id}")
    except Exception as e:
        logging.error(f"Error updating CSV with Drive URL: {e}")

def send_csv_to_webhook(csv_file_path, webhook_url):
    try:
        with open(csv_file_path, 'rb') as f:
            files = {'file': (os.path.basename(csv_file_path), f)}
            response = requests.post(webhook_url, files=files)
            if response.status_code == 200:
                logging.info(f"Successfully sent CSV to webhook: {webhook_url}")
            else:
                logging.error(f"Failed to send CSV to webhook. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error sending CSV to webhook: {e}")
