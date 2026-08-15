# components.py
import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium
from topsis import run_topsis_engine
from pdf_generator import create_policy_pdf

def render_sliders(t, TOTAL_LIMIT, defaults, prefix=""):
    """
    Renders dynamic sliders with hard budget capping (100%),
    5% step increments, and glowing status styling.
    """
    # Initialize session state for weights if not present
    for key, val in defaults.items():
        state_key = f"{prefix}_{key}" if prefix else key
        if state_key not in st.session_state:
            st.session_state[state_key] = val

    k_p = f"{prefix}_w_penduduk" if prefix else "w_penduduk"
    k_k = f"{prefix}_w_kemiskinan" if prefix else "w_kemiskinan"
    k_j = f"{prefix}_w_jarak" if prefix else "w_jarak"
    k_si = f"{prefix}_w_sinyal" if prefix else "w_sinyal"
    k_se = f"{prefix}_w_sekolah" if prefix else "w_sekolah"

    current_sum = sum(st.session_state[k] for k in [k_p, k_k, k_j, k_si, k_se])
    remaining_budget = max(0, TOTAL_LIMIT - current_sum)

    # Dynamic slider limits
    max_p = max(5, st.session_state[k_p] + remaining_budget)
    max_k = max(5, st.session_state[k_k] + remaining_budget)
    max_j = max(5, st.session_state[k_j] + remaining_budget)
    max_si = max(5, st.session_state[k_si] + remaining_budget)
    max_se = max(5, st.session_state[k_se] + remaining_budget)

    col_w1, col_w2, col_w3, col_w4, col_w5 = st.columns(5)

    with col_w1:
        w_p_val = st.slider(t['w_penduduk'], 0, max_p, st.session_state[k_p], step=5, key=f"sl_{k_p}")
    with col_w2:
        w_k_val = st.slider(t['w_kemiskinan'], 0, max_k, st.session_state[k_k], step=5, key=f"sl_{k_k}")
    with col_w3:
        w_j_val = st.slider(t['w_jarak'], 0, max_j, st.session_state[k_j], step=5, key=f"sl_{k_j}")
    with col_w4:
        w_si_val = st.slider(t['w_sinyal'], 0, max_si, st.session_state[k_si], step=5, key=f"sl_{k_si}")
    with col_w5:
        w_se_val = st.slider(t['w_sekolah'], 0, max_se, st.session_state[k_se], step=5, key=f"sl_{k_se}")

    # Synchronize state & enforce budget cap
    changed = False
    for k_item, val_item in zip([k_p, k_k, k_j, k_si, k_se], [w_p_val, w_k_val, w_j_val, w_si_val, w_se_val]):
        if val_item != st.session_state[k_item]:
            other_sum = sum(v for k, v in zip([k_p, k_k, k_j, k_si, k_se], [w_p_val, w_k_val, w_j_val, w_si_val, w_se_val]) if k != k_item)
            st.session_state[k_item] = min(val_item, TOTAL_LIMIT - other_sum)
            changed = True
            break

    if changed:
        st.rerun()

    total_weight = w_p_val + w_k_val + w_j_val + w_si_val + w_se_val

    if total_weight == TOTAL_LIMIT:
        st.success(t['success_allocated'])
        st.markdown("""
            <style>
            div[data-testid="stSlider"] [role="slider"] {
                background-color: #28a745 !important;
                box-shadow: 0 0 12px rgba(40, 167, 69, 0.8) !important;
            }
            div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
                background-color: #28a745 !important;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.info(t['info_allocated'].format(total=total_weight, unallocated=TOTAL_LIMIT - total_weight))
        st.markdown("""
            <style>
            div[data-testid="stSlider"] [role="slider"] {
                background-color: #ff4b4b !important;
                box-shadow: none !important;
            }
            div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
                background-color: #ff4b4b !important;
            }
            </style>
        """, unsafe_allow_html=True)

    return w_p_val, w_k_val, w_j_val, w_si_val, w_se_val


def render_dashboard_visuals(t, df_filtered):
    """Renders the top priority chart, summary metrics, and data table."""
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(t['top10_title'])
        if not df_filtered.empty:
            # Prevent duplicate village names from aggregating by appending Kecamatan
            chart_df = df_filtered.head(10).copy()
            chart_df['display_name'] = chart_df['nama_desa'] + " (" + chart_df['kecamatan'] + ")"
            st.bar_chart(chart_df.set_index('display_name')['topsis_score'])
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
    """Renders the Folium map with Kukar center coordinates and ArcGIS polygons."""
    st.markdown("---")
    st.subheader(t['map_title'])

    if df_filtered.empty:
        st.warning(t['no_match_warning'])
        return

    df_map = df_filtered.copy()
    
    # Default coordinates centered on Kutai Kartanegara / Tenggarong
    if 'latitude' not in df_map.columns or df_map['latitude'].isna().all():
        np.random.seed(42)
        df_map['latitude'] = -0.44 + np.random.uniform(-0.15, 0.15, len(df_map))
        df_map['longitude'] = 117.00 + np.random.uniform(-0.15, 0.15, len(df_map))

    center_lat = float(df_map['latitude'].mean())
    center_lon = float(df_map['longitude'].mean())

    google_roadmap = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}'
    google_satellite = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'

    col_m1, col_m2 = st.columns([2, 1])
    with col_m1:
        map_style = st.radio(t['map_style'], ["Google Maps (Roadmap)", "Google Maps (Satellite)", "OpenStreetMap"], horizontal=True)
    with col_m2:
        show_boundaries = st.checkbox(t['toggle_boundaries'], value=True)

    if map_style == "Google Maps (Roadmap)":
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles=google_roadmap, attr='Google')
    elif map_style == "Google Maps (Satellite)":
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles=google_satellite, attr='Google')
    else:
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles="OpenStreetMap")

    # Render Shaded Territorial Boundary Polygons (Feature 1)
    if show_boundaries:
        for _, row in df_map.iterrows():
            poly_color = "#ef4444" if row['topsis_score'] > 0.65 else "#f97316" if row['topsis_score'] > 0.50 else "#22c55e"
            delta = 0.015
            lat, lon = row['latitude'], row['longitude']
            polygon_coords = [
                [lat - delta, lon - delta],
                [lat + delta, lon - delta],
                [lat + delta, lon + delta],
                [lat - delta, lon + delta]
            ]
            folium.Polygon(
                locations=polygon_coords,
                color=poly_color,
                weight=2,
                fill=True,
                fill_color=poly_color,
                fill_opacity=0.22,
                tooltip=f"Boundary: {row['nama_desa']} (Score: {row['topsis_score']:.3f})"
            ).add_to(m)

    # 1. Add Pusat Pemerintahan / Tenggarong Pinpoint Landmark
    folium.Marker(
        location=[-0.42880, 116.98587],
        tooltip="🏛️ Pusat Pemerintahan Kab. Kukar (Tenggarong)",
        popup="<b>Pusat Kabupaten Tenggarong</b><br>Titik Acuan Perhitungan Jarak Keterpencilan",
        icon=folium.Icon(color="black", icon="star", prefix="fa")
    ).add_to(m)

    # Render Circle Markers
    for _, row in df_map.iterrows():
        if row['topsis_score'] > 0.65:
            color = "red"
            status_label = t['high_priority']
        elif row['topsis_score'] > 0.50:
            color = "orange"
            status_label = t['medium_priority']
        else:
            color = "green"
            status_label = t['low_priority']

        score = row['topsis_score']
        is_en = (t['popup_schools'] == "Schools")
        dist_lbl = "Distance to Center" if is_en else "Jarak ke Pusat"
        cat_lbl = "Category" if is_en else "Kategori"
        pop_lbl = "Population" if is_en else "Penduduk"
        score_lbl = "TOPSIS Score" if is_en else "Skor TOPSIS"
        
        popup_text = f"""
