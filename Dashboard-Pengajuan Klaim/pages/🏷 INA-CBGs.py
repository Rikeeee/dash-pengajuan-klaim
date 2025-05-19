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

model = joblib.load('rf_pipeline_bpjs.pkl')

st.set_page_config(page_title="INA-CBGs", page_icon="👩‍⚕️", layout="wide")

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

df = pd.read_excel('pengajuan_bpjs_10000.xlsx')  

if 'ADMISSION_DATE' in df.columns:
    df['ADMISSION_DATE'] = pd.to_datetime(df['ADMISSION_DATE'], format='%d/%m/%Y')
    df['BULAN'] = df['ADMISSION_DATE'].dt.month
    df['TAHUN'] = df['ADMISSION_DATE'].dt.year

bulan_mapping = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}
df['BULAN_NAMA'] = df['BULAN'].map(bulan_mapping)

if 'PROCLIST' in df.columns:
    df['PROCLIST'] = df['PROCLIST'].astype(str)

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

def BPJS(df_filtered):
    st.markdown(
    """
    <div style="background-color:rgba(106, 156, 137, 0.5);; padding:12px; border-radius:10px; text-align:center; margin-bottom: 20px;">
        <h2 style="color:black; font-size:28px; margin:0;">
            DASHBOARD EFISIENSI DAN TREN PENGAJUAN KLAIM INA-CBGs DI RS BP BATAM
        </h2>
    </div>
    """, unsafe_allow_html=True
)
    with st.expander("VIEW EXCEL DATASET"):
        showData = st.multiselect('Filter: ', df.columns, 
                          default=["SEP", "SEX", "UMUR_TAHUN", "DIAGLIST", "PROCLIST", "LOS", "OBAT", "OBAT_KRONIS", "TARIF_RS", "TOTAL_TARIF"],
                          key="filter_data")
        filtered_df = df_filtered[showData].sample(200) if len(df_filtered) > 200 else df_filtered[showData] 
                
        st.dataframe(filtered_df, use_container_width=True)
        
    total_klaim = df_filtered['SEP'].apply(lambda x: isinstance(x, str)).sum()
    klaim_disetujui = df_filtered[df_filtered['status'] == 1]['SEP'].count()  
    klaim_ditolak = df_filtered[df_filtered['status'] == 0]['SEP'].count()  

    persentase_disetujui = (klaim_disetujui / total_klaim) * 100 if total_klaim else 0
    persentase_ditolak = (klaim_ditolak / total_klaim) * 100 if total_klaim else 0

    total1, total2, total3 = st.columns(3, gap='small')

    with total1:
        st.markdown(
            f"""
            <div style="background-color:#D9F0E6; padding:12px; border-radius:10px; border: 1px solid #888; margin-bottom: 20px;">
                <h4 style="margin:0 0 6px 0; color:black; text-align:center;">🔎 Total Pengajuan Klaim INA-CBGs</h4>
                <p style="margin:0; font-size:20px; font-weight:bold;">Jumlah Klaim: <span style="color:#205781;">{total_klaim:,.0f} Klaim</span></p>
                <p style="margin:0; font-size:20px; font-weight:bold;">Total Tarif RS: <span style="color:#205781;">Rp{df['TARIF_RS'].sum():,.0f}</span></p>
                <p style="margin:0; font-size:20px; font-weight:bold;">Total Tagihan: <span style="color:#205781;">Rp{df['TOTAL_TARIF'].sum():,.0f}</span></p>
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
                <p style="margin:0; font-size:20px; font-weight:bold;">Tarif RS Disetujui: <span style="color:#205781;">Rp{df_filtered[df_filtered['status'] == 1]['TARIF_RS'].sum():,.0f}</span></p>
                <p style="margin:0; font-size:20px; font-weight:bold;">Tagihan Disetujui: <span style="color:#205781;">Rp{df_filtered[df_filtered['status'] == 1]['TOTAL_TARIF'].sum():,.0f}</span></p>
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
                <p style="margin:0; font-size:20px; font-weight:bold;">Tarif RS Ditolak: <span style="color:#205781;">Rp{df_filtered[df_filtered['status'] == 0]['TARIF_RS'].sum():,.0f}</span></p>
                <p style="margin:0; font-size:20px; font-weight:bold;">TTagihan Ditolak: <span style="color:#205781;">Rp{df_filtered[df_filtered['status'] == 0]['TOTAL_TARIF'].sum():,.0f}</span></p>
            </div>
            """,
            unsafe_allow_html=True
        )

