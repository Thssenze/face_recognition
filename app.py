# app.py — Flask Server: Dashboard Lengkap + API

from flask import Flask, request, jsonify, render_template_string, Response
from flask_cors import CORS
from database import get_absensi_hari_ini, get_semua_user
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, DB_CONFIG
from datetime import datetime, date
import mysql.connector
import csv, io

app = Flask(__name__)
CORS(app)

log_absensi = []

# ── HELPER DATABASE TAMBAHAN ──────────────────────────────────────────────────

def get_absensi_by_tanggal(tgl):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM absensi WHERE tanggal = %s ORDER BY waktu DESC", (tgl,)
    )
    hasil = cursor.fetchall()
    cursor.close(); conn.close()
    return hasil

def get_absensi_by_range(tgl_mulai, tgl_akhir):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM absensi WHERE tanggal BETWEEN %s AND %s ORDER BY tanggal DESC, waktu DESC",
        (tgl_mulai, tgl_akhir)
    )
    hasil = cursor.fetchall()
    cursor.close(); conn.close()
    return hasil

def hapus_user(user_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM absensi WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close(); conn.close()

def get_statistik():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT tanggal, COUNT(*) as jumlah
        FROM absensi
        WHERE tanggal >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
        GROUP BY tanggal ORDER BY tanggal ASC
    """)
    per_hari = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) as total FROM absensi")
    total = cursor.fetchone()['total']
    cursor.close(); conn.close()
    return per_hari, total

# ── CSS & JS BERSAMA ──────────────────────────────────────────────────────────

COMMON_STYLE = """
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}
  a{color:inherit;text-decoration:none}
  .header{background:#1e293b;padding:1rem 2rem;border-bottom:1px solid #334155;display:flex;align-items:center;justify-content:space-between}
  .header h1{font-size:1.1rem;font-weight:700;color:#f1f5f9}
  .live{background:#22c55e22;color:#22c55e;border:1px solid #22c55e44;border-radius:20px;font-size:11px;padding:3px 10px}
  .nav{background:#1e293b;border-bottom:1px solid #334155;display:flex;padding:0 2rem}
  .nav a{padding:.75rem 1.25rem;font-size:13px;color:#64748b;border-bottom:2px solid transparent;transition:.2s;display:block}
  .nav a:hover,.nav a.active{color:#38bdf8;border-bottom-color:#38bdf8}
  .container{max-width:1000px;margin:2rem auto;padding:0 1.5rem}
  .stats{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:2rem}
  .stat{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:1.2rem}
  .stat .num{font-size:1.8rem;font-weight:700;color:#38bdf8}
  .stat .lbl{font-size:12px;color:#64748b;margin-top:4px}
  .chart{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:1.2rem;margin-bottom:2rem}
  .chart-title{font-size:13px;color:#64748b;margin-bottom:1rem;font-weight:600;text-transform:uppercase;letter-spacing:.05em}
  .bars{display:flex;align-items:flex-end;gap:8px;height:90px}
  .bar-wrap{flex:1;display:flex;flex-direction:column;align-items:center;gap:4px}
  .bar{width:100%;background:#38bdf855;border-radius:4px 4px 0 0;min-height:4px}
  .bar-lbl{font-size:10px;color:#475569}
  .bar-num{font-size:11px;color:#38bdf8;font-weight:600}
  .card{background:#1e293b;border:1px solid #334155;border-radius:12px;overflow:hidden;margin-bottom:1.5rem}
  .card-head{padding:1rem 1.2rem;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #334155}
  .card-head h2{font-size:13px;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em}
  table{width:100%;border-collapse:collapse}
  th{background:#0f172a;color:#475569;font-size:11px;text-transform:uppercase;letter-spacing:.05em;padding:.7rem 1rem;text-align:left}
  td{padding:.8rem 1rem;font-size:13px;border-bottom:1px solid #0f172a}
  tr:last-child td{border-bottom:none}
  tr:hover td{background:#ffffff08}
  .badge-ok{background:#22c55e22;color:#22c55e;border:1px solid #22c55e44;border-radius:20px;font-size:11px;padding:2px 8px}
  .btn{display:inline-block;padding:6px 14px;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;border:none;transition:.2s;text-decoration:none}
  .btn-blue{background:#38bdf822;color:#38bdf8;border:1px solid #38bdf844}
  .btn-blue:hover{background:#38bdf833}
  .btn-green{background:#22c55e22;color:#22c55e;border:1px solid #22c55e44}
  .btn-green:hover{background:#22c55e33}
  .btn-red{background:#ef444422;color:#ef4444;border:1px solid #ef444444}
  .btn-red:hover{background:#ef444433}
  .filter{display:flex;gap:.75rem;align-items:center;flex-wrap:wrap;margin-bottom:1.5rem}
  .filter input,.filter select{background:#1e293b;border:1px solid #334155;color:#e2e8f0;padding:6px 12px;border-radius:8px;font-size:13px}
  .filter input:focus{outline:none;border-color:#38bdf8}
  .empty{text-align:center;color:#334155;padding:3rem;font-size:14px;line-height:1.8}
  .empty code{background:#1e293b;color:#38bdf8;padding:2px 8px;border-radius:4px}
  .modal-overlay{display:none;position:fixed;inset:0;background:#00000088;z-index:100;align-items:center;justify-content:center}
  .modal-overlay.show{display:flex}
  .modal{background:#1e293b;border:1px solid #334155;border-radius:16px;padding:1.5rem;width:380px;max-width:90vw}
  .modal h3{font-size:15px;font-weight:700;margin-bottom:.75rem}
  .modal p{font-size:13px;color:#94a3b8;margin-bottom:1.5rem;line-height:1.6}
  .modal-actions{display:flex;gap:.75rem;justify-content:flex-end}
  .info-box{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:1.2rem;margin-bottom:1rem;font-size:13px;color:#64748b;line-height:1.8}
  .info-box code{background:#0f172a;color:#38bdf8;padding:2px 6px;border-radius:4px}
  .refresh-note{font-size:11px;color:#334155;text-align:right;margin-top:1rem}
</style>
"""

COMMON_MODAL = """
<div class="modal-overlay" id="modalHapus">
  <div class="modal">
    <h3>⚠️ Konfirmasi Hapus</h3>
    <p>Apakah Anda yakin ingin menghapus user ini?<br>
    Seluruh data absensi user ini juga akan terhapus dan <strong>tidak dapat dikembalikan</strong>.</p>
    <div class="modal-actions">
      <button class="btn btn-blue" onclick="tutupModal()">Batal</button>
      <button class="btn btn-red" id="btnHapusKonfirm">Ya, Hapus</button>
    </div>
  </div>
</div>
<script>
  let hapusTargetId = null;
  function konfirmasiHapus(userId) {
    hapusTargetId = userId;
    document.getElementById('modalHapus').classList.add('show');
  }
  function tutupModal() {
    document.getElementById('modalHapus').classList.remove('show');
  }
  document.getElementById('btnHapusKonfirm').onclick = function() {
    if (hapusTargetId) {
      fetch('/api/hapus-user/' + hapusTargetId, {method:'DELETE'})
        .then(r => r.json())
        .then(() => location.reload());
    }
  }
</script>
"""

def nav_html(active):
    tabs = [('/', 'hari_ini', 'Hari Ini'),
            ('/laporan', 'laporan', 'Laporan'),
            ('/users', 'users', 'Manajemen User')]
    links = ''.join(
        f'<a href="{url}" class="{"active" if key == active else ""}">{label}</a>'
        for url, key, label in tabs
    )
    return f"""
    <!DOCTYPE html><html lang="id"><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>Dashboard Absensi</title>
    {COMMON_STYLE}
    </head><body>
    <div class="header">
      <h1>📋 Sistem Absensi Face Recognition</h1>
      <span class="live">● LIVE</span>
    </div>
    <div class="nav">{links}</div>
    <div class="container">
    """

# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route('/')
def dashboard():
    absensi = get_absensi_hari_ini()
    semua_user = get_semua_user()
    per_hari, total_semua = get_statistik()

    # Hitung tinggi bar chart
    maks = max((h['jumlah'] for h in per_hari), default=1)
    bars_html = ''
    for h in per_hari:
        tinggi = max(int(h['jumlah'] / maks * 70), 4)
        tgl_fmt = h['tanggal'].strftime('%d/%m') if hasattr(h['tanggal'], 'strftime') else str(h['tanggal'])
        bars_html += f"""
        <div class="bar-wrap">
          <div class="bar-num">{h['jumlah']}</div>
          <div class="bar" style="height:{tinggi}px"></div>
          <div class="bar-lbl">{tgl_fmt}</div>
        </div>"""

    if not bars_html:
        bars_html = '<div style="color:#334155;font-size:13px;margin:auto">Belum ada data</div>'

    rows_html = ''
    for i, row in enumerate(absensi, 1):
        rows_html += f"""
        <tr>
          <td>{i}</td><td>{row['nama']}</td><td>{row['nim']}</td>
          <td>{row['waktu']}</td>
          <td><span class="badge-ok">✓ Hadir</span></td>
        </tr>"""

    tabel = f"""
    <table>
      <thead><tr><th>#</th><th>Nama</th><th>NIM</th><th>Waktu</th><th>Status</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table>""" if absensi else """
    <div class="empty">Belum ada absensi hari ini.<br>
    Jalankan <code>python face_recognize.py</code> untuk memulai.</div>"""

    hari_ini = date.today().isoformat()
    html = nav_html('hari_ini') + f"""
    <div class="stats">
      <div class="stat"><div class="num">{len(absensi)}</div><div class="lbl">Hadir Hari Ini</div></div>
      <div class="stat"><div class="num">{len(semua_user)}</div><div class="lbl">Total Terdaftar</div></div>
      <div class="stat"><div class="num">{total_semua}</div><div class="lbl">Total Absensi</div></div>
      <div class="stat"><div class="num">{datetime.now().strftime("%H:%M")}</div><div class="lbl">Waktu Server</div></div>
    </div>
    <div class="chart">
      <div class="chart-title">Kehadiran 7 Hari Terakhir</div>
      <div class="bars">{bars_html}</div>
    </div>
    <div class="card">
      <div class="card-head">
        <h2>Rekap Kehadiran — {hari_ini}</h2>
        <a href="/export-csv?tanggal={hari_ini}" class="btn btn-green">⬇ Export CSV</a>
      </div>
      {tabel}
    </div>
    <div class="refresh-note">Auto-refresh setiap 10 detik</div>
    <meta http-equiv="refresh" content="10">
    </div>{COMMON_MODAL}</body></html>"""
    return html


@app.route('/laporan')
def laporan():
    dari   = request.args.get('dari',   date.today().isoformat())
    sampai = request.args.get('sampai', date.today().isoformat())
    absensi = get_absensi_by_range(dari, sampai)

    rows_html = ''
    for i, row in enumerate(absensi, 1):
        rows_html += f"""
        <tr>
          <td>{i}</td><td>{row['tanggal']}</td><td>{row['nama']}</td>
          <td>{row['nim']}</td><td>{row['waktu']}</td>
          <td><span class="badge-ok">✓ Hadir</span></td>
        </tr>"""

    tabel = f"""
    <table>
      <thead><tr><th>#</th><th>Tanggal</th><th>Nama</th><th>NIM</th><th>Waktu</th><th>Status</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table>""" if absensi else """
    <div class="empty">Tidak ada data pada rentang tanggal tersebut.</div>"""

    html = nav_html('laporan') + f"""
    <form method="GET" action="/laporan">
      <div class="filter">
        <label style="font-size:13px;color:#64748b">Dari:</label>
        <input type="date" name="dari" value="{dari}">
        <label style="font-size:13px;color:#64748b">Sampai:</label>
        <input type="date" name="sampai" value="{sampai}">
        <button type="submit" class="btn btn-blue">Tampilkan</button>
        <a href="/export-csv?dari={dari}&sampai={sampai}" class="btn btn-green">⬇ Export CSV</a>
      </div>
    </form>
    <div class="card">
      <div class="card-head">
        <h2>Laporan: {dari} s/d {sampai}</h2>
        <span style="font-size:12px;color:#64748b">{len(absensi)} record</span>
      </div>
      {tabel}
    </div>
    </div>{COMMON_MODAL}</body></html>"""
    return html


@app.route('/users')
def halaman_users():
    users = get_semua_user()

    rows_html = ''
    for u in users:
        rows_html += f"""
        <tr>
          <td>{u['id']}</td><td>{u['nama']}</td><td>{u['nim']}</td>
          <td>{u['created_at']}</td>
          <td><button class="btn btn-red" onclick="konfirmasiHapus({u['id']})">🗑 Hapus</button></td>
        </tr>"""

    tabel = f"""
    <table>
      <thead><tr><th>ID</th><th>Nama</th><th>NIM</th><th>Terdaftar</th><th>Aksi</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table>""" if users else """
    <div class="empty">Belum ada user terdaftar.</div>"""

    html = nav_html('users') + f"""
    <div class="card">
      <div class="card-head">
        <h2>Daftar User Terdaftar</h2>
        <span style="font-size:12px;color:#64748b">{len(users)} user</span>
      </div>
      {tabel}
    </div>
    <div class="info-box">
      💡 <strong style="color:#94a3b8">Untuk menambah user baru:</strong>
      Jalankan <code>python face_register.py</code> di CMD,
      lalu <code>python train_model.py</code> untuk melatih ulang model.
    </div>
    </div>{COMMON_MODAL}</body></html>"""
    return html


@app.route('/export-csv')
def export_csv():
    tanggal = request.args.get('tanggal')
    dari    = request.args.get('dari',   date.today().isoformat())
    sampai  = request.args.get('sampai', date.today().isoformat())

    if tanggal:
        data     = get_absensi_by_tanggal(tanggal)
        filename = f"absensi_{tanggal}.csv"
    else:
        data     = get_absensi_by_range(dari, sampai)
        filename = f"absensi_{dari}_sd_{sampai}.csv"

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['No', 'Nama', 'NIM', 'Tanggal', 'Waktu'])
    for i, row in enumerate(data, 1):
        writer.writerow([i, row['nama'], row['nim'], row['tanggal'], row['waktu']])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


@app.route('/api/hapus-user/<int:user_id>', methods=['DELETE'])
def api_hapus_user(user_id):
    hapus_user(user_id)
    return jsonify({'status': 'ok'})


@app.route('/api/hasil-absensi', methods=['POST'])
def hasil_absensi():
    data = request.get_json()
    if data:
        data['timestamp'] = datetime.now().strftime("%H:%M:%S")
        log_absensi.insert(0, data)
        if len(log_absensi) > 50:
            log_absensi.pop()
    return jsonify({'status': 'ok'})


@app.route('/api/absensi-hari-ini', methods=['GET'])
def api_absensi_hari_ini():
    return jsonify(get_absensi_hari_ini())


@app.route('/api/users', methods=['GET'])
def api_users():
    return jsonify(get_semua_user())


if __name__ == "__main__":
    print("=" * 45)
    print("   FLASK SERVER — SISTEM ABSENSI")
    print("=" * 45)
    print(f"\n[INFO] Dashboard : http://127.0.0.1:{FLASK_PORT}")
    print(f"[INFO] Laporan   : http://127.0.0.1:{FLASK_PORT}/laporan")
    print(f"[INFO] Users     : http://127.0.0.1:{FLASK_PORT}/users")
    print(f"[INFO] Tekan Ctrl+C untuk menghentikan.\n")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)