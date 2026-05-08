import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Laundrease - Kasir Laundry", layout="wide")

# --- DATABASE SEDERHANA (Session State) ---
if 'pelanggan' not in st.session_state:
    st.session_state.pelanggan = []
if 'pesanan' not in st.session_state:
    st.session_state.pesanan = []

# --- SIDEBAR (Navigasi) ---
st.sidebar.title("🧺 Laundrease")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Pilih Menu:", ["Dashboard", "Manajemen Pelanggan", "Buat Pesanan", "Status Pesanan"])

# --- 1. DASHBOARD ---
if menu == "Dashboard":
    st.title("📊 Dashboard Utama")
    
    # Hitung Statistik
    total_p = len(st.session_state.pelanggan)
    aktif = len([p for p in st.session_state.pesanan if p['status'] != 'Selesai'])
    pendapatan = sum([p['total_harga'] for p in st.session_state.pesanan if p['status'] == 'Selesai'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pelanggan", f"{total_p} Orang")
    col2.metric("Pesanan Aktif", f"{aktif} Nota")
    col3.metric("Total Pemasukan", f"Rp {pendapatan:,.0f}")
    
    st.markdown("---")
    st.subheader("Daftar Pesanan Terbaru")
    if st.session_state.pesanan:
        df_view = pd.DataFrame(st.session_state.pesanan)
        st.table(df_view[['id', 'nama_pelanggan', 'layanan', 'total_harga', 'status']].tail(10))
    else:
        st.info("Belum ada data transaksi.")

# --- 2. MANAJEMEN PELANGGAN ---
elif menu == "Manajemen Pelanggan":
    st.title("👥 Manajemen Pelanggan")
    
    tab1, tab2 = st.tabs(["Tambah Pelanggan", "Daftar Pelanggan"])
    
    with tab1:
        with st.form("form_pelanggan", clear_on_submit=True):
            nama_baru = st.text_input("Nama Lengkap")
            telp_baru = st.text_input("Nomor WhatsApp (Contoh: 62812345678)")
            alamat_baru = st.text_area("Alamat Lengkap")
            submit_p = st.form_submit_button("Simpan Data")
            
            if submit_p:
                if nama_baru and telp_baru:
                    st.session_state.pelanggan.append({
                        "nama": nama_baru,
                        "telp": telp_baru,
                        "alamat": alamat_baru
                    })
                    st.success("Pelanggan berhasil didaftarkan!")
                else:
                    st.error("Nama dan Nomor WhatsApp wajib diisi!")
    
    with tab2:
        if st.session_state.pelanggan:
            st.dataframe(pd.DataFrame(st.session_state.pelanggan), use_container_width=True)
        else:
            st.write("Belum ada data pelanggan.")

# --- 3. BUAT PESANAN ---
elif menu == "Buat Pesanan":
    st.title("📝 Buat Pesanan Baru")
    
    if not st.session_state.pelanggan:
        st.warning("Silahkan tambah pelanggan terlebih dahulu.")
    else:
        with st.form("form_order"):
            # Pilih Pelanggan
            list_pelanggan = [p['nama'] for p in st.session_state.pelanggan]
            nama_pilih = st.selectbox("Pilih Pelanggan", list_pelanggan)
            
            # Preset Layanan
            layanan_data = {
                "Cuci Reguler (3 Hari)": 7000,
                "Cuci Kilat (1 Hari)": 12000,
                "Cuci Bedcover (4 Hari)": 35000
            }
            layanan_pilih = st.selectbox("Pilih Layanan", list(layanan_data.keys()))
            
            berat = st.number_input("Berat (kg) / Jumlah Item", min_value=0.1, step=0.1)
            
            submit_order = st.form_submit_button("Proses & Cetak Struk")
            
            if submit_order:
                # Ambil data WA
                wa_pelanggan = next(p['telp'] for p in st.session_state.pelanggan if p['nama'] == nama_pilih)
                
                # Logika Estimasi
                hari = 3
                if "Kilat" in layanan_pilih: hari = 1
                elif "Bedcover" in layanan_pilih: hari = 4
                
                tgl_selesai = (datetime.now() + timedelta(days=hari)).strftime("%d-%b-%Y")
                total_bayar = berat * layanan_data[layanan_pilih]
                
                # Simpan ke Database
                order_id = len(st.session_state.pesanan) + 1
                data_final = {
                    "id": order_id,
                    "nama_pelanggan": nama_pilih,
                    "telp": wa_pelanggan,
                    "layanan": layanan_pilih,
                    "total_harga": total_bayar,
                    "status": "Menunggu",
                    "estimasi": tgl_selesai
                }
                st.session_state.pesanan.append(data_final)
                
                st.balloons()
                st.success(f"Pesanan #{order_id} Berhasil Dibuat!")
                
                # Tombol WhatsApp
                teks_wa = f"Halo {nama_pilih},\n\nTerima kasih telah mencuci di Laundrease.\nNota: #{order_id}\nLayanan: {layanan_pilih}\nTotal: Rp {total_bayar:,.0f}\nEstimasi Selesai: {tgl_selesai}\n\nKami akan kabari jika sudah siap diambil."
                encoded_wa = urllib.parse.quote(teks_wa)
                url_wa = f"https://wa.me/{wa_pelanggan}?text={encoded_wa}"
                
                st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25d366;color:white;padding:10px;border-radius:5px;text-align:center;">📲 Kirim Struk Ke WhatsApp</div></a>', unsafe_allow_html=True)

# --- 4. STATUS PESANAN ---
elif menu == "Status Pesanan":
    st.title("⏳ Update Status Laundry")
    
    if not st.session_state.pesanan:
        st.info("Belum ada pesanan masuk.")
    else:
        for i, order in enumerate(st.session_state.pesanan):
            with st.expander(f"Nota #{order['id']} - {order['nama_pelanggan']} ({order['status']})"):
                st.write(f"**Layanan:** {order['layanan']}")
                st.write(f"**Total Harga:** Rp {order['total_harga']:,.0f}")
                st.write(f"**Estimasi Selesai:** {order['estimasi']}")
                
                status_baru = st.selectbox(
                    "Ubah Status Ke:", 
                    ["Menunggu", "Dicuci", "Dikeringkan", "Siap Diambil", "Selesai"],
                    index=["Menunggu", "Dicuci", "Dikeringkan", "Siap Diambil", "Selesai"].index(order['status']),
                    key=f"status_sel_{i}"
                )
                
                if st.button("Simpan Perubahan Status", key=f"btn_upd_{i}"):
                    st.session_state.pesanan[i]['status'] = status_baru
                    st.rerun()
