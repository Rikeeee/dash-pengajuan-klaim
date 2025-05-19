import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
import altair as alt
import joblib
import time
from PIL import Image
import base64
from streamlit_extras.metric_cards import style_metric_cards
from pycaret.regression import load_model, predict_model

model = joblib.load('rf_obat.pkl')

st.set_page_config(page_title="Obat", page_icon="💊", layout="wide")

st.markdown("""  
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">  
""", unsafe_allow_html=True)

def add_bg_from_local(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_local('assets/background.png')  

# ========== Tampilan Loading ==========
with st.spinner("Memuat dashboard..."):
    time.sleep(1.5)

df = pd.read_excel('pengajuan_obat_dengan_status.xlsx')  

if 'TGL_RESEP' in df.columns:
    df['TGL_RESEP'] = pd.to_datetime(df['TGL_RESEP'], format='%d/%m/%Y')
    df['BULAN'] = df['TGL_RESEP'].dt.month
    df['TAHUN'] = df['TGL_RESEP'].dt.year

bulan_mapping = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}
df['BULAN_NAMA'] = df['BULAN'].map(bulan_mapping)

def filter_df():
    st.sidebar.header("Filter Data")

    # Tahun
    all_years = sorted(df['TAHUN'].unique(), reverse=True)
    tahun_options = ["All"] + all_years
    selected_years = st.sidebar.multiselect("Pilih Tahun", options=tahun_options, default=["All"])

    if "All" in selected_years or not selected_years:
        selected_years = all_years

    # Bulan
    all_months = list(bulan_mapping.values())
    bulan_options = ["All"] + all_months
    selected_months = st.sidebar.multiselect("Pilih Bulan", options=bulan_options, default=["All"])

    if "All" in selected_months or not selected_months:
        selected_months = all_months

    df_filtered = df.copy()

    df_filtered = df_filtered[df_filtered['TAHUN'].isin(selected_years)]

    bulan_angka = {v: k for k, v in bulan_mapping.items()}
    selected_bulan_angka = [bulan_angka[bulan] for bulan in selected_months]
    df_filtered = df_filtered[df_filtered['BULAN'].isin(selected_bulan_angka)]

    return df_filtered

