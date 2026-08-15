# data_loader.py
import os
import json
import requests
import pandas as pd
import numpy as np

PALAPA_WFS_URL = "https://palapa.kukarkab.go.id/geoserver/palapa/ows"
GEOJSON_FILE_PATH = "pusat_pemerintahan_kukar.geojson"
EXCEL_FILE_PATH = "hasil_clustering_desa_kukar.xlsx"

# 1. Spatial Math Utilities
def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates great-circle distance (in km) between GPS coordinates."""
    R = 6371.0  # Earth radius in kilometers
    lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
    lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = np.sin(dlat / 2.0)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0)**2
    c = 2.0 * np.arcsin(np.sqrt(a))
    return R * c

def assign_isolation_tier(dist_km):
    """Categorizes isolation level based on distance to the regency center."""
    if dist_km >= 60.0:
        return "Sangat Terpencil (>60 km)"
    elif dist_km >= 35.0:
        return "Terpencil (35-60 km)"
    elif dist_km >= 15.0:
        return "Cukup Terjangkau (15-35 km)"
    else:
        return "Dekat Pusat Kota (<15 km)"

# 2. GeoServer WFS Fetcher
def fetch_palapa_kukar_data():
    """Fetches spatial data from Palapa Kukar GeoServer as GeoJSON."""
    params = {
        'service': 'WFS',
        'version': '1.0.0',
        'request': 'GetFeature',
        'typeName': 'palapa:PUSAT_PEMERINTAHAN_PT',
        'outputFormat': 'application/json',
        'srsName': 'EPSG:4326',
        'maxFeatures': '500'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    try:
        response = requests.get(PALAPA_WFS_URL, params=params, headers=headers, timeout=15)
        if response.status_code == 200:
            geojson_data = response.json()
            with open(GEOJSON_FILE_PATH, "w") as f:
                json.dump(geojson_data, f)
            return geojson_data
    except Exception as e:
        print(f"Palapa Server Fetch Notice: {e}")
    return None

# 3. Main Loader & Data Preparation Engine
def load_and_clean_data(file_path=None):
    """
    Unified loader: Reads from uploaded/local Excel, local GeoJSON,
    or falls back to live Palapa GeoServer / synthetic coordinates.
    """
    df = pd.DataFrame()
    
    # Priority 1: Check for Excel file (e.g., Murad's 206 village clustering dataset)
    target_excel = file_path if file_path else (EXCEL_FILE_PATH if os.path.exists(EXCEL_FILE_PATH) else None)
    if target_excel and os.path.exists(target_excel):
        try:
            df = pd.read_excel(target_excel)
        except Exception as e:
            print(f"Excel read error: {e}")

    # Priority 2: Parse GeoJSON (Local File or WFS API) if no Excel dataset loaded
    if df.empty:
        geojson_data = None
        if os.path.exists(GEOJSON_FILE_PATH) and os.path.getsize(GEOJSON_FILE_PATH) > 0:
            try:
                with open(GEOJSON_FILE_PATH, "r") as f:
                    geojson_data = json.load(f)
            except Exception:
                geojson_data = fetch_palapa_kukar_data()
        else:
            geojson_data = fetch_palapa_kukar_data()

        records = []
        if geojson_data and 'features' in geojson_data:
            for feature in geojson_data['features']:
                props = feature.get('properties', {})
                geom = feature.get('geometry', {})
                
                if geom and geom.get('coordinates'):
                    coords = geom['coordinates']
                    if geom['type'] == 'MultiPoint' and len(coords) > 0:
                        lon, lat = coords[0][0], coords[0][1]
                    elif geom['type'] == 'Point':
                        lon, lat = coords[0], coords[1]
                    else:
                        lon, lat = None, None

                    props['longitude'] = lon
                    props['latitude'] = lat
                
                records.append(props)

        df = pd.DataFrame(records)

    # Priority 3: Fallback if all sources fail
    if df.empty or 'latitude' not in [c.lower() for c in df.columns]:
        np.random.seed(42)
        df = pd.DataFrame({
            'namobj': [f'Desa Kukar {i}' for i in range(1, 30)],
            'latitude': np.random.uniform(-0.80, 0.20, 29),
            'longitude': np.random.uniform(116.30, 117.40, 29)
        })

    # Standardize column names (handles 'namobj', 'desa', 'Desa / Kelurahan', etc.)
    col_map = {col.lower().strip(): col for col in df.columns}
    
    if 'desa / kelurahan' in col_map:
        df['nama_desa'] = df[col_map['desa / kelurahan']].astype(str).str.title()
    elif 'desa' in col_map:
        df['nama_desa'] = df[col_map['desa']].astype(str).str.title()
    elif 'namobj' in col_map:
        df['nama_desa'] = df[col_map['namobj']].astype(str).str.title()
    elif 'label' in col_map:
        df['nama_desa'] = df[col_map['label']].astype(str).str.title()
    else:
        df['nama_desa'] = [f"Desa {i+1}" for i in range(len(df))]

    # Standardize Kecamatan if present
    if 'kecamatan' in col_map:
        df['kecamatan'] = df[col_map['kecamatan']].astype(str).str.title()
    else:
        df['kecamatan'] = "Kutai Kartanegara"

    # Clean & validate coordinate datatypes
    lat_col = col_map.get('latitude', 'latitude')
    lon_col = col_map.get('longitude', 'longitude')
    df['latitude'] = pd.to_numeric(df[lat_col], errors='coerce')
    df['longitude'] = pd.to_numeric(df[lon_col], errors='coerce')

    # Calculate actual distance to Tenggarong (Pusat Kabupaten)
    TENGGARONG_LAT = -0.44019
    TENGGARONG_LON = 116.98139
    df['jarak_ke_pusat_kota_km'] = calculate_haversine_distance(
        df['latitude'], df['longitude'], TENGGARONG_LAT, TENGGARONG_LON
    ).round(2)

    # Assign isolation tiers
    df['tingkat_keterpencilan'] = df['jarak_ke_pusat_kota_km'].apply(assign_isolation_tier)

    # Populate evaluation criteria for TOPSIS
    np.random.seed(42)
    n = len(df)
    df['jumlah_penduduk'] = np.random.randint(600, 5500, size=n)
    df['persentase_kemiskinan'] = np.random.uniform(6.0, 32.0, size=n).round(1)
    df['jumlah_sekolah'] = np.random.randint(1, 9, size=n)
    
    df['status_sinyal_eksisting'] = np.random.choice(
        ['No Signal / Blank Spot', 'Weak 2G/3G', 'Moderate 4G'],
        size=n,
        p=[0.45, 0.35, 0.20]
    )

    signal_map = {
        'No Signal / Blank Spot': 3,
        'Weak 2G/3G': 2,
        'Moderate 4G': 1,
        'No Signal': 3,
        '2G/3G': 2,
        '4G Weak': 1
    }
    df['sinyal_score'] = df['status_sinyal_eksisting'].map(signal_map).fillna(1)

    return df