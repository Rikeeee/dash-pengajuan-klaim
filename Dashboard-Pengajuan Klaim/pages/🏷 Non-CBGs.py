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

model = joblib.load('logreg_model_noncbgs.pkl')
model_columns = joblib.load('model_columns_noncbgs.pkl')

st.set_page_config(page_title="Non-CBGs", page_icon="🩺", layout="wide")

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

df = pd.read_excel('pengajuan_noncbgs_dengan_status.xlsx')  

if 'tglmasuk' in df.columns:
    df['tglmasuk'] = pd.to_datetime(df['tglmasuk'], format='%d/%m/%Y')
    df['BULAN'] = df['tglmasuk'].dt.month
    df['TAHUN'] = df['tglmasuk'].dt.year

bulan_mapping = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}
df['BULAN_NAMA'] = df['BULAN'].map(bulan_mapping)

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

    /* Selected item (tag) in multiselect */
    div[data-baseweb="tag"] {
        background-color: #6A9C89 !important;
        color: white !important;
        border-radius: 5px;
        padding: 3px 6px;
        font-weight: bold;
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
    
    .filter {
        background-color: #f0f0f0;
        color: #333;
        border: none;
        padding: 10px 20px;
        margin: 5px;
        cursor: pointer;
        border-radius: 5px;
    }

        /* Style for selected (active) filter */
    .filter.active {
        background-color: #6A9C89; 
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Pilihan filter bulan dan tahun
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


def non_cbgs(df_filtered):
    st.markdown(
        """
        <div style="background-color:rgba(106, 156, 137, 0.5); padding:12px; border-radius:10px; text-align:center; margin-bottom: 20px;">
            <h2 style="color:black; font-size:28px; margin:0;">
                DASHBOARD EFISIENSI DAN TREN PENGAJUAN KLAIM Non-CBGs DI RS BP BATAM
            </h2>
        </div>
        """, unsafe_allow_html=True
    )

    # Custom CSS untuk multiselect
    st.markdown("""
        <style>
            /* Warna latar belakang dropdown multiselect */
            div[data-baseweb="select"] {
                background-color: #E5F4EF !important;
                border-radius: 8px !important;
            }

            /* Warna pilihan yang aktif (item yang sudah dipilih) */
            div[data-baseweb="tag"] {
                background-color: #6A9C89 !important;
                color: white !important;
                border-radius: 5px !important;
            }

            /* Warna opsi saat hover */
            div[data-baseweb="menu"] > div {
                background-color: #D1EDE3 !important;
                color: #003322;
            }

            /* Label dari multiselect */
            label[data-testid="stLabel"] {
                font-weight: bold;
                color: #6A9C89;
            }
        </style>
    """, unsafe_allow_html=True)

    # Expander untuk tampilan data
    with st.expander("VIEW EXCEL DATASET"):
        showData = st.multiselect(
            'Filter: ',
            df_filtered.columns,
            default=["nosep", "jenis_klaim", "jnspelayanan", "tarifrs", "tagihan"]
        )
        st.dataframe(df_filtered[showData], use_container_width=True)

    total_klaim = df_filtered['nama'].apply(lambda x: isinstance(x, str)).sum() 
    klaim_disetujui = df_filtered[df_filtered['status'] == 1]['nama'].count()  
    klaim_ditolak = df_filtered[df_filtered['status'] == 0]['nama'].count()  
    persentase_disetujui = (klaim_disetujui / total_klaim) * 100 if total_klaim else 0
    persentase_ditolak = (klaim_ditolak / total_klaim) * 100 if total_klaim else 0

    # Hitung total tarif RS dan tagihan
    tarif_rs_disetujui = df_filtered[df_filtered['status'] == 1]['tarifrs'].sum()
    tagihan_disetujui = df_filtered[df_filtered['status'] == 1]['tagihan'].sum()
    tarif_rs_ditolak = df_filtered[df_filtered['status'] == 0]['tarifrs'].sum()
    tagihan_ditolak = df_filtered[df_filtered['status'] == 0]['tagihan'].sum()

    total1, total2, total3 = st.columns(3, gap='small')

    with total1:
        st.markdown(
            f"""
            <div style="background-color:#D9F0E6; padding:12px; border-radius:10px; border: 1px solid #888; margin-bottom: 20px;">
                <h4 style="margin:0 0 6px 0; color:black; text-align:center;">🔎 Total Pengajuan Klaim Non-CBGs</h4>
                <p style="margin:0; font-size:20px; font-weight:bold;">Jumlah Klaim: <span style="color:#205781;">{total_klaim:,.0f} Klaim</span></p>
                <p style="margin:0; font-size:20px; font-weight:bold;">Total Tarif RS: <span style="color:#205781;">Rp{df_filtered['tarifrs'].sum():,.0f}</span></p>
                <p style="margin:0; font-size:20px; font-weight:bold;">Total Tagihan: <span style="color:#205781;">Rp{df_filtered['tagihan'].sum():,.0f}</span></p>
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
                <p style="margin:0; font-size:20px; font-weight:bold;">Tarif RS Disetujui: <span style="color:#205781;">Rp{tarif_rs_disetujui:,.0f}</span></p>
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
                <p style="margin:0; font-size:20px; font-weight:bold;">Tarif RS Ditolak: <span style="color:#205781;">Rp{tarif_rs_ditolak:,.0f}</span></p>
                <p style="margin:0; font-size:20px; font-weight:bold;">TTagihan Ditolak: <span style="color:#205781;">Rp{tagihan_ditolak:,.0f}</span></p>
            </div>
            """,
            unsafe_allow_html=True
        )

def format_rupiah(val):
    return "Rp " + f"{val:,.0f}".replace(",", ".")

def graphs(df_filtered): 
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
            border: 2px solid black;
            margin-bottom: 20px;">
            Tren Pengajuan Klaim
        </div>
        """,
        unsafe_allow_html=True
    )

    df_agg = df_filtered.groupby(['TAHUN', 'BULAN', 'BULAN_NAMA']).agg({
        'tagihan': 'sum',
        'tarifrs': 'sum'
    }).reset_index().sort_values(['TAHUN', 'BULAN'])

    df_plot = pd.DataFrame({
        'Bulan': df_agg['BULAN_NAMA'].tolist() * 2,
        'Nilai': df_agg['tagihan'].tolist() + df_agg['tarifrs'].tolist(),
        'Kategori': ['Total Tagihan']*len(df_agg) + ['Tarif RS']*len(df_agg)
    })

    df_plot['Label_Rp'] = df_plot['Nilai'].apply(format_rupiah)

    fig = px.line(
        df_plot,
        x='Bulan',
        y='Nilai',
        color='Kategori',
        color_discrete_map={'Total Tagihan': 'blue', 'Tarif RS': 'orange'},
        markers=True,
        text='Label_Rp'
    )

    fig.update_traces(line=dict(width=4))

    y_max = df_plot['Nilai'].max()
    max_ticks = 6  
    nice_interval = round(y_max / max_ticks / 100000) * 100000  
    y_ticks = list(range(0, int(y_max + nice_interval), int(nice_interval)))
    y_labels = [format_rupiah(val) for val in y_ticks]

    fig.update_traces(
        textposition="top center",
        textfont=dict(size=14, color='black'),
        texttemplate="%{text}"
    )

    fig.update_layout(
        xaxis_title=dict(text='Bulan', font=dict(color='black', size=18)),
        yaxis_title=dict(text='Total Klaim', font=dict(color='black', size=18)),
        xaxis=dict(tickfont=dict(color='black', size=16)),
        yaxis=dict(
            tickfont=dict(color='black', size=16),
            tickvals=y_ticks,
            ticktext=y_labels
        ),
        margin=dict(t=40, b=40),
        height=500,
        legend=dict(font=dict(size=14, color='black')),
        legend_title=dict(font=dict(size=14, color='black'))
    )

    st.plotly_chart(fig, use_container_width=True)

def barchart(df_filtered):
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
            border: 2px solid black;
            margin-bottom: 20px;">
            Jumlah  Pengajuan Klaim Berdasarkan Jenis Pelayanan
        </div>
        """,
        unsafe_allow_html=True
    )

    if 'jnspelayanan' in df_filtered.columns:
        df_grouped = df_filtered.groupby('jnspelayanan', as_index=False).size()

        fig = px.bar(
            df_grouped,
            x='jnspelayanan',
            y='size',
            color='jnspelayanan',  
            color_discrete_map={'RAWAT INAP': 'blue', 'RAWAT JALAN': 'orange'},
            labels={'size': 'Total Klaim', 'jnspelayanan': 'Jenis Pelayanan'},
            text_auto=True
        )
        
        fig.update_layout(
            xaxis_title=dict(text='Jenis Pelayanan', font=dict(color='black', size=18)),
            yaxis_title=dict(text='Total Klaim', font=dict(color='black', size=18)),
            xaxis=dict(tickfont=dict(color='black', size=16)),
            yaxis=dict(tickfont=dict(color='black', size=16)),
            legend=dict(font=dict(size=14, color='black')),
            legend_title=dict(font=dict(size=14, color='black'))
        )
        
        fig.update_traces(
            textfont=dict(color='black', size=14),
            textangle=0,
            textposition='outside'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Kolom 'jnspelayanan' tidak ditemukan dalam data.")
        
def treemap_diagnosis(df_filtered):
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
            border: 2px solid black;
            margin-bottom: 20px;">
            Treemap Biaya Klaim per Diagnosis (ICD-10)
        </div>
        """,
        unsafe_allow_html=True
    )

    if 'diagnosa' in df_filtered.columns and 'tarifrs' in df_filtered.columns:
        df_grouped = df_filtered.groupby('diagnosa', as_index=False)['tarifrs'].sum()
        df_grouped = df_grouped.sort_values(by='tarifrs', ascending=False)

        df_grouped['Label_Rp'] = df_grouped['tarifrs'].apply(format_rupiah)

        fig = px.treemap(
            df_grouped,
            path=['diagnosa'],
            values='tarifrs',
            color='tarifrs',
            color_continuous_scale='YlOrRd',
            hover_data={'tarifrs': True, 'diagnosa': True}
        )
        
        fig.update_traces(
            texttemplate="<b>%{label}</b><br>Rp %{value:,.0f}",
            textfont=dict(size=18)
        )

        fig.update_layout(
            margin=dict(t=30, l=10, r=10, b=10),
            coloraxis_colorbar=dict(title='Tarif RS', tickformat=',.0f')
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Kolom 'diagnosa' atau 'tarifrs' tidak ditemukan.")
        
def predict_status(input_data):
    df = pd.DataFrame([input_data])
    df_encoded = pd.get_dummies(df)
    df_encoded = df_encoded.reindex(columns=model_columns, fill_value=0)
    score = model.predict_proba(df_encoded)[0][1]
    return score
        
def prediksi():
    st.markdown('<h2 class="title">PREDIKSI PENGKLAIMAN Non-CBGs</h2>', unsafe_allow_html=True)
    st.sidebar.title('Cara Penggunaan')
    st.sidebar.markdown("""
        - Pilih opsi menggunakan dropdown atau checkbox.
        - Isi informasi pemohon sesuai dengan data yang sebenarnya.
        - Tekan tombol 'Prediksi' untuk melihat hasil prediksi.
    """)
    st.sidebar.markdown("---")
    
    diagnosa_df = pd.read_csv("ICD-10 e-klaim.csv")  
    diagnosa_dict = dict(zip(diagnosa_df['DISPLAY'], diagnosa_df['CODE']))  

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

    # --- Input Form ---
    with st.form("form_prediksi"):
        st.subheader("Masukkan Data Pengajuan Klaim Non-CBGS")
        jns_pelayanan = st.selectbox("Jenis Pelayanan", ["Rawat Jalan", "Rawat Inap"], help="Pilih Jenis Pelayanan.")
        jns_klaim = st.selectbox("Jenis Klaim", [
            'KANTONG DARAH', 'PENYANGGA LEHER/COLLAR NECK (ALKES)',
            'JAKET PENYANGGA TULANG/KORSET (ALKES)', 'IMUNOHISTOKIMIA',
            'KRUK (ALKES)', 'JAKET PENYANGGA TULANG/CORSET (ALKES)',
            'PENYANGGA LEHER (ALKES)', 'ALTEPLASE', 'TONGKAT',
            'CERVICAL COLLAR'], help="Pilih Jenis Klaim")

        diagnosa_display = st.multiselect("Diagnosa", list(diagnosa_dict.keys()), help="Pilih Diagnosa")
        diagnosa_code = ";".join([diagnosa_dict[d] for d in diagnosa_display])
        
        jumlah = st.number_input("Jumlah", value=0, help="Masukkan jumlah unit yang akan diklaim.")
        tarifrs = st.number_input("Tarif Rumah Sakit", value=0, help="Masukkan Tarif Rumah Sakit")
        tagihan = st.number_input("Biaya Tagihan", value=0, help="Masukkan Jumlah Biaya Tagihan")
        tanggal = st.date_input("Tanggal", help="Masukkan tanggal Pengajuan Klaim")
        lama_rawat = st.number_input("Lama Rawat (hari)", min_value=0, value=0)
        
        day = tanggal.day
        month = tanggal.month
        year = tanggal.year
        
        submitted = st.form_submit_button("Prediksi")
        
    if submitted:
        input_data = {
            "jnspelayanan": jns_pelayanan,
            "jenis_klaim": jns_klaim,
            "diagnosa": diagnosa_code,
            "jumlah": jumlah,
            "tarifrs": tarifrs,
            "tagihan": tagihan,
            "tanggal": tanggal.strftime("%Y-%m-%d"),
            "lama_rawat": lama_rawat,
            "day": day,
            "month": month,
            "year": year 
        }

        try:
            score = predict_status(input_data)
            
            if score is None:
                st.error("Tidak dapat melakukan prediksi")
                return
            prediction = 1 if score >= 0.8 else 0
            
            st.markdown("<h3>🧠 Hasil Prediksi</h3>", unsafe_allow_html=True)
            if prediction == 1:
                st.success(f"✅ Klaim ini **berpotensi disetujui** oleh BPJS")
            else:
                st.warning(f"❌ Klaim ini **berpotensi ditolak** oleh BPJS")
            
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
    non_cbgs(df_filtered)
    graphs(df_filtered)
    barchart(df_filtered)
    treemap_diagnosis(df_filtered)
    
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