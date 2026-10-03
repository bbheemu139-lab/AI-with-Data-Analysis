import sqlite3
import pandas as pd
import re

class SQLEngine:
    def __init__(self, df, table_name="dataset"):
        self.df = df
        self.table_name = table_name
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        # Load df into SQLite
        self.df.to_sql(self.table_name, self.conn, if_exists="replace", index=False)

    def execute_query(self, query):
        """Executes raw SQL query and returns result DataFrame or error message."""
        try:
            result_df = pd.read_sql_query(query, self.conn)
            return result_df, None
        except Exception as e:
            return None, str(e)

    def get_table_schema(self):
        """Returns column names and types for prompt context."""
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.table_name})")
        columns = cursor.fetchall()
        # columns format: (cid, name, type, notnull, dflt_value, pk)
        schema_desc = [f"{col[1]} ({col[2]})" for col in columns]
        return ", ".join(schema_desc)

    def generate_sql_from_nl(self, question):
        """Rule-based smart Text-to-SQL converter fallback."""
        q = question.lower()
        cols = list(self.df.columns)
        tbl = self.table_name

        # Find sales/revenue column
        sales_col = next((c for c in cols if 'sale' in c.lower() or 'revenue' in c.lower() or 'amount' in c.lower() or 'total' in c.lower()), None)
        num_col = next((c for c in cols if pd.api.types.is_numeric_dtype(self.df[c])), None)
        val_col = sales_col or num_col or cols[0]

        # Find category/product column
        prod_col = next((c for c in cols if 'prod' in c.lower() or 'item' in c.lower()), None)
        cat_col = next((c for c in cols if 'cat' in c.lower() or 'seg' in c.lower() or 'region' in c.lower()), None)
        group_col = prod_col or cat_col or (cols[1] if len(cols) > 1 else cols[0])

        if "highest revenue" in q or "top product" in q or "top 5" in q or "highest sales" in q:
            limit = 5 if "5" in q else (10 if "10" in q else 1)
            sql = f"SELECT `{group_col}`, SUM(`{val_col}`) AS Total_Revenue FROM `{tbl}` GROUP BY `{group_col}` ORDER BY Total_Revenue DESC LIMIT {limit};"
        elif "region" in q or "by region" in q:
            reg_col = next((c for c in cols if 'region' in c.lower()), group_col)
            sql = f"SELECT `{reg_col}`, SUM(`{val_col}`) AS Total_Sales, AVG(`{val_col}`) AS Avg_Sales FROM `{tbl}` GROUP BY `{reg_col}` ORDER BY Total_Sales DESC;"
        elif "category" in q or "by category" in q:
            c_col = next((c for c in cols if 'cat' in c.lower()), group_col)
            sql = f"SELECT `{c_col}`, SUM(`{val_col}`) AS Total_Sales, COUNT(*) AS Total_Orders FROM `{tbl}` GROUP BY `{c_col}` ORDER BY Total_Sales DESC;"
        elif "average" in q or "avg" in q:
            sql = f"SELECT `{group_col}`, AVG(`{val_col}`) AS Avg_Value FROM `{tbl}` GROUP BY `{group_col}` ORDER BY Avg_Value DESC;"
        elif "window" in q or "rank" in q or "top per" in q:
            sql = f"SELECT `{group_col}`, `{val_col}`, RANK() OVER (ORDER BY `{val_col}` DESC) as Rank_Num FROM `{tbl}` LIMIT 10;"
        elif "count" in q or "total orders" in q:
            sql = f"SELECT `{group_col}`, COUNT(*) AS Total_Count FROM `{tbl}` GROUP BY `{group_col}` ORDER BY Total_Count DESC;"
        else:
            sql = f"SELECT `{group_col}`, SUM(`{val_col}`) AS Total_Sum, COUNT(*) AS Row_Count FROM `{tbl}` GROUP BY `{group_col}` ORDER BY Total_Sum DESC LIMIT 10;"

        return sql
