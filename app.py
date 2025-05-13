import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Drilling Cost Dashboard", layout="wide")
st.title("🚀 Drilling Cost Optimization Dashboard")
st.markdown("""
<style>
    .stTabs [data-baseweb="tab"] {
        font-size: 18px;
        padding: 8px 16px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📥 Upload Cost Optimization Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    mud_cost_per_bbl = 100
    haul_off_cost_per_bbl = 20

    df["Mud_Cost"] = df["Total_Dil"] * mud_cost_per_bbl
    df["Haul_Off_Cost"] = df["Haul_OFF"] * haul_off_cost_per_bbl
    df["Dilution_Cost_Per_Foot"] = df["Mud_Cost"] / df["IntLength"]
    df["Haul_Off_Cost_Per_Foot"] = df["Haul_Off_Cost"] / df["IntLength"]
    df["Cumulative_Cost"] = df["Mud_Cost"] + df["Haul_Off_Cost"]
    df["Cost_Per_Day"] = df["Cumulative_Cost"] / df["DOW"]

    df["TD_Date"] = pd.to_datetime(df["TD_Date"], errors='coerce')
    df["Year"] = df["TD_Date"].dt.year
    df["Month"] = df["TD_Date"].dt.month

    tab1, tab2, tab3 = st.tabs(["📊 Calculations", "📈 YOY & MOM Trends", "🧠 Insights & Summary"])

    with tab1:
        st.markdown("### 🔍 Filter Options")
        col1, col2, col3 = st.columns(3)
        with col1:
            operator_filter = st.multiselect("Operator", df["Operator"].dropna().unique())
        with col2:
            contractor_filter = st.multiselect("Contractor", df["Contractor"].dropna().unique())
        with col3:
            well_filter = st.multiselect("Well Job ID", df["Well_Job_ID"].dropna().unique())

        filtered_df = df.copy()
        if operator_filter:
            filtered_df = filtered_df[filtered_df["Operator"].isin(operator_filter)]
        if contractor_filter:
            filtered_df = filtered_df[filtered_df["Contractor"].isin(contractor_filter)]
        if well_filter:
            filtered_df = filtered_df[filtered_df["Well_Job_ID"].isin(well_filter)]

        st.markdown("### 📋 Calculated Cost Metrics")
        st.dataframe(filtered_df[[
            "Well_Job_ID", "Operator", "Contractor", "Total_Dil", "Haul_OFF", "IntLength", "DOW",
            "Mud_Cost", "Haul_Off_Cost", "Dilution_Cost_Per_Foot",
            "Haul_Off_Cost_Per_Foot", "Cumulative_Cost", "Cost_Per_Day"
        ]], use_container_width=True)

        st.download_button("📤 Download Data as Excel", data=filtered_df.to_excel(index=False, engine='openpyxl'), file_name="drilling_cost_report.xlsx")

    with tab2:
        st.markdown("### 📅 YOY and MOM Trend Analysis")
        flowline_filter = st.multiselect("Flowline Shaker", df["flowline_Shakers"].dropna().unique())
        operator2_filter = st.multiselect("Operator", df["Operator"].dropna().unique(), key="op2")
        contractor2_filter = st.multiselect("Contractor", df["Contractor"].dropna().unique(), key="cont2")

        dff = df.copy()
        if flowline_filter:
            dff = dff[dff["flowline_Shakers"].isin(flowline_filter)]
        if operator2_filter:
            dff = dff[dff["Operator"].isin(operator2_filter)]
        if contractor2_filter:
            dff = dff[dff["Contractor"].isin(contractor2_filter)]

        trend_df = dff.groupby(["Year", "Month"]).agg({
            "Cumulative_Cost": "mean",
            "Dilution_Cost_Per_Foot": "mean",
            "Haul_Off_Cost_Per_Foot": "mean",
            "Cost_Per_Day": "mean"
        }).reset_index()
        trend_df["Date"] = pd.to_datetime(trend_df[["Year", "Month"]].assign(DAY=1))

        st.plotly_chart(px.line(trend_df, x="Date", y="Cumulative_Cost", title="Cumulative Cost Over Time"), use_container_width=True)
        st.plotly_chart(px.line(trend_df, x="Date", y="Cost_Per_Day", title="Cost Per Day Trend"), use_container_width=True)

    with tab3:
        st.markdown("### 🧠 Summary of Key Cost Drivers")
        st.markdown("""
        - 📌 **Dilution Cost**: Investigate high dilution cost per foot for inefficiencies in fluid systems.
        - 📌 **Haul-Off Cost**: Track contractors with high haul-off costs—possible solids control issues.
        - 📌 **Cumulative Cost**: Use per day normalization to compare well economics fairly.
        - 📌 **Filter Strategy**: Use operator, contractor, and shaker filters to isolate performance clusters.
        - 📌 **Actionable Insight**: Target DSRE improvement zones to reduce screen consumption.
        """)
else:
    st.info("📂 Please upload a valid Excel file to proceed.")
