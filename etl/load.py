import pandas as pd
import logging
from sqlalchemy import create_engine

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

def load_to_postgres(data , table_name, connection_string = None):
    if connection_string is None:
        # connection_string = "postgresql://de_user:postgres@127.0.0.1:5434/de_db"
        connection_string = "postgresql://postgres:5412@127.0.0.1:5432/postgres"
    try:
        engine = create_engine(connection_string)
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
