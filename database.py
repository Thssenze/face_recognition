# database.py — Semua fungsi query database
# Tidak boleh ada query langsung di app.py (lihat context.md bagian 12)

import mysql.connector
from config import DB_CONFIG
from datetime import date, datetime, timedelta


def get_connection():
    """Buat koneksi baru ke MySQL."""
    return mysql.connector.connect(**DB_CONFIG)


# ══════════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════════

def hitung_admin():
    """Hitung jumlah admin di database. Return 0 jika gagal."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM admin")
        hasil = cursor.fetchone()[0]
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return 0


def tambah_admin(username, password_hash):
    """Simpan admin baru. Return id admin atau None."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO admin (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        conn.commit()
        admin_id = cursor.lastrowid
        cursor.close(); conn.close()
        return admin_id
    except Exception:
        return None


def get_admin_by_username(username):
    """Ambil data admin berdasarkan username. Return dict atau None."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
        hasil = cursor.fetchone()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════
# KELAS
# ══════════════════════════════════════════════════════════════

def get_semua_kelas():
    """Ambil semua kelas. Return list dict atau []."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM kelas ORDER BY nama_kelas")
        hasil = cursor.fetchall()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return []


def get_kelas_by_id(kelas_id):
    """Ambil satu kelas berdasarkan id. Return dict atau None."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM kelas WHERE id = %s", (kelas_id,))
        hasil = cursor.fetchone()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return None


def tambah_kelas(nama_kelas, angkatan, dibuat_oleh=None):
    """Simpan kelas baru. Return id kelas atau None."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO kelas (nama_kelas, angkatan, dibuat_oleh) VALUES (%s, %s, %s)",
            (nama_kelas, angkatan, dibuat_oleh)
        )
        conn.commit()
        kelas_id = cursor.lastrowid
        cursor.close(); conn.close()
        return kelas_id
    except Exception:
        return None


def update_kelas(kelas_id, nama_kelas, angkatan):
    """Update data kelas. Return True/False."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE kelas SET nama_kelas = %s, angkatan = %s WHERE id = %s",
            (nama_kelas, angkatan, kelas_id)
        )
        conn.commit()
        cursor.close(); conn.close()
        return True
    except Exception:
        return False


def hapus_kelas(kelas_id):
    """Hapus kelas (CASCADE ke matakuliah/jadwal). Return True/False."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM kelas WHERE id = %s", (kelas_id,))
        conn.commit()
        cursor.close(); conn.close()
        return True
    except Exception:
        return False


def hitung_mahasiswa_per_kelas(kelas_id):
    """Hitung jumlah mahasiswa di satu kelas."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE kelas_id = %s", (kelas_id,))
        hasil = cursor.fetchone()[0]
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return 0


# ══════════════════════════════════════════════════════════════
# MATAKULIAH
# ══════════════════════════════════════════════════════════════

def get_semua_matakuliah():
    """Ambil semua matakuliah dengan nama kelas. Return list dict."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.*, k.nama_kelas
            FROM matakuliah m
            JOIN kelas k ON m.kelas_id = k.id
            ORDER BY m.nama_mk
        """)
        hasil = cursor.fetchall()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return []


def get_matakuliah_by_kelas(kelas_id):
    """Ambil matakuliah berdasarkan kelas_id."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM matakuliah WHERE kelas_id = %s ORDER BY nama_mk",
            (kelas_id,)
        )
        hasil = cursor.fetchall()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return []


def get_matakuliah_by_id(mk_id):
    """Ambil satu matakuliah."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM matakuliah WHERE id = %s", (mk_id,))
        hasil = cursor.fetchone()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return None


def tambah_matakuliah(nama_mk, kode_mk, kelas_id, sks=2):
    """Simpan matakuliah baru. Return id atau None."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO matakuliah (nama_mk, kode_mk, kelas_id, sks) VALUES (%s,%s,%s,%s)",
            (nama_mk, kode_mk, kelas_id, sks)
        )
        conn.commit()
        mk_id = cursor.lastrowid
        cursor.close(); conn.close()
        return mk_id
    except Exception:
        return None


