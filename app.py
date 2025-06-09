import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="IMA I20 AI Support System", layout="wide")
st.title("📊 IMA I20 AI Support System")

creds = Credentials.from_service_account_info(st.secrets["google_service_account"])
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1GjfnGfWaE6dDtNU9fCjK9SRz8MWXlxTNaYip0Fctu70")
worksheet = sheet.sheet1

def load_data():
    records = worksheet.get_all_records()
    return pd.DataFrame(records)

def append_data(row):
    worksheet.append_row(row)

def update_sheet(dataframe):
    worksheet.clear()
    worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

df = load_data()

with st.expander("➕ Log New Machine Shift Data", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        operator_id = st.text_input("Operator ID (e.g. PNG1080)")
        machine = st.selectbox("Machine", sorted(set([
            "Press 40", "Wrapper 41", "Press 42", "Wrapper 43", "Press 44", "Wrapper 45",
            "Press 46", "Wrapper 47", "Press 48", "Wrapper 49", "Press 50", "Wrapper 51",
            "Press 62", "Wrapper 63", "Press 64", "Wrapper 65", "Press 66", "Wrapper 67",
            "Press 68", "Wrapper 69", "Press 80", "Wrapper 81", "Press 82", "Wrapper 83",
            "Press 84", "Wrapper 85", "Press 86", "Wrapper 87", "Press 88", "Wrapper 89"
        ])))
        oee = st.number_input("OEE (%)", min_value=0.0, max_value=100.0, step=0.1)
        runtime = st.number_input("Runtime (mins)", min_value=0)
        downtime = st.number_input("Downtime (mins)", min_value=0)
    with col2:
        date = st.date_input("Date")
        shift = st.selectbox("Shift", ["DAY A", "NIGHT A", "DAY B", "NIGHT B"])
        issue = st.text_area("Issue Faced")
        fix = st.text_area("Fix Applied")
    if st.button("Submit Entry"):
        row = [date.strftime("%Y-%m-%d"), shift, machine, oee, runtime, downtime, issue, fix, operator_id]
        append_data(row)
        st.success("✅ Entry logged successfully.")
        df = load_data()

st.subheader("📈 Performance Overview")
machines = df['Machine'].unique().tolist() if not df.empty else []
selected_machines = st.multiselect("Filter by Machine", machines, default=machines)
filtered_df = df[df['Machine'].isin(selected_machines)] if machines else df

if not filtered_df.empty:
    fig, axes = plt.subplots(1, 3, figsize=(18, 4))
    filtered_df.groupby("Machine")["OEE (%)"].mean().plot(kind="bar", ax=axes[0], title="Avg OEE")
    filtered_df.groupby("Machine")["Runtime (mins)"].sum().plot(kind="bar", ax=axes[1], title="Total Runtime")
    filtered_df.groupby("Machine")["Downtime (mins)"].sum().plot(kind="bar", ax=axes[2], title="Total Downtime")
    st.pyplot(fig)
else:
    st.info("No data available to display charts.")

st.subheader("📋 Editable Log History")
edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
if st.button("💾 Save Changes"):
    update_sheet(edited_df)
    st.success("✅ Log history updated successfully.")