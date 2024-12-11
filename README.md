Certainly! Here’s a **detailed README.md** file for your script, with an extended explanation of each section, including commands and expected outputs.

```markdown
# Shopify Product Management Automation Script

This Python script automates the process of managing Shopify products. It integrates several functions, such as generating Shopify product data from PDFs, uploading the data to Google Drive, sending product data to a webhook, and optionally activating or deleting products on your Shopify store. 

This script is ideal for automating and streamlining the process of managing product listings, especially when handling multiple files and interacting with external services like Shopify and Google Drive.

---

## Features

- **Process PDFs and Create Shopify Products**: Automatically processes PDF files in the given source folder and uses them to create product listings on Shopify.
- **Google Drive Integration**: Uploads the processed product data to Google Drive and adds links back to the CSV file.
- **Webhook Integration**: Sends product data (in CSV format) to a webhook URL for further processing or storage.
- **Product Activation/Deletion**: Provides an option to activate or delete the products on your Shopify store after processing.

---

## Requirements

Before running this script, make sure you have the following installed:

### Python Libraries
Install the necessary Python libraries by running the following command:

```bash
pip install -r requirements.txt
```

The script requires these Python libraries:
- `argparse` – For parsing command-line arguments.
- `logging` – For logging program execution.
- `os` – For file management tasks.
- `shopify` – To interact with the Shopify API.
- `google_drive` – To upload files to Google Drive.
- `file_operations` – For sending data to a webhook.

### Credentials
- **Google Drive API Credentials**: You need a Google Drive API credentials file (`credentials.json`). Set this up by following the guide in [Google's API documentation](https://developers.google.com/drive/api/v3/quickstart/python).
  
- **Shopify API Access**: You’ll need a valid Shopify API access token (`access_token`) and your store URL (`store_url`). Ensure that your API credentials have sufficient permissions to manage products on your Shopify store.

---

## Setup

### 1. Clone or Download the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/your-repo/shopify-product-management.git
cd shopify-product-management
```

### 2. Modify the Configuration File

In the `config.json` file, define any static configuration settings required for processing the product PDFs. The script will automatically read this file during execution.

### 3. Install Dependencies

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

### 4. Google Drive and Shopify Setup

Ensure your Google Drive API credentials (`credentials.json`) are set up and your Shopify API access token is available.

---

## Usage

### Running the Script

The script can be executed from the command line, and it requires several arguments to be passed in for proper execution. The primary arguments are the source folder where PDFs and configuration files are stored, the Shopify store URL, and API credentials.

Here is the general command format to run the script:

```bash
python script_name.py --source_folder "<path_to_source_folder>" \
                      --store_url "<shopify_store_url>" \
                      --access_token "<shopify_access_token>" \
                      --credentials_path "<path_to_google_credentials_json>" \
                      --year "<year>" --quarter "<quarter>" \
                      [--markets_to_process <number_of_markets>]
```

### Arguments Breakdown:
- `--source_folder`: Path to the folder containing product PDFs and configuration files. (e.g., `/home/user/store/2024Q3`)
- `--store_url`: Your Shopify store URL (e.g., `project-digital-shop.myshopify.com`).
- `--access_token`: The access token for authenticating with Shopify's API.
- `--credentials_path`: Path to your Google Drive API credentials file (e.g., `/home/user/credentials.json`).
- `--year`: Year for the product data (e.g., `2024`).
- `--quarter`: Quarter for the product data (1-4).
- `--markets_to_process`: (Optional) Number of markets to process. Leave empty for all markets.

#### Example:

```bash
python script_name.py --source_folder "/home/user/store/2024Q3" \
                      --store_url "project-digital-shop.myshopify.com" \
                      --access_token "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" \
                      --credentials_path "/home/user/credentials.json" \
                      --year "2024" --quarter "3" --markets_to_process 2
```

---

## Program Execution Flow

1. **Input Parameters**:
   - When executed, the script will ask for the following inputs interactively:
     - **Year**: The year for which the products should be processed (e.g., `2024`).
     - **Quarter**: The quarter of the year to process (e.g., `3`).
     - **Markets to Process**: The number of markets to process (can be left empty to process all).

2. **Processing PDFs**:
   - The script will then process the PDFs located in the source folder. It extracts the required information and creates product entries for Shopify using the provided API credentials.

3. **Uploading to Google Drive**:
   - After processing, the script uploads the product CSV file to Google Drive and updates the CSV with the generated Google Drive links.

4. **Sending Data to Webhook**:
   - The CSV file is sent to the specified webhook URL for further processing or storage.

5. **User Action (Activate/Delete)**:
   - The user will be prompted with the option to either:
     - **Activate**: Activates the products on Shopify.
     - **Delete**: Deletes the products from Shopify.
     - **Skip**: Skips product activation/deletion.

---

## Example Interaction

When running the script, you’ll see something like this in the terminal:

```bash
Starting main program execution
Using source folder: /home/user/store/2024Q3
Using store URL: project-digital-shop.myshopify.com
Enter the year (e.g., 2024): 2024
User entered year: 2024
Enter the quarter (1-4): 3
User entered quarter: 3
Enter markets to process (leave empty for all): 
User entered markets to process: all

Processing PDFs and creating products...
Uploading files to Google Drive...
Sending CSV to webhook...

Do you want to Activate or Delete the products? (Activate/Delete/Skip): activate
```

---

## Logging

The script uses Python’s `logging` library to keep track of its execution. Log entries are written to the terminal and can be configured to write to a log file for further review. You can adjust logging settings within the script to suit your needs.

### Example log output:
```bash
INFO:root:Starting main program execution
INFO:root:Using source folder: /home/user/store/2024Q3
INFO:root:User entered year: 2024
INFO:root:Processing PDFs and creating products...
INFO:root:Uploading files to Google Drive...
INFO:root:Sending CSV to webhook...
```

---

## Error Handling

The script includes error handling for common issues, such as:

- **Missing Config File**: If the `config.json` file is missing, the script logs an error and stops execution.
- **Missing CSV File**: If the required CSV file (`product_pdf_data.csv`) is not found, an error message is logged.
- **Invalid User Input**: If the user inputs an invalid action (other than `Activate`, `Delete`, or `Skip`), the script prompts the user to enter a valid option.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## Conclusion

This script streamlines the process of managing Shopify products by automating PDF processing, Google Drive uploads, and integration with Shopify’s API. It’s an efficient tool for those managing large product catalogs and ensures that all product information is correctly handled and updated across multiple platforms.

For any issues or further customization, feel free to modify the code as per your needs.

---

## Acknowledgements

- This project uses the [Shopify API](https://shopify.dev/docs/admin-api) to manage product data on Shopify.
- Google Drive API documentation was used for the Google Drive integration setup.

```

### Key Changes and Additions:
1. **Extended Explanation**: This version of the README includes more details about each section, explaining the setup and execution flow.
2. **Example Outputs**: The interaction with the script, including user inputs and logging, is demonstrated with example log output.
3. **Detailed Command Structure**: The arguments required for running the script are explained in more detail, including optional and mandatory arguments.
4. **Logging and Error Handling**: Describes how the script logs execution steps and handles errors.

This should now provide a comprehensive guide for users to set up and run the script effectively!
