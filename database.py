# database.py — Manajemen Koneksi & Query Database

import mysql.connector
from config import DB_CONFIG
from datetime import date

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ── USER ──────────────────────────────────────────────
def tambah_user(nama, nim):
    """Simpan user baru ke tabel users. Return id user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (nama, nim) VALUES (%s, %s)", (nama, nim))
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return user_id

def get_semua_user():
    """Ambil semua user dari database."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users ORDER BY id")
    hasil = cursor.fetchall()
    cursor.close()
    conn.close()
    return hasil

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    hasil = cursor.fetchone()
    cursor.close()
    conn.close()
    return hasil

def nim_sudah_ada(nim):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE nim = %s", (nim,))
    hasil = cursor.fetchone()
    cursor.close()
    conn.close()
    return hasil is not None

# ── ABSENSI ───────────────────────────────────────────
def catat_absensi(user_id, nama, nim):
    """Simpan rekaman absensi. Return False jika sudah absen hari ini."""
    conn = get_connection()
    cursor = conn.cursor()

    # Cek duplikasi: sudah absen hari ini?
    cursor.execute(
        "SELECT id FROM absensi WHERE user_id = %s AND tanggal = %s",
        (user_id, date.today())
    )
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return False   # sudah absen

    from datetime import datetime
    now = datetime.now()
    cursor.execute(
        "INSERT INTO absensi (user_id, nama, nim, tanggal, waktu) VALUES (%s,%s,%s,%s,%s)",
        (user_id, nama, nim, now.date(), now.strftime("%H:%M:%S"))
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True   # berhasil dicatat

def get_absensi_hari_ini():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM absensi WHERE tanggal = %s ORDER BY waktu DESC",
        (date.today(),)
    )
    hasil = cursor.fetchall()
    cursor.close()
    conn.close()
    return hasil