def graphs_bpjs(df_filtered):
    if 'TAHUN' in df_filtered.columns and 'BULAN_NAMA' in df_filtered.columns and 'KELAS_RAWAT' in df_filtered.columns:
        bulan_urutan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                        "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

        df_filtered['BULAN_ORDER'] = df_filtered['BULAN_NAMA'].map({bulan: i for i, bulan in enumerate(bulan_urutan)})
        df_agg = df_filtered.groupby(['TAHUN', 'BULAN_NAMA', 'BULAN_ORDER', 'KELAS_RAWAT'], as_index=False)['TOTAL_TARIF'].sum()
        df_agg['TAHUN_BULAN'] = df_agg['TAHUN'].astype(str) + ' ' + df_agg['BULAN_NAMA']
        df_agg = df_agg.sort_values(by=['TAHUN', 'BULAN_ORDER'])

        df_agg['TEXT_LABEL'] = ""
        for kelas in df_agg['KELAS_RAWAT'].unique():
            kelas_df = df_agg[df_agg['KELAS_RAWAT'] == kelas]
            min_idx = kelas_df['TOTAL_TARIF'].idxmin()
            max_idx = kelas_df['TOTAL_TARIF'].idxmax()
            df_agg.loc[min_idx, 'TEXT_LABEL'] = f"Rp {kelas_df.loc[min_idx, 'TOTAL_TARIF']:,.0f}"
            df_agg.loc[max_idx, 'TEXT_LABEL'] = f"Rp {kelas_df.loc[max_idx, 'TOTAL_TARIF']:,.0f}"

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
                Tren Pengajuan Klaim
            </div>
            """,
            unsafe_allow_html=True
        )

        fig = px.line(
            df_agg, 
            x='TAHUN_BULAN',  
            y='TOTAL_TARIF', 
            color='KELAS_RAWAT', 
            markers=True,  
            labels={'TOTAL_TARIF': 'Total Tarif (Rp)', 'TAHUN_BULAN': 'Tahun - Bulan', 'KELAS_RAWAT': 'Kelas Rawat'},
            color_discrete_map={1: "#205781", 2: "#FFB433", 3: "#E50046"},  
            text='TEXT_LABEL'
        )
        
        fig.update_traces(line=dict(width=4), textposition='top center', textfont=dict(color='black', size=14))

        fig.update_xaxes(
            title_text="Tahun - Bulan",
            tickangle=60, 
            tickmode='array',
            tickvals=df_agg['TAHUN_BULAN'],
        )

        fig.update_yaxes(
            title_text="Total Tarif (Rp)",
            tickformat=",",
            tickprefix="Rp ",
            showgrid=True,
            separatethousands=True
        )

        fig.update_layout(
            width=900, height=500,
            font=dict(size=14, color="black"),
            showlegend=True,
            legend_title_text="Kelas Rawat",
            plot_bgcolor="white",
            xaxis_title=dict(text='Tahun - Bulan', font=dict(color='black', size=18)),
            yaxis_title=dict(text='Total Tarif (Rp)', font=dict(color='black', size=18)),
            xaxis=dict(tickfont=dict(color='black', size=16)),
            yaxis=dict(tickfont=dict(color='black', size=16)),
            legend=dict(font=dict(size=14, color='black')),
            legend_title=dict(font=dict(size=14, color='black'))
        )

        st.plotly_chart(fig)
        
def tarif_comparison(df_filtered):
    if all(col in df_filtered.columns for col in ['KELAS_RAWAT', 'TARIF_RS', 'TOTAL_TARIF']):
        try:
            df_filtered['KELAS_RAWAT'] = df_filtered['KELAS_RAWAT'].astype(str)
            df_agg = df_filtered.groupby('KELAS_RAWAT', observed=True).agg(
                TARIF_RS=('TARIF_RS', 'sum'),
                TOTAL_TARIF=('TOTAL_TARIF', 'sum')
            ).reset_index()
            
            df_melt = df_agg.melt(
                id_vars='KELAS_RAWAT',
                value_vars=['TARIF_RS', 'TOTAL_TARIF'],
                var_name='JENIS_TARIF',
                value_name='NOMINAL'
            )

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
                    Perbandingan Tarif RS vs Tagihan BPJS per Kelas Rawat
                </div>
                """,
                unsafe_allow_html=True
            )

            df_melt['TEXT_RUPIAH'] = df_melt['NOMINAL'].apply(lambda x: f"Rp {x:,.0f}")
            fig = px.bar(
                df_melt,
                x='KELAS_RAWAT',
                y='NOMINAL',
                color='JENIS_TARIF',
                barmode='group',
                labels={
                    'KELAS_RAWAT': 'Kelas Rawat',
                    'NOMINAL': 'Nominal (Rp)',
                    'JENIS_TARIF': 'Jenis Tarif'
                },
                color_discrete_map={
                    'TARIF_RS': '#1f77b4',
                    'TOTAL_TARIF': '#ff7f0e'
                }
            )

            fig.update_traces(textposition='outside',textfont=dict(color='black', size=14))
            fig.update_layout(
                xaxis_title=dict(text='Kelas Rawat', font=dict(color='black', size=18)),
                yaxis_title=dict(text='Total Tarif (Rp)', font=dict(color='black', size=18)),
                xaxis=dict(tickfont=dict(color='black',size=16)),
                yaxis=dict(tickfont=dict(color='black', size=16)),
                uniformtext_minsize=8,
                uniformtext_mode='hide',
                plot_bgcolor='white',
                legend=dict(font=dict(size=14, color='black')),
                legend_title=dict(font=dict(size=14, color='black'))
            )
            
            fig.update_yaxes(
                tickformat=",",
                tickprefix="Rp ",  
                showgrid=True,
                ticksuffix="",
            )
            

            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Terjadi kesalahan saat membuat grafik perbandingan tarif: {e}")
            
