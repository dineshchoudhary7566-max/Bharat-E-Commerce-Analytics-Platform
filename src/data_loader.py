# Data loading and cleaning functions
import pandas as pd
import os

def load_data():
    """
    This function reads all CSV files in the processed folder,
    performs the necessary merges, and returns an analysis-ready 'Master DataFrame'.
    """
    
    # 1. Dynamic File Path Determination
    # Go up 2 folders from where this file (data_loader.py) is, enter data/processed.
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_PATH = os.path.join(BASE_DIR, 'data')

    try:
        # 2. Read Files
        df_orders = pd.read_csv(os.path.join(DATA_PATH, 'clean_orders.csv'))
        df_details = pd.read_csv(os.path.join(DATA_PATH, 'clean_ordersdetails.csv'))
        df_products = pd.read_csv(os.path.join(DATA_PATH, 'clean_products.csv'))
        df_customers = pd.read_csv(os.path.join(DATA_PATH, 'clean_customers.csv'))
        df_categories = pd.read_csv(os.path.join(DATA_PATH, 'clean_categories.csv'))

        # 3. Fix Date Format
        df_orders['OrderDate'] = pd.to_datetime(df_orders['OrderDate'])

        # 4. THE BIG MERGE
        df_master = df_details.merge(df_orders, on='OrderID', how='left') \
                              .merge(df_products, on='ProductID', how='left') \
                              .merge(df_categories, on='CategoryID', how='left') \
                              .merge(df_customers, on='CustomerID', how='left')

        # 5. Cleaning (Remove those without a date)
        df_master = df_master.dropna(subset=['OrderDate'])

        # 6. Feature Engineering (New Columns)
        df_master['Month'] = df_master['OrderDate'].dt.month_name()
        df_master['Year'] = df_master['OrderDate'].dt.year
        df_master['Month_Year'] = df_master['OrderDate'].dt.to_period('M').astype(str)

        print("✅ Data successfully loaded and merged!")
        return df_master

    except FileNotFoundError as e:
        print(f"❌ ERROR: File not found! {e}")
        return pd.DataFrame() # Return empty dataframe on error