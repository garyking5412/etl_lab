import logging
from etl.extract import extract_data
from etl.transform import clean_orders, clean_customers, clean_products, join_order_customer, join_order_product, convert_excel_to_csv
from etl.load import load_data_to_csv, load_to_postgres

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def etl(code):
    match code:
        case "1":
            try:
                logging.info('Cleaning customers data')
                logging.info('extracting data into data frame >>>')
                df = extract_data("input/customers.csv")
                clean_df = clean_customers(df)
                load_to_postgres(clean_df, 'cleaned_customers')
                load_data_to_csv(clean_df, "output/cleaned_customers.csv")
            except Exception as e:
                logging.error(f"An error occurred during the ETL process: {e}")
                raise
        case "2":
            try:
                logging.info('Cleaning orders data')
                df = extract_data("input/retail_orders.csv")
                clean_df = clean_orders(df)
                load_to_postgres(clean_df, 'cleaned_orders')
                load_data_to_csv(clean_df, "output/cleaned_orders.csv")
            except Exception as e:
                logging.error(f"An error occurred during the ETL process: {e}")
                raise
        case "3":
            try:
                logging.info('Cleaning products data')
                df = extract_data("input/products.csv")
                clean_df = clean_products(df)
                load_to_postgres(clean_df, 'cleaned_products')
                load_data_to_csv(clean_df, "output/cleaned_products.csv")
            except Exception as e:
                logging.error(f"An error occurred during the ETL process: {e}")
                raise
        case "4":
            try:
                logging.info('Aggregating from orders and customers >>>')
                df_orders = extract_data("input/retail_orders.csv")
                df_customers = extract_data("input/customers.csv")
                clean_orders_df = clean_orders(df_orders)
                clean_customers_df = clean_customers(df_customers)
                # Example aggregation - replace with actual logic   
                aggregated_df = join_order_customer(clean_orders_df, clean_customers_df)
                load_to_postgres(aggregated_df, 'aggregated_order_customer')
                load_data_to_csv(aggregated_df, "output/aggregated_order_customer.csv")
            except Exception as e:
                logging.error(f"An error occurred during the ETL process: {e}")
                raise
        case "5":
            try:
                logging.info('Aggregating from orders and products >>>')
                df_orders = extract_data("input/retail_orders.csv")
                df_products = extract_data("input/products.csv")
                clean_orders_df = clean_orders(df_orders)
                clean_products_df = clean_products(df_products)
                # Example aggregation - replace with actual logic
                aggregated_df = join_order_product(clean_orders_df, clean_products_df)
                load_to_postgres(aggregated_df, 'aggregated_order_product')
                load_data_to_csv(aggregated_df, "output/aggregated_order_product.csv")
            except Exception as e:
                logging.error(f"An error occurred during the ETL process: {e}")
                raise
        case _:
            logging.info('Exiting the program.')

def run_basic_pipeline():
    logging.info('starting basic ETL pipeline')
    
    while True:
        print("\n[1] Clean CSV Customers")
        print("[2] Clean CSV Retail_Orders")
        print("[3] Clean CSV Products")
        print("[4] Aggregate Orders and Customers")
        print("[5] Aggregate Orders and Products")
        print("[6] Convert Excel to CSV")
        print("[7] Exit")

        choice = input("Enter your choice: ")
        match choice:
            case "1"|"2"|"3"|"4"|"5":
                etl(choice)
                # break
            case "6":
                file = input("Enter the path to the Excel file: ")
                try:
                    logging.info('Converting Excel to CSV >>>')
                    convert_excel_to_csv('/home/takeshi_tran/Documents/code/de-bootcamp/data/' + file, f"input/{file.split('/')[-1].split('.')[0]}.csv")
                except Exception as e:
                    logging.error(f"An error occurred during the conversion process: {e}")
                    raise
            case "7":
                logging.info('Exiting the program.')
                return
            case _:
                print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, or 7.")

if __name__ == "__main__" :
    run_basic_pipeline()