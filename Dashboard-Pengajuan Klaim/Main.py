import streamlit as st
import base64
import time
import os
from pathlib import Path
import plotly.express as px
import pandas as pd

# ========== Konfigurasi Halaman ==========
st.set_page_config(
    page_title="🏥Dashboard Klaim INA-CBGs, Non-CBGs & Obat",
    layout="wide"
)

# ========== Fungsi Load Gambar Base64 ==========
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ========== Load Background Jika Ada ==========
bg_path = "assets/Latar-belakang.png"
bg_image = get_base64(bg_path) if os.path.exists(bg_path) else ""

# ========== Load Font Google Poppins ==========
st.markdown("""  
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">  
""", unsafe_allow_html=True)

# ========== Loading Spinner ==========
with st.spinner("Memuat dashboard..."):
    time.sleep(1.5)
    
# ========== Sidebar ==========
with st.sidebar:
    st.sidebar.markdown("## 🏥 Info Dashboard")
    st.sidebar.markdown("""
    Dashboard ini menyajikan analisis dan prediksi klaim BPJS Kesehatan untuk:
    - **INA-CBGs**
    - **Non-CBGs**
    - **Obat**

    Gunakan tombol navigasi di halaman utama untuk menjelajahi tiap jenis klaim.
    """)

    st.sidebar.markdown("## ❓ Petunjuk")
    st.sidebar.markdown("""
    Pilih jenis klaim di halaman utama  
    🔽 Lihat ringkasan, tren & prediksi  
    📊 Data ditampilkan interaktif  
    """)
    
    #st.sidebar.markdown("## 📂 Sumber Data")
    #st.sidebar.markdown("""
    #Data diambil dari:
    #- SIM RS
    #- e-Klaim BPJS
    #- Unit Pengelola Klaim
    #""")
    
    st.sidebar.markdown("## 👨‍💻 Pengembang")
    st.sidebar.markdown("""
    Dikembangkan oleh:  
    **Rike Anindhita**  
    📧 rikeanindhita17@gmail.com  
    📞 +6287772376646
    """)

# ========== Styling CSS ==========
st.markdown(f"""
    <style>
        section[data-testid="stSidebar"] {{
            background-color: #6A9C89 !important; 
            padding: 15px;
            font-size: 15px;
        }}
        
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3 {{
            font-size: 20px;
            text-align:center;
            font-weight: bold;
            color: #2C3333;
            margin-top: 10px;
            margin-bottom: 8px;
            background-color: #9ACBD0;
            border-radius: 8px;
        }}
        
        .penjelasan-container {{
            font-size: 18px;
            line-height: 1.6;
            padding: 0 20px 30px 20px;
            background-color: #ffffffdd;
            border-radius: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }}

        .penjelasan-container h2 {{
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #2C3333;
        }}

        .penjelasan-container ul {{
            padding-left: 20px;
            margin-top: 0;
        }}

        .penjelasan-container li {{
            margin-bottom: 12px;
        }}

            html {{
            scroll-behavior: smooth;
            -webkit-font-smoothing: antialiased;
        }}

        body, .stApp {{
            font-family: 'Poppins', sans-serif;
            background-color: #A6CDC6;
            animation: fadeIn 1.2s ease-in;
        }}

        @keyframes fadeIn {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}

        #MainMenu, header, footer {{
            display: none !important;
        }}

        .hero {{
            height: 350px;
            background-image: url("data:image/png;base64,{bg_image}");
            background-size: cover;
            background-position: center;
            border-radius: 15px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            transition: filter 0.3s ease;
        }}

        .hero:hover {{
            filter: brightness(1.05);
        }}

        .hero h1 {{
            background: rgba(0, 0, 0, 0.5);
            padding: 2rem 3rem;
            border-radius: 12px;
            font-size: 3.2rem;
            text-shadow: 2px 2px 10px #000;
        }}

        .block-container {{
            padding: 0rem 0rem;
        }}

        .card-container {{
            display: flex;
            flex-wrap: wrap;
            width: 100%;
            gap: 2rem;
            justify-content: center;
        }}

        .card {{
            width: 600px;
            background-color: #ffffffdd;
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            transition: transform 0.3s ease, background-color 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border: 2px solid #A6CDC6;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: 200px;
            box-sizing: border-box;
            opacity: 0;
            transform: translateY(20px);
            animation: slideIn 0.6s ease forwards;
        }}

        .card:hover {{
            transform: translateY(-8px);
            background-color: #d9f2ef;
            color: #333;
            box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        }}

        .card:active {{
            transform: scale(0.97);
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        }}

        .card-icon {{
            font-size: 50px;
            margin-bottom: 10px;
        }}

        .card-title {{
            font-size: 30px;
            font-weight: bold;
            margin-bottom: 8px;
        }}

        .card-desc {{
            font-size: 18px;
        }}

        .card a {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            text-decoration: none;
            color: inherit;
        }}
        
        .klaim-section {{
            display: flex;
            justify-content: space-around;
            gap: 1.5rem;
            padding: 0 40px;
            flex-wrap: wrap;
            margin: 40px 0;
        }}
        
        .klaim-judul {{
            text-align: center;
            font-size: 26px;
            font-weight: 600;
            margin-top: 50px;
            margin-bottom: 20px;
            padding: 0 40px;
            border-radius: 12px;
            background-color: #e4f4f1;
            color: #2C3333;
            box-shadow: 0 4px 8px rgba(0,0,0,0.08);
            font-family: 'Poppins', sans-serif;
        }}


        .klaim-card {{
            flex: 1 1 300px;
            background-color: #ffffffdd;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .klaim-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        }}

        .klaim-icon {{
            font-size: 40px;
            color: #6A9C89;
            margin-bottom: 15px;
        }}

        .klaim-title {{
            font-size: 22px;
            font-weight: 600;
            color: #2C3333;
            margin-left: 15px;
            margin-right: 15px;
            margin-bottom: 12px;
        }}

        .klaim-desc {{
            font-size: 16px;
            line-height: 1.6;
            color: #333;
        }}

        @keyframes slideIn {{
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @media (max-width: 768px) {{
            .card {{
                width: 100%;
            }}
        }}

        @media (max-width: 480px) {{
            .card {{
                padding: 1rem;
                min-height: 180px;
            }}
            .card-title {{
                font-size: 24px;
            }}
            .card-icon {{
                font-size: 40px;
            }}
        }}
    </style>
""", unsafe_allow_html=True)

