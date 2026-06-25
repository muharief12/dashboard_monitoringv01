import streamlit as st
import pandas as pd
import plotly.express as px
import json

# ==========================================
# 1. KONFIGURASI HALAMAN & TEMA
# ==========================================
st.set_page_config(
    page_title="Dashboard Monitoring Kekerasan Perempuan",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Dashboard Monitoring Kekerasan pada Perempuan Dewasa Pulau Jawa")
st.markdown("---")

# ==========================================
# 2. DATASET INGESTION & PREPROCESSING
# ==========================================
@st.cache_data
def load_data():
    # Definisikan struktur sesuai dataset Anda
    # Dalam implementasi nyata, gunakan: 
    df = pd.read_excel("dataset01.xlsx", sheet_name="dataset01")
    return df
    # data = {
    #     'No': [1, 2, 3, 4, 5, 6],
    #     'Provinsi': ['Jawa Barat', 'Jawa Barat', 'Jawa Timur', 'Jawa Timur', 'Jawa Tengah', 'Jawa Tengah'],
    #     'Kabupaten/Kota': ['Bandung', 'Bogor', 'Surabaya', 'Malang', 'Semarang', 'Surakarta'],
    #     'Tahun': [2024, 2025, 2024, 2025, 2024, 2025],
    #     'Satuan': ['Kasus', 'Kasus', 'Kasus', 'Kasus', 'Kasus', 'Kasus'],
    #     'Fisik': [120, 140, 95, 110, 80, 85],
    #     'Psikis': [85, 90, 110, 115, 70, 75],
    #     'Seksual': [150, 165, 130, 145, 90, 95],
    #     'Eksploitasi': [10, 12, 5, 7, 12, 10],
    #     'TPPO': [25, 30, 15, 18, 8, 12],
    #     'Penelantaran': [40, 45, 50, 52, 35, 38]
    # }
    # return pd.DataFrame(data)

@st.cache_data
def load_geojson():
    try:
        # Memuat koordinat batas wilayah spasial Indonesia
        with open("indonesia.geojson", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

df = load_data()
geojson_indo = load_geojson()

# List kolom kategori kekerasan untuk formulasi matematis
kategori_kekerasan = ['Fisik', 'Psikis', 'Seksual', 'Eksploitasi', 'TPPO', 'Penelantaran']

# Formulasi: Total Seluruh Kasus = jumlah semua kategori per baris
df['Total Kasus'] = df[kategori_kekerasan].sum(axis=1)

# ==========================================
# 3. GLOBAL FILTER (SIDEBAR NAVIGATION)
# ==========================================
st.sidebar.header("🎛️ Panel Kontrol & Filter")

# Filter Tahun
list_tahun = sorted(df['Tahun'].unique())
selected_tahun = st.sidebar.multiselect("Periode Tahun:", options=list_tahun, default=list_tahun)

# Filter Provinsi
list_provinsi = sorted(df['Provinsi'].unique())
selected_provinsi = st.sidebar.multiselect("Wilayah Provinsi:", options=list_provinsi, default=list_provinsi)

# Aplikasi Filter ke Dataset
df_filtered = df[(df['Tahun'].isin(selected_tahun)) & (df['Provinsi'].isin(selected_provinsi))]

# ==========================================
# 4. IMPLEMENTASI MATRIKS KOMPONEN
# ==========================================

# --- KOMPONEN 1: RINGKASAN EKSEKUTIF (KPI CARDS) ---
# Tujuan: Gambaran singkat total beban kasus nasional/regional
st.subheader("📌Ringkasan Data Jenis Kekerasan Perempuan Dewasa (Kasus)")
# total_seluruh_kasus = df_filtered['Total Kasus'].sum()

# # Layout untuk angka besar (Single Value Cards)
# cols_kpi = st.columns(len(kategori_kekerasan) + 1)
# cols_kpi[0].metric(label="Total", value=f"{total_seluruh_kasus:,}")

# for i, kat in enumerate(kategori_kekerasan):
#     total_kat = df_filtered[kat].sum()
#     cols_kpi[i+1].metric(label=f"{kat}", value=f"{total_kat:,}")

# 1. Kustomisasi CSS untuk memberikan garis pembatas (boundaries) pada KPI Card
st.markdown("""
    <style>
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
        color: #2c3e50;
    }
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 2px solid #e2e8f0;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 2. Formulasi Matematis Dinamis (Adaptif Terhadap Filter Lokasi)
if not df_filtered.empty:
    # A. Total Seluruh Kasus
    total_seluruh_kasus = df_filtered['Total Kasus'].sum()
    
    # B. LOGIKA ADAPTIF UNTUK FILTER LOKASI (Provinsi vs Kabupaten)
    # Memeriksa berapa banyak provinsi yang sedang aktif di filter
    jumlah_provinsi_terfilter = len(df_filtered['Provinsi'].unique())
    
    if jumlah_provinsi_terfilter > 1:
        # Kondisi Banyak Provinsi: Cari Provinsi Tertinggi
        df_prov_top = df_filtered.groupby('Provinsi')['Total Kasus'].sum().reset_index()
        idx_max_prov = df_prov_top['Total Kasus'].idxmax()
        provinsi_tertinggi = df_prov_top.loc[idx_max_prov, 'Provinsi']
        kasus_prov_tertinggi = df_prov_top.loc[idx_max_prov, 'Total Kasus']
        
        label_kpi2 = "👑 Provinsi Kasus Tertinggi"
        val_kpi2 = f"{provinsi_tertinggi} ({kasus_prov_tertinggi:,})"
    else:
        # Kondisi 1 Provinsi: Cari Kabupaten/Kota Tertinggi di Provinsi Tersebut
        df_kab_top = df_filtered.groupby('Kabupaten/Kota')['Total Kasus'].sum().reset_index()
        idx_max_kab = df_kab_top['Total Kasus'].idxmax()
        kabupaten_tertinggi = df_kab_top.loc[idx_max_kab, 'Kabupaten/Kota']
        kasus_kab_tertinggi = df_kab_top.loc[idx_max_kab, 'Total Kasus']
        
        # Mengambil nama provinsi tunggal yang sedang dipilih untuk label
        provinsi_aktif = df_filtered['Provinsi'].iloc[0]
        label_kpi2 = f"🏅 Kab/Kota Tertinggi di {provinsi_aktif}"
        val_kpi2 = f"{kabupaten_tertinggi} ({kasus_kab_tertinggi:,})"

    # C. Mencari Jenis Kekerasan Paling Dominan
    df_kat_top = df_filtered[kategori_kekerasan].sum().reset_index()
    df_kat_top.columns = ['Jenis Kekerasan', 'Total']
    idx_max_kat = df_kat_top['Total'].idxmax()
    kekerasan_dominan = df_kat_top.loc[idx_max_kat, 'Jenis Kekerasan']
    kasus_kat_dominan = df_kat_top.loc[idx_max_kat, 'Total']
    val_kekerasan_dominan = f"{kekerasan_dominan} ({kasus_kat_dominan:,})"
else:
    total_seluruh_kasus = 0
    label_kpi2 = "👑 Provinsi Kasus Tertinggi"
    val_kpi2 = "-"
    val_kekerasan_dominan = "-"

# 3. Representasi Visual Grid Card
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.metric(label="📊 Total Seluruh Kasus", value=f"{total_seluruh_kasus:,}")

with col_kpi2:
    # Label dan Value sekarang bersifat dinamis mengikuti aturan kondisional di atas
    st.metric(label=label_kpi2, value=val_kpi2)

with col_kpi3:
    st.metric(label="⚠️ Jenis Kekerasan Dominan", value=val_kekerasan_dominan)

st.markdown("---")

# Layout dua kolom untuk Tren Waktu dan Perbandingan Kategori
col_left, col_right = st.columns(2)

# with col_left:
#     # --- KOMPONEN 2: ANALISIS TREN WAKTU (LINE CHART) ---
#     # Tujuan: Mengidentifikasi tren naik/turun/stagnan
#     st.subheader("📈 Analisis Tren Waktu Perkembangan Kasus")
#     df_tren = df_filtered.groupby('Tahun')[kategori_kekerasan].sum().reset_index()
    
#     # Transformasi data agar sesuai untuk grafik multi-line
#     df_tren_melted = df_tren.melt(id_vars='Tahun', var_name='Jenis Kekerasan', value_name='Jumlah Kasus')
    
#     fig_line = px.line(df_tren_melted, x='Tahun', y='Jumlah Kasus', color='Jenis Kekerasan', markers=True,
#                        title="Tren Kasus Berdasarkan Jenis Kekerasan Tahunan")
#     fig_line.update_layout(xaxis_type='category')
#     st.plotly_chart(fig_line, use_container_width=True)

with col_left:
    # --- KOMPONEN 2: ANALISIS TREN WAKTU (BAR CHART) ---
    # Tujuan: Mengidentifikasi perbandingan volume kasus antar-tahun secara diskrit
    st.subheader("📊 Perkembangan Kasus Tahunan")
    df_tren = df_filtered.groupby('Tahun')[kategori_kekerasan].sum().reset_index()
    
    # Transformasi data dari format wide ke long agar sesuai untuk pengelompokan Plotly
    df_tren_melted = df_tren.melt(id_vars='Tahun', var_name='Jenis Kekerasan', value_name='Jumlah Kasus')
    
    # Mengubah px.line menjadi px.bar dengan pengelompokan warna berdasarkan Jenis Kekerasan
    fig_bar_tren = px.bar(
        df_tren_melted, 
        x='Tahun', 
        y='Jumlah Kasus', 
        color='Jenis Kekerasan',
        barmode='group',  # Membuat batang berjejer berdampingan per tahun
        title="Perbandingan Kasus Berdasarkan Jenis Kekerasan (2022-2024)",
        color_discrete_sequence=px.colors.qualitative.Set1  # Opsional: Menyelaraskan palet warna pastel
    )
    
    # Memastikan sumbu X bertipe kategori agar tidak muncul angka desimal (seperti 2022.5)
    fig_bar_tren.update_layout(xaxis_type='category')
    
    st.plotly_chart(fig_bar_tren, use_container_width=True)

with col_right:
    # --- KOMPONEN 3: PERBANDINGAN JENIS KEKERASAN (DONUT CHART) ---
    # Tujuan: Mengetahui jenis kekerasan yang mendominasi (Persentase Kasus)
    st.subheader("🍩 Proporsi Jenis Kekerasan")
    df_proporsi = df_filtered[kategori_kekerasan].sum().reset_index()
    df_proporsi.columns = ['Jenis Kekerasan', 'Total']
    
    fig_donut = px.pie(df_proporsi, values='Total', names='Jenis Kekerasan', hole=0.4,
                        title="Persentase Kontribusi Jenis Kekerasan")
    fig_donut.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("---")

# Layout dua kolom untuk Sebaran Spasial dan Analisis Pareto Wilayah
col_map, col_pareto = st.columns(2)

with col_map:
        # --- KOMPONEN 4: SEBARAN GEOGRAFIS / SPASIAL (GEOMAP) ---
        st.subheader("🗺️ Sebaran Geografis Tingkat Kasus")

        # 1. PAKSA data Excel menjadi HURUF BESAR SEMUA agar sinkron dengan GeoJSON Anda
        df_filtered['Provinsi'] = df_filtered['Provinsi'].astype(str).str.strip().str.upper()
        df_map = df_filtered.groupby('Provinsi')['Total Kasus'].sum().reset_index()
        
        if geojson_indo is not None:
            # Menggunakan Mapbox Choropleth untuk peta interaktif lokal
            fig_map = px.choropleth_mapbox(
                df_map,
                geojson=geojson_indo,
                locations='Provinsi',
                featureidkey='properties.Propinsi',  # Sesuaikan kunci ini dengan properties file GeoJSON Anda
                color='Total Kasus',
                #color_continuous_scale="Reds",
                range_color=(0, df_map['Total Kasus'].max() if not df_map.empty else 100),
                color_continuous_scale=["#2ecc71", "#f1c40f", "#e74c3c"],
                mapbox_style="carto-positron",
                # zoom=3.8,
                # center={"lat": -2.5, "lon": 118.0},
                zoom=5.5,                                 # Diperdekat (Zoom-in) dari 3.8 ke 5.5 agar fokus ke Jawa
                center={"lat": -7.2, "lon": 110.0},
                opacity=0.6,
                labels={'Total Kasus': 'Jumlah Kasus'}
            )
            fig_map.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("File 'indonesia.geojson' absen. Fallback menggunakan grafik batang standar:")
            fig_fallback = px.bar(df_map, x='Provinsi', y='Total Kasus', color='Total Kasus', color_continuous_scale="Reds")
            st.plotly_chart(fig_fallback, use_container_width=True)

with col_pareto:
    # --- KOMPONEN 5: PERINGKAT WILAYAH / ANALISIS PARETO (HORIZONTAL BAR CHART) ---
    # Tujuan: Mengidentifikasi Top Kabupaten/Kota untuk efisiensi monitoring
    st.subheader("📊 Peringkat Wilayah")
    df_pareto = df_filtered.groupby('Kabupaten/Kota')['Total Kasus'].sum().sort_values(ascending=True).tail(10).reset_index()
    
    fig_pareto = px.bar(df_pareto, x='Total Kasus', y='Kabupaten/Kota', orientation='h',
                        color='Total Kasus', color_continuous_scale=px.colors.sequential.Jet,
                        title="Top Kabupaten/Kota Berdasarkan Urutan Kasus Tertinggi")
    st.plotly_chart(fig_pareto, use_container_width=True)

# ==========================================
# 5. TABULAR DETAIL (UNTUK AUDIT DATA)
# ==========================================
st.markdown("---")
st.subheader("🔍 Detail Datatabular Terfilter")
st.dataframe(df_filtered, use_container_width=True)

# ==========================================
# 6. Footer
# ==========================================
st.markdown("---")
st.caption("Sumber: Data Kekerasan pada Perempuan Dewasa berdasarkan Jenisnya oleh BPS dari Tahun 2022-2024 ")