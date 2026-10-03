import sys
import io
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

class PythonRunner:
    @staticmethod
    def run_code(df, code_str):
        """Executes python code string with df provided in scope."""
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        
        local_scope = {
            'df': df.copy(),
            'pd': pd,
            'np': np,
            'px': px,
            'go': go,
            'plt': plt,
            'result': None,
            'fig': None
        }
        
        error = None
        try:
            exec(code_str, globals(), local_scope)
        except Exception as e:
            error = str(e)
            
        sys.stdout = old_stdout
        logs = redirected_output.getvalue()
        
        return {
            'result': local_scope.get('result'),
            'fig': local_scope.get('fig'),
            'logs': logs,
            'error': error
        }

    @staticmethod
    def generate_sample_python_code(question, df):
        """Generates template python code based on user prompt."""
        cols = list(df.columns)
        num_cols = list(df.select_dtypes(include=[np.number]).columns)
        val_col = num_cols[0] if num_cols else cols[0]
        cat_cols = list(df.select_dtypes(include=['object', 'category']).columns)
        grp_col = cat_cols[0] if cat_cols else cols[0]

        code = f"""# Python Analysis for: {question}
import pandas as pd
import plotly.express as px

# 1. Group & Aggregate
grouped = df.groupby('{grp_col}')['{val_col}'].agg(['sum', 'mean', 'count']).reset_index()
grouped.columns = ['{grp_col}', 'Total_{val_col}', 'Avg_{val_col}', 'Order_Count']
result = grouped.sort_values(by='Total_{val_col}', ascending=False)

# 2. Create Visualization
fig = px.bar(
    result, 
    x='{grp_col}', 
    y='Total_{val_col}',
    title='Total {val_col} by {grp_col}',
    color='Total_{val_col}',
    color_continuous_scale='Purples'
)
fig.update_layout(template='plotly_dark')

print(f"Top category: {{result.iloc[0]['{grp_col}']}} with Total: {{result.iloc[0]['Total_{val_col}']:,.2f}}")
"""
        return code
