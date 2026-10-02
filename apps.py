import os
import re
import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Import custom modules
from config import APP_TITLE, APP_SUBTITLE, load_css
from assets.themes import apply_theme
from modules.data_loader import DataLoader
from modules.data_cleaner import DataCleaner
from modules.auto_eda import AutoEDA
from modules.sql_engine import SQLEngine
from modules.python_runner import PythonRunner
from modules.dashboard_builder import DashboardBuilder
from modules.ai_analyst import AIAnalyst
from modules.excel_studio import ExcelStudio
from modules.pivot_studio import PivotStudio
from modules.exporter import DataExporter
from modules.voice_processor import VoiceProcessor

# Page configuration
st.set_page_config(
    page_title="AI Data Analyst Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load base dark glassmorphic CSS
load_css()

# Initialize session state for working DataFrame
if "raw_df" not in st.session_state:
    st.session_state.raw_df = None
if "df" not in st.session_state:
    st.session_state.df = None
if "cleaning_log" not in st.session_state:
    st.session_state.cleaning_log = []
if "active_data_key" not in st.session_state:
    st.session_state.active_data_key = None
if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = "dataset"

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.markdown("<h2 style='color:#3b82f6;margin-bottom:0;'>🚀 AI Data Analyst</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.8rem;color:#94a3b8;'>Excel + SQL + Python + Power BI + GenAI</p>", unsafe_allow_html=True)
    st.divider()

    st.markdown("### 📂 Data Source")
    data_source_mode = st.radio(
        "Choose Source:",
        ["Sample Datasets (1-Click Test)", "Upload CSV / Excel File"]
    )

    loaded_df = None
    data_key = None
    default_alias = "dataset"

    if data_source_mode == "Sample Datasets (1-Click Test)":
        samples = DataLoader.get_sample_datasets()
        selected_sample_label = st.selectbox("Select Sample Dataset:", list(samples.keys()))
        sample_path = samples[selected_sample_label]
        
        sheet_name = 0
        if sample_path.endswith('.xlsx'):
            sheets = DataLoader.get_excel_sheets(sample_path)
            if len(sheets) > 1:
                sheet_name = st.selectbox("Select Sheet:", sheets)
                
        loaded_df = DataLoader.load_file(sample_path, sheet_name=sheet_name)
        data_key = f"sample_{selected_sample_label}_{sheet_name}"
        default_alias = "Sales_Data" if "Sales" in selected_sample_label else "Ecommerce_Orders"

    else:
        uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])
        if uploaded_file is not None:
            sheet_name = 0
            if uploaded_file.name.endswith(('.xlsx', '.xls')):
                sheets = DataLoader.get_excel_sheets(uploaded_file)
                if len(sheets) > 1:
                    sheet_name = st.selectbox("Select Sheet:", sheets)
            loaded_df = DataLoader.load_file(uploaded_file, sheet_name=sheet_name)
            data_key = f"upload_{uploaded_file.name}_{uploaded_file.size}_{sheet_name}"
            default_alias = os.path.splitext(uploaded_file.name)[0]

    if loaded_df is not None and data_key is not None:
        if st.session_state.active_data_key != data_key:
            st.session_state.active_data_key = data_key
            st.session_state.raw_df = loaded_df.copy()
            st.session_state.df = loaded_df.copy()
            st.session_state.cleaning_log = []

    st.markdown("### 🏷️ Dataset Custom Name")
    user_alias = st.text_input("Dataset / Table Alias:", value=default_alias, help="Used as table name in SQL queries and reports.")
    clean_alias = re.sub(r'[^a-zA-Z0-9_]', '_', user_alias.strip()) or "dataset"
    st.session_state.dataset_name = clean_alias

    st.markdown("### 🎨 Personalization & Theme")
    custom_app_title = st.text_input("Application Title:", value="🚀 AI Data Analyst Platform", help="Customize main platform title.")
    author_name = st.text_input("Analyst / Creator Name:", value="Bheemu", help="Your personal or company name on dashboards.")
    selected_theme = st.selectbox("Dashboard Theme:", ["Dark Glassmorphic (Default)", "Emerald Neon", "Corporate Light Mode"])
    apply_theme(selected_theme)
    
    st.session_state.app_title = custom_app_title
    st.session_state.author_name = author_name

    st.divider()

    # AI Model Settings
    st.markdown("### 🤖 Generative AI Settings")
    ai_provider = st.selectbox("AI Engine Provider:", ["Gemini API", "OpenAI API", "Smart Offline Engine"])
    api_key_input = ""
    if ai_provider in ["Gemini API", "OpenAI API"]:
        api_key_input = st.text_input(f"Enter {ai_provider} Key:", type="password", help="Optional. Leaves blank to use smart offline mode.")

    st.divider()
    
    # Data Quality Badge in Sidebar
    if st.session_state.df is not None:
        metrics = DataLoader.get_data_quality_metrics(st.session_state.df)
        score = metrics.get('quality_score', 100)
        st.markdown(f"""
        <div style='background:rgba(30,41,59,0.8);padding:12px;border-radius:10px;border-left:4px solid #10b981;'>
            <div style='font-size:0.75rem;color:#94a3b8;'>DATA QUALITY SCORE</div>
            <div style='font-size:1.6rem;font-weight:bold;color:#34d399;'>{score} / 100</div>
            <div style='font-size:0.75rem;color:#cbd5e1;'>Rows: {metrics.get('total_rows', 0):,} | Cols: {metrics.get('total_cols', 0)}</div>
        </div>
        """, unsafe_allow_html=True)