def update_matakuliah(mk_id, nama_mk, kode_mk, kelas_id, sks):
    """Update matakuliah. Return True/False."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE matakuliah SET nama_mk=%s, kode_mk=%s, kelas_id=%s, sks=%s WHERE id=%s",
            (nama_mk, kode_mk, kelas_id, sks, mk_id)
        )
        conn.commit()
        cursor.close(); conn.close()
        return True
    except Exception:
        return False


def hapus_matakuliah(mk_id):
    """Hapus matakuliah (CASCADE ke jadwal). Return True/False."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM matakuliah WHERE id = %s", (mk_id,))
        conn.commit()
        cursor.close(); conn.close()
        return True
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════
# JADWAL
# ══════════════════════════════════════════════════════════════

def get_semua_jadwal():
    """Ambil semua jadwal lengkap dengan nama MK dan kelas."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT j.*, m.nama_mk, m.kode_mk, k.nama_kelas
            FROM jadwal j
            JOIN matakuliah m ON j.matakuliah_id = m.id
            JOIN kelas k ON m.kelas_id = k.id
            ORDER BY FIELD(j.hari,'Senin','Selasa','Rabu','Kamis','Jumat','Sabtu'),
                     j.jam_mulai
        """)
        hasil = cursor.fetchall()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return []


def get_jadwal_by_id(jadwal_id):
    """Ambil satu jadwal."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT j.*, m.nama_mk, m.kode_mk, m.kelas_id, k.nama_kelas
            FROM jadwal j
            JOIN matakuliah m ON j.matakuliah_id = m.id
            JOIN kelas k ON m.kelas_id = k.id
            WHERE j.id = %s
        """, (jadwal_id,))
        hasil = cursor.fetchone()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return None


def tambah_jadwal(matakuliah_id, hari, jam_mulai, jam_selesai, batas_terlambat=None):
    """Simpan jadwal baru. batas_terlambat otomatis jika None."""
    try:
        if batas_terlambat is None:
            # Hitung otomatis: jam_mulai + 15 menit
            fmt = "%H:%M:%S" if len(str(jam_mulai)) > 5 else "%H:%M"
            mulai_dt = datetime.strptime(str(jam_mulai), fmt)
            batas_dt = mulai_dt + timedelta(minutes=15)
            batas_terlambat = batas_dt.strftime("%H:%M:%S")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO jadwal (matakuliah_id, hari, jam_mulai, jam_selesai, batas_terlambat)
               VALUES (%s, %s, %s, %s, %s)""",
            (matakuliah_id, hari, jam_mulai, jam_selesai, batas_terlambat)
        )
        conn.commit()
        jadwal_id = cursor.lastrowid
        cursor.close(); conn.close()
        return jadwal_id
    except Exception:
        return None


def hapus_jadwal(jadwal_id):
    """Hapus jadwal. Return True/False."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jadwal WHERE id = %s", (jadwal_id,))
        conn.commit()
        cursor.close(); conn.close()
        return True
    except Exception:
        return False


def get_jadwal_aktif(hari, waktu_sekarang):
    """Cari jadwal yang sedang berlangsung (jam_mulai <= now <= jam_selesai + 30 menit)."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT j.*, m.nama_mk, m.kelas_id
            FROM jadwal j
            JOIN matakuliah m ON j.matakuliah_id = m.id
            WHERE j.hari = %s
              AND %s >= j.jam_mulai
              AND %s <= ADDTIME(j.jam_selesai, '00:30:00')
        """, (hari, waktu_sekarang, waktu_sekarang))
        hasil = cursor.fetchall()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return []


# ══════════════════════════════════════════════════════════════
# USERS (MAHASISWA)
# ══════════════════════════════════════════════════════════════

def get_semua_user():
    """Ambil semua mahasiswa dengan nama kelas."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.*, k.nama_kelas
            FROM users u
            JOIN kelas k ON u.kelas_id = k.id
            ORDER BY u.nama
        """)
        hasil = cursor.fetchall()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return []