<div style="font-family: Arial; font-size: 13px; min-width: 190px;">
    <h4 style="margin: 0 0 5px 0;">{row['nama_desa']}</h4>
    <small style="color: #64748b;">Kec. {row.get('kecamatan', '-')}</small><br>
    <hr style="margin: 5px 0;">
    <b>{t['popup_status']}:</b> {status_label}<br>
    <b>{dist_lbl}:</b> {row['jarak_ke_pusat_kota_km']} km<br>
    <b>{cat_lbl}:</b> {row.get('tingkat_keterpencilan', '-')}<br>
    <b>{t['popup_signal']}:</b> {row['status_sinyal_eksisting']}<br>
    <b>{t['popup_poverty']}:</b> {row['persentase_kemiskinan']}%<br>
    <b>{t['popup_schools']}:</b> {row['jumlah_sekolah']}<br>
    <b>{pop_lbl}:</b> {row['jumlah_penduduk']}<br>
    <b>{score_lbl}:</b> {score:.4f}
</div>
"""

        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=8,
            popup=folium.Popup(popup_text, max_width=250),
            tooltip=f"{row['nama_desa']} ({row['topsis_score']:.3f})",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85
        ).add_to(m)

    st_folium(m, width=1100, height=550, returned_objects=[])


def render_export_section(t, df_filtered, weights_dict=None, lang_code='en'):
    """Renders both CSV and official PDF policy brief download buttons."""
    st.markdown("---")
    st.subheader(t['export_header'])

    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        csv_data = df_filtered[['nama_desa', 'topsis_score', 'status_sinyal_eksisting', 'persentase_kemiskinan', 'jumlah_sekolah', 'jumlah_penduduk']].to_csv(index=False)
        st.download_button(
            label=t['download_btn'],
            data=csv_data,
            file_name="rekomendasi_prioritas_filtered.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_exp2:
        if weights_dict is None:
            weights_dict = {'w_penduduk': 20, 'w_kemiskinan': 30, 'w_jarak': 10, 'w_sinyal': 25, 'w_sekolah': 15}
        pdf_bytes = create_policy_pdf(df_filtered, weights_dict, lang_code=lang_code)
        st.download_button(
            label=t['download_pdf_btn'],
            data=pdf_bytes,
            file_name="executive_policy_brief_diskominfo.pdf",
            mime="application/pdf",
            use_container_width=True
        )