# --- MAIN HEADER ---
cur_title = st.session_state.get('app_title', APP_TITLE)
cur_author = st.session_state.get('author_name', 'Bheemu')

st.markdown(f"<h1>{cur_title}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#94a3b8;font-size:1.05rem;'>{APP_SUBTITLE} &nbsp;|&nbsp; <span style='background:rgba(59,130,246,0.2);color:#60a5fa;padding:4px 12px;border-radius:12px;font-size:0.85rem;font-weight:600;'>👤 Lead Analyst: {cur_author}</span></p>", unsafe_allow_html=True)

if st.session_state.df is None:
    st.info("👈 Please select a sample dataset or upload a CSV/Excel file in the left sidebar to start analysis!")
    st.stop()

# --- MAIN NAVIGATION TABS ---
tab_hub, tab_clean, tab_eda, tab_bi, tab_excel, tab_sql, tab_python, tab_ai, tab_voice, tab_export = st.tabs([
    "📂 Data Hub",
    "🧹 AI Cleaning",
    "📊 Extended EDA Studio",
    "📈 Power BI Dashboard",
    "📊 Excel Studio",
    "🗄️ SQL Studio",
    "🐍 Python Sandbox",
    "🤖 AI Copilot",
    "🎙️ Voice AI",
    "💾 Export Center"
])

# ---------------------------------------------------------
# TAB 1: DATA HUB
# ---------------------------------------------------------
with tab_hub:
    st.markdown(f"<div class='section-banner'><h2>📂 Data Hub & Schema Preview ({st.session_state.dataset_name})</h2><p>Inspect raw dataset schema, datatypes, and initial record views</p></div>", unsafe_allow_html=True)

    metrics = DataLoader.get_data_quality_metrics(st.session_state.df)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Rows</div><div class='metric-value'>{metrics['total_rows']:,}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Columns</div><div class='metric-value'>{metrics['total_cols']}</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Missing Cells</div><div class='metric-value'>{metrics['missing_pct']}%</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Duplicates</div><div class='metric-value'>{metrics['duplicate_rows']}</div></div>", unsafe_allow_html=True)
    with c5:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Memory Usage</div><div class='metric-value'>{metrics['memory_mb']} MB</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([3, 1])

    with col_left:
        st.subheader("📋 Dataset Preview")
        st.dataframe(st.session_state.df, use_container_width=True, height=400)

    with col_right:
        st.subheader("🔍 Column Schema")
        schema_df = pd.DataFrame({
            "Column": st.session_state.df.columns,
            "DataType": [str(st.session_state.df[c].dtype) for c in st.session_state.df.columns],
            "Nulls": [st.session_state.df[c].isnull().sum() for c in st.session_state.df.columns]
        })
        st.dataframe(schema_df, use_container_width=True, height=400)


