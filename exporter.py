import io
import sqlite3
import pandas as pd
import json

class DataExporter:
    @staticmethod
    def to_excel_bytes(df, sheet_name="Cleaned_Data"):
        """Converts DataFrame to Excel bytes buffer for Streamlit download."""
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def to_csv_bytes(df):
        """Converts DataFrame to CSV bytes buffer."""
        return df.to_csv(index=False).encode('utf-8')

    @staticmethod
    def to_json_bytes(df):
        """Converts DataFrame to formatted JSON string bytes."""
        json_str = df.to_json(orient='records', indent=2, date_format='iso')
        return json_str.encode('utf-8')

    @staticmethod
    def to_sqlite_bytes(df, table_name="dataset"):
        """Dumps DataFrame into SQLite database file bytes."""
        output = io.BytesIO()
        conn = sqlite3.connect(":memory:")
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        
        # Backup memory db to output
        backup_db = sqlite3.connect(":memory:")
        conn.backup(backup_db)
        
        # Write bytes
        db_bytes = io.BytesIO()
        for line in backup_db.iterdump():
            db_bytes.write(f"{line}\n".encode('utf-8'))
        db_bytes.seek(0)
        return db_bytes.getvalue()
