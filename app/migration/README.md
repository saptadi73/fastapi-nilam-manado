# Migrasi Database

Migrasi memakai Alembic dan membaca koneksi dari `DATABASE_URL` di file `.env`.

Jalankan migrasi:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Buat revision baru:

```powershell
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "nama perubahan"
```

Jika tabel `users` sudah terlanjur dibuat manual atau dari `create_all`, revision awal ini aman dijalankan karena mengecek keberadaan tabel dulu.