# ---------------------------------------------------------
# TAB 2: AI DATA CLEANING
# ---------------------------------------------------------
with tab_clean:
    st.markdown("<div class='section-banner'><h2>🧹 AI Data Cleaning Studio</h2><p>Automatically detect & resolve missing values, duplicate rows, datatypes, and outliers</p></div>", unsafe_allow_html=True)

    col_clean_btn, col_reset_btn = st.columns([2, 1])
    with col_clean_btn:
        if st.button("✨ Run 1-Click AI Auto-Clean", type="primary", use_container_width=True):
            cleaned, logs = DataCleaner.auto_clean(st.session_state.df)
            st.session_state.df = cleaned
            st.session_state.cleaning_log.extend(logs)
            st.success("✅ AI Auto-Cleaning applied successfully!")
            st.rerun()

    with col_reset_btn:
        if st.button("🔄 Reset to Original Data", use_container_width=True):
            st.session_state.df = st.session_state.raw_df.copy()
            st.session_state.cleaning_log = []
            st.info("Dataset reset to original raw format.")
            st.rerun()

    st.markdown("---")
    st.subheader("🛠️ Granular Cleaning Actions")
    clean_action_tabs = st.tabs(["Missing Values", "Remove Duplicates", "Cast Data Types", "Cap Outliers"])

    with clean_action_tabs[0]:
        c1, c2, c3 = st.columns(3)
        with c1:
            target_col = st.selectbox("Select Column with Missing Values:", st.session_state.df.columns, key="fill_col")
        with c2:
            strategy = st.selectbox("Strategy:", ["median", "mean", "mode", "zero", "drop"], key="fill_strat")
        with c3:
            st.write("&nbsp;")
            if st.button("Apply Imputation", key="btn_fill"):
                cleaned = DataCleaner.fill_missing(st.session_state.df, target_col, strategy=strategy)
                st.session_state.df = cleaned
                st.success(f"Filled missing values in '{target_col}' using {strategy}.")
                st.rerun()

    with clean_action_tabs[1]:
        dups_cnt = st.session_state.df.duplicated().sum()
        st.write(f"Current duplicate rows count: **{dups_cnt}**")
        if st.button("Remove Duplicates", key="btn_rem_dup"):
            cleaned, removed = DataCleaner.remove_duplicates(st.session_state.df)
            st.session_state.df = cleaned
            st.success(f"Removed {removed} duplicate rows.")
            st.rerun()

    with clean_action_tabs[2]:
        c1, c2, c3 = st.columns(3)
        with c1:
            cast_col = st.selectbox("Select Column:", st.session_state.df.columns, key="cast_col")
        with c2:
            target_type = st.selectbox("Target Type:", ["Integer", "Float", "DateTime", "String"], key="cast_type")
        with c3:
            st.write("&nbsp;")
            if st.button("Cast Data Type", key="btn_cast"):
                cleaned = DataCleaner.cast_type(st.session_state.df, cast_col, target_type)
                st.session_state.df = cleaned
                st.success(f"Converted '{cast_col}' to {target_type}.")
                st.rerun()

    with clean_action_tabs[3]:
        num_cols = list(st.session_state.df.select_dtypes(include=[np.number]).columns)
        if num_cols:
            c1, c2 = st.columns([2, 1])
            with c1:
                cap_col = st.selectbox("Numeric Column for Outlier Capping:", num_cols, key="cap_col")
            with c2:
                st.write("&nbsp;")
                if st.button("Cap Outliers (IQR)", key="btn_cap"):
                    cleaned, count = DataCleaner.cap_outliers_iqr(st.session_state.df, cap_col)
                    st.session_state.df = cleaned
                    st.success(f"Capped {count} outliers in '{cap_col}'.")
                    st.rerun()

    if st.session_state.cleaning_log:
        st.markdown("### 📜 Cleaning Execution Log")
        for log in st.session_state.cleaning_log:
            st.markdown(f"- {log}")


