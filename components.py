import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium

def render_sliders(t, TOTAL_LIMIT, defaults):
    # Initialize session state for weights if not present
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Calculate remaining budget based on session state values
    current_sum = sum(st.session_state[k] for k in defaults.keys())
    remaining_budget = max(0, TOTAL_LIMIT - current_sum)

    # Determine dynamic max_value for each slider
    max_penduduk = max(5, st.session_state['w_penduduk'] + remaining_budget)
    max_kemiskinan = max(5, st.session_state['w_kemiskinan'] + remaining_budget)
    max_jarak = max(5, st.session_state['w_jarak'] + remaining_budget)
    max_sinyal = max(5, st.session_state['w_sinyal'] + remaining_budget)
    max_sekolah = max(5, st.session_state['w_sekolah'] + remaining_budget)

    col_w1, col_w2, col_w3, col_w4, col_w5 = st.columns(5)

    # Render sliders with dynamic max_value and explicitly bound value
    with col_w1:
        w_penduduk_val = st.slider(t['w_penduduk'], min_value=0, max_value=max_penduduk, value=st.session_state['w_penduduk'], step=5)

    with col_w2:
        w_kemiskinan_val = st.slider(t['w_kemiskinan'], min_value=0, max_value=max_kemiskinan, value=st.session_state['w_kemiskinan'], step=5)

    with col_w3:
        w_jarak_val = st.slider(t['w_jarak'], min_value=0, max_value=max_jarak, value=st.session_state['w_jarak'], step=5)

    with col_w4:
        w_sinyal_val = st.slider(t['w_sinyal'], min_value=0, max_value=max_sinyal, value=st.session_state['w_sinyal'], step=5)

    with col_w5:
        w_sekolah_val = st.slider(t['w_sekolah'], min_value=0, max_value=max_sekolah, value=st.session_state['w_sekolah'], step=5)

    # Detect if any slider was moved, cap it to the remaining budget, update session state and rerun
    changed = False
    if w_penduduk_val != st.session_state['w_penduduk']:
        other_sum = w_kemiskinan_val + w_jarak_val + w_sinyal_val + w_sekolah_val
        st.session_state['w_penduduk'] = min(w_penduduk_val, TOTAL_LIMIT - other_sum)
        changed = True
    elif w_kemiskinan_val != st.session_state['w_kemiskinan']:
        other_sum = w_penduduk_val + w_jarak_val + w_sinyal_val + w_sekolah_val
        st.session_state['w_kemiskinan'] = min(w_kemiskinan_val, TOTAL_LIMIT - other_sum)
        changed = True
    elif w_jarak_val != st.session_state['w_jarak']:
        other_sum = w_penduduk_val + w_kemiskinan_val + w_sinyal_val + w_sekolah_val
        st.session_state['w_jarak'] = min(w_jarak_val, TOTAL_LIMIT - other_sum)
        changed = True
    elif w_sinyal_val != st.session_state['w_sinyal']:
        other_sum = w_penduduk_val + w_kemiskinan_val + w_jarak_val + w_sekolah_val
        st.session_state['w_sinyal'] = min(w_sinyal_val, TOTAL_LIMIT - other_sum)
        changed = True
    elif w_sekolah_val != st.session_state['w_sekolah']:
        other_sum = w_penduduk_val + w_kemiskinan_val + w_jarak_val + w_sinyal_val
        st.session_state['w_sekolah'] = min(w_sekolah_val, TOTAL_LIMIT - other_sum)
        changed = True

    if changed:
        st.rerun()

    total_weight = w_penduduk_val + w_kemiskinan_val + w_jarak_val + w_sinyal_val + w_sekolah_val

    # Status indicator & dynamic visual locking style
    if total_weight == TOTAL_LIMIT:
        st.success(t['success_allocated'])
        st.markdown("""
            <style>
            /* Turn slider handles green with a glow effect when capped */
            div[data-testid="stSlider"] [role="slider"] {
                background-color: #28a745 !important;
                box-shadow: 0 0 12px rgba(40, 167, 69, 0.8) !important;
            }
            /* Turn track progress bar green */
            div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
                background-color: #28a745 !important;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.info(t['info_allocated'].format(total=total_weight, unallocated=TOTAL_LIMIT - total_weight))
        st.markdown("""
            <style>
            /* Reset slider handles and tracks to red/standard theme when budget remains */
            div[data-testid="stSlider"] [role="slider"] {
                background-color: #ff4b4b !important;
                box-shadow: none !important;
            }
            div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
                background-color: #ff4b4b !important;
            }
            </style>
        """, unsafe_allow_html=True)

    return w_penduduk_val, w_kemiskinan_val, w_jarak_val, w_sinyal_val, w_sekolah_val


def render_dashboard_visuals(t, df_filtered):
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(t['top10_title'])
        if not df_filtered.empty:
            st.bar_chart(df_filtered.set_index('nama_desa')['topsis_score'].head(10))
        else:
            st.warning(t['no_match_warning'])

    with col2:
        st.subheader(t['summary_title'])
        if not df_filtered.empty:
            st.metric(t['top_village'], df_filtered.iloc[0]['nama_desa'])
            st.metric(t['top_score'], f"{df_filtered.iloc[0]['topsis_score']:.4f}")
        else:
            st.metric(t['top_village'], "N/A")

    st.subheader(t['table_title'])
    st.dataframe(
        df_filtered[['nama_desa', 'topsis_score', 'status_sinyal_eksisting', 'persentase_kemiskinan', 'jumlah_sekolah', 'jumlah_penduduk']].head(15),
        use_container_width=True
    )


def render_geospatial_map(t, df_filtered):
    st.markdown("---")
    st.subheader(t['map_title'])

    if df_filtered.empty:
        st.warning(t['no_match_warning'])
        return

    # Ensure coordinates exist
    df_map = df_filtered.copy()
    if 'latitude' not in df_map.columns:
        np.random.seed(42)
        df_map['latitude'] = -6.98 + np.random.uniform(-0.1, 0.1, len(df_map))
        df_map['longitude'] = 107.63 + np.random.uniform(-0.1, 0.1, len(df_map))

    center_lat = df_map['latitude'].mean()
    center_lon = df_map['longitude'].mean()

    google_roadmap = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}'
    google_satellite = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'

    map_style = st.radio(t['map_style'], ["Google Maps (Roadmap)", "Google Maps (Satellite)", "OpenStreetMap"], horizontal=True)

    if map_style == "Google Maps (Roadmap)":
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles=google_roadmap, attr='Google')
    elif map_style == "Google Maps (Satellite)":
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles=google_satellite, attr='Google')
    else:
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles="OpenStreetMap")

    for idx, row in df_map.iterrows():
        if row['topsis_score'] > 0.65:
            color = "red"
            status_label = t['high_priority']
        elif row['topsis_score'] > 0.50:
            color = "orange"
            status_label = t['medium_priority']
        else:
            color = "green"
            status_label = t['low_priority']
            
        popup_text = f"""
        <div style="font-family: Arial; font-size: 13px;">
            <b>{row['nama_desa']}</b><br>
            <b>{t['popup_status']}:</b> {status_label}<br>
            <b>TOPSIS Score:</b> {row['topsis_score']:.4f}<br>
            <b>{t['popup_signal']}:</b> {row['status_sinyal_eksisting']}<br>
            <b>{t['popup_poverty']}:</b> {row['persentase_kemiskinan']}%<br>
            <b>{t['popup_schools']}:</b> {row['jumlah_sekolah']}
        </div>
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=9,
            popup=folium.Popup(popup_text, max_width=250),
            tooltip=f"{row['nama_desa']} ({row['topsis_score']:.3f})",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85
        ).add_to(m)

    st_folium(m, width=1100, height=550)


def render_export_section(t, df_filtered):
    st.markdown("---")
    st.subheader(t['export_header'])

    csv_data = df_filtered[['nama_desa', 'topsis_score', 'status_sinyal_eksisting', 'persentase_kemiskinan', 'jumlah_sekolah', 'jumlah_penduduk']].to_csv(index=False)

    st.download_button(
        label=t['download_btn'],
        data=csv_data,
        file_name="rekomendasi_prioritas_filtered.csv",
        mime="text/csv"
    )