def selisih_tarif_per_diagnosa(df_filtered):
    import streamlit as st
    import plotly.express as px

    if all(col in df_filtered.columns for col in ['DESKRIPSI_INACBG', 'TARIF_RS', 'TOTAL_TARIF']):
        try:
            df_filtered = df_filtered.copy()
            df_filtered['SELISIH'] = df_filtered['TARIF_RS'] - df_filtered['TOTAL_TARIF']
            df_grouped = df_filtered.groupby('DESKRIPSI_INACBG', observed=True).agg(
                RATA_TARIF_RS=('TARIF_RS', 'mean'),
                RATA_TOTAL_TARIF=('TOTAL_TARIF', 'mean'),
                RATA_SELISIH=('SELISIH', 'mean'),
                FREKUENSI=('DESKRIPSI_INACBG', 'count')
            ).reset_index()

            df_grouped = df_grouped.sort_values(by='RATA_SELISIH', ascending=False)

            # Header
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
                    Rata-rata Selisih Tarif RS vs Tarif BPJS per Diagnosa
                </div>
                """,
                unsafe_allow_html=True
            )

            # Filter diagnosa untung dan rugi
            top_rugi = df_grouped[df_grouped['RATA_SELISIH'] < 0].sort_values(by='RATA_SELISIH').head(10).copy()
            top_untung = df_grouped[df_grouped['RATA_SELISIH'] > 0].sort_values(by='RATA_SELISIH', ascending=False).head(10).copy()

            # Pilihan user
            pilihan = st.radio(
                "Pilih jenis diagnosa yang ingin ditampilkan:",
                ('Diagnosa yang Merugikan RS', 'Diagnosa yang Menguntungkan RS')
            )

            if pilihan == 'Diagnosa yang Merugikan RS':
                if top_rugi.empty:
                    st.write("Tidak ada diagnosa yang merugikan RS.")
                else:
                    top_rugi['TEXT_RUPIAH'] = top_rugi['RATA_SELISIH'].apply(lambda x: f"Rp {x:,.0f}")
                    fig = px.bar(
                        top_rugi,
                        x='RATA_SELISIH',
                        y='DESKRIPSI_INACBG',
                        orientation='h',
                        text='TEXT_RUPIAH',
                        labels={
                            'RATA_SELISIH': 'Rata-rata Selisih Tarif (Rp)',
                            'DESKRIPSI_INACBG': 'Diagnosa Utama'
                        },
                        color='RATA_SELISIH',
                        color_continuous_scale='Reds',
                        title='🟥 Diagnosa yang Paling Merugikan RS'
                    )
            else:
                if top_untung.empty:
                    st.write("Tidak ada diagnosa yang menguntungkan RS.")
                    return
                else:
                    top_untung['TEXT_RUPIAH'] = top_untung['RATA_SELISIH'].apply(lambda x: f"Rp {x:,.0f}")
                    fig = px.bar(
                        top_untung,
                        x='RATA_SELISIH',
                        y='DESKRIPSI_INACBG',
                        orientation='h',
                        text='TEXT_RUPIAH',
                        labels={
                            'RATA_SELISIH': 'Rata-rata Selisih Tarif (Rp)',
                            'DESKRIPSI_INACBG': 'Diagnosa Utama'
                        },
                        color='RATA_SELISIH',
                        color_continuous_scale='Greens',
                        title='🟩 Diagnosa yang Paling Menguntungkan RS'
                    )

            # Layout umum
            fig.update_traces(textposition='outside')
            fig.update_layout(
                yaxis=dict(
                    autorange="reversed",
                    tickfont=dict(color='black', size=16),
                    title=dict(text='Diagnosa Utama', font=dict(color='black', size=18))
                ),
                xaxis=dict(
                    tickfont=dict(color='black', size=16),
                    title=dict(text='Rata-rata Selisih Tarif (Rp)', font=dict(color='black', size=18))
                ),
                width=900,
                height=600,
                font=dict(size=14, color="black"),
                plot_bgcolor="white",
                coloraxis_colorbar=dict(title='Selisih')
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

def predict_status(input_data):
    df = pd.DataFrame([input_data])
    score = model.predict_proba(df)[0][1]
    return score

def prediksi():
    st.markdown('<h2 class="title">PREDIKSI PENGKLAIMAN INA-CBGs</h2>', unsafe_allow_html=True)
    st.sidebar.title('Cara Penggunaan')
    st.sidebar.markdown("""
        - Pilih opsi menggunakan dropdown atau checkbox.
        - Isi informasi pemohon sesuai dengan data yang sebenarnya.
        - Tekan tombol 'Prediksi' untuk melihat hasil prediksi.
    """)
    st.sidebar.markdown("---")
        
    discharge_df = pd.read_excel("E:/KP_BPBATAM/discharge_status.xlsx")  
    discharge_dict = dict(zip(discharge_df['discharge_status'], discharge_df['kode']))
        
    diaglist_df = pd.read_csv("ICD-10 e-klaim.csv")  
    diaglist_dict = dict(zip(diaglist_df['DISPLAY'], diaglist_df['CODE'])) 
        
    proclist_df = pd.read_excel("ICD-9-CM.xlsx")  
    proclist_dict = dict(zip(proclist_df['Deskripsi (Indonesia)'], proclist_df['Kode'])) 
    
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
        st.subheader("Masukkan Data Pengajuan Klaim BPJS")

        umur_tahun = st.number_input("Umur (tahun)", value=0)
        kelas_rawat = st.selectbox("Kelas Rawat", [1, 2, 3])
        ptd = st.selectbox("Pelayanan Tidak Ditanggung", [1, 2])
            
        diaglist_display = st.multiselect("Diaglist", list(diaglist_dict.keys()))
        diaglist_code = ";".join([str(diaglist_dict[d]) for d in diaglist_display])

        proclist_display = st.multiselect("Proclist", list(proclist_dict.keys()))
        proclist_code = ";".join([str(proclist_dict[p]) for p in proclist_display])
            
        versi_inacbg = st.number_input("Versi INACBG", value=0.0, step=0.1)
        tarifrs = st.number_input("Tarif Rumah Sakit", value=0)
        tarif_inacbg = st.number_input("Tarif INACBG", value=0)
            
        discharge_display = st.selectbox("Discharge Status", list(discharge_dict.keys()))
        discharge_code = discharge_dict[discharge_display]
            
        los = st.number_input("Lama Rawat (LOS)", value=0)
            
        submitted = st.form_submit_button("Prediksi")

    if submitted:
        selisih_tarif = tarifrs - tarif_inacbg
        jumlah_diag = len(str(diaglist_code).split(';'))  
        jumlah_proc = len(str(proclist_code).split(';'))  
        tarif_melebihi_inacbg = 1 if selisih_tarif > 0 else 0

        input_data = {
            "UMUR_TAHUN": umur_tahun,
            "KELAS_RAWAT": kelas_rawat,
            "PTD": ptd,
            "DIAGLIST": diaglist_code,
            "PROCLIST": proclist_code,
            "VERSI_INACBG": versi_inacbg,
            "TARIF_RS": tarifrs,
            "TARIF_INACBG": tarif_inacbg,
            "LOS": los,
            "DISCHARGE_STATUS": discharge_code,
            "SELISIH_TARIF": selisih_tarif,
            "JUMLAH_DIAG": jumlah_diag,  
            "JUMLAH_PROC": jumlah_proc,  
            "TARIF_MELEBIHI_INACBG": tarif_melebihi_inacbg
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
    BPJS(df_filtered)  
    graphs_bpjs(df_filtered)  
    tarif_comparison(df_filtered)  
    selisih_tarif_per_diagnosa(df_filtered)
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