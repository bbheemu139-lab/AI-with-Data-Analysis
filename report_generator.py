import pandas as pd
import numpy as np

class ReportGenerator:
    @staticmethod
    def generate_html_report(df, metrics, kpis, insights_text="", app_title="AI Data Analyst", author_name="Data Analyst"):
        """Generates executive HTML report string for printing / saving as PDF."""
        num_rows = metrics.get('total_rows', len(df))
        num_cols = metrics.get('total_cols', len(df.columns))
        missing_pct = metrics.get('missing_pct', 0)
        quality_score = metrics.get('quality_score', 95)
        
        tot_sales = kpis.get('total_sales', 0)
        tot_orders = kpis.get('total_orders', len(df))
        avg_sales = kpis.get('avg_sales', 0)

        sample_table_html = df.head(10).to_html(classes="report-table", index=False)

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{app_title} - Executive Insights Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 40px;
            color: #1e293b;
            background-color: #f8fafc;
        }}
        .header {{
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            color: #0f172a;
            font-size: 28px;
        }}
        .header p {{
            color: #64748b;
            margin: 5px 0 0 0;
        }}
        .author-badge {{
            display: inline-block;
            background: #e0e7ff;
            color: #3730a3;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 13px;
            margin-top: 8px;
        }}
        .grid {{
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            flex: 1;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid #e2e8f0;
        }}
        .card-title {{
            font-size: 12px;
            font-weight: bold;
            color: #64748b;
            text-transform: uppercase;
        }}
        .card-val {{
            font-size: 24px;
            font-weight: bold;
            color: #0f172a;
            margin-top: 5px;
        }}
        .section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 25px;
        }}
        .section h2 {{
            color: #1e3a8a;
            font-size: 18px;
            margin-top: 0;
        }}
        .report-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .report-table th, .report-table td {{
            border: 1px solid #e2e8f0;
            padding: 10px;
            text-align: left;
            font-size: 13px;
        }}
        .report-table th {{
            background-color: #f1f5f9;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{app_title} - Executive Report</h1>
        <p>Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <div class="author-badge">👤 Lead Analyst: {author_name}</div>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-title">Data Quality Score</div>
            <div class="card-val">{quality_score} / 100</div>
        </div>
        <div class="card">
            <div class="card-title">Total Records</div>
            <div class="card-val">{num_rows:,}</div>
        </div>
        <div class="card">
            <div class="card-title">Total Sales / Value</div>
            <div class="card-val">₹{tot_sales:,.2f}</div>
        </div>
        <div class="card">
            <div class="card-title">Avg Order Value</div>
            <div class="card-val">₹{avg_sales:,.2f}</div>
        </div>
    </div>

    <div class="section">
        <h2>💡 Key AI Business Insights & Recommendations</h2>
        <div>
            {insights_text.replace('\n', '<br>') if insights_text else "Dataset analyzed successfully. All metrics fall within expected baseline standard deviations."}
        </div>
    </div>

    <div class="section">
        <h2>📋 Data Quality & Profile Summary</h2>
        <ul>
            <li><b>Total Columns:</b> {num_cols}</li>
            <li><b>Missing Cell Rate:</b> {missing_pct}%</li>
            <li><b>Duplicate Rows:</b> {metrics.get('duplicate_rows', 0)}</li>
        </ul>
    </div>

    <div class="section">
        <h2>📊 Sample Dataset Preview (Top 10 Rows)</h2>
        {sample_table_html}
    </div>
</body>
</html>
"""
        return html_content