# ---------------------------------------------------------
# TAB 3: EXTENDED AUTOMATED EDA STUDIO (EXPANDED!)
# ---------------------------------------------------------
with tab_eda:
    st.markdown("<div class='section-banner'><h2>📊 Extended Automated EDA Studio</h2><p>Comprehensive statistical summary, correlation heatmaps, violin plots, treemaps & density contours</p></div>", unsafe_allow_html=True)

    eda_tabs = st.tabs([
        "Summary Statistics", 
        "Correlation Matrix", 
        "Violin & Distribution Plots", 
        "Hierarchical Treemaps", 
        "2D Density Contours",
        "Outlier Profiling"
    ])

    with eda_tabs[0]:
        st.subheader("🔢 Numerical Columns Summary Statistics")
        num_summary = AutoEDA.get_numeric_summary(st.session_state.df)
        if not num_summary.empty:
            st.dataframe(num_summary, use_container_width=True)
        else:
            st.info("No numerical columns found.")

        st.subheader("🔤 Categorical Columns Summary")
        cat_summary = AutoEDA.get_categorical_summary(st.session_state.df)
        if not cat_summary.empty:
            st.dataframe(cat_summary, use_container_width=True)

    with eda_tabs[1]:
        corr_fig = AutoEDA.create_correlation_heatmap(st.session_state.df)
        if corr_fig:
            st.plotly_chart(corr_fig, use_container_width=True)
        else:
            st.info("Requires at least 2 numerical columns for correlation matrix.")

    with eda_tabs[2]:
        num_cols = list(st.session_state.df.select_dtypes(include=[np.number]).columns)
        cat_cols = list(st.session_state.df.select_dtypes(include=['object', 'category']).columns)
        if num_cols:
            c1, c2 = st.columns(2)
            with c1:
                dist_col = st.selectbox("Select Numeric Column:", num_cols, key="eda_dist_col")
                dist_fig = AutoEDA.create_distribution_plot(st.session_state.df, dist_col)
                if dist_fig:
                    st.plotly_chart(dist_fig, use_container_width=True)
            with c2:
                cat_sub_col = st.selectbox("Group By Category (Optional):", [None] + cat_cols, key="eda_v_cat")
                v_fig = AutoEDA.create_violin_plot(st.session_state.df, dist_col, cat_col=cat_sub_col)
                if v_fig:
                    st.plotly_chart(v_fig, use_container_width=True)

    with eda_tabs[3]:
        cat_cols = list(st.session_state.df.select_dtypes(include=['object', 'category']).columns)
        num_cols = list(st.session_state.df.select_dtypes(include=[np.number]).columns)
        if cat_cols and num_cols:
            tm_cats = st.multiselect("Select Hierarchy Categories:", cat_cols, default=cat_cols[:2] if len(cat_cols)>=2 else cat_cols, key="tm_cats")
            tm_val = st.selectbox("Select Metric Value:", num_cols, key="tm_val")
            if tm_cats and tm_val:
                tm_fig = AutoEDA.create_treemap_chart(st.session_state.df, tm_cats, tm_val)
                if tm_fig:
                    st.plotly_chart(tm_fig, use_container_width=True)

    with eda_tabs[4]:
        num_cols = list(st.session_state.df.select_dtypes(include=[np.number]).columns)
        if len(num_cols) >= 2:
            dc1, dc2 = st.columns(2)
            with dc1:
                x_c = st.selectbox("X-Axis Feature:", num_cols, index=0, key="dc_x")
            with dc2:
                y_c = st.selectbox("Y-Axis Feature:", num_cols, index=1 if len(num_cols)>1 else 0, key="dc_y")
            dc_fig = AutoEDA.create_density_contour(st.session_state.df, x_c, y_c)
            if dc_fig:
                st.plotly_chart(dc_fig, use_container_width=True)

    with eda_tabs[5]:
        st.subheader("🚨 Outlier Profiling Table")
        outliers_df = AutoEDA.detect_outliers_summary(st.session_state.df)
        st.dataframe(outliers_df, use_container_width=True)


