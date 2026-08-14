import pandas as pd
import streamlit as st

@st.cache_data
def load_and_clean_data():
    df = pd.read_csv('dataset_desa_fiktif.csv', sep=None, engine='python')
    df.columns = df.columns.str.strip().str.replace('"', '')
    
    def clean_numeric_col(val, is_percentage=False):
        if pd.isna(val): return val
        val_str = str(val).strip().replace(',', '.')
        if val_str.endswith('.00'): val_str = val_str[:-3]
        if val_str.count('.') > 1:
            parts = val_str.split('.')
            val_str = parts[0] + '.' + parts[1]
        res = float(val_str)
        if is_percentage and res <= 1.0: res *= 100
        return res

    df['persentase_kemiskinan'] = df['persentase_kemiskinan'].apply(lambda x: clean_numeric_col(x, is_percentage=True))
    df['jarak_ke_pusat_kota_km'] = df['jarak_ke_pusat_kota_km'].apply(clean_numeric_col)
    
    signal_map = {'No Signal': 3, '2G/3G': 2, '4G Weak': 1}
    df['sinyal_score'] = df['status_sinyal_eksisting'].map(signal_map)
    return df