# ========== Hero Section ==========
st.markdown(f"""
    <div class="hero">
        <h1>Dashboard Klaim INA-CBGs, Non-CBGs & Obat</h1>
    </div>
""", unsafe_allow_html=True)

# ========== Penjelasan ==========
col1, col2 = st.columns([2, 1])  

with col1:
    st.markdown("""
    <div style="font-size:25px; margin-left:90px; margin-top:100px; margin-bottom:20px; font-family: 'Poppins', sans-serif; ">
    <b>BPJS Kesehatan</b> (Badan Penyelenggara Jaminan Sosial Kesehatan) adalah lembaga yang dibentuk oleh pemerintah berdasarkan <b>Undang-Undang Nomor 24 Tahun 2011</b> tentang BPJS, dan mulai beroperasi secara penuh pada <b>1 Januari 2014</b>. Tujuannya adalah untuk menyelenggarakan <b>jaminan kesehatan nasional (JKN)</b> bagi seluruh rakyat Indonesia secara menyeluruh dan merata.<br><br>
    """, unsafe_allow_html=True)

with col2:
    st.image("assets/bpjs.png", width=900)
    
st.markdown("""
    <div class="klaim-judul">
        Jenis Sistem Pengajuan Klaim BPJS Kesehatan
    </div>
""", unsafe_allow_html=True)
    
# ========== Klaim Cards ==========
st.markdown("""
    <div class="klaim-section">
        <div class="klaim-card">
            <div class="klaim-icon">💼</div>
            <div class="klaim-title">INA-CBGs</div>
            <div class="klaim-desc">
                Sistem paket pembayaran berdasarkan diagnosa dan prosedur medis. Setiap pasien dikelompokkan ke dalam satu tarif standar sesuai kelompok kasus yang ditetapkan pemerintah.
            </div>
        </div>
        <div class="klaim-card">
            <div class="klaim-icon">📋</div>
            <div class="klaim-title">Non-CBGs</div>
            <div class="klaim-desc">
                Klaim di luar paket INA-CBGs seperti pelayanan khusus, tindakan non-standar, atau rujukan tertentu yang dihitung secara individual berdasarkan jenis layanan.
            </div>
        </div>
        <div class="klaim-card">
            <div class="klaim-icon">💊</div>
            <div class="klaim-title">Obat</div>
            <div class="klaim-desc">
                Klaim pengadaan obat-obatan yang digunakan untuk pelayanan pasien, baik yang termasuk paket CBG maupun obat tambahan yang diklaim terpisah.
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

ina_cbgs = pd.read_excel('pengajuan_bpjs_10000.xlsx')
non_cbgs = pd.read_excel('pengajuan_noncbgs_dengan_status.xlsx')
obat = pd.read_excel('pengajuan_obat_dengan_status.xlsx')

def prepare_verifikasi_data(df, jenis):
    return pd.DataFrame({
        "Jenis Klaim": [jenis] * 2,
        "Status": ["Disetujui", "Ditolak"],
        "Jumlah": [
            df[df['status'] == 1].shape[0],
            df[df['status'] == 0].shape[0]
        ]
    })

df_ina = prepare_verifikasi_data(ina_cbgs, "INA-CBGs")
df_non = prepare_verifikasi_data(non_cbgs, "Non-CBGs")
df_obat = prepare_verifikasi_data(obat, "Obat")
df_verifikasi = pd.concat([df_ina, df_non, df_obat], ignore_index=True)

st.markdown("""
    <div class="klaim-judul">
        Distribusi Status Verifikasi Klaim
    </div>
""", unsafe_allow_html=True)

pie_col = st.columns(3)
jenis_klaim = ["INA-CBGs", "Non-CBGs", "Obat"]

for i, klaim in enumerate(jenis_klaim):
    df_pie = df_verifikasi[df_verifikasi["Jenis Klaim"] == klaim]
    fig = px.pie(
        df_pie,
        values="Jumlah",
        names="Status",
        title=f"{klaim}",
        color_discrete_map={"Disetujui": "#6A9C89", "Ditolak": "#E55050"}
    )
    fig.update_traces(textinfo='percent+label', pull=[0.05, 0])
    fig.update_layout(margin=dict(t=50, b=20, l=20, r=20), height=350)
    pie_col[i].plotly_chart(fig, use_container_width=True)
    
st.markdown("""
    <style>
    .element-container:has(.js-plotly-plot) {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 15px;
        margin-left: 15px;
        margin-right: 30px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease-in-out;
    }

    .element-container:has(.js-plotly-plot):hover {
        transform: scale(1.02);
    }

    .klaim-judul {
        font-size: 28px;
        font-weight: 600;
        color: #2F4F4F;
        margin-left: 15px;
        margin-right: 15px;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# ========== Copyright ==========
st.markdown("""  
    <div style='text-align: center; padding: 20px 0 10px 0; font-size: 14px; color: #555;'>  
        © 2025 | Dashboard Klaim BPJS Kesehatan – All rights reserved.  
    </div>  
""", unsafe_allow_html=True)



