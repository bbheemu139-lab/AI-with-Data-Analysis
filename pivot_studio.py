import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

class PivotStudio:
    @staticmethod
    def generate_pivot(df, index_cols, col_cols, value_col, agg_func="sum"):
        """Generates dynamic pivot table DataFrame and visualization."""
        if not index_cols or not value_col:
            return None, None, "Please select at least one Row Index column and one Value column."
            
        try:
            pivot_df = pd.pivot_table(
                df,
                index=index_cols,
                columns=col_cols if col_cols else None,
                values=value_col,
                aggfunc=agg_func,
                fill_value=0
            )
            
            # Format pivot df for display
            if isinstance(pivot_df.columns, pd.MultiIndex):
                pivot_df.columns = ['_'.join(map(str, col)).strip() for col in pivot_df.columns.values]
                
            pivot_display = pivot_df.reset_index()
            
            # Create Plotly Heatmap or Stacked Bar
            if col_cols:
                fig = px.imshow(
                    pivot_df,
                    text_auto=True,
                    aspect="auto",
                    color_continuous_scale="Purples",
                    title=f"🧮 Heatmapped Pivot: {value_col} ({agg_func.upper()}) by {index_cols[0]} vs {col_cols[0]}"
                )
            else:
                fig = px.bar(
                    pivot_display,
                    x=index_cols[0],
                    y=value_col,
                    title=f"📊 Pivot Aggregation: {value_col} ({agg_func.upper()}) by {index_cols[0]}",
                    color=value_col,
                    color_continuous_scale="Viridis"
                )
                
            fig.update_layout(
                template="plotly_dark",
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            return pivot_display, fig, None
            
        except Exception as e:
            return None, None, f"Pivot Calculation Error: {str(e)}"
