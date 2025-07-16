import pandas as pd
import requests
import openpyxl
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
 
# --- FUNCTION TO FETCH PAGESPEED DATA ---
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
 
# --- FUNCTION TO PROCESS FILE ---
def process_file(filepath, api_key, strategy):
    try:
        df = pd.read_excel(filepath, engine='openpyxl')
        if 'URL' not in df.columns:
            raise ValueError("Excel file must contain a column named 'URL'.")
 
        urls = df['URL'].dropna().tolist()
        results = [fetch_pagespeed_data(url, strategy, api_key) for url in urls]
        result_df = pd.DataFrame(results)
        output_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[["Excel files", "*.xlsx"]])
        if output_path:
            result_df.to_excel(output_path, index=False)
            messagebox.showinfo("Success", f"PageSpeed report saved to {output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Error processing file: {e}")
 
# --- GUI ---
def run_gui():
    root = tk.Tk()
    root.title("PageSpeed Insights Bulk Checker")
    root.geometry("400x300")
 
    tk.Label(root, text="Google API Key:").pack(pady=5)
    api_key_entry = tk.Entry(root, width=50)
    api_key_entry.pack()
 
    tk.Label(root, text="Strategy:").pack(pady=5)
    strategy_choice = ttk.Combobox(root, values=["mobile", "desktop"])
    strategy_choice.set("mobile")
    strategy_choice.pack()
 
    def browse_file():
        filepath = filedialog.askopenfilename(filetypes=[["Excel files", "*.xlsx"]])
        if filepath:
            api_key = api_key_entry.get().strip()
            strategy = strategy_choice.get()
            if not api_key:
                messagebox.showerror("Missing API Key", "Please enter your Google API key.")
                return
            threading.Thread(target=process_file, args=(filepath, api_key, strategy), daemon=True).start()
 
    tk.Button(root, text="Select Excel File & Run", command=browse_file).pack(pady=20)
    root.mainloop()
 
if __name__ == "__main__":
    run_gui()
