import pandas as pd
import logging
from sqlalchemy import create_engine
from datetime import datetime
import boto3
import os
from io import BytesIO


# connection_string = "postgresql://de_user:postgres@127.0.0.1:5434/de_db"
# connection_string = "postgresql://postgres:5412@127.0.0.1:5432/postgres"
connection_string = "postgresql://dwh_user:dwh_pass@127.0.0.1:5434/dwh"
engine = create_engine(connection_string)


MINIO_CONFIG = {
    "endpoint_url": "http://localhost:9000",
    "aws_access_key_id": "minio",
    "aws_secret_access_key": "minio12345",
    }
PROJECT_PREFIX = "lakehouse"
RAW_BUCKET = "raw"
BRONZE_BUCKET = "bronze"
SOURCE_FILE = "data.csv"

s3_client = boto3.client("s3", **MINIO_CONFIG)

def create_table_from_dataframe(df, table_name):
    try:
        logging.info(f"Creating table '{table_name}' in PostgreSQL")
        df.head(0).to_sql(table_name, engine, if_exists='replace', index=False)
        logging.info(f"Table '{table_name}' created successfully")
    except Exception as e:
        logging.error(f"An error occurred while creating table: {e}")
        raise
    
def load_data_to_csv(data, output_path):
    """
    Load the cleaned data to a CSV file.
    
    Parameters:
    data (pd.DataFrame): The cleaned data as a DataFrame.
    output_path (str): The path to save the cleaned data CSV file.

    Returns:
    None
    """
    try:
        logging.info(f"Saving cleaned data to {output_path}")
        data.to_csv(output_path, index=False)
        logging.info(f"Cleaned data saved successfully to {output_path}")
    except Exception as e:
        logging.error(f"An error occurred while loading data: {e}")
        raise

def load_to_postgres(data , table_name):
    try:
        logging.info(f'loading {len(data)} of rows into PostgreSQL table {table_name}')
        data.to_sql(
            table_name,
            engine,
            if_exists="replace",
            index=False
        )
        logging.info(f"Successfully loaded data to table '{table_name}'")
    except Exception as exception:
        logging.error(f"Error loading data to PostgreSQL: {exception}")
        raise

def extract_data_frame_from_minio():
    # Implement logic to load data from MinIO
    files_to_process = get_files_from_minio(f"{PROJECT_PREFIX}")
    if len(files_to_process) == 0:
        logging.info("No files to process from MinIO.")
        return
    for file_key in files_to_process:
        logging.info(f"Processing file '{file_key}' from MinIO bucket '{PROJECT_PREFIX}'")
        try:
            response = s3_client.get_object(Bucket=PROJECT_PREFIX, Key=file_key)
            file_content = response['Body'].read()
            df = pd.read_csv(BytesIO(file_content))
            object_name = f"cleansed_{os.path.splitext(os.path.basename(file_key))[0]}.xlsx"
            yield {object_name: df}
        except Exception as e:
            logging.error(f"An error occurred while processing file '{file_key}': {e}")
            continue

def get_files_from_minio(bucket_name):
    # Implement logic to list files in MinIO bucket
    folder_prefix = f"{RAW_BUCKET}/{datetime.now().strftime('%Y/%m/%d')}"
    logging.info(f"Listing files in bucket '{bucket_name}' with prefix '{folder_prefix}'")
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
    files = [obj['Key'] for obj in response.get('Contents', [])]
    if not files or len(files) == 0: 
        logging.warning(f"No files found in bucket '{bucket_name}' with prefix '{folder_prefix}'")
        return []
    logging.info(f"Found {len(files)} files in bucket '{bucket_name}' with prefix '{folder_prefix}'")
    return files

def convert_excel_and_upload_file_to_minio(df, object_name):
    try:
        file_path = f"{BRONZE_BUCKET}/{datetime.now().strftime('%Y/%m/%d')}"
        logging.info(f"Converting DataFrame to Excel file '{file_path}'")
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_buffer.seek(0)
        
        logging.info(f"Uploading file '{file_path}' to MinIO bucket '{PROJECT_PREFIX}' as '{object_name}'")
        s3_client.put_object(Bucket=PROJECT_PREFIX, Key=f"{file_path}/{object_name}",Body=excel_buffer.getvalue(), ContentLength=len(excel_buffer.getvalue()),ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        logging.info(f"File '{file_path}' uploaded successfully to bucket '{PROJECT_PREFIX}' as '{object_name}'")
    except Exception as e:
        logging.error(f"An error occurred while uploading file to MinIO: {e}")
        raise