import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data():
    os.makedirs("C:/Users/LENOVO/.gemini/antigravity/scratch/ai_data_analyst/sample_data", exist_ok=True)
    
    # 1. Sales Data (.xlsx)
    np.random.seed(42)
    n_rows = 500
    
    start_date = datetime(2025, 1, 1)
    dates = [start_date + timedelta(days=int(i)) for i in np.random.choice(365, n_rows)]
    
    categories = ['Electronics', 'Furniture', 'Clothing', 'Office Supplies', 'Accessories']
    products = {
        'Electronics': ['Product A (Laptop)', 'Product B (Smart TV)', 'Product C (Smartphone)'],
        'Furniture': ['Product D (Ergonomic Chair)', 'Product E (Standing Desk)'],
        'Clothing': ['Product F (Jacket)', 'Product G (Sneakers)'],
        'Office Supplies': ['Product H (Notebook Set)', 'Product I (Monitor Stand)'],
        'Accessories': ['Product J (Wireless Mouse)', 'Product K (Keyboard)']
    }
    regions = ['North', 'South', 'East', 'West', 'Central']
    sales_reps = ['Bheemu', 'Anitha', 'Rajesh', 'Priya', 'Kiran', 'Suresh']
    
    data = []
    for i in range(n_rows):
        cat = np.random.choice(categories)
        prod = np.random.choice(products[cat])
        reg = np.random.choice(regions)
        rep = np.random.choice(sales_reps)
        units = int(np.random.exponential(scale=10) + 1)
        
        # Product A has higher revenue for testing AI insights!
        if 'Product A' in prod:
            unit_price = float(np.random.uniform(45000, 65000))
        elif 'Smart TV' in prod or 'Smartphone' in prod:
            unit_price = float(np.random.uniform(25000, 40000))
        else:
            unit_price = float(np.random.uniform(1500, 12000))
            
        sales = round(units * unit_price, 2)
        cost = round(sales * np.random.uniform(0.55, 0.82), 2)
        profit = round(sales - cost, 2)
        rating = round(np.random.uniform(3.0, 5.0), 1)
        
        data.append({
            'Order_ID': f'ORD-{1000 + i}',
            'Order_Date': dates[i].strftime('%Y-%m-%d'),
            'Category': cat,
            'Product': prod,
            'Region': reg,
            'Sales_Rep': rep,
            'Units_Sold': units,
            'Unit_Price_INR': round(unit_price, 2),
            'Total_Sales_INR': sales,
            'Profit_INR': profit,
            'Customer_Rating': rating
        })
        
    df_sales = pd.DataFrame(data)
    
    # Introduce some realistic raw data defects for Data Cleaning Demo (Missing values, Duplicates)
    # Missing values
    df_sales.loc[15:20, 'Customer_Rating'] = np.nan
    df_sales.loc[45:48, 'Sales_Rep'] = np.nan
    df_sales.loc[100:102, 'Profit_INR'] = np.nan
    
    # Duplicates
    dup_rows = df_sales.iloc[10:14].copy()
    df_sales = pd.concat([df_sales, dup_rows], ignore_index=True)
    
    sales_path = "C:/Users/LENOVO/.gemini/antigravity/scratch/ai_data_analyst/sample_data/Sales_Data.xlsx"
    df_sales.to_excel(sales_path, index=False, sheet_name='Sales_Transactions')
    print(f"Generated {sales_path} with {len(df_sales)} rows.")
    
    # 2. Ecommerce Orders (.csv)
    n_csv = 300
    dates_csv = [start_date + timedelta(days=int(i)) for i in np.random.choice(365, n_csv)]
    segments = ['Consumer', 'Corporate', 'Home Office']
    payments = ['UPI', 'Credit Card', 'Net Banking', 'Cash on Delivery']
    statuses = ['Completed', 'Pending', 'Cancelled', 'Returned']
    
    csv_data = []
    for i in range(n_csv):
        amt = float(np.random.uniform(500, 25000))
        disc = float(np.random.choice([0, 5, 10, 15, 20]))
        final_amt = amt * (1 - disc / 100)
        csv_data.append({
            'Transaction_ID': f'TXN-{5000 + i}',
            'Date': dates_csv[i].strftime('%Y-%m-%d'),
            'Customer_Segment': np.random.choice(segments),
            'Payment_Method': np.random.choice(payments),
            'Amount_INR': round(amt, 2),
            'Discount_Percent': disc,
            'Final_Amount_INR': round(final_amt, 2),
            'Status': np.random.choice(statuses, p=[0.75, 0.1, 0.1, 0.05])
        })
    
    df_csv = pd.DataFrame(csv_data)
    csv_path = "C:/Users/LENOVO/.gemini/antigravity/scratch/ai_data_analyst/sample_data/Ecommerce_Orders.csv"
    df_csv.to_csv(csv_path, index=False)
    print(f"Generated {csv_path} with {len(df_csv)} rows.")

if __name__ == "__main__":
    generate_sample_data()