def get_user_by_id(user_id):
    """Ambil satu mahasiswa."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.*, k.nama_kelas
            FROM users u
            JOIN kelas k ON u.kelas_id = k.id
            WHERE u.id = %s
        """, (user_id,))
        hasil = cursor.fetchone()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return None


def get_user_by_nim(nim):
    """Cari mahasiswa berdasarkan NIM."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE nim = %s", (nim,))
        hasil = cursor.fetchone()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return None


def get_users_by_kelas(kelas_id):
    """Ambil semua mahasiswa di satu kelas."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE kelas_id = %s ORDER BY nama",
            (kelas_id,)
        )
        hasil = cursor.fetchall()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return []


def tambah_user(nama, nim, kelas_id, foto_path=None):
    """Simpan mahasiswa baru. Return id user atau None."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (nama, nim, kelas_id, foto_path) VALUES (%s,%s,%s,%s)",
            (nama, nim, kelas_id, foto_path)
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close(); conn.close()
        return user_id
    except Exception:
        return None


def update_user(user_id, nama, nim, kelas_id, foto_path=None):
    """Update data mahasiswa. Return True/False."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if foto_path:
            cursor.execute(
                "UPDATE users SET nama=%s, nim=%s, kelas_id=%s, foto_path=%s WHERE id=%s",
                (nama, nim, kelas_id, foto_path, user_id)
            )
        else:
            cursor.execute(
                "UPDATE users SET nama=%s, nim=%s, kelas_id=%s WHERE id=%s",
                (nama, nim, kelas_id, user_id)
            )
        conn.commit()
        cursor.close(); conn.close()
        return True
    except Exception:
        return False


def hapus_user(user_id):
    """Hapus mahasiswa (CASCADE ke absensi). Return True/False."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close(); conn.close()
        return True
    except Exception:
        return False


def nim_sudah_ada(nim):
    """Cek apakah NIM sudah terdaftar."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE nim = %s", (nim,))
        hasil = cursor.fetchone()
        cursor.close(); conn.close()
        return hasil is not None
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════
# ABSENSI
# ══════════════════════════════════════════════════════════════

def catat_absensi(user_id, jadwal_id, tanggal, waktu_absen, status,
                  snapshot_path=None, dibuat_manual=False):
    """Simpan record absensi. Return id atau None (duplikat/gagal)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO absensi
               (user_id, jadwal_id, tanggal, waktu_absen, status, snapshot_path, dibuat_manual)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (user_id, jadwal_id, tanggal, waktu_absen, status,
             snapshot_path, dibuat_manual)
        )
        conn.commit()
        absensi_id = cursor.lastrowid
        cursor.close(); conn.close()
        return absensi_id
    except Exception:
        # Kemungkinan UNIQUE constraint violation (sudah absen)
        return None


def cek_sudah_absen(user_id, jadwal_id, tanggal):
    """Cek apakah mahasiswa sudah absen di jadwal ini hari ini."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM absensi WHERE user_id=%s AND jadwal_id=%s AND tanggal=%s",
            (user_id, jadwal_id, tanggal)
        )
        hasil = cursor.fetchone()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return None


def get_absensi_hari_ini():
    """Ambil semua absensi hari ini lengkap dengan data mahasiswa."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.*, u.nama, u.nim, k.nama_kelas,
                   m.nama_mk, j.jam_mulai, j.jam_selesai
            FROM absensi a
            JOIN users u ON a.user_id = u.id
            JOIN kelas k ON u.kelas_id = k.id
            JOIN jadwal j ON a.jadwal_id = j.id
            JOIN matakuliah m ON j.matakuliah_id = m.id
            WHERE a.tanggal = %s
            ORDER BY a.waktu_absen DESC
        """, (date.today(),))
        hasil = cursor.fetchall()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return []


