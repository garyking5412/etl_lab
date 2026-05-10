import pandas as pd
import logging
from datetime import datetime
import great_expectations as ge
import webbrowser
import os
import uuid

def convert_excel_to_csv(excel_file_path, csv_file_path):
    """
    Convert an Excel file to CSV format.

    Parameters:
    excel_file_path (str): The path to the input Excel file.
    csv_file_path (str): The path to the output CSV file.
    """
    try:
        logging.info(f"Converting {excel_file_path} to {csv_file_path}")
        df = pd.read_excel(excel_file_path)
        df.to_csv(csv_file_path, index=False)
        logging.info(f"Conversion successful: {csv_file_path}")
    except FileNotFoundError:
        logging.error(f"File not found: {excel_file_path}")
        raise
    except Exception as e:
        logging.error(f"An error occurred during conversion: {e}")
        raise
    
def clean_orders(order):
    """
    Clean the orders data.

    Parameters:
    data (pd.DataFrame): The orders data as a DataFrame.

    Returns:
    pd.DataFrame: The cleaned orders data.
    """
    logging.info("Cleaning orders data")
    clean_data = order.copy()
    # Example cleaning steps - replace with actual cleaning logic
    inital_count = len(clean_data)
    logging.info(f"Initial number of records: {inital_count}")
    clean_data = clean_data[clean_data['quantity'] > 0]  # Remove orders with non-positive quantities
    removed_count = inital_count - len(clean_data)
    logging.info(f"Removed {removed_count} records with non-positive amounts")
    clean_data["updated_at"] = pd.to_datetime(clean_data["updated_at"], errors='coerce')  # Convert order_date to datetime
    logging.info("Converted updated_at to datetime format")
    clean_data = clean_data.dropna(subset=['order_id', 'customer_id', 'product_id'], how='any')  # Remove rows with null order_id, customer_id, or product_id
    clean_data = clean_data.drop_duplicates()
    logging.info("Orders data cleaned successfully")
    return clean_data

def clean_customers(df):
    logging.info("Starting customers data cleaning")
    
    df_clean = df.copy()
    
    # Loại bỏ các dòng có customer_id / phone / email / country null
    initial_count = len(df_clean)
    df_clean = df_clean.dropna(subset=['customer_id','email','phone','country'], how='any')
    removed_count = initial_count - len(df_clean)
    logging.info(f"Removed {removed_count} rows with null customer_id")
    
    # Chuyển đổi cột signup_date sang datetime
    df_clean["signup_date"] = pd.to_datetime(df_clean["signup_date"])
    logging.info("Converted signup_date to datetime")
    
    # Chuyển đổi is_active sang boolean
    df_clean["is_active"] = df_clean["is_active"].astype(bool)
    logging.info("Converted is_active to boolean")

    # chuyển đổi định dạng số điện thoại
    df_clean["phone"] = df_clean["phone"].astype(str)
    df_clean["phone"] = df_clean["phone"].replace(r'[.,\s]','',regex=True)
    logging.info("Converted phone number to String")
    
    logging.info(f"Customers cleaning completed. Final dataset: {len(df_clean)} rows")
    return df_clean

def clean_products(df):
    logging.info("Starting products data cleaning")
    
    df_clean = df.copy()
    
    # Loại bỏ các dòng có product_id / price null
    initial_count = len(df_clean)
    df_clean = df_clean.dropna(subset=['product_id'])
    removed_count = initial_count - len(df_clean)
    logging.info(f"Removed {removed_count} rows with null product_id")
    
    # chuyển đổi giá trị price mặc định
    df_clean['price'] = df_clean['price'].replace(r'[^\d.]', '', regex=True)  # Remove non-numeric characters
    df_clean["price"] = df_clean["price"].fillna("0")

    # Chuyển đổi cột price sang numeric
    df_clean["price"] = pd.to_numeric(df_clean["price"], errors='coerce')
    logging.info("Converted price to numeric")

    # Loại bỏ các dòng có price <= 0
    # initial_count = len(df_clean)
    # df_clean = df_clean[df_clean['price'] > 0]
    # removed_count = initial_count - len(df_clean)
    # logging.info(f"Removed {removed_count} rows with non-positive price")
    
    logging.info(f"Products cleaning completed. Final dataset: {len(df_clean)} rows")
    return df_clean

def join_order_customer(order_df, customer_df):
    logging.info('Merging data from order on customer data frames')
    merged_df = pd.merge(order_df, customer_df, on='customer_id', how='left')
    logging.info(f"Join completed. Result: {len(merged_df)} rows")
    return merged_df

def join_order_product(order_df, product_df):
    logging.info('Merging data from order on product data frames')
    merged_df = pd.merge(order_df, product_df, on='product_id', how='left')
    logging.info(f"Join completed. Result: {len(merged_df)} rows")
    return merged_df

def validate_minio_raw_data(df):
    # Implement validation logic for raw data in MinIO
    logging.info("Validating raw data from MinIO")
    context = ge.get_context()
    context.add_or_update_expectation_suite(expectation_suite_name="bronze_data_expectation_suite")
    datasource_name = "pandas_datasource"
    data_asset_name = "current_dataframe"
    datasource = context.sources.add_or_update_pandas(name=datasource_name)
    data_asset = datasource.add_dataframe_asset(name=data_asset_name)
    batch_request = data_asset.build_batch_request(dataframe=df)
    
    validator = context.get_validator(batch_request=batch_request, expectation_suite_name="bronze_data_expectation_suite")
    validator.expect_column_values_to_not_be_null("stock_name")
    validator.expect_column_values_to_be_of_type("stock_name", "str")
    validator.expect_column_values_to_not_be_null(column="price", mostly=0.95)
    validator.expect_column_values_to_be_of_type("price", "float64")
    # validator.expect_column_values_to_be_between(column = "request_time", min_value=datetime.combine(datetime.now().date(), datetime.min.time()), max_value=datetime.now())
    
    validator.save_expectation_suite(discard_failed_expectations=False)
    # validation_results = validator.validate()
    
    checkpoint = context.add_or_update_checkpoint(
        name="my_checkpoint",
        validator=validator,
    )
    
    validation_results = checkpoint.run()
    context.build_data_docs()
    context.open_data_docs()
    
    logging.info(f"Validation results documented: {context.get_docs_sites_urls()}")
    if validation_results["success"]:
        logging.info("Validation successful: Raw data from MinIO is valid")
        return True
    else:
        logging.error("Validation failed: Raw data from MinIO is invalid")
        return False
    
def enrich_data(df):
    # Implement data enrichment logic
    logging.info("Enriching data")
    df['id'] = [uuid.uuid4() for _ in range(len(df))]
    logging.info("Data enrichment completed")
    return df