import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Power BI Clone", layout="wide")
st.title("📊 Power BI Style Interactive Dashboard")

# Upload Excel file
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_name = st.selectbox("Choose Sheet", xls.sheet_names)
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

    st.subheader("🔍 Raw Data Preview")
    st.dataframe(df.head())

    # Identify columns
    num_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(include='object').columns.tolist()
    date_cols = df.select_dtypes(include='datetime').columns.tolist()

    # Optional Filters
    st.sidebar.header("🎚️ Filters")

    selected_filters = {}
    for col in cat_cols:
        unique_vals = df[col].dropna().unique().tolist()
        selected_vals = st.sidebar.multiselect(f"Filter by {col}", unique_vals, default=unique_vals)
        selected_filters[col] = selected_vals
        df = df[df[col].isin(selected_vals)]

    st.markdown("## 📈 Visualizations")

    col1, col2 = st.columns(2)

    with col1:
        if num_cols:
            metric_col = st.selectbox("Choose numeric column (for summary)", num_cols)
            st.metric(label=f"Total {metric_col}", value=f"{df[metric_col].sum():,.2f}")

            bar_fig = px.histogram(df, x=metric_col, nbins=20, title=f"{metric_col} Distribution")
            st.plotly_chart(bar_fig, use_container_width=True)

        if cat_cols and num_cols:
            pie_cat = st.selectbox("Choose category for pie chart", cat_cols)
            pie_val = st.selectbox("Choose numeric for pie", num_cols)
            pie_data = df.groupby(pie_cat)[pie_val].sum().reset_index()
            pie_fig = px.pie(pie_data, names=pie_cat, values=pie_val, title=f"{pie_val} by {pie_cat}")
            st.plotly_chart(pie_fig, use_container_width=True)

    with col2:
        if cat_cols and num_cols:
            x_axis = st.selectbox("Bar Chart - X axis (category)", cat_cols)
            y_axis = st.selectbox("Bar Chart - Y axis (numeric)", num_cols)
            bar_chart = px.bar(df, x=x_axis, y=y_axis, color=x_axis, title=f"{y_axis} by {x_axis}")
            st.plotly_chart(bar_chart, use_container_width=True)

        if len(date_cols) > 0 and num_cols:
            time_col = st.selectbox("Time series - Date column", date_cols)
            ts_metric = st.selectbox("Time series - Value", num_cols)
            time_data = df.groupby(time_col)[ts_metric].sum().reset_index()
            line_fig = px.line(time_data, x=time_col, y=ts_metric, title=f"{ts_metric} over Time")
            st.plotly_chart(line_fig, use_container_width=True)

    st.markdown("## 🧮 Pivot Table")
    pivot_cat = st.selectbox("Pivot - Row category", cat_cols)
    pivot_val = st.selectbox("Pivot - Value column", num_cols)
    pivot_df = df.pivot_table(index=pivot_cat, values=pivot_val, aggfunc='sum').reset_index()
    st.dataframe(pivot_df)

        # Export Pivot - FIXED
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pivot_df.to_excel(writer, index=False, sheet_name='PivotSummary')
    output.seek(0)

    st.download_button(
        label="⬇️ Download Pivot Table as Excel",
        data=output,
        file_name="pivot_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Please upload an Excel file to begin.")
