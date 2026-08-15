# app.py
import streamlit as st
from config import LANG_TEXTS, TOTAL_LIMIT, DEFAULT_WEIGHTS, SLIDER_CSS
from data_loader import load_and_clean_data
from topsis import run_topsis_engine
from components import (
    render_sliders,
    render_dashboard_visuals,
    render_geospatial_map,
    render_export_section,
    render_sensitivity_analysis
)

# 1. Page Configuration
st.set_page_config(page_title="Village Wi-Fi Priority Index (TOPSIS)", layout="wide")

# Initialize language session state if not set
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'English'

# Inject CSS styles for sliders
st.markdown(SLIDER_CSS, unsafe_allow_html=True)

# 2. Header Layout (Bilingual selector on the top right)
header_col1, header_col2 = st.columns([5, 1])

# Check and update language state
with header_col2:
    selected_lang = st.selectbox(
        "Language Selection", 
        ["English", "Bahasa Indonesia"], 
        index=0 if st.session_state['lang'] == 'English' else 1,
        label_visibility="collapsed"
    )
    if selected_lang != st.session_state['lang']:
        st.session_state['lang'] = selected_lang
        st.rerun()

lang_code = 'en' if st.session_state['lang'] == "English" else 'id'
t = LANG_TEXTS[lang_code]

with header_col1:
    st.title(t['title'])
    st.caption(t['subtitle'])

# 3. Load & Clean Data
df = load_and_clean_data()

# 4. Main TOPSIS Dashboard View
st.write(t['weight_header'])
w_p_val, w_k_val, w_j_val, w_si_val, w_se_val = render_sliders(t, TOTAL_LIMIT, DEFAULT_WEIGHTS)

# Run TOPSIS
w_p, w_k, w_j, w_si, w_se = w_p_val/100, w_k_val/100, w_j_val/100, w_si_val/100, w_se_val/100
df_ranked = run_topsis_engine(df, w_p, w_k, w_j, w_si, w_se)

# Filter & Search Controls
st.markdown("---")
st.subheader(t['filter_header'])
f1, f2, f3, f4 = st.columns([2, 2, 2, 2])
with f1:
    search_query = st.text_input(t['search_label'], "", placeholder=t['search_placeholder'])
with f2:
    sig_opts = df_ranked['status_sinyal_eksisting'].unique().tolist()
    sel_sigs = st.multiselect(t['filter_signal'], options=sig_opts, default=sig_opts)
with f3:
    iso_opts = df_ranked['tingkat_keterpencilan'].unique().tolist()
    sel_iso = st.multiselect("📍 Filter Keterpencilan:", options=iso_opts, default=iso_opts)
with f4:
    min_pov = st.slider(t['filter_poverty'], 0.0, 100.0, 0.0, step=5.0)

# Apply filters
df_filtered = df_ranked.copy()
if search_query.strip():
    df_filtered = df_filtered[df_filtered['nama_desa'].str.contains(search_query.strip(), case=False, na=False)]
if sel_sigs:
    df_filtered = df_filtered[df_filtered['status_sinyal_eksisting'].isin(sel_sigs)]
if sel_iso:
    df_filtered = df_filtered[df_filtered['tingkat_keterpencilan'].isin(sel_iso)]
df_filtered = df_filtered[df_filtered['persentase_kemiskinan'] >= min_pov]

st.caption(t['showing_caption'].format(filtered=len(df_filtered), total=len(df_ranked)))

# Main Visualizations
st.markdown("---")
render_dashboard_visuals(t, df_filtered)

# Geospatial Boundary Map (Feature 1)
render_geospatial_map(t, df_filtered)

# Automated PDF & CSV Export (Feature 4)
weights_dict = {
    'w_penduduk': w_p_val,
    'w_kemiskinan': w_k_val,
    'w_jarak': w_j_val,
    'w_sinyal': w_si_val,
    'w_sekolah': w_se_val
}
render_export_section(t, df_filtered, weights_dict, lang_code)

# Decision Sensitivity Analysis (Stress-Testing Weights)
render_sensitivity_analysis(df_filtered, w_p, w_k, w_j, w_si, w_se)