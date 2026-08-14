# app.py
import streamlit as st
from config import LANG_TEXTS, TOTAL_LIMIT, DEFAULT_WEIGHTS, SLIDER_CSS
from data_loader import load_and_clean_data
from topsis import run_topsis_engine
from components import (
    render_sliders,
    render_dashboard_visuals,
    render_scenario_comparator,
    render_geospatial_map,
    render_export_section
)

# 1. Page Configuration
st.set_page_config(page_title="Village Wi-Fi Priority Index (TOPSIS)", layout="wide")

# 2. Sidebar Language Selection
st.sidebar.header("🌐 Language Selection")
selected_lang = st.sidebar.selectbox("Select Language:", ["English", "Bahasa Indonesia"], index=0)
lang_code = 'en' if selected_lang == "English" else 'id'
t = LANG_TEXTS[lang_code]

st.title(t['title'])
st.caption(t['subtitle'])

# Inject CSS styles for sliders
st.markdown(SLIDER_CSS, unsafe_allow_html=True)

# 3. Load & Clean Data
df = load_and_clean_data()

# 4. Tabs Architecture
tab_main, tab_comparator = st.tabs([t['tab_single'], t['tab_compare']])

with tab_main:
    st.write(t['weight_header'])
    w_p_val, w_k_val, w_j_val, w_si_val, w_se_val = render_sliders(t, TOTAL_LIMIT, DEFAULT_WEIGHTS)

    # Run TOPSIS
    w_p, w_k, w_j, w_si, w_se = w_p_val/100, w_k_val/100, w_j_val/100, w_si_val/100, w_se_val/100
    df_ranked = run_topsis_engine(df, w_p, w_k, w_j, w_si, w_se)

    # Filter & Search Controls
    st.markdown("---")
    st.subheader(t['filter_header'])
    f1, f2, f3 = st.columns([2, 2, 2])
    with f1:
        search_query = st.text_input(t['search_label'], "", placeholder=t['search_placeholder'])
    with f2:
        sig_opts = df_ranked['status_sinyal_eksisting'].unique().tolist()
        sel_sigs = st.multiselect(t['filter_signal'], options=sig_opts, default=sig_opts)
    with f3:
        min_pov = st.slider(t['filter_poverty'], 0.0, 100.0, 0.0, step=5.0)

    df_filtered = df_ranked.copy()
    if search_query.strip():
        df_filtered = df_filtered[df_filtered['nama_desa'].str.contains(search_query.strip(), case=False, na=False)]
    if sel_sigs:
        df_filtered = df_filtered[df_filtered['status_sinyal_eksisting'].isin(sel_sigs)]
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

with tab_comparator:
    # Scenario Comparison Mode (Feature 2)
    render_scenario_comparator(t, df)