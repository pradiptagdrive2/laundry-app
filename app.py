import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Laundrease - Kasir", layout="wide")

# --- DATABASE SEDERHANA (Session State) ---
# Dalam produksi, ini biasanya menggunakan database sungguhan (SQLite/PostgreSQL)
if 'pelanggan' not in st.session_state:
    st.session_state.pelanggan = []
if 'pesanan' not in st.session_state:
    st.session_state.pesanan = []

# --- FUNGSI HELPER ---
def hitung_total(berat, harga_per_kg):
    return berat * harga_per_kg

# --- SIDEBAR (Navigasi) ---
st.sidebar.title("🧺 Laundrease")
menu = st.sidebar.radio("Pilih Menu:", ["Dashboard", "Manajemen Pelanggan", "Buat Pesanan", "Status Pesanan"])

# --- 1. DASHBOARD ---
if menu == "Dashboard":
    st.title("Selamat Datang, Owner! 👋")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pelanggan", len(st.session_state.pelanggan))
    col2.metric("Pesanan Aktif", len([p for p in st.session_state.pesanan if p['status'] != 'Selesai']))
    
    st.subheader("Ringkasan Pesanan Terbaru")
    if st.session_state.pesanan:
        df_pesanan = pd.DataFrame(st.session_state.pesanan)
        st.table(df_pesanan[['nama_pelanggan', 'layanan', 'total_harga', 'status']].tail())
    else:
        st.info("Belum ada transaksi hari ini.")

# --- 2. MANAJEMEN PELANGGAN ---
elif menu == "Manajemen Pelanggan":
    st.title("👥 Manajemen Pelanggan")
    
    with st.form("tambah_pelanggan"):
        nama = st.text_input("Nama Pelanggan")
        telp = st.text_input("Nomor Telepon (WhatsApp)")
        alamat = st.text_area("Alamat")
        submit = st.form_submit_button("Simpan Pelanggan")
        
        if submit and nama and telp:
            st.session_state.pelanggan.append({"nama": nama, "telp": telp, "alamat": alamat})
            st.success(f"Pelanggan {nama} berhasil ditambah!")

# --- 3. BUAT PESANAN ---
elif menu == "Buat Pesanan":
    st.title("📝 Buat Pesanan Baru")
    
    if not st.session_state.pelanggan:
        st.warning("Tambahkan pelanggan terlebih dahulu di menu Manajemen Pelanggan.")
    else:
        # Pilih Pelanggan
        daftar_nama = [p['nama'] for p in st.session_state.pelanggan]
        nama_pilih = st.selectbox("Pilih Pelanggan", daftar_nama)
        
        # Pilih Layanan
        layanan_dict = {
            "Cuci Reguler (3 Hari)": 7000,
            "Cuci Kilat (1 Hari)": 12000,
            "Cuci Bedcover": 35000
        }
        layanan_pilih = st.selectbox("Pilih Layanan", list(layanan_dict.keys()))
        
        berat = st.number_input("Berat (kg)", min_value=0.1, step=0.1)
        total = hitung_total(berat, layanan_dict[layanan_pilih])
        
        st.write(f"### Total Harga: **Rp {total:,.0f}**")
        
        if st.button("Proses Pesanan"):
            no_wa = next(p['telp'] for p in st.session_state.pelanggan if p['nama'] == nama_pilih)
...             estimasi = datetime.now() + timedelta(days=1 if "Kilat" in layanan_pilih else 3)
...             
...             new_order = {
...                 "id": len(st.session_state.pesanan) + 1,
...                 "nama_pelanggan": nama_pilih,
...                 "telp": no_wa,
...                 "layanan": layanan_pilih,
...                 "berat": berat,
...                 "total_harga": total,
...                 "status": "Menunggu",
...                 "estimasi": estimasi.strftime("%d-%m-%Y")
...             }
...             st.session_state.pesanan.append(new_order)
...             st.success("Pesanan berhasil dibuat!")
...             
...             # Link WhatsApp
...             pesan_wa = f"Halo {nama_pilih}, pesanan laundry {layanan_pilih} Anda sudah kami terima. Total: Rp {total:,.0f}. Estimasi selesai: {new_order['estimasi']}."
...             st.markdown(f"[📲 Kirim Struk via WhatsApp](https://wa.me/{no_wa}?text={pesan_wa})")
... 
... # --- 4. STATUS PESANAN ---
... elif menu == "Status Pesanan":
...     st.title("⏳ Status Laundry")
...     if st.session_state.pesanan:
...         for i, p in enumerate(st.session_state.pesanan):
...             with st.expander(f"Nota #{p['id']} - {p['nama_pelanggan']} ({p['status']})"):
...                 st.write(f"Layanan: {p['layanan']}")
...                 st.write(f"Estimasi Selesai: {p['estimasi']}")
...                 new_status = st.selectbox("Ubah Status", ["Menunggu", "Dicuci", "Dikeringkan", "Siap Diambil", "Selesai"], key=f"status_{i}")
...                 if st.button("Update Status", key=f"btn_{i}"):
...                     st.session_state.pesanan[i]['status'] = new_status
...                     st.rerun()
...     else:
