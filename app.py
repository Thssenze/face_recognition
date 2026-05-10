# app.py — Entry point Flask, semua route
# Komentar dalam Bahasa Indonesia sesuai konvensi (context.md bagian 12)

from flask import (Flask, request, jsonify, render_template,
                   redirect, url_for, session, flash)
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, date
import os
import database as db
from config import (FLASK_HOST, FLASK_PORT, FLASK_SECRET_KEY,
                    SNAPSHOT_PATH, TOLERANSI_MENIT, DATASET_PATH)

# ── Inisialisasi Flask ────────────────────────────────────────
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
CORS(app)


# ══════════════════════════════════════════════════════════════
# DECORATOR: login_required
# Semua route kecuali /login dan /register wajib pakai ini
# ══════════════════════════════════════════════════════════════
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Silakan login terlebih dahulu.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ══════════════════════════════════════════════════════════════
# AUTH: Login, Register, Logout
# ══════════════════════════════════════════════════════════════

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Halaman login admin."""
    # Jika sudah login, langsung ke dashboard
    if 'admin_id' in session:
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            error = 'Username dan password wajib diisi.'
        else:
            admin = db.get_admin_by_username(username)
            if admin and check_password_hash(admin['password_hash'], password):
                # Login berhasil — simpan ke session
                session['admin_id'] = admin['id']
                session['username'] = admin['username']
                flash('Login berhasil!', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Username atau password salah.'

    # Tampilkan link register hanya jika belum ada admin sama sekali
    show_register = (db.hitung_admin() == 0)

    return render_template('login.html', error=error, show_register=show_register)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Halaman register admin pertama.
    Hanya bisa diakses jika tabel admin masih kosong (0 record).
    Jika sudah ada admin, redirect ke /login.
    """
    # Cek apakah sudah ada admin
    if db.hitung_admin() > 0:
        flash('Admin sudah terdaftar. Silakan login.', 'error')
        return redirect(url_for('login'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # Validasi input
        if not username or not password:
            error = 'Username dan password wajib diisi.'
        elif len(password) < 8:
            error = 'Password minimal 8 karakter.'
        elif password != confirm:
            error = 'Konfirmasi password tidak cocok.'
        else:
            # Hash password dan simpan
            hashed = generate_password_hash(password)
            admin_id = db.tambah_admin(username, hashed)
            if admin_id:
                # Langsung login setelah register
                session['admin_id'] = admin_id
                session['username'] = username
                flash('Akun admin berhasil dibuat!', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Gagal membuat akun. Username mungkin sudah dipakai.'

    return render_template('register_admin.html', error=error)


@app.route('/logout')
def logout():
    """Logout admin — hapus session."""
    session.clear()
    flash('Anda telah logout.', 'success')
    return redirect(url_for('login'))


# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════

@app.route('/')
@login_required
def dashboard():
    """Halaman utama dashboard."""
    statistik = db.get_statistik_dashboard()
    absensi = db.get_absensi_hari_ini()
    return render_template('dashboard.html',
                           active_page='dashboard',
                           statistik=statistik,
                           absensi_hari_ini=absensi)


# ══════════════════════════════════════════════════════════════
# MANAJEMEN KELAS
# ══════════════════════════════════════════════════════════════

@app.route('/kelas')
@login_required
def kelas_index():
    """Daftar semua kelas."""
    daftar = db.get_semua_kelas()
    # Tambahkan jumlah mahasiswa per kelas
    for k in daftar:
        k['jumlah_mhs'] = db.hitung_mahasiswa_per_kelas(k['id'])
    return render_template('kelas/index.html',
                           active_page='kelas', daftar_kelas=daftar)


@app.route('/kelas/tambah', methods=['GET', 'POST'])
@login_required
def kelas_tambah():
    """Tambah kelas baru."""
    error = None
    if request.method == 'POST':
        nama = request.form.get('nama_kelas', '').strip()
        angkatan = request.form.get('angkatan', '').strip()
        if not nama or not angkatan:
            error = 'Nama kelas dan angkatan wajib diisi.'
        else:
            hasil = db.tambah_kelas(nama, angkatan, session.get('admin_id'))
            if hasil:
                flash('Kelas berhasil ditambahkan!', 'success')
                return redirect(url_for('kelas_index'))
            error = 'Gagal menambahkan kelas.'
    return render_template('kelas/form.html',
                           active_page='kelas', kelas=None, error=error)


@app.route('/kelas/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def kelas_edit(id):
    """Edit kelas."""
    kelas = db.get_kelas_by_id(id)
    if not kelas:
        flash('Kelas tidak ditemukan.', 'error')
        return redirect(url_for('kelas_index'))
    error = None
    if request.method == 'POST':
        nama = request.form.get('nama_kelas', '').strip()
        angkatan = request.form.get('angkatan', '').strip()
        if not nama or not angkatan:
            error = 'Nama kelas dan angkatan wajib diisi.'
        elif db.update_kelas(id, nama, angkatan):
            flash('Kelas berhasil diperbarui!', 'success')
            return redirect(url_for('kelas_index'))
        else:
            error = 'Gagal memperbarui kelas.'
    return render_template('kelas/form.html',
                           active_page='kelas', kelas=kelas, error=error)


@app.route('/kelas/hapus/<int:id>', methods=['POST'])
@login_required
def kelas_hapus(id):
    """Hapus kelas (CASCADE ke MK dan jadwal)."""
    if db.hapus_kelas(id):
        flash('Kelas berhasil dihapus.', 'success')
    else:
        flash('Gagal menghapus kelas. Mungkin masih ada mahasiswa terkait.', 'error')
    return redirect(url_for('kelas_index'))


@app.route('/kelas/<int:id>/matakuliah')
@login_required
def kelas_detail(id):
    """Detail kelas + daftar matakuliah."""
    kelas = db.get_kelas_by_id(id)
    if not kelas:
        flash('Kelas tidak ditemukan.', 'error')
        return redirect(url_for('kelas_index'))
    matakuliah = db.get_matakuliah_by_kelas(id)
    jumlah_mhs = db.hitung_mahasiswa_per_kelas(id)
    return render_template('kelas/detail.html',
                           active_page='kelas', kelas=kelas,
                           matakuliah=matakuliah, jumlah_mhs=jumlah_mhs)


# ══════════════════════════════════════════════════════════════
# MANAJEMEN MATAKULIAH
# ══════════════════════════════════════════════════════════════

@app.route('/matakuliah/tambah', methods=['GET', 'POST'])
@login_required
def matakuliah_tambah():
    """Tambah matakuliah baru."""
    kelas_id_param = request.args.get('kelas_id', type=int)
    kelas_asal = db.get_kelas_by_id(kelas_id_param) if kelas_id_param else None
    error = None
    if request.method == 'POST':
        nama = request.form.get('nama_mk', '').strip()
        kode = request.form.get('kode_mk', '').strip()
        kid  = request.form.get('kelas_id', type=int)
        sks  = request.form.get('sks', 2, type=int)
        if not nama or not kode or not kid:
            error = 'Semua field wajib diisi.'
        else:
            hasil = db.tambah_matakuliah(nama, kode, kid, sks)
            if hasil:
                flash('Mata kuliah berhasil ditambahkan!', 'success')
                return redirect(url_for('kelas_detail', id=kid))
            error = 'Gagal menambahkan. Kode MK mungkin sudah dipakai.'
    return render_template('matakuliah/form.html', active_page='kelas',
                           mk=None, kelas_asal=kelas_asal,
                           daftar_kelas=db.get_semua_kelas(), error=error)


@app.route('/matakuliah/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def matakuliah_edit(id):
    """Edit matakuliah."""
    mk = db.get_matakuliah_by_id(id)
    if not mk:
        flash('Matakuliah tidak ditemukan.', 'error')
        return redirect(url_for('kelas_index'))
    kelas_asal = db.get_kelas_by_id(mk['kelas_id'])
    error = None
    if request.method == 'POST':
        nama = request.form.get('nama_mk', '').strip()
        kode = request.form.get('kode_mk', '').strip()
        kid  = request.form.get('kelas_id', type=int)
        sks  = request.form.get('sks', 2, type=int)
        if db.update_matakuliah(id, nama, kode, kid, sks):
            flash('Mata kuliah berhasil diperbarui!', 'success')
            return redirect(url_for('kelas_detail', id=kid))
        error = 'Gagal memperbarui. Kode MK mungkin sudah dipakai.'
    return render_template('matakuliah/form.html', active_page='kelas',
                           mk=mk, kelas_asal=kelas_asal,
                           daftar_kelas=db.get_semua_kelas(), error=error)


@app.route('/matakuliah/hapus/<int:id>', methods=['POST'])
@login_required
def matakuliah_hapus(id):
    """Hapus matakuliah (CASCADE ke jadwal)."""
    mk = db.get_matakuliah_by_id(id)
    kelas_id = mk['kelas_id'] if mk else None
    if db.hapus_matakuliah(id):
        flash('Mata kuliah berhasil dihapus.', 'success')
    else:
        flash('Gagal menghapus mata kuliah.', 'error')
    return redirect(url_for('kelas_detail', id=kelas_id) if kelas_id
                    else url_for('kelas_index'))


# ══════════════════════════════════════════════════════════════
# MANAJEMEN JADWAL
# ══════════════════════════════════════════════════════════════

@app.route('/jadwal')
@login_required
def jadwal_index():
    """Daftar semua jadwal."""
    return render_template('jadwal/index.html', active_page='jadwal',
                           daftar_jadwal=db.get_semua_jadwal())


@app.route('/jadwal/tambah', methods=['GET', 'POST'])
@login_required
def jadwal_tambah():
    """Tambah jadwal baru."""
    error = None
    if request.method == 'POST':
        mk_id       = request.form.get('matakuliah_id', type=int)
        hari         = request.form.get('hari', '').strip()
        jam_mulai    = request.form.get('jam_mulai', '').strip()
        jam_selesai  = request.form.get('jam_selesai', '').strip()
        if not mk_id or not hari or not jam_mulai or not jam_selesai:
            error = 'Semua field wajib diisi.'
        else:
            # batas_terlambat dihitung otomatis di database.py
            hasil = db.tambah_jadwal(mk_id, hari, jam_mulai, jam_selesai)
            if hasil:
                flash('Jadwal berhasil ditambahkan!', 'success')
                return redirect(url_for('jadwal_index'))
            error = 'Gagal menambahkan jadwal.'
    return render_template('jadwal/form.html', active_page='jadwal',
                           daftar_mk=db.get_semua_matakuliah(), error=error)


@app.route('/jadwal/hapus/<int:id>', methods=['POST'])
@login_required
def jadwal_hapus(id):
    """Hapus jadwal."""
    if db.hapus_jadwal(id):
        flash('Jadwal berhasil dihapus.', 'success')
    else:
        flash('Gagal menghapus jadwal.', 'error')
    return redirect(url_for('jadwal_index'))


# ══════════════════════════════════════════════════════════════
# MANAJEMEN MAHASISWA
# ══════════════════════════════════════════════════════════════

@app.route('/mahasiswa')
@login_required
def mahasiswa_index():
    """Daftar semua mahasiswa."""
    filter_kelas = request.args.get('kelas_id', type=int)
    if filter_kelas:
        daftar = db.get_users_by_kelas(filter_kelas)
    else:
        daftar = db.get_semua_user()
    # Hitung foto per mahasiswa untuk status biometrik
    for m in daftar:
        folder = os.path.join(DATASET_PATH, str(m['id']))
        if os.path.isdir(folder):
            m['foto_count'] = len([f for f in os.listdir(folder) if f.endswith('.jpg')])
        else:
            m['foto_count'] = 0
    total_mhs = len(db.get_semua_user())
    bio_aktif = sum(1 for m in db.get_semua_user()
                    if os.path.isdir(os.path.join(DATASET_PATH, str(m['id'])))
                    and len(os.listdir(os.path.join(DATASET_PATH, str(m['id'])))) > 0)
    return render_template('mahasiswa/index.html', active_page='mahasiswa',
                           daftar_mahasiswa=daftar,
                           daftar_kelas=db.get_semua_kelas(),
                           filter_kelas=filter_kelas,
                           total_mhs=total_mhs, bio_aktif=bio_aktif)


@app.route('/mahasiswa/register', methods=['GET', 'POST'])
@login_required
def mahasiswa_register():
    """Form registrasi mahasiswa baru (data + foto kamera)."""
    error = None
    return render_template('mahasiswa/register.html', active_page='mahasiswa',
                           daftar_kelas=db.get_semua_kelas(), error=error)


@app.route('/mahasiswa/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def mahasiswa_edit(id):
    """Edit data mahasiswa."""
    mhs = db.get_user_by_id(id)
    if not mhs:
        flash('Mahasiswa tidak ditemukan.', 'error')
        return redirect(url_for('mahasiswa_index'))
    error = None
    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        nim  = request.form.get('nim', '').strip()
        kid  = request.form.get('kelas_id', type=int)
        if not nama or not nim or not kid:
            error = 'Semua field wajib diisi.'
        elif db.update_user(id, nama, nim, kid):
            flash('Data mahasiswa berhasil diperbarui!', 'success')
            return redirect(url_for('mahasiswa_index'))
        else:
            error = 'Gagal memperbarui. NIM mungkin sudah dipakai.'
    return render_template('mahasiswa/edit.html', active_page='mahasiswa',
                           mhs=mhs, daftar_kelas=db.get_semua_kelas(), error=error)


@app.route('/mahasiswa/hapus/<int:id>', methods=['POST'])
@login_required
def mahasiswa_hapus(id):
    """Hapus mahasiswa + folder dataset foto."""
    mhs = db.get_user_by_id(id)
    if db.hapus_user(id):
        # Hapus folder foto dataset jika ada
        if mhs:
            folder = os.path.join(DATASET_PATH, str(id))
            if os.path.isdir(folder):
                import shutil
                shutil.rmtree(folder, ignore_errors=True)
        flash('Mahasiswa berhasil dihapus.', 'success')
    else:
        flash('Gagal menghapus mahasiswa.', 'error')
    return redirect(url_for('mahasiswa_index'))


# ══════════════════════════════════════════════════════════════
# PLACEHOLDER — akan diimplementasi tahap selanjutnya
# ══════════════════════════════════════════════════════════════

@app.route('/absensi/rekap')
@login_required
def absensi_rekap():
    """Rekap absensi."""
    return render_template('dashboard.html', active_page='rekap',
                           statistik=db.get_statistik_dashboard(),
                           absensi_hari_ini=[])


@app.route('/laporan')
@login_required
def laporan_index():
    """Laporan kehadiran."""
    return render_template('dashboard.html', active_page='laporan',
                           statistik=db.get_statistik_dashboard(),
                           absensi_hari_ini=[])


# ══════════════════════════════════════════════════════════════
# API ENDPOINTS
# ══════════════════════════════════════════════════════════════

@app.route('/api/absensi/hari-ini')
@login_required
def api_absensi_hari_ini():
    """Data absensi hari ini dalam format JSON."""
    data = db.get_absensi_hari_ini()
    return jsonify({'status': 'ok', 'data': data, 'pesan': None})


@app.route('/api/foto/upload', methods=['POST'])
@login_required
def api_foto_upload():
    """Terima foto wajah via AJAX (base64) dan simpan ke dataset/."""
    import base64
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'pesan': 'Data tidak valid.'}), 400

    nama     = data.get('nama', '').strip()
    nim      = data.get('nim', '').strip()
    kelas_id = data.get('kelas_id')
    foto_b64 = data.get('foto', '')
    index    = data.get('index', 0)

    if not nama or not nim or not kelas_id or not foto_b64:
        return jsonify({'status': 'error', 'pesan': 'Field tidak lengkap.'}), 400

    try:
        # Pastikan user sudah ada di DB, buat jika belum
        user = db.get_user_by_nim(nim)
        if not user:
            user_id = db.tambah_user(nama, nim, int(kelas_id))
            if not user_id:
                return jsonify({'status': 'error', 'pesan': 'NIM sudah terdaftar atau gagal simpan.'}), 400
        else:
            user_id = user['id']

        # Decode base64 → simpan ke dataset/{user_id}/
        header, encoded = foto_b64.split(',', 1)
        foto_bytes = base64.b64decode(encoded)

        folder = os.path.join(DATASET_PATH, str(user_id))
        os.makedirs(folder, exist_ok=True)

        filepath = os.path.join(folder, f'{index}.jpg')
        with open(filepath, 'wb') as f:
            f.write(foto_bytes)

        return jsonify({'status': 'ok', 'pesan': f'Foto {index} tersimpan.', 'data': {'user_id': user_id}})

    except Exception as e:
        return jsonify({'status': 'error', 'pesan': str(e)}), 500


@app.route('/api/training/start', methods=['POST'])
@login_required
def api_training_start():
    """Mulai training LBPH di background thread."""
    import threading

    def run_training():
        """Jalankan training di background."""
        try:
            from face.trainer import train_model
            train_model()
        except Exception as e:
            print(f'[ERROR] Training gagal: {e}')

    thread = threading.Thread(target=run_training, daemon=True)
    thread.start()

    return jsonify({
        'status': 'ok',
        'pesan': 'Training dimulai di background. Model akan diperbarui otomatis.',
        'data': None
    })


# ══════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 45)
    print("   FLASK SERVER - SISTEM ABSENSI")
    print("=" * 45)
    print(f"\n[INFO] Dashboard : http://127.0.0.1:{FLASK_PORT}")
    print(f"[INFO] Login     : http://127.0.0.1:{FLASK_PORT}/login")
    print(f"[INFO] Tekan Ctrl+C untuk menghentikan.\n")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)