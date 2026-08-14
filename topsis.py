import numpy as np
import pandas as pd

def run_topsis_engine(df, w_penduduk, w_kemiskinan, w_jarak, w_sinyal, w_sekolah):
    features = ['jumlah_penduduk', 'persentase_kemiskinan', 'jarak_ke_pusat_kota_km', 'sinyal_score', 'jumlah_sekolah']
    matrix = df[features].values
    
    # Vector normalization
    norm_matrix = matrix / np.sqrt((matrix**2).sum(axis=0))
    weights = np.array([w_penduduk, w_kemiskinan, w_jarak, w_sinyal, w_sekolah])
    weighted_matrix = norm_matrix * weights

    # Ideal solutions
    ideal_best = weighted_matrix.max(axis=0)
    ideal_worst = weighted_matrix.min(axis=0)

    # Distances
    d_best = np.sqrt(((weighted_matrix - ideal_best)**2).sum(axis=1))
    d_worst = np.sqrt(((weighted_matrix - ideal_worst)**2).sum(axis=1))

    # TOPSIS Score
    denom = d_best + d_worst
    df_out = df.copy()
    df_out['topsis_score'] = np.where(denom == 0, 0, d_worst / denom)
    
    return df_out.sort_values(by='topsis_score', ascending=False)
