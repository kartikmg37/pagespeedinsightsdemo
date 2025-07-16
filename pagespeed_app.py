import streamlit as st
import requests
import pandas as pd
from io import BytesIO

def fetch_pagespeed_data(url, strategy, api_key):
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        'url': url,
        'strategy': strategy,
        'key': api_key
    }

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        lighthouse = data.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})

        return {
            'URL': url,
            'Strategy': strategy,
            'Performance': categories.get('performance', {}).get('score', None),
            'Accessibility': categories.get('accessibility', {}).get('score', None),
            'Best Practices': categories.get('best-practices', {}).get('score', None),
            'SEO': categories.get('seo', {}).get('score', None)
        }

    except Exception as e:
        return {'URL': url, 'Error': str(e)}

# --- STREAMLIT UI ---
st.title("📊 Google PageSpeed Insights Report Tool")

api_key = st.text_input("🔐 Enter your Google API Key", type="password")

urls_input = st.text_area("🌐 Enter URLs (one per line)")

strategy = st.selectbox("📱 Select Strategy", ["Mobile", "Desktop"])

if st.button("⚡ Fetch Reports"):
    if not urls_input.strip() or not api_key.strip():
        st.error("Please enter both URLs and a valid API key.")
    else:
        urls = [url.strip() for url in urls_input.strip().splitlines()]
        results = []

        with st.spinner("Fetching data..."):
            for url in urls:
                result = fetch_pagespeed_data(url, strategy.lower(), api_key)
                results.append(result)

        df = pd.DataFrame(results)

        st.success("✅ Report generated!")
        st.dataframe(df)

        # Download link
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        st.download_button(
            label="📥 Download Excel Report",
            data=output.getvalue(),
            file_name="pagespeed_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
