import pandas as pd
import numpy as np

class DataCleaner:
    @staticmethod
    def auto_clean(df):
        """Performs automated 1-click data cleaning."""
        cleaned_df = df.copy()
        cleaning_log = []

        # 1. Drop exact duplicate rows
        initial_rows = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        dups_removed = initial_rows - len(cleaned_df)
        if dups_removed > 0:
            cleaning_log.append(f"Removed {dups_removed} duplicate rows.")

        # 2. Trim string whitespace
        string_cols = cleaned_df.select_dtypes(include=['object']).columns
        for col in string_cols:
            cleaned_df[col] = cleaned_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

        # 3. Handle missing values
        for col in cleaned_df.columns:
            null_count = cleaned_df[col].isnull().sum()
            if null_count > 0:
                if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                    median_val = cleaned_df[col].median()
                    cleaned_df[col] = cleaned_df[col].fillna(median_val)
                    cleaning_log.append(f"Imputed {null_count} missing values in '{col}' with Median ({round(median_val, 2)}).")
                else:
                    mode_series = cleaned_df[col].mode()
                    mode_val = mode_series[0] if not mode_series.empty else "Unknown"
                    cleaned_df[col] = cleaned_df[col].fillna(mode_val)
                    cleaning_log.append(f"Imputed {null_count} missing values in '{col}' with Mode ('{mode_val}').")

        # 4. Convert date columns
        for col in cleaned_df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
                    cleaning_log.append(f"Converted '{col}' to DateTime format.")
                except Exception:
                    pass

        return cleaned_df, cleaning_log

    @staticmethod
    def remove_duplicates(df):
        before = len(df)
        cleaned = df.drop_duplicates()
        return cleaned, before - len(cleaned)

    @staticmethod
    def fill_missing(df, column, strategy='median', custom_val=None):
        cleaned = df.copy()
        if column not in cleaned.columns:
            return cleaned
        
        if strategy == 'mean':
            val = cleaned[column].mean()
        elif strategy == 'median':
            val = cleaned[column].median()
        elif strategy == 'mode':
            val = cleaned[column].mode()[0] if not cleaned[column].mode().empty else ""
        elif strategy == 'zero':
            val = 0
        elif strategy == 'custom':
            val = custom_val
        elif strategy == 'drop':
            return cleaned.dropna(subset=[column])
        else:
            val = cleaned[column].median()
            
        cleaned[column] = cleaned[column].fillna(val)
        return cleaned

    @staticmethod
    def cast_type(df, column, target_type):
        cleaned = df.copy()
        if column not in cleaned.columns:
            return cleaned
        
        try:
            if target_type == 'Integer':
                cleaned[column] = pd.to_numeric(cleaned[column], errors='coerce').fillna(0).astype(int)
            elif target_type == 'Float':
                cleaned[column] = pd.to_numeric(cleaned[column], errors='coerce')
            elif target_type == 'DateTime':
                cleaned[column] = pd.to_datetime(cleaned[column], errors='coerce')
            elif target_type == 'String':
                cleaned[column] = cleaned[column].astype(str)
        except Exception as e:
            pass
        return cleaned

    @staticmethod
    def cap_outliers_iqr(df, column):
        cleaned = df.copy()
        if not pd.api.types.is_numeric_dtype(cleaned[column]):
            return cleaned, 0
        
        q1 = cleaned[column].quantile(0.25)
        q3 = cleaned[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers_count = ((cleaned[column] < lower_bound) | (cleaned[column] > upper_bound)).sum()
        cleaned[column] = np.where(cleaned[column] < lower_bound, lower_bound, cleaned[column])
        cleaned[column] = np.where(cleaned[column] > upper_bound, upper_bound, cleaned[column])
        
        return cleaned, outliers_count
