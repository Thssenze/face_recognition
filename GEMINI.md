# Sistem Absensi Face Recognition — Project Rules

## Konteks Proyek
Sistem absensi berbasis face recognition menggunakan Python 3.10 + Flask + 
MySQL + OpenCV LBPH. Baca context.md untuk spesifikasi lengkap sebelum 
menulis kode apapun.

## Aturan Wajib
- Gunakan Python 3.10, bukan versi lain
- Semua query database HANYA di database.py
- Semua konfigurasi HANYA di config.py, tidak boleh hardcode nilai
- Semua route kecuali /login dan /register wajib @login_required
- Komentar kode dalam Bahasa Indonesia
- Response API selalu JSON: {"status":"ok/error","data":...,"pesan":...}
- Error handling wajib try/except di semua fungsi database
- Training LBPH wajib di background thread, tidak boleh blokir Flask
- UNIQUE constraint absensi: (user_id, jadwal_id, tanggal)
- Jangan pernah sentuh config.py, dataset/, models/ untuk di-commit

## Stack
- Backend: Flask 3.0, MySQL 8.0, opencv-contrib-python 4.8
- Auth: Flask session + werkzeug password hash
- Realtime: Flask-SocketIO + gevent
- Export: openpyxl untuk Excel, csv built-in untuk CSV
- Deploy: Railway (Procfile + gunicorn + gevent worker)

## Tampilan
- Semua tampilan menggunakan file HTML dari folder templates/stitch/ sebagai referensi
- Konversi ke Jinja2 dengan {% extends 'base.html' %} dan {% block content %}
- Data statis diganti variabel Jinja2: angka hardcode → {{ variabel }}
- Loop data → {% for item in data %}
- Sidebar dan navbar yang identik di semua halaman dipindah ke base.html