def get_rekap_absensi(kelas_id=None, tanggal_dari=None, tanggal_sampai=None,
                      matakuliah_id=None):
    """Ambil rekap absensi dengan filter opsional."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT a.*, u.nama, u.nim, k.nama_kelas,
                   m.nama_mk, m.kode_mk, j.hari, j.jam_mulai
            FROM absensi a
            JOIN users u ON a.user_id = u.id
            JOIN kelas k ON u.kelas_id = k.id
            JOIN jadwal j ON a.jadwal_id = j.id
            JOIN matakuliah m ON j.matakuliah_id = m.id
            WHERE 1=1
        """
        params = []

        if kelas_id:
            query += " AND u.kelas_id = %s"
            params.append(kelas_id)
        if tanggal_dari:
            query += " AND a.tanggal >= %s"
            params.append(tanggal_dari)
        if tanggal_sampai:
            query += " AND a.tanggal <= %s"
            params.append(tanggal_sampai)
        if matakuliah_id:
            query += " AND j.matakuliah_id = %s"
            params.append(matakuliah_id)

        query += " ORDER BY a.tanggal DESC, a.waktu_absen DESC"

        cursor.execute(query, params)
        hasil = cursor.fetchall()
        cursor.close(); conn.close()
        return hasil
    except Exception:
        return []


def update_status_absensi(absensi_id, status_baru):
    """Update status absensi (untuk absensi manual). Return True/False."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE absensi SET status = %s, dibuat_manual = TRUE WHERE id = %s",
            (status_baru, absensi_id)
        )
        conn.commit()
        cursor.close(); conn.close()
        return True
    except Exception:
        return False


def get_persentase_kehadiran(kelas_id=None, tanggal_dari=None, tanggal_sampai=None):
    """Hitung persentase kehadiran per status. Return dict."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT status, COUNT(*) as jumlah
            FROM absensi a
            JOIN users u ON a.user_id = u.id
            WHERE 1=1
        """
        params = []
        if kelas_id:
            query += " AND u.kelas_id = %s"
            params.append(kelas_id)
        if tanggal_dari:
            query += " AND a.tanggal >= %s"
            params.append(tanggal_dari)
        if tanggal_sampai:
            query += " AND a.tanggal <= %s"
            params.append(tanggal_sampai)
        query += " GROUP BY status"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close(); conn.close()

        total = sum(r['jumlah'] for r in rows) or 1
        hasil = {s: 0 for s in ['hadir', 'terlambat', 'izin', 'alpha']}
        for r in rows:
            hasil[r['status']] = round(r['jumlah'] / total * 100, 1)
        hasil['total'] = total
        return hasil
    except Exception:
        return {'hadir': 0, 'terlambat': 0, 'izin': 0, 'alpha': 0, 'total': 0}


# ══════════════════════════════════════════════════════════════
# SPOOFING LOG
# ══════════════════════════════════════════════════════════════

def get_ringkasan_rekap(kelas_id=None, tanggal_dari=None, tanggal_sampai=None, matakuliah_id=None):
    """Hitung jumlah record per status untuk kartu ringkasan rekap. Return dict."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT status, COUNT(*) as jumlah
            FROM absensi a
            JOIN users u ON a.user_id = u.id
            JOIN jadwal j ON a.jadwal_id = j.id
            WHERE 1=1
        """
        params = []
        if kelas_id:
            query += " AND u.kelas_id = %s"
            params.append(kelas_id)
        if tanggal_dari:
            query += " AND a.tanggal >= %s"
            params.append(tanggal_dari)
        if tanggal_sampai:
            query += " AND a.tanggal <= %s"
            params.append(tanggal_sampai)
        if matakuliah_id:
            query += " AND j.matakuliah_id = %s"
            params.append(matakuliah_id)
        query += " GROUP BY status"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close(); conn.close()
        hasil = {'hadir': 0, 'terlambat': 0, 'izin': 0, 'alpha': 0}
        for r in rows:
            if r['status'] in hasil:
                hasil[r['status']] = r['jumlah']
        return hasil
    except Exception:
        return {'hadir': 0, 'terlambat': 0, 'izin': 0, 'alpha': 0}


def get_ranking_kelas(tanggal_dari=None, tanggal_sampai=None):
    """Hitung persentase kehadiran per kelas untuk laporan ranking. Return list dict."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        # Ambil semua kelas terlebih dahulu
        cursor.execute("SELECT id, nama_kelas, angkatan FROM kelas ORDER BY nama_kelas")
        kelas_list = cursor.fetchall()
        ranking = []
        for k in kelas_list:
            q = """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN a.status = 'hadir' THEN 1 ELSE 0 END) as hadir
                FROM absensi a
                JOIN users u ON a.user_id = u.id
                WHERE u.kelas_id = %s
            """
            params = [k['id']]
            if tanggal_dari:
                q += " AND a.tanggal >= %s"
                params.append(tanggal_dari)
            if tanggal_sampai:
                q += " AND a.tanggal <= %s"
                params.append(tanggal_sampai)
            cursor.execute(q, params)
            stat = cursor.fetchone()
            total = stat['total'] or 0
            hadir = stat['hadir'] or 0
            persen = round(hadir / total * 100, 1) if total > 0 else 0
            ranking.append({
                'id': k['id'],
                'nama_kelas': k['nama_kelas'],
                'angkatan': k['angkatan'],
                'total': total,
                'hadir': hadir,
                'persen': persen
            })
        cursor.close(); conn.close()
        # Urutkan dari persen tertinggi
        ranking.sort(key=lambda x: x['persen'], reverse=True)
        return ranking
    except Exception:
        return []


