import streamlit as st
from config import LANG_TEXTS, TOTAL_LIMIT, DEFAULT_WEIGHTS, SLIDER_CSS
from data_loader import load_and_clean_data
from topsis import run_topsis_engine
from components import (
    render_sliders,
    render_dashboard_visuals,
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
st.write(t['subtitle'])

# Inject CSS styles for sliders
st.markdown(SLIDER_CSS, unsafe_allow_html=True)

# 3. Load & Clean Data
df = load_and_clean_data()

# 4. Render Sliders (Session state weights allocation)
w_penduduk_val, w_kemiskinan_val, w_jarak_val, w_sinyal_val, w_sekolah_val = render_sliders(
    t, TOTAL_LIMIT, DEFAULT_WEIGHTS
)

# Convert to scale for TOPSIS
w_penduduk = w_penduduk_val / 100
w_kemiskinan = w_kemiskinan_val / 100
w_jarak = w_jarak_val / 100
w_sinyal = w_sinyal_val / 100
w_sekolah = w_sekolah_val / 100

# 5. Run TOPSIS Engine
df_ranked = run_topsis_engine(df, w_penduduk, w_kemiskinan, w_jarak, w_sinyal, w_sekolah)

# 6. Filter & Search Controls
st.markdown("---")
st.subheader(t['filter_header'])

filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 2])

with filter_col1:
    search_query = st.text_input(t['search_label'], "", placeholder=t['search_placeholder'])

with filter_col2:
    signal_options = df_ranked['status_sinyal_eksisting'].unique().tolist()
    selected_signals = st.multiselect(t['filter_signal'], options=signal_options, default=signal_options)

with filter_col3:
    min_poverty = st.slider(t['filter_poverty'], 0.0, 100.0, 0.0, step=5.0)

# Apply Filter Logic
df_filtered = df_ranked.copy()

if search_query.strip():
    df_filtered = df_filtered[df_filtered['nama_desa'].str.contains(search_query.strip(), case=False, na=False)]

if selected_signals:
    df_filtered = df_filtered[df_filtered['status_sinyal_eksisting'].isin(selected_signals)]

df_filtered = df_filtered[df_filtered['persentase_kemiskinan'] >= min_poverty]

st.caption(t['showing_caption'].format(filtered=len(df_filtered), total=len(df_ranked)))

# 7. Render Visualization Dashboard
st.markdown("---")
render_dashboard_visuals(t, df_filtered)

# 8. Render Geospatial Map
render_geospatial_map(t, df_filtered)

# 9. Export Section
render_export_section(t, df_filtered)