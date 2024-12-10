# Shopify Product Creation & File Upload Automation

This project automates the process of creating products on Shopify, uploading PDF files to Google Drive, and updating product details with Google Drive URLs. It also handles image matching, product activation, and deletion. The workflow integrates with a CSV file for tracking product details.

## Features

- **Create Products on Shopify**: Automatically create products on Shopify with metadata such as title, price, description, and collections.
- **Image Attachment**: Matches images from a specified folder to products and attaches them to the Shopify product.
- **Upload PDFs to Google Drive**: Upload PDF files from a folder to Google Drive and retrieve a shareable link.
- **Update CSV File**: Store product information, including Drive URLs, in a CSV file.
- **Activate/Deactivate Products**: Update the product status on Shopify to `active` or delete products as required.
- **Webhook Integration**: Sends the final CSV file to a specified webhook.

## Prerequisites

- Python 3.x
- Required Python Libraries:
  - `requests`
  - `pandas`
  - `google-auth`
  - `google-api-python-client`
  - `google-auth-httplib2`
  - `google-auth-oauthlib`
  
  You can install them via `pip`:
  ```bash
  pip install requests pandas google-auth google-api-python-client google-auth-httplib2 google-auth-oauthlib
