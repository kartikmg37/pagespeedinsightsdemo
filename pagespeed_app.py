import streamlit as st
import pandas as pd
import requests

def fetch_pagespeed_data(url, strategy, api_key):
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        'url': url,
        'key': api_key,
        'strategy': strategy
    }
    try:
        response = requests.get(endpoint, params=params)
        data = response.json()

        lighthouse_score = data['lighthouseResult']['categories']['performance']['score'] * 100
        audits = data['lighthouseResult']['audits']

        return {
            'URL': url,
            'Performance Score': lighthouse_score,
            'FCP': audits.get('first-contentful-paint', {}).get('displayValue', 'N/A'),
            'LCP': audits.get('largest-contentful-paint', {}).get('displayValue', 'N/A'),
            'CLS': audits.get('cumulative-layout-shift', {}).get('displayValue', 'N/A'),
            'INP': audits.get('interactive', {}).get('displayValue', 'N/A'),
            'Improvement Areas': "; ".join([
                audit.get("title") for audit in audits.values()
                if audit.get("score") is not None and audit.get("scoreDisplayMode") == "numeric" and audit.get("score") < 0.9
            ]) or "None"
        }
    except Exception as e:
        return {
            'URL': url,
            'Error': str(e)
        }

st.title("📊 PageSpeed Insights Bulk Checker")

api_key = st.text_input("Enter your Google API Key", type="password")
strategy = st.selectbox("Select Strategy", ["mobile", "desktop"])
uploaded_file = st.file_uploader("Upload Excel file with 'URL' column", type="xlsx")

if uploaded_file and api_key:
    try:
        df = pd.read_excel(uploaded_file)
        if 'URL' not in df.columns:
            st.error("Excel file must contain a column named 'URL'.")
        else:
            urls = df['URL'].dropna().tolist()
            with st.spinner("Fetching PageSpeed data..."):
                results = [fetch_pagespeed_data(url, strategy, api_key) for url in urls]
            result_df = pd.DataFrame(results)
            st.success("Report generated!")

            st.download_button(
                label="📥 Download Results as Excel",
                data=result_df.to_excel(index=False, engine='openpyxl'),
                file_name="pagespeed_report.xlsx"
            )

            st.dataframe(result_df)
    except Exception as e:
        st.error(f"Error: {e}")