def get_top_mahasiswa(tanggal_dari=None, tanggal_sampai=None):
    """Cari mahasiswa dengan kehadiran tertinggi. Return dict atau None."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        q = """
            SELECT u.nama, k.nama_kelas,
                   COUNT(*) as total,
                   SUM(CASE WHEN a.status = 'hadir' THEN 1 ELSE 0 END) as hadir
            FROM absensi a
            JOIN users u ON a.user_id = u.id
            JOIN kelas k ON u.kelas_id = k.id
            WHERE 1=1
        """
        params = []
        if tanggal_dari:
            q += " AND a.tanggal >= %s"
            params.append(tanggal_dari)
        if tanggal_sampai:
            q += " AND a.tanggal <= %s"
            params.append(tanggal_sampai)
        q += " GROUP BY u.id, u.nama, k.nama_kelas HAVING total > 0 ORDER BY (hadir/total) DESC LIMIT 1"
        cursor.execute(q, params)
        row = cursor.fetchone()
        cursor.close(); conn.close()
        if row and row['total'] > 0:
            row['persen'] = round(row['hadir'] / row['total'] * 100, 1)
        return row
    except Exception:
        return None


def catat_spoofing(snapshot_path, confidence_score):
    """Simpan log percobaan spoofing. Return id atau None."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO spoofing_log (snapshot_path, confidence_score) VALUES (%s, %s)",
            (snapshot_path, confidence_score)
        )
        conn.commit()
        log_id = cursor.lastrowid
        cursor.close(); conn.close()
        return log_id
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════
# STATISTIK DASHBOARD
# ══════════════════════════════════════════════════════════════

def get_statistik_dashboard():
    """Ambil statistik ringkas untuk dashboard. Return dict."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Total mahasiswa
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_mhs = cursor.fetchone()['total']

        # Absensi hari ini per status
        cursor.execute("""
            SELECT status, COUNT(*) as jumlah
            FROM absensi WHERE tanggal = %s GROUP BY status
        """, (date.today(),))
        status_hari_ini = {r['status']: r['jumlah'] for r in cursor.fetchall()}

        # Total kelas
        cursor.execute("SELECT COUNT(*) as total FROM kelas")
        total_kelas = cursor.fetchone()['total']

        cursor.close(); conn.close()

        return {
            'total_mahasiswa': total_mhs,
            'total_kelas': total_kelas,
            'hadir_hari_ini': status_hari_ini.get('hadir', 0),
            'terlambat_hari_ini': status_hari_ini.get('terlambat', 0),
            'alpha_hari_ini': status_hari_ini.get('alpha', 0),
        }
    except Exception:
        return {
            'total_mahasiswa': 0, 'total_kelas': 0,
            'hadir_hari_ini': 0, 'terlambat_hari_ini': 0, 'alpha_hari_ini': 0,
        }