st.markdown("""
    <style>
    /* Ubah background seluruh sidebar (bukan hanya kontennya) */
    section[data-testid="stSidebar"] {
        background-color: #6A9C89 !important; 
        padding: 15px;
        font-family: 'Poppins', sans-serif;
    }
    
    /* Sidebar header (Filter Data) */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        font-size: 20px;
        text-align:center;
        font-weight: bold;
        color: #2C3333;
        margin-top: 10px;
        margin-bottom: 8px;
        background-color: #9ACBD0;
        border-radius: 8px;
        font-family: 'Poppins', sans-serif;
    }
    
    /* Multiselect container */
    .stMultiSelect > div {
        background-color: #ffffff;
        border-radius: 8px;
        border: 1px solid #A6CDC6;
        padding: 4px;
        transition: border-color 0.3s;
    }

    /* Selected text inside multiselect */
    .css-1d391kg, .css-1n76uvr {
        background-color: #6A9C89 !important;
        color: white !important;
        border-radius: 5px;
        padding: 3px 6px;
    }

    /* Label styling ("Pilih Tahun", "Pilih Bulan") */
    label.css-1544g2n {  
        font-size: 16px;
        font-weight: 600;
        color: #2C3333;
        margin-bottom: 4px;
    }

    /* Hover effect on dropdown items */
    div[data-baseweb="select"] > div:hover {
        border-color: #88B5A2 !important;
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 6px;
    }

    ::-webkit-scrollbar-thumb {
        background-color: #A6CDC6;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

def obat(df_filtered):
    st.markdown(
    """
    <div style="background-color:rgba(106, 156, 137, 0.5);; padding:12px; border-radius:10px; text-align:center; margin-bottom: 20px;">
        <h2 style="color:black; font-size:28px; margin:0;">
            DASHBOARD EFISIENSI DAN TREN PENGAJUAN KLAIM OBAT DI RS BP BATAM
        </h2>
    </div>
    """, unsafe_allow_html=True
)
    with st.expander("VIEW EXCEL DATASET"):
        showData = st.multiselect(
            'Filter: ',
            df_filtered.columns,
            default=["SEP_KUNJUNGAN", "jenisresep", "obat", "jmlobat", "BIAYA_TAGIHAN", "biayasetuju"]
        )        
        st.dataframe(df_filtered[showData],use_container_width=True) 

    total_klaim = df_filtered['status'].count() 
    klaim_disetujui = df_filtered[df_filtered['status'] == 1]['status'].count()  
    klaim_ditolak = df_filtered[df_filtered['status'] == 0]['status'].count()  
    persentase_disetujui = (klaim_disetujui / total_klaim) * 100 if total_klaim else 0
    persentase_ditolak = (klaim_ditolak / total_klaim) * 100 if total_klaim else 0

    biayasetuju_disetujui = df_filtered[df_filtered['status'] == 1]['biayasetuju'].sum()
    tagihan_disetujui = df_filtered[df_filtered['status'] == 1]['BIAYA_TAGIHAN'].sum()
    biayasetuju_ditolak = df_filtered[df_filtered['status'] == 0]['biayasetuju'].sum()
    tagihan_ditolak = df_filtered[df_filtered['status'] == 0]['BIAYA_TAGIHAN'].sum()

    total1, total2, total3 = st.columns(3, gap='small')

    with total1:
        st.markdown(
            f"""
            <div style="background-color:#D9F0E6; padding:12px; border-radius:10px; border: 1px solid #888; margin-bottom: 20px;">
                <h4 style="margin:0 0 6px 0; color:black; text-align:center;">🔎 Total Pengajuan Klaim Obat</h4>
                <p style="margin:0; font-size:20px; font-weight:bold;">Jumlah Klaim: <span style="color:#205781;">{total_klaim:,.0f} Klaim</span></p>
                <p style="margin:0; font-size:20px; font-weight:bold;">Total Tarif RS: <span style="color:#205781;">Rp{df_filtered['biayasetuju'].sum():,.0f}</span></p>
                <p style="margin:0; font-size:20px; font-weight:bold;">Total Tagihan: <span style="color:#205781;">Rp{df_filtered['BIAYA_TAGIHAN'].sum():,.0f}</span></p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with total2:
        st.markdown(
            f"""
            <div style="background-color:#D9F0E6; padding:12px; border-radius:10px; border: 1px solid #888; margin-bottom: 20px;">
                <h4 style="margin:0 0 8px 0; color:black; text-align:center;">✅ Klaim Disetujui</h4>
                <p style="margin:0; font-size:20px; font-weight:bold;">Jumlah Klaim Disetujui: <span style="color:#205781;">{klaim_disetujui:,.0f} Klaim ({persentase_disetujui:.2f}%)</span></p>
                <p style="margin:0; font-size:20px; font-weight:bold;">Tarif RS Disetujui: <span style="color:#205781;">Rp{biayasetuju_disetujui:,.0f}</span></p>
                <p style="margin:0; font-size:20px; font-weight:bold;">Tagihan Disetujui: <span style="color:#205781;">Rp{tagihan_disetujui:,.0f}</span></p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with total3:
        st.markdown(
            f"""
            <div style="background-color:#D9F0E6; padding:12px; border-radius:10px; border: 1px solid #888; margin-bottom: 20px;">
                <h4 style="margin:0 0 8px 0; color:black; text-align:center;">❎ Klaim Ditolak</h4>
                <p style="margin:0; font-size:20px; font-weight:bold;">Jumlah Klaim Ditolak: <span style="color:#205781;">{klaim_ditolak:,.0f} Klaim ({persentase_ditolak:.2f}%)</span></p>
                <p style="margin:0; font-size:20px; font-weight:bold;">Tarif RS Ditolak: <span style="color:#205781;">Rp{biayasetuju_ditolak:,.0f}</span></p>
                <p style="margin:0; font-size:20px; font-weight:bold;">TTagihan Ditolak: <span style="color:#205781;">Rp{tagihan_ditolak:,.0f}</span></p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
def obat_chart(df_filtered, line_width=4):
    df_filtered['TAHUN_BULAN'] = df_filtered['TAHUN'].astype(str) + " " + df_filtered['BULAN_NAMA']
    df_filtered['TAHUN_BULAN_ORDER'] = df_filtered['TAHUN'] * 100 + df_filtered['BULAN']

    df_agg = df_filtered.groupby(["TAHUN_BULAN", "TAHUN_BULAN_ORDER"])['jmlobat'].count().reset_index()
    df_agg = df_agg.sort_values(by=["TAHUN_BULAN_ORDER"], ascending=True)
    category_order = df_agg["TAHUN_BULAN"].tolist()

    # Tambahkan kolom label
    df_agg['LABEL'] = df_agg['jmlobat'].apply(lambda x: f"{x:,}")

    st.markdown(
        """
        <div style="
            background-color: #A6CDC6; 
            color: black; 
            padding: 8px; 
            text-align: center; 
            font-size: 20px; 
            font-weight: bold; 
            border-radius: 10px;
            border: 2px solid black;">
            Tren Resep
        </div>
        """,
        unsafe_allow_html=True
    )

    fig = px.line(df_agg, 
                  x="TAHUN_BULAN", 
                  y="jmlobat", 
                  markers=True,
                  labels={"jmlobat": "Jumlah Obat", "TAHUN_BULAN": "Bulan-Tahun"},
                  template="plotly_white",
                  category_orders={"TAHUN_BULAN": category_order},
                  text='LABEL')  

    fig.update_traces(line=dict(width=line_width), textposition='top center', textfont=dict(color='black', size=14))

    fig.update_xaxes(
        type="category", 
        tickangle=-45,
        title_text="Bulan-Tahun",
        title_font=dict(color='black', size=18),
        tickfont=dict(color='black', size=16)
    )
    
    fig.update_yaxes(
        tickformat=',.0f',
        title_text="Jumlah Obat",
        title_font=dict(color='black', size=18),
        tickfont=dict(color='black', size=16)
    )
    
    fig.update_layout(legend=dict(font=dict(size=12, color='black')))
    st.plotly_chart(fig, use_container_width=True)
    
def format_rupiah(value):
    if value >= 1_000_000_000:
        return f"Rp {value/1_000_000_000:.1f} M"
    elif value >= 1_000_000:
        return f"Rp {value/1_000_000:.0f} jt"
    elif value >= 1_000:
        return f"Rp {value/1_000:.0f} rb"
    else:
        return f"Rp {value}"

def biaya_per_obat_chart(df_filtered, top_n=10):
    agg = (df_filtered
           .groupby('obat', as_index=False)
           .agg({'BIAYA_TAGIHAN': 'sum', 'biayasetuju': 'sum'}))

    agg = agg.sort_values('BIAYA_TAGIHAN', ascending=False)

    if len(agg) > top_n:
        top = agg.head(top_n)
        others = pd.DataFrame({
            'obat': ['Lainnya'],
            'BIAYA_TAGIHAN': [agg['BIAYA_TAGIHAN'][top_n:].sum()],
            'biayasetuju': [agg['biayasetuju'][top_n:].sum()]
        })
        agg = pd.concat([top, others], ignore_index=True)

    agg_melt = agg.melt(id_vars='obat',
                        value_vars=['BIAYA_TAGIHAN', 'biayasetuju'],
                        var_name='Kategori',
                        value_name='Total')

    agg_melt['Label'] = agg_melt['Total'].apply(format_rupiah)

    st.markdown("""
        <div style="
            background-color:#A6CDC6;
            color:black;
            padding:8px;
            text-align:center;
            font-size:20px;
            font-weight:bold;
            border-radius:10px;
            border:2px solid black;">
            Biaya Tagihan vs Biaya Disetujui per Jenis Obat
        </div>""", unsafe_allow_html=True)

    fig = px.bar(agg_melt,
                 x='obat',
                 y='Total',
                 color='Kategori',
                 barmode='group',
                 text='Label',
                 color_discrete_map={
                     'BIAYA_TAGIHAN': '#FF4B4B',
                     'biayasetuju'  : '#00CC96'
                 },
                 labels={'obat': 'Nama Obat',
                         'Total': 'Total Biaya (Rp)',
                         'Kategori': 'Kategori'})

    fig.update_layout(
        plot_bgcolor='white',
        xaxis_title=dict(text='Nama Obat', font=dict(color='black', size=18)),
        yaxis_title=dict(text='Total Biaya (Rp)', font=dict(color='black', size=18)),
        xaxis_tickangle=-45,
        xaxis_tickfont=dict(color='black', size=14),
        yaxis_tickformat=',',
        yaxis_tickfont=dict(color='black', size=14),
        legend=dict(font=dict(size=12, color='black')),
        height=550
    )

    fig.update_traces(textposition='outside', textfont=dict(size=12, color='black'))
    st.plotly_chart(fig, use_container_width=True)

def predict_status(input_data):
    df = pd.DataFrame([input_data])
    score = model.predict_proba(df)[0][1]
    return score
    
def prediksi():
    st.markdown('<h2 class="title">PREDIKSI PENGKLAIMAN OBAT</h2>', unsafe_allow_html=True)
    st.sidebar.title('Cara Penggunaan')
    st.sidebar.markdown("""
        - Pilih opsi menggunakan dropdown atau checkbox.
        - Isi informasi pemohon sesuai dengan data yang sebenarnya.
        - Tekan tombol 'Prediksi' untuk melihat hasil prediksi.
    """)
    st.sidebar.markdown("---")

    try:
        df_obat = pd.read_csv(
            '/KP_BPBATAM/daftar_obat_unik.csv',
            header=None,
            names=['Nama_Obat'],
            on_bad_lines='skip'
        )
        # Drop baris jika isinya adalah string "Nama_Obat"
        df_obat = df_obat[df_obat['Nama_Obat'].str.lower() != 'nama_obat']
        list_obat = df_obat['Nama_Obat']
    except Exception as e:
        st.error(f"Gagal memuat daftar obat: {str(e)}")
        list_obat = ["Obat Tidak Tersedia"]

    st.markdown("""
        <style>
        /* Ubah latar belakang form */
        div[data-testid="stForm"] {
            background-color: #D9F0E6; 
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #cce5ff;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            box-color: #006A71;
        }

        /* Ubah warna tombol submit */
        button[kind="primary"] {
            background-color: #D9F0E6;
            color: white;
            border-radius: 5px;
        }

        /* Ubah warna teks label input */
        label {
            color: #D9F0E6;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.form("form_prediksi"):
        st.subheader("Masukkan Data Pengajuan Klaim Obat")
        jns_resep = st.selectbox("Jenis Resep", ["Obat Kemoterapi", "Obat Kronis Blm Stabil"])
        obat = st.selectbox("Obat", list_obat.tolist())
        tgl_resep = st.date_input("Tanggal Resep")
        jmlobat = st.number_input("Jumlah Obat", value=0)
        biaya_tagihan = st.number_input("Biaya Tagihan", value=0)
        jmlobatsetuju = st.number_input("Jumlah Obat Disetujui", value=0)
        biaya_setuju = st.number_input("Biaya Setuju", value=0)

        submitted = st.form_submit_button("Prediksi")

    if submitted:
        bulan_resep = tgl_resep.month
        hari_resep = tgl_resep.day
        hari_ke = tgl_resep.weekday()  

        selisih_jmlobat = jmlobat - jmlobatsetuju
        selisih_biaya = biaya_tagihan - biaya_setuju
        proporsi_biaya_disetujui = biaya_setuju / (biaya_tagihan if biaya_tagihan != 0 else 1)

        input_data = {
            "jenisresep": jns_resep,
            "obat": obat,
            "jmlobat": jmlobat,
            "BIAYA_TAGIHAN": biaya_tagihan,
            "jmlobatsetuju": jmlobatsetuju,
            "biayasetuju": biaya_setuju,
            "bulan_resep": bulan_resep,
            "hari_resep": hari_resep,
            "hari_ke": hari_ke,
            "selisih_jmlobat": selisih_jmlobat,
            "selisih_biaya": selisih_biaya,
            "proporsi_biaya_disetujui": proporsi_biaya_disetujui
        }

        try:
            score = predict_status(input_data)
            if score is None:
                st.error("Tidak dapat melakukan prediksi")
                return

            prediction = 1 if score >= 0.8 else 0

            st.markdown("<h3>🧠 Hasil Prediksi</h3>", unsafe_allow_html=True)
            if prediction == 1:
                st.success("✅ Klaim ini **berpotensi disetujui** oleh BPJS")
            else:
                st.warning("❌ Klaim ini **berpotensi ditolak** oleh BPJS")

            st.markdown("<h3>🔢 Detail Skor dan Label Prediksi</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:20px'><b>Prediction Score (Probabilitas Disetujui):</b> {score:.4f}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:20px'><b>Prediction Label:</b> {prediction}</p>", unsafe_allow_html=True)
            
            st.markdown("<h3>📋 Data Input</h3>", unsafe_allow_html=True)
            st.json(input_data)

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses prediksi: {str(e)}")

def sideBar():
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu", 
            options=["Dashboard", "Prediksi"],
            icons=["bar-chart", "activity"],
            menu_icon="cast",  
            default_index=0,
            orientation="vertical",
            styles={
                "container": {"background-color": "white", "padding": "10px"},
                "icon": {"color": "black", "font-size": "18px"}, 
                "nav-link": {"font-size": "16px", "color": "black", "text-align": "left", "margin": "5px", "--hover-color": "#D9F0E6"},
                "nav-link-selected": {"background-color": "#6A9C89", "font-weight": "bold", "color": "white"},
            }
        )
    return selected

selected = sideBar()

if selected == "Dashboard":
    df_filtered = filter_df()  
    obat(df_filtered)
    obat_chart(df_filtered)
    biaya_per_obat_chart(df_filtered, top_n=10)
    
elif selected == "Prediksi":
    prediksi()
    
with st.sidebar:       
    st.sidebar.markdown("## 👨‍💻 Pengembang")
    st.sidebar.markdown("""
    Dikembangkan oleh:  
    **Rike Anindhita**  
    📧 rikeanindhita17@gmail.com  
    📞 +6287772376646
    """) 

# ========== Copyright ==========  
st.markdown("""  
    <div style='text-align: center; padding: 20px 0 10px 0; font-size: 14px; color: #555;'>  
        © 2025 | Dashboard Klaim BPJS Kesehatan – All rights reserved.  
    </div>  
""", unsafe_allow_html=True)