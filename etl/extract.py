import pandas as pd
import os   
import logging

def extract_data(file_path):
    """
    Extract data from a CSV file.

    Parameters:
    file_path (str): The path to the CSV file.

    Returns:
    pd.DataFrame: The extracted data as a DataFrame.
    """
    try:
        logging.info(f"Reading data from {file_path}")
        data = pd.read_csv(file_path)
        logging.info(f"Data extracted successfully from {file_path}")
        return data
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logging.error(f"An error occurred while extracting data: {e}")
        raise