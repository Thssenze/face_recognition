# scratch/test_search.py
# Tes fungsi cari_mahasiswa dan cari_jadwal di database.py

import sys
sys.path.append('c:\\Users\\Hype\\Documents\\A galang data\\semester 6 project\\ProyekAbsensi\\ProyekAbsensi')

import database as db

print("=== MEMULAI TES FUNGSI PENCARIAN ===")

# Ambil semua user/jadwal yang ada untuk tahu data apa yang bisa dicari
semua_mhs = db.get_semua_user()
semua_jdw = db.get_semua_jadwal()

print(f"Total Mahasiswa di DB: {len(semua_mhs)}")
print(f"Total Jadwal di DB: {len(semua_jdw)}")

if semua_mhs:
    sample_mhs = semua_mhs[0]
    query_nama = sample_mhs['nama'][:4]  # Ambil 4 karakter pertama nama
    print(f"\nMencari mahasiswa dengan query: '{query_nama}'...")
    hasil_mhs = db.cari_mahasiswa(query_nama)
    print(f"Ditemukan {len(hasil_mhs)} mahasiswa:")
    for m in hasil_mhs:
        print(f" - [ID: {m['id']}] NIM: {m['nim']} | Nama: {m['nama']} | Kelas: {m['nama_kelas']}")

if semua_jdw:
    sample_jdw = semua_jdw[0]
    query_mk = sample_jdw['nama_mk'][:4]  # Ambil 4 karakter pertama MK
    print(f"\nMencari jadwal dengan query: '{query_mk}'...")
    hasil_jdw = db.cari_jadwal(query_mk)
    print(f"Ditemukan {len(hasil_jdw)} jadwal:")
    for j in hasil_jdw:
        print(f" - [ID: {j['id']}] MK: {j['nama_mk']} ({j['kode_mk']}) | Hari: {j['hari']} | Waktu: {j['jam_mulai']}-{j['jam_selesai']} | Kelas: {j['nama_kelas']}")

print("\n=== TES PENCARIAN SELESAI ===")
