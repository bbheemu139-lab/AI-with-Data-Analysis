import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

class AutoEDA:
    @staticmethod
    @st.cache_data(show_spinner=False)
    def get_numeric_summary(df):
        """Generates comprehensive summary statistics for numerical columns."""
        num_cols = df.select_dtypes(include=[np.number]).columns
        if len(num_cols) == 0:
            return pd.DataFrame()
        
        summary = df[num_cols].describe().T
        summary['skewness'] = df[num_cols].skew()
        summary['kurtosis'] = df[num_cols].kurt()
        summary['missing_count'] = df[num_cols].isnull().sum()
        summary = summary.round(2)
        return summary

    @staticmethod
    @st.cache_data(show_spinner=False)
    def get_categorical_summary(df):
        """Generates summary statistics for categorical columns."""
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(cat_cols) == 0:
            return pd.DataFrame()
        
        records = []
        for col in cat_cols:
            top_val = df[col].mode()[0] if not df[col].mode().empty else "N/A"
            top_freq = df[col].value_counts().max() if not df[col].empty else 0
            records.append({
                'Column': col,
                'Unique Values': df[col].nunique(),
                'Top Value': top_val,
                'Top Frequency': top_freq,
                'Missing Count': df[col].isnull().sum()
            })
        return pd.DataFrame(records)

    @staticmethod
    def create_correlation_heatmap(df):
        """Creates Plotly correlation matrix heatmap."""
        num_cols = df.select_dtypes(include=[np.number]).columns
        if len(num_cols) < 2:
            return None
        
        corr = df[num_cols].corr().round(2)
        
        fig = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Purples",
            title="🔥 Numerical Feature Correlation Matrix"
        )
        fig.update_layout(
            template="plotly_dark",
            margin=dict(l=40, r=40, t=50, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig

    @staticmethod
    def create_distribution_plot(df, column):
        """Creates distribution histogram and boxplot for a column."""
        if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
            return None
        
        fig = px.histogram(
            df, 
            x=column, 
            marginal="box",
            title=f"📈 Distribution & Outliers: {column}",
            color_discrete_sequence=['#8b5cf6']
        )
        fig.update_layout(
            template="plotly_dark",
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig

    @staticmethod
    def create_violin_plot(df, num_col, cat_col=None):
        """Creates Violin plot for distribution density."""
        if num_col not in df.columns:
            return None
            
        fig = px.violin(
            df,
            y=num_col,
            x=cat_col if cat_col and cat_col in df.columns else None,
            box=True,
            points="all",
            title=f"🎻 Kernel Density Violin Plot: {num_col}" + (f" by {cat_col}" if cat_col else ""),
            color_discrete_sequence=['#3b82f6']
        )
        fig.update_layout(
            template="plotly_dark",
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig

    @staticmethod
    def create_treemap_chart(df, cat_cols, val_col):
        """Creates Treemap chart for hierarchical breakdown."""
        if not cat_cols or val_col not in df.columns:
            return None
            
        fig = px.treemap(
            df,
            path=cat_cols[:2] if len(cat_cols)>=2 else cat_cols,
            values=val_col,
            title=f"🌳 Hierarchical Treemap: {val_col} by {' -> '.join(cat_cols[:2])}",
            color=val_col,
            color_continuous_scale="Purples"
        )
        fig.update_layout(
            template="plotly_dark",
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig

    @staticmethod
    def create_density_contour(df, x_col, y_col):
        """Creates 2D Density Contour plot."""
        if x_col not in df.columns or y_col not in df.columns:
            return None
            
        fig = px.density_contour(
            df,
            x=x_col,
            y=y_col,
            marginal_x="histogram",
            marginal_y="box",
            title=f"🌌 2D Density Contour: {y_col} vs {x_col}"
        )
        fig.update_layout(
            template="plotly_dark",
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig

    @staticmethod
    def create_category_bar(df, column, top_n=10):
        """Creates bar chart for top values in categorical column."""
        if column not in df.columns:
            return None
        
        counts = df[column].value_counts().head(top_n).reset_index()
        counts.columns = [column, 'Count']
        
        fig = px.bar(
            counts,
            x=column,
            y='Count',
            title=f"📊 Top {top_n} Frequencies in '{column}'",
            color='Count',
            color_continuous_scale="Viridis"
        )
        fig.update_layout(
            template="plotly_dark",
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig

    @staticmethod
    @st.cache_data(show_spinner=False)
    def detect_outliers_summary(df):
        """Detects outliers count per numeric column using IQR."""
        num_cols = df.select_dtypes(include=[np.number]).columns
        records = []
        for col in num_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers = df[(df[col] < lower) | (df[col] > upper)]
            count = len(outliers)
            records.append({
                'Column': col,
                'Outliers Count': count,
                'Outliers %': round((count / len(df)) * 100, 2) if len(df) > 0 else 0,
                'Lower Bound': round(lower, 2),
                'Upper Bound': round(upper, 2)
            })
        return pd.DataFrame(records)
