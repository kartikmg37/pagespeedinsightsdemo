import streamlit as st
import pandas as pd
import requests
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
        audits = lighthouse.get("audits", {})

        # Extract Core Web Vitals if present
        lcp = audits.get("largest-contentful-paint", {}).get("displayValue", None)
        fcp = audits.get("first-contentful-paint", {}).get("displayValue", None)
        cls = audits.get("cumulative-layout-shift", {}).get("displayValue", None)

        return {
            'URL': url,
            'Strategy': strategy,
            'Performance': categories.get('performance', {}).get('score', None),
            'Accessibility': categories.get('accessibility', {}).get('score', None),
            'Best Practices': categories.get('best-practices', {}).get('score', None),
            'SEO': categories.get('seo', {}).get('score', None),
            'LCP': lcp,
            'FCP': fcp,
            'CLS': cls,
            'Error': '',
            'Manual Test': f"https://pagespeed.web.dev/report?url={url}"
        }

    except Exception as e:
        return {
            'URL': url,
            'Strategy': strategy,
            'Performance': None,
            'Accessibility': None,
            'Best Practices': None,
            'SEO': None,
            'LCP': None,
            'FCP': None,
            'CLS': None,
            'Error': str(e),
            'Manual Test': f"https://pagespeed.web.dev/report?url={url}"
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title="PageSpeed Report Tool", layout="centered")
st.title("📊 Google PageSpeed Insights Report Tool")

api_key = st.text_input("🔐 Enter your Google API Key", type="password")
uploaded_file = st.file_uploader("📄 Upload Excel or CSV file with URLs", type=["xlsx", "csv"])
strategy = st.selectbox("📱 Select Strategy", ["Mobile", "Desktop"])

if st.button("⚡ Fetch Reports"):
    if not uploaded_file or not api_key.strip():
        st.error("Please upload a valid file and enter an API key.")
    else:
        try:
            # Detect file type
            if uploaded_file.name.endswith(".csv"):
                url_df = pd.read_csv(uploaded_file)
            else:
                url_df = pd.read_excel(uploaded_file)

            if url_df.shape[1] == 0:
                st.error("Uploaded file has no columns.")
            else:
                url_column = url_df.columns[0]
                urls = url_df[url_column].dropna().astype(str).tolist()

                results = []
                with st.spinner("Fetching data..."):
                    for url in urls:
                        result = fetch_pagespeed_data(url.strip(), strategy.lower(), api_key)
                        results.append(result)

                df = pd.DataFrame(results)
                df.fillna("N/A", inplace=True)

                st.success("✅ Report generated!")
                st.dataframe(df)

                # Download to Excel
                output = BytesIO()
                df.to_excel(output, index=False, engine='openpyxl')
                st.download_button(
                    label="📥 Download Excel Report",
                    data=output.getvalue(),
                    file_name="pagespeed_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
