import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

class MLForecaster:
    @staticmethod
    def forecast_sales(df, date_col, sales_col, periods=30):
        """Forecasts future sales/revenue over specified days/months using linear regression & trend extrapolation."""
        df_clean = df.dropna(subset=[date_col, sales_col]).copy()
        
        try:
            df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors='coerce')
            df_clean = df_clean.dropna(subset=[date_col]).sort_values(by=date_col)
            
            # Aggregate by Date (daily or monthly)
            grouped = df_clean.groupby(pd.Grouper(key=date_col, freq='D'))[sales_col].sum().reset_index()
            grouped = grouped[grouped[sales_col] > 0]  # Filter out empty days
            
            if len(grouped) < 5:
                # Monthly aggregation fallback if daily rows are too sparse
                grouped = df_clean.groupby(pd.Grouper(key=date_col, freq='ME'))[sales_col].sum().reset_index()
                
            if len(grouped) < 3:
                return None, "Requires at least 3 historical date data points to forecast."
                
            # Create day indices for linear regression
            grouped['day_idx'] = (grouped[date_col] - grouped[date_col].min()).dt.days
            
            x = grouped['day_idx'].values
            y = grouped[sales_col].values
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Generate future dates
            last_date = grouped[date_col].max()
            future_days = np.arange(1, periods + 1)
            future_dates = [last_date + pd.Timedelta(days=int(d)) for d in future_days]
            future_x = np.array([(fd - grouped[date_col].min()).days for fd in future_dates])
            
            future_y = intercept + slope * future_x
            future_y = np.maximum(future_y, y.min() * 0.5)  # Ensure non-negative predictions
            
            historical_df = pd.DataFrame({
                'Date': grouped[date_col],
                'Sales': y,
                'Type': 'Historical Actual'
            })
            
            forecast_df = pd.DataFrame({
                'Date': future_dates,
                'Sales': round(pd.Series(future_y), 2),
                'Type': 'AI Predicted Forecast'
            })
            
            combined_df = pd.concat([historical_df, forecast_df], ignore_index=True)
            
            # Calculate Trend Metrics
            total_predicted = forecast_df['Sales'].sum()
            avg_predicted = forecast_df['Sales'].mean()
            r_squared = round(r_value ** 2, 3)
            trend_direction = "📈 Upward Growth" if slope > 0 else "📉 Downward Shift"
            
            # Plotly Visualization
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=historical_df['Date'], 
                y=historical_df['Sales'],
                mode='lines+markers',
                name='Historical Actual',
                line=dict(color='#3b82f6', width=3)
            ))
            fig.add_trace(go.Scatter(
                x=forecast_df['Date'], 
                y=forecast_df['Sales'],
                mode='lines+markers',
                name=f'AI Forecast (Next {periods} Days)',
                line=dict(color='#10b981', width=3, dash='dash')
            ))
            
            fig.update_layout(
                title=f"🔮 Sales Forecast & Predictive Model (R² Confidence: {r_squared})",
                template="plotly_dark",
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            metrics = {
                'total_predicted': total_predicted,
                'avg_predicted': avg_predicted,
                'r_squared': r_squared,
                'trend_direction': trend_direction,
                'slope': round(slope, 2)
            }
            
            return {
                'fig': fig,
                'forecast_df': forecast_df,
                'metrics': metrics
            }, None
            
        except Exception as e:
            return None, f"Forecasting Error: {str(e)}"
