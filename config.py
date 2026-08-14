# config.py

LANG_TEXTS = {
    'en': {
        'page_title': "Village Wi-Fi Priority Index (TOPSIS)",
        'title': "🌐 Village Wi-Fi Priority Index (TOPSIS Engine)",
        'subtitle': "Multi-Criteria Decision Support & Geospatial Intelligence for Public Policy.",
        'tab_single': "🎯 Live Decision Engine",
        'tab_compare': "⚖️ Policy Scenario Comparator",
        'tab_map': "🗺️ Geospatial & Boundary Map",
        'tab_report': "📑 Executive Policy Brief (PDF)",
        'weight_header': "⚙️ TOPSIS Weight Allocation",
        'w_penduduk': "Population Weight (%)",
        'w_kemiskinan': "Poverty Rate Weight (%)",
        'w_jarak': "Distance Weight (%)",
        'w_sinyal': "Signal Need Weight (%)",
        'w_sekolah': "Schools Weight (%)",
        'success_allocated': "✅ **Total Allocated:** `100%` / `100%` (Perfect Fit - Budget Capped 🔒)",
        'info_allocated': "📊 **Total Allocated:** `{total}%` / `100%` (Unallocated: `{unallocated}%`)",
        'filter_header': "🔍 Filter & Search Controls",
        'search_label': "🔎 Search Village Name:",
        'search_placeholder': "Type village name...",
        'filter_signal': "📶 Filter by Existing Signal:",
        'filter_poverty': "📉 Min Poverty Rate (%)",
        'showing_caption': "Showing **{filtered}** out of **{total}** total villages.",
        'no_match_warning': "No villages match the active search/filter criteria.",
        'top10_title': "Top Priority Villages (TOPSIS Ranking)",
        'summary_title': "Criteria Summary",
        'top_village': "Top Ranked Village",
        'top_score': "Top TOPSIS Score",
        'table_title': "Detailed Ranking Table",
        'export_header': "📄 Export Results",
        'download_btn': "📥 Download Filtered Priority List CSV",
        'download_pdf_btn': "📥 Generate & Download Official PDF Policy Brief",
        'map_title': "🗺️ Interactive Geospatial & ArcGIS Polygon View",
        'map_style': "Select Base Map Style:",
        'toggle_boundaries': "Show ArcGIS Village / Kecamatan Boundaries",
        'high_priority': "🔴 High Priority",
        'medium_priority': "🟠 Medium Priority",
        'low_priority': "🟢 Low Priority",
        'popup_status': "Status",
        'popup_signal': "Signal",
        'popup_poverty': "Poverty",
        'popup_schools': "Schools",
        'scenario_a_title': "Scenario A (e.g. Education-Focused)",
        'scenario_b_title': "Scenario B (e.g. Economic/Poverty-Focused)",
        'rank_shift_col': "Rank Shift (A → B)",
        'select_lang': "Select Language / Pilih Bahasa:"
    },
    'id': {
        'page_title': "Indeks Prioritas Wi-Fi Desa (TOPSIS)",
        'title': "🌐 Indeks Prioritas Wi-Fi Desa (TOPSIS Engine)",
        'subtitle': "Sistem Pendukung Keputusan Spasial & Kebijakan Publik Berbasis Multi-Kriteria.",
        'tab_single': "🎯 Mesin Keputusan Langsung",
        'tab_compare': "⚖️ Komparator Skenario Kebijakan",
        'tab_map': "🗺️ Peta Geospasial & Poligon Wilayah",
        'tab_report': "📑 Ringkasan Eksekutif (PDF)",
        'weight_header': "⚙️ Alokasi Bobot TOPSIS",
        'w_penduduk': "Bobot Jumlah Penduduk (%)",
        'w_kemiskinan': "Bobot Tingkat Kemiskinan (%)",
        'w_jarak': "Bobot Jarak ke Kota (%)",
        'w_sinyal': "Bobot Kebutuhan Sinyal (%)",
        'w_sekolah': "Bobot Jumlah Sekolah (%)",
        'success_allocated': "✅ **Total Dialokasikan:** `100%` / `100%` (Sesuai Sempurna - Batas Maksimal 🔒)",
        'info_allocated': "📊 **Total Dialokasikan:** `{total}%` / `100%` (Belum Dialokasikan: `{unallocated}%`)",
        'filter_header': "🔍 Kontrol Filter & Pencarian",
        'search_label': "🔎 Cari Nama Desa:",
        'search_placeholder': "Ketik nama desa...",
        'filter_signal': "📶 Filter Status Sinyal:",
        'filter_poverty': "📉 Min Tingkat Kemiskinan (%)",
        'showing_caption': "Menampilkan **{filtered}** dari total **{total}** desa.",
        'no_match_warning': "Tidak ada desa yang sesuai dengan kriteria filter.",
        'top10_title': "Top Desa Prioritas (Peringkat TOPSIS)",
        'summary_title': "Ringkasan Kriteria",
        'top_village': "Desa Peringkat Teratas",
        'top_score': "Skor TOPSIS Tertinggi",
        'table_title': "Tabel Peringkat Detail",
        'export_header': "📄 Ekspor Hasil",
        'download_btn': "📥 Unduh CSV Daftar Prioritas Terfilter",
        'download_pdf_btn': "📥 Buat & Unduh Dokumen Ringkasan Eksekutif PDF",
        'map_title': "🗺️ Tampilan Geospasial & Poligon ArcGIS Interaktif",
        'map_style': "Pilih Gaya Peta Dasar:",
        'toggle_boundaries': "Tampilkan Batas Poligon Desa/Kecamatan ArcGIS",
        'high_priority': "🔴 Prioritas Tinggi",
        'medium_priority': "🟠 Prioritas Sedang",
        'low_priority': "🟢 Prioritas Rendah",
        'popup_status': "Status",
        'popup_signal': "Sinyal",
        'popup_poverty': "Kemiskinan",
        'popup_schools': "Sekolah",
        'scenario_a_title': "Skenario A (Fokus Pendidikan)",
        'scenario_b_title': "Skenario B (Fokus Pengentasan Kemiskinan)",
        'rank_shift_col': "Pergeseran Peringkat (A → B)",
        'select_lang': "Pilih Bahasa / Select Language:"
    }
}

TOTAL_LIMIT = 100

DEFAULT_WEIGHTS = {
    'w_penduduk': 20,
    'w_kemiskinan': 30,
    'w_jarak': 10,
    'w_sinyal': 25,
    'w_sekolah': 15
}

SLIDER_CSS = """
    <style>
    div[data-testid="stSlider"] label p { font-size: 1.15rem !important; font-weight: 600 !important; }
    div[data-testid="stSlider"] [data-baseweb="slider"] > div { height: 12px !important; }
    div[data-testid="stSlider"] [role="slider"] { width: 26px !important; height: 26px !important; border: 2px solid #ffffff !important; }
    div[data-testid="stSlider"] div { font-size: 1.05rem !important; }
    </style>
"""