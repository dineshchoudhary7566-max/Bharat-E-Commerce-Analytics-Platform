import pandas as pd
import datetime as dt

def calculate_kpis(df):
    """
    Calculates values for the Summary Cards (KPIs) at the top of the Dashboard.
    Returns a dictionary: Total Revenue, Total Orders, Total Customers, Avg Order Value.
    """
    total_revenue = df['TotalAmount'].sum()
    total_orders = df['OrderID'].nunique()
    total_customers = df['CustomerID'].nunique()
    
    # Average Order Value (AOV)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    return {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'avg_order_value': avg_order_value
    }

def get_monthly_sales(df):
    """
    Calculates monthly revenue for the time series graph (Line Chart).
    Index: Date, Value: Revenue
    """
    df_trend = df.set_index('OrderDate')
    # 'ME' = Month End. If older pandas versions throw an error, change it to 'M'.
    monthly_sales = df_trend['TotalAmount'].resample('ME').sum()
    
    return monthly_sales

def get_category_performance(df):
    """
    Sorts categories for Pareto Analysis (Bar Chart).
    Returns sorted from the highest revenue category to the lowest.
    """
    cat_perf = df.groupby('CategoryName')['TotalAmount'].sum().reset_index()
    cat_perf = cat_perf.sort_values('TotalAmount', ascending=False)
    
    # Let's calculate the percentage share as well (Needed in the Dashboard)
    total_rev = cat_perf['TotalAmount'].sum()
    cat_perf['Share_Percent'] = (cat_perf['TotalAmount'] / total_rev) * 100
    
    return cat_perf

def get_top_products(df, n=10):
    """
    Gets the top 'n' best-selling products.
    Defaults to the top 10 products.
    """
    prod_perf = df.groupby('ProductName')['TotalAmount'].sum().reset_index()
    prod_perf = prod_perf.sort_values('TotalAmount', ascending=False).head(n)
    
    return prod_perf


def get_daily_sales_performance(df):
    """
    Analyzes the distribution of sales across the days of the week.
    """
    temp_df = df.copy()
    
    # Map day numbers to English day names
    day_mapping = {
        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 
        3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
    }
    
    temp_df['Day_Name'] = temp_df['OrderDate'].dt.dayofweek.map(day_mapping)
    
    # Calculate daily total revenue
    daily_analysis = temp_df.groupby(['Day_Name'])['TotalAmount'].sum().reset_index()
    
    # Sort days in a logical order (starting from Monday)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_analysis['Day_Name'] = pd.Categorical(daily_analysis['Day_Name'], categories=day_order, ordered=True)
    daily_analysis = daily_analysis.sort_values('Day_Name')
    
    return daily_analysis

def calculate_rfm(df):
    """
    Performs Customer Segmentation (RFM Analysis).
    Segments customers into classes like 'Champions', 'At Risk'.
    """
    # 1. Analysis Date (2 days after the latest date)
    last_date = df['OrderDate'].max()
    analysis_date = last_date + pd.Timedelta(days=2)

    # 2. Metrics
    rfm = df.groupby('CustomerID').agg({
        'OrderDate': lambda date: (analysis_date - date.max()).days,
        'OrderID': 'nunique',
        'TotalAmount': 'sum'
    })

    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    rfm = rfm[rfm['Monetary'] > 0] # Clear negatives

    # 3. Scoring (1-5 Points)
    rfm["RecencyScore"] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["FrequencyScore"] = pd.qcut(rfm['Frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    
    # Score Combination
    rfm["RFM_SCORE"] = (rfm['RecencyScore'].astype(str) + 
                        rfm['FrequencyScore'].astype(str))

    # 4. Segment Naming (Regex Map)
    seg_map = {
        r'[1-2][1-2]': 'Hibernating',
        r'[1-2][3-4]': 'At Risk',
        r'[1-2]5': 'Can\'t Loose',
        r'3[1-2]': 'About to Sleep',
        r'33': 'Need Attention',
        r'[3-4][4-5]': 'Loyal Customers',
        r'41': 'Promising',
        r'51': 'New Customers',
        r'[4-5][2-3]': 'Potential Loyalists',
        r'5[4-5]': 'Champions'
    }

    rfm['Segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

    return rfm


def calculate_monthly_growth(df):
    """
    Calculates Month-over-Month Growth rates for revenue.
    Used in the Dashboard to state 'We grew by X% compared to last month'.
    """
    df_trend = df.set_index('OrderDate')
    monthly_sales = df_trend['TotalAmount'].resample('ME').sum()
    
    # Percentage Change (PCT Change)
    growth_df = pd.DataFrame(monthly_sales)
    growth_df['Growth_Rate'] = growth_df['TotalAmount'].pct_change() * 100
    
    return growth_df


def calculate_cohort_matrix(df):
    """
    Prepares data for the famous Cohort Analysis (Retention Heatmap).
    Shows how many customers stayed in the months following their first visit.
    """
    # 1. Let's copy the data
    cohort_data = df[['CustomerID', 'OrderDate']].copy()
    
    # 2. Find the Order Month
    cohort_data['OrderMonth'] = cohort_data['OrderDate'].dt.to_period('M')
    
    # 3. Find the customer's FIRST order date (Cohort Month)
    cohort_data['CohortMonth'] = cohort_data.groupby('CustomerID')['OrderDate'] \
                                            .transform('min').dt.to_period('M')
    
    # 4. Cohort Index (How many months has the customer been with us?)
    # Formula: (Order Year - Cohort Year) * 12 + (Order Month - Cohort Month) + 1
    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        return year, month

    order_year, order_month = get_date_int(cohort_data, 'OrderMonth')
    cohort_year, cohort_month = get_date_int(cohort_data, 'CohortMonth')

    years_diff = order_year - cohort_year
    months_diff = order_month - cohort_month

    cohort_data['CohortIndex'] = years_diff * 12 + months_diff + 1
    
    # 5. Pivot Table (Rows: Cohort Month, Columns: Number of Months Passed, Value: Number of Customers)
    cohort_counts = cohort_data.groupby(['CohortMonth', 'CohortIndex'])['CustomerID'].nunique().reset_index()
    cohort_matrix = cohort_counts.pivot(index='CohortMonth', columns='CohortIndex', values='CustomerID')
    
    # 6. Convert to Retention Rate (Divide by the number in the first month)
    cohort_size = cohort_matrix.iloc[:, 0]
    retention = cohort_matrix.divide(cohort_size, axis=0)
    
    return retention