# ---------------------------------------------------------
# TAB 4: ADVANCED POWER BI DASHBOARD (EXPANDED!)
# ---------------------------------------------------------
with tab_bi:
    st.markdown("<div class='section-banner'><h2>📈 Advanced Power BI-Style Interactive Dashboard</h2><p>Executive KPI cards, Target Gauge indicators, Conversion Funnel, and dynamic slicers</p></div>", unsafe_allow_html=True)

    df_filtered = st.session_state.df.copy()

    # Interactive Slicers Panel
    st.subheader("🎛️ Dashboard Slicers & Filters")
    slicer_cols = st.columns(3)

    cat_cols = list(df_filtered.select_dtypes(include=['object', 'category']).columns)
    if cat_cols:
        with slicer_cols[0]:
            sel_cat_col = st.selectbox("Filter Category Column:", cat_cols, key="bi_cat_col")
            unique_vals = list(df_filtered[sel_cat_col].dropna().unique())
            selected_cat_vals = st.multiselect("Select Values:", unique_vals, default=unique_vals[:4] if len(unique_vals)>4 else unique_vals)
            if selected_cat_vals:
                df_filtered = df_filtered[df_filtered[sel_cat_col].isin(selected_cat_vals)]

    num_cols = list(df_filtered.select_dtypes(include=[np.number]).columns)
    if num_cols:
        with slicer_cols[1]:
            num_filter_col = st.selectbox("Filter Range Column:", num_cols, key="bi_num_col")
            min_val = float(df_filtered[num_filter_col].min())
            max_val = float(df_filtered[num_filter_col].max())
            if min_val < max_val:
                selected_range = st.slider("Select Range:", min_val, max_val, (min_val, max_val))
                df_filtered = df_filtered[(df_filtered[num_filter_col] >= selected_range[0]) & (df_filtered[num_filter_col] <= selected_range[1])]

    # KPI Calculation
    kpis = DashboardBuilder.calculate_kpis(df_filtered)

    st.markdown("<br>", unsafe_allow_html=True)
    kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)
    with kpi_c1:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Revenue / Sales</div><div class='metric-value'>₹{kpis['total_sales']:,.2f}</div><div class='metric-badge badge-positive'>⬆ +18.4% YoY</div></div>", unsafe_allow_html=True)
    with kpi_c2:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Orders / Records</div><div class='metric-value'>{kpis['total_orders']:,}</div><div class='metric-badge badge-positive'>Active Transactions</div></div>", unsafe_allow_html=True)
    with kpi_c3:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Avg Transaction Value</div><div class='metric-value'>₹{kpis['avg_sales']:,.2f}</div><div class='metric-badge badge-warning'>Stable Margin</div></div>", unsafe_allow_html=True)
    with kpi_c4:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Net Profit Margin</div><div class='metric-value'>{kpis['profit_margin']}%</div><div class='metric-badge badge-positive'>Healthy Profit</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Target Gauge Chart & Sales Funnel
    g0_left, g0_right = st.columns(2)
    sales_col = kpis.get('sales_col', num_cols[0] if num_cols else df_filtered.columns[0])
    group_cat_col = cat_cols[0] if cat_cols else df_filtered.columns[0]

    with g0_left:
        target_revenue = kpis['total_sales'] * 1.15
        gauge_fig = DashboardBuilder.create_gauge_chart(kpis['total_sales'], target_revenue, title="🎯 Q3 Revenue Target Completion")
        st.plotly_chart(gauge_fig, use_container_width=True)

    with g0_right:
        funnel_fig = DashboardBuilder.create_funnel_chart(df_filtered, group_cat_col, sales_col)
        if funnel_fig:
            st.plotly_chart(funnel_fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    g1, g2 = st.columns(2)

    date_cols = list(df_filtered.select_dtypes(include=['datetime', 'datetime64']).columns)
    if not date_cols:
        for c in df_filtered.columns:
            if 'date' in c.lower() or 'time' in c.lower():
                date_cols.append(c)

    with g1:
        if date_cols and sales_col in df_filtered.columns:
            trend_fig = DashboardBuilder.create_sales_trend_chart(df_filtered, date_cols[0], sales_col)
            st.plotly_chart(trend_fig, use_container_width=True)
        else:
            bar_fig = DashboardBuilder.create_top_products_chart(df_filtered, group_cat_col, sales_col)
            st.plotly_chart(bar_fig, use_container_width=True)

    with g2:
        if group_cat_col and sales_col in df_filtered.columns:
            pie_fig = DashboardBuilder.create_category_pie_chart(df_filtered, group_cat_col, sales_col)
            st.plotly_chart(pie_fig, use_container_width=True)


# ---------------------------------------------------------
# TAB 5: INTERACTIVE EXCEL STUDIO (NEW!)
# ---------------------------------------------------------
with tab_excel:
    st.markdown("<div class='section-banner'><h2>📊 Interactive Excel Studio</h2><p>Excel formula engine, conditional formatting, and dynamic matrix pivot summarizer</p></div>", unsafe_allow_html=True)

    ex_tabs = st.tabs(["Excel Formula Engine", "Conditional Formatting Table", "Excel Matrix Pivot"])

    with ex_tabs[0]:
        st.subheader("⚡ Excel Formula Evaluator")
        st.markdown("Try formulas like `=SUM(Total_Sales_INR)`, `=AVERAGE(Profit_INR)`, `=COUNT(Order_ID)`, `=MAX(Unit_Price_INR)`, `=MIN(Profit_INR)`")
        
        col_list = list(st.session_state.df.columns)
        num_col_sample = list(st.session_state.df.select_dtypes(include=[np.number]).columns)
        default_formula = f"=SUM({num_col_sample[0]})" if num_col_sample else f"=COUNT({col_list[0]})"

        formula_input = st.text_input("Enter Excel Formula:", value=default_formula)
        if st.button("Evaluate Formula", type="primary"):
            res_str, err = ExcelStudio.evaluate_excel_formula(st.session_state.df, formula_input)
            if err:
                st.error(err)
            else:
                st.success(res_str)

    with ex_tabs[1]:
        st.subheader("🎨 Excel Conditional Formatting Color Scale")
        num_cols = list(st.session_state.df.select_dtypes(include=[np.number]).columns)
        if num_cols:
            fmt_col = st.selectbox("Select Numerical Column for Color Gradient:", num_cols, key="fmt_col")
            styled_df = ExcelStudio.apply_conditional_formatting(st.session_state.df.head(25), fmt_col)
            st.dataframe(styled_df, use_container_width=True)

    with ex_tabs[2]:
        st.subheader("🧮 Excel Matrix Pivot Summarizer")
        cat_cols = list(st.session_state.df.select_dtypes(include=['object', 'category']).columns)
        num_cols = list(st.session_state.df.select_dtypes(include=[np.number]).columns)

        if cat_cols and num_cols:
            p1, p2, p3 = st.columns(3)
            with p1:
                idx = st.selectbox("Row Category:", cat_cols, key="ex_p_idx")
            with p2:
                val = st.selectbox("Value Metric:", num_cols, key="ex_p_val")
            with p3:
                agg = st.selectbox("Aggregation:", ["sum", "mean", "count", "max", "min"], key="ex_p_agg")

            p_display, p_fig, p_err = PivotStudio.generate_pivot(st.session_state.df, [idx], None, val, agg_func=agg)
            if p_display is not None:
                st.dataframe(p_display, use_container_width=True)
                if p_fig:
                    st.plotly_chart(p_fig, use_container_width=True)


# ---------------------------------------------------------
# TAB 6: SQL ANALYSIS STUDIO
# ---------------------------------------------------------
with tab_sql:
    tbl_name = st.session_state.get("dataset_name", "dataset")
    st.markdown(f"<div class='section-banner'><h2>🗄️ SQL Analysis Studio ({tbl_name})</h2><p>Run ANSI SQL queries on database table `{tbl_name}`</p></div>", unsafe_allow_html=True)

    sql_engine = SQLEngine(st.session_state.df, table_name=tbl_name)

    st.markdown(f"**Target Table Name:** `{tbl_name}` &nbsp;|&nbsp; **Schema:** `{sql_engine.get_table_schema()}`")

    default_sql = f"SELECT Category, SUM(Total_Sales_INR) as Total_Revenue, COUNT(*) as Orders FROM `{tbl_name}` GROUP BY Category ORDER BY Total_Revenue DESC;" if "Total_Sales_INR" in st.session_state.df.columns else f"SELECT * FROM `{tbl_name}` LIMIT 10;"

    sql_query_input = st.text_area("Write ANSI SQL Query:", value=default_sql, height=120)

    if st.button("🚀 Execute SQL Query", type="primary"):
        res_df, err = sql_engine.execute_query(sql_query_input)
        if err:
            st.error(f"SQL Execution Error: {err}")
        else:
            st.success(f"Query returned {len(res_df)} rows!")
            st.dataframe(res_df, use_container_width=True)

            if not res_df.empty and len(res_df.columns) >= 2:
                fig = px.bar(res_df, x=res_df.columns[0], y=res_df.columns[1], title=f"SQL Visualization (`{tbl_name}`)", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------
# TAB 7: PYTHON SANDBOX
# ---------------------------------------------------------
with tab_python:
    st.markdown("<div class='section-banner'><h2>🐍 Python Analytics Sandbox</h2><p>Execute custom Pandas / NumPy / Plotly code snippets in a safe isolated environment</p></div>", unsafe_allow_html=True)

    default_python = PythonRunner.generate_sample_python_code(f"Analysis for {st.session_state.dataset_name}", st.session_state.df)
    py_code_input = st.text_area("Python Code Editor:", value=default_python, height=220)

    if st.button("▶ Run Python Code", type="primary"):
        exec_res = PythonRunner.run_code(st.session_state.df, py_code_input)
        if exec_res['error']:
            st.error(f"Python Execution Error: {exec_res['error']}")
        else:
            st.success("Python script executed cleanly!")
            if exec_res['logs']:
                st.markdown("### 🖥️ Console Output")
                st.code(exec_res['logs'])

            if exec_res['result'] is not None and isinstance(exec_res['result'], pd.DataFrame):
                st.markdown("### 📊 Result Dataframe")
                st.dataframe(exec_res['result'], use_container_width=True)

            if exec_res['fig'] is not None:
                st.markdown("### 📈 Generated Figure")
                st.plotly_chart(exec_res['fig'], use_container_width=True)


# ---------------------------------------------------------
# TAB 8: GENERATIVE AI COPILOT
# ---------------------------------------------------------
with tab_ai:
    st.markdown(f"<div class='section-banner'><h2>🤖 Generative AI Data Analyst ({st.session_state.dataset_name})</h2><p>Ask complex business questions and get answers, SQL, Python & Charts</p></div>", unsafe_allow_html=True)

    user_q = st.text_input(
        "Ask your business question:",
        value="Which product generated the highest revenue and why?",
        placeholder="e.g. Which product generated highest sales? Find unusual anomalies."
    )

    quick_prompts = st.columns(4)
    with quick_prompts[0]:
        if st.button("🏆 Top Products Revenue"):
            user_q = "Which product generated the highest revenue and why?"
    with quick_prompts[1]:
        if st.button("📉 Sales Decrease Causes"):
            user_q = "Why did sales decrease in certain categories?"
    with quick_prompts[2]:
        if st.button("🚨 Find Anomalies"):
            user_q = "Find unusual data anomalies and high value outliers"
    with quick_prompts[3]:
        if st.button("💡 Strategic Advice"):
            user_q = "Give business recommendations to improve profitability"

    if st.button("✨ Ask AI Analyst", type="primary", use_container_width=True):
        with st.spinner("🤖 AI Analyst is querying SQL, synthesizing Python code, and building insights..."):
            tbl_name = st.session_state.get("dataset_name", "dataset")
            ai_analyst = AIAnalyst(st.session_state.df, api_key=api_key_input, provider=ai_provider, table_name=tbl_name)
            res = ai_analyst.analyze_question(user_q)

            st.markdown("<div class='ai-insight-box'>", unsafe_allow_html=True)
            st.markdown("<div class='ai-insight-title'>🤖 AI Business Analysis & Recommendations</div>", unsafe_allow_html=True)
            st.markdown(res['answer'])
            st.markdown("</div>", unsafe_allow_html=True)

            if res['fig']:
                st.plotly_chart(res['fig'], use_container_width=True)

            code_col1, code_col2 = st.columns(2)
            with code_col1:
                st.markdown(f"### 🗄️ Executed SQL Query (`{tbl_name}`)")
                st.code(res['sql_query'], language="sql")
                if res['sql_result'] is not None:
                    st.dataframe(res['sql_result'], use_container_width=True)

            with code_col2:
                st.markdown("### 🐍 Synthesized Python Pandas Code")
                st.code(res['python_code'], language="python")



# ---------------------------------------------------------
# TAB 9: VOICE AI  (Speech-to-Text + Text-to-Speech)
# ---------------------------------------------------------
with tab_voice:
    st.markdown("<div class='section-banner'><h2>🎙️ Voice AI Assistant</h2><p>Ask data questions using your voice — Speech-to-Text + AI Answer + Read-Aloud TTS</p></div>", unsafe_allow_html=True)

    voice_tabs = st.tabs(["🎤 Voice Question", "📢 Text-to-Speech", "ℹ️ Setup Guide"])

    # ── Sub-tab 1: Voice Question → AI Answer ────────────────────────────────
    with voice_tabs[0]:
        st.markdown("### 🎙️ Speak Your Data Question")
        st.info("📌 Upload a WAV/MP3/M4A audio file with your question. The AI will transcribe and answer it!", icon="🎤")

        transcribed_q = VoiceProcessor.render_voice_input_widget(key_prefix="main_voice")

        if transcribed_q:
            st.markdown("---")
            st.markdown("### 🤖 AI Answer for your Voice Question")
            if st.button("✨ Analyze Voice Question with AI", type="primary", use_container_width=True, key="voice_ai_btn"):
                with st.spinner("🤖 AI is analyzing your voice question..."):
                    tbl_name = st.session_state.get("dataset_name", "dataset")
                    ai_analyst = AIAnalyst(
                        st.session_state.df,
                        api_key=api_key_input,
                        provider=ai_provider,
                        table_name=tbl_name
                    )
                    res = ai_analyst.analyze_question(transcribed_q)

                    st.markdown("<div class='ai-insight-box'>", unsafe_allow_html=True)
                    st.markdown("<div class='ai-insight-title'>🤖 AI Business Analysis (Voice Query)</div>", unsafe_allow_html=True)
                    st.markdown(res['answer'])
                    st.markdown("</div>", unsafe_allow_html=True)

                    # Store answer for TTS
                    st.session_state["last_ai_voice_answer"] = res['answer']

                    if res['fig']:
                        st.plotly_chart(res['fig'], use_container_width=True)

                    c1, c2 = st.columns(2)
                    with c1:
                        st.code(res.get('sql_query', ''), language="sql")
                    with c2:
                        st.code(res.get('python_code', ''), language="python")

            # TTS for last AI answer
            last_answer = st.session_state.get("last_ai_voice_answer", "")
            if last_answer:
                st.markdown("---")
                VoiceProcessor.render_tts_widget(last_answer, key_prefix="voice_ans_tts")

    # ── Sub-tab 2: Manual Text-to-Speech ────────────────────────────────────
    with voice_tabs[1]:
        st.markdown("### 📢 Convert Any Text to Speech")
        tts_input = st.text_area(
            "Enter text to speak:",
            value="Welcome to the AI Data Analyst Platform. I am ready to help you analyze your data.",
            height=150,
            key="manual_tts_text"
        )
        if st.button("🔊 Generate Audio", type="primary", key="manual_tts_btn"):
            with st.spinner("Generating audio..."):
                wav_bytes, err = VoiceProcessor.text_to_speech(tts_input)
                if err:
                    st.warning(f"TTS Error: {err}")
                elif wav_bytes:
                    st.success("✅ Audio generated!")
                    st.audio(wav_bytes, format="audio/wav")

    # ── Sub-tab 3: Setup Guide ────────────────────────────────────────────────
    with voice_tabs[2]:
        st.markdown("""
### 🛠️ Voice AI Setup Guide

#### Option A — Full Offline (Recommended)
```bash
pip install SpeechRecognition pyttsx3 openai-whisper
```
- **Whisper** = Best accuracy, works without internet
- **pyttsx3** = Text-to-Speech, fully offline

#### Option B — Online (Google API)
```bash
pip install SpeechRecognition pyttsx3
```
- Uses Google Speech API (needs internet for transcription)

#### Supported Audio Formats
| Format | Extension | Notes |
|--------|-----------|-------|
| WAV | .wav | Best quality, recommended |
| MP3 | .mp3 | Compressed, widely supported |
| M4A | .m4a | iPhone recordings |
| OGG | .ogg | Open source format |
| FLAC | .flac | Lossless quality |

#### 🎤 How to Record Voice on Windows
1. Open **Sound Recorder** (Windows Key → search "Sound Recorder")
2. Record your question
3. Save as `.wav` or `.m4a`
4. Upload in the **Voice Question** tab above
        """)
        st.success("✅ Voice AI module is active — upload an audio file to start!")


# ---------------------------------------------------------
# TAB 10: MULTI-FORMAT EXPORT CENTER
# ---------------------------------------------------------
with tab_export:

    st.markdown(f"<div class='section-banner'><h2>💾 Multi-Format Cleaned Data Export Center</h2><p>Download cleaned dataset `{st.session_state.dataset_name}` in Excel, CSV, JSON, or SQLite DB formats</p></div>", unsafe_allow_html=True)

    tbl_name = st.session_state.get("dataset_name", "dataset")

    ex1, ex2, ex3, ex4 = st.columns(4)

    with ex1:
        st.markdown("### 🟢 Excel Workbook (.xlsx)")
        excel_data = DataExporter.to_excel_bytes(st.session_state.df, sheet_name=tbl_name)
        st.download_button(
            label="📥 Download Excel (.xlsx)",
            data=excel_data,
            file_name=f"{tbl_name}_Cleaned.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with ex2:
        st.markdown("### 🔵 CSV File (.csv)")
        csv_data = DataExporter.to_csv_bytes(st.session_state.df)
        st.download_button(
            label="📥 Download CSV (.csv)",
            data=csv_data,
            file_name=f"{tbl_name}_Cleaned.csv",
            mime="text/csv",
            use_container_width=True
        )

    with ex3:
        st.markdown("### 🟣 JSON Array (.json)")
        json_data = DataExporter.to_json_bytes(st.session_state.df)
        st.download_button(
            label="📥 Download JSON (.json)",
            data=json_data,
            file_name=f"{tbl_name}_Cleaned.json",
            mime="application/json",
            use_container_width=True
        )

    with ex4:
        st.markdown("### 🗄️ SQLite DB Script (.db)")
        sqlite_data = DataExporter.to_sqlite_bytes(st.session_state.df, table_name=tbl_name)
        st.download_button(
            label="📥 Download SQLite (.db)",
            data=sqlite_data,
            file_name=f"{tbl_name}_Database.db",
            mime="application/x-sqlite3",
            use_container_width=True
        )
