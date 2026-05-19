# Dokumentasi API Frontend

Dokumen ini menjelaskan endpoint backend yang sudah tersedia untuk implementasi frontend ERP budidaya nilam, khususnya modul master wilayah GIS dan data petani.

Base URL saat development:

```txt
http://localhost:8000
```

Jalankan backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

## Format Umum

Semua request dan response menggunakan JSON, kecuali endpoint login OAuth2 yang memakai `application/x-www-form-urlencoded`.

Header umum:

```txt
Content-Type: application/json
```

Semua primary key internal seperti `users.id`, `farmers.id`, `lands.id`, dan `land_coordinates.id` memakai UUID string, bukan auto increment integer. Khusus master wilayah GIS, identifier yang dipakai tetap `kode` wilayah resmi dari CSV.

Semua response backend memakai wrapper baku:

```json
{
  "status": "success",
  "message": "Pesan response",
  "data": {}
}
```

Response error juga memakai format yang sama:

```json
{
  "status": "error",
  "message": "Pesan error",
  "data": null
}
```

Catatan: contoh object/list pada bagian endpoint di bawah adalah isi dari field `data`, kecuali jika contoh menampilkan wrapper lengkap.

## Auth

### Register User

```txt
POST /auth/register
```

Payload:

```json
{
  "name": "Admin Nilam",
  "email": "admin@nilam.local",
  "password": "password123"
}
```

Response `200 OK`:

```json
{
  "status": "success",
  "message": "Registrasi berhasil",
  "data": {
    "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
    "name": "Admin Nilam",
    "email": "admin@nilam.local",
    "password": "$2b$12$..."
  }
}
```

Error umum:

```json
{
  "status": "error",
  "message": "Email already registered",
  "data": null
}
```

### Login

```txt
POST /auth/login
```

Content-Type:

```txt
application/x-www-form-urlencoded
```

Payload form:

```txt
username=admin@nilam.local
password=password123
```

Response `200 OK`:

```json
{
  "status": "success",
  "message": "Login berhasil",
  "data": {
    "access_token": "jwt-token",
    "token_type": "bearer"
  }
}
```

Simpan `access_token` di frontend untuk endpoint yang nanti membutuhkan auth.

## Master Wilayah GIS

Data wilayah berasal dari:

```txt
app/reference/gis/kode wilayah.csv
```

Struktur kode:

```txt
provinsi        : 2 digit
kabupaten/kota : 4 digit
kecamatan      : 6 digit
desa/kelurahan : 10 digit
```

Response wilayah:

```json
{
  "kode": "1101012001",
  "nama": "Keude Bakongan",
  "level": "desa_kelurahan",
  "parent_kode": "110101"
}
```

### Ambil Provinsi

```txt
GET /wilayah/provinsi
GET /wilayah/provinsi?search=aceh
```

Response `200 OK`:

```json
[
  {
    "kode": "11",
    "nama": "ACEH",
    "level": "provinsi",
    "parent_kode": null
  }
]
```

### Ambil Kabupaten/Kota

```txt
GET /wilayah/kabupaten-kota?provinsi_kode=11
GET /wilayah/kabupaten-kota?provinsi_kode=11&search=selatan
```

Response `200 OK`:

```json
[
  {
    "kode": "1101",
    "nama": "KAB. ACEH SELATAN",
    "level": "kabupaten_kota",
    "parent_kode": "11"
  }
]
```

### Ambil Kecamatan

```txt
GET /wilayah/kecamatan?kabupaten_kota_kode=1101
GET /wilayah/kecamatan?kabupaten_kota_kode=1101&search=bakongan
```

Response `200 OK`:

```json
[
  {
    "kode": "110101",
    "nama": "Bakongan",
    "level": "kecamatan",
    "parent_kode": "1101"
  }
]
```

### Ambil Desa/Kelurahan

```txt
GET /wilayah/desa-kelurahan?kecamatan_kode=110101
GET /wilayah/desa-kelurahan?kecamatan_kode=110101&search=keude
```

Response `200 OK`:

```json
[
  {
    "kode": "1101012001",
    "nama": "Keude Bakongan",
    "level": "desa_kelurahan",
    "parent_kode": "110101"
  }
]
```

### Alur Dropdown Frontend

1. Saat form dibuka, panggil `GET /wilayah/provinsi`.
2. Setelah user memilih provinsi, simpan `provinsi_kode`, lalu reset pilihan kabupaten/kota, kecamatan, dan desa/kelurahan.
3. Panggil `GET /wilayah/kabupaten-kota?provinsi_kode={provinsi_kode}`.
4. Setelah user memilih kabupaten/kota, simpan `kabupaten_kota_kode`, lalu reset kecamatan dan desa/kelurahan.
5. Panggil `GET /wilayah/kecamatan?kabupaten_kota_kode={kabupaten_kota_kode}`.
6. Setelah user memilih kecamatan, simpan `kecamatan_kode`, lalu reset desa/kelurahan.
7. Panggil `GET /wilayah/desa-kelurahan?kecamatan_kode={kecamatan_kode}`.
8. Saat submit petani, kirim semua kode wilayah, bukan nama wilayah.

## Petani

### Object Petani

Response petani selalu mengembalikan kode dan nama wilayah:

```json
{
  "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
  "nama": "Budi Santoso",
  "nik": "1234567890123456",
  "alamat": "Jl. Nilam No. 1",
  "hp": "08123456789",
  "foto_path": null,
  "foto_url": null,
  "desa_kelurahan_kode": "1101012001",
  "kecamatan_kode": "110101",
  "kabupaten_kota_kode": "1101",
  "provinsi_kode": "11",
  "desa_kelurahan": "Keude Bakongan",
  "kecamatan": "Bakongan",
  "kabupaten_kota": "KAB. ACEH SELATAN",
  "provinsi": "ACEH"
}
```

Field:

```txt
nama                 required, max 150
nik                  required, 16 digit/string, unique
alamat               required, max 255
hp                   optional, max 30
foto_path            optional, path internal file foto
foto_url             optional, URL publik untuk menampilkan foto
provinsi_kode        required, kode provinsi valid
kabupaten_kota_kode  required, harus anak dari provinsi
kecamatan_kode       required, harus anak dari kabupaten/kota
desa_kelurahan_kode  required, harus anak dari kecamatan
```

### List Petani

```txt
GET /farmers
GET /farmers?search=budi
GET /farmers?search=1234567890123456
```

Response `200 OK`:

```json
[
  {
    "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
    "nama": "Budi Santoso",
    "nik": "1234567890123456",
    "alamat": "Jl. Nilam No. 1",
    "hp": "08123456789",
    "foto_path": null,
    "foto_url": null,
    "desa_kelurahan_kode": "1101012001",
    "kecamatan_kode": "110101",
    "kabupaten_kota_kode": "1101",
    "provinsi_kode": "11",
    "desa_kelurahan": "Keude Bakongan",
    "kecamatan": "Bakongan",
    "kabupaten_kota": "KAB. ACEH SELATAN",
    "provinsi": "ACEH"
  }
]
```

### Detail Petani

```txt
GET /farmers/{id}
```

Contoh:

```txt
GET /farmers/243b7917-8586-432e-9199-47bcedd8f2f9
```

Response `200 OK` sama seperti object petani.

Jika tidak ditemukan:

```json
{
  "status": "error",
  "message": "Petani tidak ditemukan",
  "data": null
}
```

### Buat Petani

```txt
POST /farmers
```

Payload:

```json
{
  "nama": "Budi Santoso",
  "nik": "1234567890123456",
  "alamat": "Jl. Nilam No. 1",
  "hp": "08123456789",
  "provinsi_kode": "11",
  "kabupaten_kota_kode": "1101",
  "kecamatan_kode": "110101",
  "desa_kelurahan_kode": "1101012001"
}
```

Response `201 Created`:

```json
{
  "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
  "nama": "Budi Santoso",
  "nik": "1234567890123456",
  "alamat": "Jl. Nilam No. 1",
  "hp": "08123456789",
  "foto_path": null,
  "foto_url": null,
  "desa_kelurahan_kode": "1101012001",
  "kecamatan_kode": "110101",
  "kabupaten_kota_kode": "1101",
  "provinsi_kode": "11",
  "desa_kelurahan": "Keude Bakongan",
  "kecamatan": "Bakongan",
  "kabupaten_kota": "KAB. ACEH SELATAN",
  "provinsi": "ACEH"
}
```

Error NIK duplikat:

```json
{
  "status": "error",
  "message": "NIK petani sudah terdaftar",
  "data": null
}
```

Error wilayah tidak valid:

```json
{
  "status": "error",
  "message": "Kode kabupaten/kota tidak sesuai provinsi",
  "data": null
}
```

Pesan validasi wilayah yang mungkin muncul:

```txt
Kode provinsi tidak valid
Kode kabupaten/kota tidak sesuai provinsi
Kode kecamatan tidak sesuai kabupaten/kota
Kode desa/kelurahan tidak sesuai kecamatan
```

### Update Petani

```txt
PUT /farmers/{id}
```

Payload boleh parsial. Contoh update nomor HP:

```json
{
  "hp": "082222222222"
}
```

Contoh pindah wilayah:

```json
{
  "provinsi_kode": "11",
  "kabupaten_kota_kode": "1101",
  "kecamatan_kode": "110101",
  "desa_kelurahan_kode": "1101012002"
}
```

Response `200 OK` sama seperti object petani.

Catatan frontend: jika mengubah salah satu level wilayah, sebaiknya kirim ulang seluruh rantai kode wilayah agar state form tetap eksplisit.

### Upload Foto Petani

Foto petani bersifat opsional. Buat data petani dulu lewat `POST /farmers`, lalu upload foto dengan endpoint ini.

```txt
POST /farmers/{id}/foto
```

Content-Type:

```txt
multipart/form-data
```

Field form:

```txt
foto: File
```

Format file yang diterima:

```txt
image/jpeg
image/png
image/webp
```

Response `200 OK`:

```json
{
  "status": "success",
  "message": "Foto petani berhasil diupload",
  "data": {
    "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
    "nama": "Budi Santoso",
    "nik": "1234567890123456",
    "alamat": "Jl. Nilam No. 1",
    "hp": "08123456789",
    "foto_path": "uploads/farmers/abc123.png",
    "foto_url": "/uploads/farmers/abc123.png",
    "desa_kelurahan_kode": "1101012001",
    "kecamatan_kode": "110101",
    "kabupaten_kota_kode": "1101",
    "provinsi_kode": "11",
    "desa_kelurahan": "Keude Bakongan",
    "kecamatan": "Bakongan",
    "kabupaten_kota": "KAB. ACEH SELATAN",
    "provinsi": "ACEH"
  }
}
```

Error format file:

```json
{
  "status": "error",
  "message": "Foto harus berformat JPG, PNG, atau WEBP",
  "data": null
}
```

### Hapus Foto Petani

```txt
DELETE /farmers/{id}/foto
```

Response `200 OK` sama seperti object petani, dengan `foto_path` dan `foto_url` bernilai `null`.

### Hapus Petani

```txt
DELETE /farmers/{id}
```

Response `200 OK`:

```json
{
  "status": "success",
  "message": "Data petani berhasil dihapus",
  "data": null
}
```

## Contoh Fetch Frontend

### Load Dropdown Bertingkat

```js
const API_BASE_URL = "http://localhost:8000";

async function getProvinsi(search = "") {
  const params = new URLSearchParams();
  if (search) params.set("search", search);

  const response = await fetch(`${API_BASE_URL}/wilayah/provinsi?${params}`);
  if (!response.ok) throw new Error("Gagal mengambil provinsi");
  return response.json();
}

async function getKabupatenKota(provinsiKode, search = "") {
  const params = new URLSearchParams({ provinsi_kode: provinsiKode });
  if (search) params.set("search", search);

  const response = await fetch(`${API_BASE_URL}/wilayah/kabupaten-kota?${params}`);
  if (!response.ok) throw new Error("Gagal mengambil kabupaten/kota");
  return response.json();
}

async function getKecamatan(kabupatenKotaKode, search = "") {
  const params = new URLSearchParams({ kabupaten_kota_kode: kabupatenKotaKode });
  if (search) params.set("search", search);

  const response = await fetch(`${API_BASE_URL}/wilayah/kecamatan?${params}`);
  if (!response.ok) throw new Error("Gagal mengambil kecamatan");
  return response.json();
}

async function getDesaKelurahan(kecamatanKode, search = "") {
  const params = new URLSearchParams({ kecamatan_kode: kecamatanKode });
  if (search) params.set("search", search);

  const response = await fetch(`${API_BASE_URL}/wilayah/desa-kelurahan?${params}`);
  if (!response.ok) throw new Error("Gagal mengambil desa/kelurahan");
  return response.json();
}
```

### Submit Petani

```js
async function createFarmer(payload) {
  const response = await fetch(`${API_BASE_URL}/farmers`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || "Gagal menyimpan petani");
  }

  return data.data;
}
```

Payload dari form:

```js
await createFarmer({
  nama: "Budi Santoso",
  nik: "1234567890123456",
  alamat: "Jl. Nilam No. 1",
  hp: "08123456789",
  provinsi_kode: selectedProvinsi.kode,
  kabupaten_kota_kode: selectedKabupatenKota.kode,
  kecamatan_kode: selectedKecamatan.kode,
  desa_kelurahan_kode: selectedDesaKelurahan.kode,
});
```

### Upload Foto

```js
async function uploadFarmerPhoto(farmerId, file) {
  const formData = new FormData();
  formData.append("foto", file);

  const response = await fetch(`${API_BASE_URL}/farmers/${farmerId}/foto`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || "Gagal upload foto petani");
  }

  return data.data;
}
```

## TypeScript Types

```ts
export type WilayahLevel =
  | "provinsi"
  | "kabupaten_kota"
  | "kecamatan"
  | "desa_kelurahan";

export interface Wilayah {
  kode: string;
  nama: string;
  level: WilayahLevel;
  parent_kode: string | null;
}

export interface Farmer {
  id: string;
  nama: string;
  nik: string;
  alamat: string;
  hp: string | null;
  foto_path: string | null;
  foto_url: string | null;
  desa_kelurahan_kode: string;
  kecamatan_kode: string;
  kabupaten_kota_kode: string;
  provinsi_kode: string;
  desa_kelurahan: string | null;
  kecamatan: string | null;
  kabupaten_kota: string | null;
  provinsi: string | null;
}

export type FarmerCreatePayload = Omit<
  Farmer,
  | "id"
  | "foto_path"
  | "foto_url"
  | "desa_kelurahan"
  | "kecamatan"
  | "kabupaten_kota"
  | "provinsi"
>;

export type FarmerUpdatePayload = Partial<FarmerCreatePayload>;
```

## Rekomendasi UI

Untuk form petani:

```txt
Provinsi dropdown
Kabupaten/Kota dropdown, disabled sampai provinsi dipilih
Kecamatan dropdown, disabled sampai kabupaten/kota dipilih
Desa/Kelurahan dropdown, disabled sampai kecamatan dipilih
```

Setiap kali parent berubah, kosongkan child dropdown:

```txt
ubah provinsi -> reset kabupaten/kota, kecamatan, desa/kelurahan
ubah kabupaten/kota -> reset kecamatan, desa/kelurahan
ubah kecamatan -> reset desa/kelurahan
```

Gunakan field `kode` sebagai value dropdown, dan field `nama` sebagai label.

## Lahan

Modul lahan menyimpan data kebun/lahan nilam, pemilik dari tabel petani, foto lahan opsional, dan titik koordinat polygon dalam tabel relasi tersendiri.

Nilai `kepemilikan` yang valid:

```txt
hak milik
sewa
pinjam
```

### Object Lahan

```json
{
  "id": "ccd178d6-77bd-4d12-819f-3bb1fe30ba4c",
  "kode": "LHN-001",
  "luas": 1.25,
  "elevasi": 325.5,
  "kepemilikan": "hak milik",
  "pemilik_id": "243b7917-8586-432e-9199-47bcedd8f2f9",
  "pemilik_nama": "Budi Santoso",
  "pemilik": {
    "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
    "nama": "Budi Santoso",
    "nik": "1234567890123456",
    "hp": "08123456789"
  },
  "foto_path": null,
  "foto_url": null,
  "provinsi_kode": "11",
  "kabupaten_kota_kode": "1101",
  "kecamatan_kode": "110101",
  "desa_kelurahan_kode": "1101012001",
  "provinsi": "ACEH",
  "kabupaten_kota": "KAB. ACEH SELATAN",
  "kecamatan": "Bakongan",
  "desa_kelurahan": "Keude Bakongan",
  "koordinat": [
    {
      "id": "ecde5b2b-0171-4fef-84b8-ce606872d9bd",
      "latitude": 1.1,
      "longitude": 124.1,
      "urutan": 1
    },
    {
      "id": 2,
      "latitude": 1.2,
      "longitude": 124.1,
      "urutan": 2
    }
  ]
}
```

Field:

```txt
kode         required, unique, max 50
luas         required, angka > 0
elevasi      optional, angka elevasi/mdpl
kepemilikan  required, hak milik | sewa | pinjam
pemilik_id   required, id petani yang sudah ada
foto_path    optional, path internal file foto
foto_url     optional, URL publik untuk menampilkan foto
pemilik      object petani pemilik, tersedia di response list/detail lahan
provinsi_kode        optional, kode provinsi lokasi lahan
kabupaten_kota_kode  optional, kode kabupaten/kota lokasi lahan
kecamatan_kode       optional, kode kecamatan lokasi lahan
desa_kelurahan_kode  optional, kode desa/kelurahan lokasi lahan
koordinat    optional array, berisi titik GPS polygon
```

### List Lahan

```txt
GET /lands
GET /lands?search=LHN
GET /lands?pemilik_id=243b7917-8586-432e-9199-47bcedd8f2f9
GET /lands?provinsi_kode=11
GET /lands?kabupaten_kota_kode=1101
GET /lands?kecamatan_kode=110101
GET /lands?desa_kelurahan_kode=1101012001
```

Gunakan query `pemilik_id` untuk mengambil daftar lahan berdasarkan petani tertentu.
Gunakan query wilayah untuk mengambil daftar lahan berdasarkan provinsi, kabupaten/kota, kecamatan, atau desa/kelurahan.

Response `200 OK`:

```json
{
  "status": "success",
  "message": "Data lahan berhasil diambil",
  "data": [
    {
      "id": "ccd178d6-77bd-4d12-819f-3bb1fe30ba4c",
      "kode": "LHN-001",
      "luas": 1.25,
      "elevasi": 325.5,
      "kepemilikan": "hak milik",
      "pemilik_id": "243b7917-8586-432e-9199-47bcedd8f2f9",
      "pemilik_nama": "Budi Santoso",
      "pemilik": {
        "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
        "nama": "Budi Santoso",
        "nik": "1234567890123456",
        "hp": "08123456789"
      },
      "foto_path": null,
      "foto_url": null,
      "provinsi_kode": "11",
      "kabupaten_kota_kode": "1101",
      "kecamatan_kode": "110101",
      "desa_kelurahan_kode": "1101012001",
      "provinsi": "ACEH",
      "kabupaten_kota": "KAB. ACEH SELATAN",
      "kecamatan": "Bakongan",
      "desa_kelurahan": "Keude Bakongan",
      "koordinat": []
    }
  ]
}
```

### Detail Lahan

```txt
GET /lands/{id}
```

Response `200 OK` sama seperti object lahan.

Jika tidak ditemukan:

```json
{
  "status": "error",
  "message": "Lahan tidak ditemukan",
  "data": null
}
```

### Buat Lahan

```txt
POST /lands
```

Payload:

```json
{
  "kode": "LHN-001",
  "luas": 1.25,
  "elevasi": 325.5,
  "kepemilikan": "hak milik",
  "pemilik_id": "243b7917-8586-432e-9199-47bcedd8f2f9",
  "provinsi_kode": "11",
  "kabupaten_kota_kode": "1101",
  "kecamatan_kode": "110101",
  "desa_kelurahan_kode": "1101012001",
  "koordinat": [
    {
      "latitude": 1.1,
      "longitude": 124.1,
      "urutan": 1
    },
    {
      "latitude": 1.2,
      "longitude": 124.1,
      "urutan": 2
    },
    {
      "latitude": 1.2,
      "longitude": 124.2,
      "urutan": 3
    },
    {
      "latitude": 1.1,
      "longitude": 124.2,
      "urutan": 4
    }
  ]
}
```

Catatan koordinat:

```txt
latitude  harus antara -90 sampai 90
longitude harus antara -180 sampai 180
urutan    optional; jika kosong backend mengisi sesuai urutan array
```

Response `201 Created`:

```json
{
  "status": "success",
  "message": "Data lahan berhasil dibuat",
  "data": {
    "id": "ccd178d6-77bd-4d12-819f-3bb1fe30ba4c",
    "kode": "LHN-001",
    "luas": 1.25,
    "elevasi": 325.5,
    "kepemilikan": "hak milik",
    "pemilik_id": "243b7917-8586-432e-9199-47bcedd8f2f9",
    "pemilik_nama": "Budi Santoso",
    "pemilik": {
      "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
      "nama": "Budi Santoso",
      "nik": "1234567890123456",
      "hp": "08123456789"
    },
    "foto_path": null,
    "foto_url": null,
    "provinsi_kode": "11",
    "kabupaten_kota_kode": "1101",
    "kecamatan_kode": "110101",
    "desa_kelurahan_kode": "1101012001",
    "provinsi": "ACEH",
    "kabupaten_kota": "KAB. ACEH SELATAN",
    "kecamatan": "Bakongan",
    "desa_kelurahan": "Keude Bakongan",
    "koordinat": [
      {
        "id": "ecde5b2b-0171-4fef-84b8-ce606872d9bd",
        "latitude": 1.1,
        "longitude": 124.1,
        "urutan": 1
      }
    ]
  }
}
```

Error umum:

```json
{
  "status": "error",
  "message": "Kode lahan sudah terdaftar",
  "data": null
}
```

```json
{
  "status": "error",
  "message": "Pemilik petani tidak ditemukan",
  "data": null
}
```

```json
{
  "status": "error",
  "message": "Kepemilikan harus salah satu dari: hak milik, sewa, pinjam",
  "data": null
}
```

### Update Lahan

```txt
PUT /lands/{id}
```

Payload boleh parsial. Contoh update luas:

```json
{
  "luas": 2.5
}
```

Contoh update elevasi:

```json
{
  "elevasi": 340
}
```

Contoh mengganti semua koordinat polygon:

```json
{
  "koordinat": [
    {
      "latitude": 1.11,
      "longitude": 124.11,
      "urutan": 1
    },
    {
      "latitude": 1.22,
      "longitude": 124.11,
      "urutan": 2
    },
    {
      "latitude": 1.22,
      "longitude": 124.22,
      "urutan": 3
    }
  ]
}
```

Catatan: saat field `koordinat` dikirim pada update, backend mengganti seluruh daftar koordinat lama dengan daftar baru.

Response `200 OK` sama seperti object lahan.

### Upload Foto Lahan

Foto lahan bersifat opsional. Buat data lahan dulu lewat `POST /lands`, lalu upload foto dengan endpoint ini.

```txt
POST /lands/{id}/foto
```

Content-Type:

```txt
multipart/form-data
```

Field form:

```txt
foto: File
```

Format file yang diterima:

```txt
image/jpeg
image/png
image/webp
```

Response `200 OK`:

```json
{
  "status": "success",
  "message": "Foto lahan berhasil diupload",
  "data": {
    "id": "ccd178d6-77bd-4d12-819f-3bb1fe30ba4c",
    "kode": "LHN-001",
    "foto_path": "uploads/lands/abc123.png",
    "foto_url": "/uploads/lands/abc123.png"
  }
}
```

### Hapus Foto Lahan

```txt
DELETE /lands/{id}/foto
```

Response `200 OK` sama seperti object lahan, dengan `foto_path` dan `foto_url` bernilai `null`.

### Hapus Lahan

```txt
DELETE /lands/{id}
```

Response `200 OK`:

```json
{
  "status": "success",
  "message": "Data lahan berhasil dihapus",
  "data": null
}
```

### Contoh Fetch Lahan

```js
async function createLand(payload) {
  const response = await fetch(`${API_BASE_URL}/lands`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || "Gagal menyimpan lahan");
  }

  return data.data;
}

async function uploadLandPhoto(landId, file) {
  const formData = new FormData();
  formData.append("foto", file);

  const response = await fetch(`${API_BASE_URL}/lands/${landId}/foto`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || "Gagal upload foto lahan");
  }

  return data.data;
}
```

### TypeScript Lahan

```ts
export type LandOwnership = "hak milik" | "sewa" | "pinjam";

export interface LandCoordinate {
  id?: string;
  latitude: number;
  longitude: number;
  urutan?: number | null;
}

export interface Land {
  id: string;
  kode: string;
  luas: number;
  elevasi: number | null;
  kepemilikan: LandOwnership;
  pemilik_id: string;
  pemilik_nama: string | null;
  pemilik: {
    id: string;
    nama: string;
    nik: string;
    hp: string | null;
  } | null;
  foto_path: string | null;
  foto_url: string | null;
  provinsi_kode: string | null;
  kabupaten_kota_kode: string | null;
  kecamatan_kode: string | null;
  desa_kelurahan_kode: string | null;
  provinsi: string | null;
  kabupaten_kota: string | null;
  kecamatan: string | null;
  desa_kelurahan: string | null;
  koordinat: LandCoordinate[];
}

export interface LandCreatePayload {
  kode: string;
  luas: number;
  elevasi?: number | null;
  kepemilikan: LandOwnership;
  pemilik_id: string;
  provinsi_kode?: string | null;
  kabupaten_kota_kode?: string | null;
  kecamatan_kode?: string | null;
  desa_kelurahan_kode?: string | null;
  koordinat?: Omit<LandCoordinate, "id">[];
}

export type LandUpdatePayload = Partial<LandCreatePayload>;
```

## Produksi Tanam

Modul produksi tanam menyimpan proses budidaya/tanam nilam dari rencana sampai selesai. Relasi `petani_id` wajib, sedangkan `lahan_id` opsional.

Nilai `status` yang valid:

```txt
rencana
berjalan
selesai
```

### Object Produksi Tanam

```json
{
  "id": "0dd9c084-4253-46d9-8660-6fa87736b8f2",
  "kode": "PT-001",
  "tanggal_mulai": "2026-05-18",
  "tanggal_akhir": "2026-08-18",
  "aktual_tanggal_akhir": null,
  "luas_garapan": 1.5,
  "jarak_tanam": "30x30 cm",
  "jumlah_batang": 1200,
  "hasil_produksi_basah": 1000,
  "aktual_hasil_produksi_basah": 900,
  "aktual_hasil_produksi_kering": 180,
  "varietas_bibit": "Nilam Aceh",
  "sumber_bibit": null,
  "cara_tanam": null,
  "perawatan": null,
  "pupuk": null,
  "musim_tanam": null,
  "status": "berjalan",
  "petani_id": "243b7917-8586-432e-9199-47bcedd8f2f9",
  "lahan_id": "ccd178d6-77bd-4d12-819f-3bb1fe30ba4c",
  "rasio_berat_kering_ke_basah": 0.2,
  "rasio_luas_garapan_ke_hasil_kering": 120,
  "user_update_id": null,
  "petani": {
    "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
    "nama": "Budi Santoso",
    "nik": "1234567890123456",
    "hp": "08123456789"
  },
  "lahan": {
    "id": "ccd178d6-77bd-4d12-819f-3bb1fe30ba4c",
    "kode": "LHN-001",
    "luas": 1.25,
    "elevasi": 325.5
  },
  "user_update": null
}
```

Field:

```txt
kode                              required, unique, max 50
tanggal_mulai                     required, format YYYY-MM-DD
tanggal_akhir                     optional, format YYYY-MM-DD
aktual_tanggal_akhir              optional, format YYYY-MM-DD
luas_garapan                      required, angka > 0
jarak_tanam                       optional
jumlah_batang                     optional, angka >= 0
hasil_produksi_basah              optional, angka >= 0
aktual_hasil_produksi_basah       optional, angka >= 0
aktual_hasil_produksi_kering      optional, angka >= 0
varietas_bibit                    optional
sumber_bibit                      optional
cara_tanam                        optional
perawatan                         optional
pupuk                             optional
musim_tanam                       optional
status                            required, rencana | berjalan | selesai
petani_id                         required, UUID petani
lahan_id                          optional, UUID lahan
rasio_berat_kering_ke_basah       dihitung backend
rasio_luas_garapan_ke_hasil_kering dihitung backend
user_update_id                    optional, UUID user
```

Catatan rasio:

```txt
rasio_berat_kering_ke_basah = aktual_hasil_produksi_kering / aktual_hasil_produksi_basah

rasio_luas_garapan_ke_hasil_kering = aktual_hasil_produksi_kering / luas_garapan
```

Saat `status` diubah menjadi `selesai`, backend memvalidasi gabungan data payload dan data yang sudah tersimpan. Field berikut wajib sudah terisi:

```txt
aktual_tanggal_akhir
aktual_hasil_produksi_basah
aktual_hasil_produksi_kering
luas_garapan
```

### List Produksi Tanam

```txt
GET /planting-productions
GET /planting-productions?search=PT
GET /planting-productions?status=berjalan
GET /planting-productions?petani_id=243b7917-8586-432e-9199-47bcedd8f2f9
GET /planting-productions?lahan_id=ccd178d6-77bd-4d12-819f-3bb1fe30ba4c
GET /planting-productions?kabupaten_kota_kode=1101
GET /planting-productions?kecamatan_kode=110101
```

Gunakan `kabupaten_kota_kode` atau `kecamatan_kode` untuk mengambil produksi tanam berdasarkan wilayah petani.

Response `200 OK`:

```json
{
  "status": "success",
  "message": "Data produksi tanam berhasil diambil",
  "data": []
}
```

### Detail Produksi Tanam

```txt
GET /planting-productions/{id}
```

Response `200 OK` sama seperti object produksi tanam.

Jika tidak ditemukan:

```json
{
  "status": "error",
  "message": "Produksi tanam tidak ditemukan",
  "data": null
}
```

### Buat Produksi Tanam

```txt
POST /planting-productions
```

Payload minimal:

```json
{
  "kode": "PT-001",
  "tanggal_mulai": "2026-05-18",
  "luas_garapan": 1.5,
  "status": "rencana",
  "petani_id": "243b7917-8586-432e-9199-47bcedd8f2f9"
}
```

Payload lengkap:

```json
{
  "kode": "PT-001",
  "tanggal_mulai": "2026-05-18",
  "tanggal_akhir": "2026-08-18",
  "aktual_tanggal_akhir": null,
  "luas_garapan": 1.5,
  "jarak_tanam": "30x30 cm",
  "jumlah_batang": 1200,
  "hasil_produksi_basah": 1000,
  "aktual_hasil_produksi_basah": 900,
  "aktual_hasil_produksi_kering": 180,
  "varietas_bibit": "Nilam Aceh",
  "sumber_bibit": "Pembibitan internal",
  "cara_tanam": "Stek",
  "perawatan": "Penyiraman rutin",
  "pupuk": "Kompos",
  "musim_tanam": "Musim hujan",
  "status": "berjalan",
  "petani_id": "243b7917-8586-432e-9199-47bcedd8f2f9",
  "lahan_id": "ccd178d6-77bd-4d12-819f-3bb1fe30ba4c",
  "user_update_id": null
}
```

Response `201 Created` sama seperti object produksi tanam.

Error umum:

```json
{
  "status": "error",
  "message": "Kode produksi tanam sudah terdaftar",
  "data": null
}
```

```json
{
  "status": "error",
  "message": "Status harus salah satu dari: rencana, berjalan, selesai",
  "data": null
}
```

```json
{
  "status": "error",
  "message": "Lahan tidak sesuai petani",
  "data": null
}
```

### Update Produksi Tanam

```txt
PUT /planting-productions/{id}
```

Payload boleh parsial. Contoh ubah status dan tanggal aktual selesai:

```json
{
  "status": "selesai",
  "aktual_tanggal_akhir": "2026-08-20"
}
```

Contoh input hasil akhir:

```json
{
  "aktual_hasil_produksi_basah": 900,
  "aktual_hasil_produksi_kering": 180
}
```

Response `200 OK` sama seperti object produksi tanam. Rasio akan dihitung ulang oleh backend.

### Hapus Produksi Tanam

```txt
DELETE /planting-productions/{id}
```

Response `200 OK`:

```json
{
  "status": "success",
  "message": "Data produksi tanam berhasil dihapus",
  "data": null
}
```

### TypeScript Produksi Tanam

```ts
export type PlantingProductionStatus = "rencana" | "berjalan" | "selesai";

export interface PlantingProduction {
  id: string;
  kode: string;
  tanggal_mulai: string;
  tanggal_akhir: string | null;
  aktual_tanggal_akhir: string | null;
  luas_garapan: number;
  jarak_tanam: string | null;
  jumlah_batang: number | null;
  hasil_produksi_basah: number | null;
  aktual_hasil_produksi_basah: number | null;
  aktual_hasil_produksi_kering: number | null;
  varietas_bibit: string | null;
  sumber_bibit: string | null;
  cara_tanam: string | null;
  perawatan: string | null;
  pupuk: string | null;
  musim_tanam: string | null;
  status: PlantingProductionStatus;
  petani_id: string;
  lahan_id: string | null;
  rasio_berat_kering_ke_basah: number | null;
  rasio_luas_garapan_ke_hasil_kering: number | null;
  user_update_id: string | null;
  petani: {
    id: string;
    nama: string;
    nik: string;
    hp: string | null;
  } | null;
  lahan: {
    id: string;
    kode: string;
    luas: number;
    elevasi: number | null;
  } | null;
  user_update: {
    id: string;
    name: string | null;
    email: string | null;
  } | null;
}

export interface PlantingProductionCreatePayload {
  kode: string;
  tanggal_mulai: string;
  tanggal_akhir?: string | null;
  aktual_tanggal_akhir?: string | null;
  luas_garapan: number;
  jarak_tanam?: string | null;
  jumlah_batang?: number | null;
  hasil_produksi_basah?: number | null;
  aktual_hasil_produksi_basah?: number | null;
  aktual_hasil_produksi_kering?: number | null;
  varietas_bibit?: string | null;
  sumber_bibit?: string | null;
  cara_tanam?: string | null;
  perawatan?: string | null;
  pupuk?: string | null;
  musim_tanam?: string | null;
  status: PlantingProductionStatus;
  petani_id: string;
  lahan_id?: string | null;
  user_update_id?: string | null;
}

export type PlantingProductionUpdatePayload = Partial<PlantingProductionCreatePayload>;
```

## Produksi Minyak

Modul produksi minyak menyimpan proses penyulingan dari bahan kering menjadi minyak nilam. Relasi `petani_id` wajib, sedangkan `lahan_id` opsional.

Nilai `status` yang valid:

```txt
rencana
berjalan
selesai
```

### Object Produksi Minyak

```json
{
  "id": "b4e8fa3e-4abd-4e04-9f9c-5c71ef6c8801",
  "kode": "OM-001",
  "tanggal_mulai": "2026-05-18",
  "tanggal_akhir": "2026-05-20",
  "aktual_tanggal_akhir": "2026-05-20",
  "berat_kering_bahan": 1000,
  "hasil_minyak": 24,
  "aktual_hasil_minyak": 25,
  "redaman": 0.025,
  "petani_id": "243b7917-8586-432e-9199-47bcedd8f2f9",
  "lahan_id": "ccd178d6-77bd-4d12-819f-3bb1fe30ba4c",
  "status": "selesai",
  "user_update_id": null,
  "petani": {
    "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
    "nama": "Budi Santoso",
    "nik": "1234567890123456",
    "hp": "08123456789"
  },
  "lahan": {
    "id": "ccd178d6-77bd-4d12-819f-3bb1fe30ba4c",
    "kode": "LHN-001",
    "luas": 1.25,
    "elevasi": 325.5
  },
  "user_update": null
}
```

Field:

```txt
kode                  required, unique, max 50
tanggal_mulai         required, format YYYY-MM-DD
tanggal_akhir         optional, format YYYY-MM-DD
aktual_tanggal_akhir  optional, format YYYY-MM-DD
berat_kering_bahan    optional, angka >= 0
hasil_minyak          optional, angka >= 0
aktual_hasil_minyak   optional, angka >= 0
redaman               dihitung backend
petani_id             required, UUID petani
lahan_id              optional, UUID lahan
status                required, rencana | berjalan | selesai
user_update_id        optional, UUID user
```

Catatan redaman:

```txt
redaman = aktual_hasil_minyak / berat_kering_bahan
```

Saat `status` diubah menjadi `selesai`, backend memvalidasi gabungan data payload dan data yang sudah tersimpan. Field berikut wajib sudah terisi:

```txt
aktual_tanggal_akhir
berat_kering_bahan
aktual_hasil_minyak
```

### List Produksi Minyak

```txt
GET /oil-productions
GET /oil-productions?search=OM
GET /oil-productions?status=selesai
GET /oil-productions?petani_id=243b7917-8586-432e-9199-47bcedd8f2f9
GET /oil-productions?lahan_id=ccd178d6-77bd-4d12-819f-3bb1fe30ba4c
GET /oil-productions?kabupaten_kota_kode=1101
GET /oil-productions?kecamatan_kode=110101
```

Response `200 OK`:

```json
{
  "status": "success",
  "message": "Data produksi minyak berhasil diambil",
  "data": []
}
```

### Detail Produksi Minyak

```txt
GET /oil-productions/{id}
```

Response `200 OK` sama seperti object produksi minyak.

Jika tidak ditemukan:

```json
{
  "status": "error",
  "message": "Produksi minyak tidak ditemukan",
  "data": null
}
```

### Buat Produksi Minyak

```txt
POST /oil-productions
```

Payload minimal:

```json
{
  "kode": "OM-001",
  "tanggal_mulai": "2026-05-18",
  "status": "rencana",
  "petani_id": "243b7917-8586-432e-9199-47bcedd8f2f9"
}
```

Payload lengkap:

```json
{
  "kode": "OM-001",
  "tanggal_mulai": "2026-05-18",
  "tanggal_akhir": "2026-05-20",
  "aktual_tanggal_akhir": "2026-05-20",
  "berat_kering_bahan": 1000,
  "hasil_minyak": 24,
  "aktual_hasil_minyak": 25,
  "petani_id": "243b7917-8586-432e-9199-47bcedd8f2f9",
  "lahan_id": "ccd178d6-77bd-4d12-819f-3bb1fe30ba4c",
  "status": "selesai",
  "user_update_id": null
}
```

Response `201 Created` sama seperti object produksi minyak.

Error umum:

```json
{
  "status": "error",
  "message": "Kode produksi minyak sudah terdaftar",
  "data": null
}
```

```json
{
  "status": "error",
  "message": "Status selesai membutuhkan data: Aktual tanggal akhir, Aktual hasil minyak",
  "data": null
}
```

### Update Produksi Minyak

```txt
PUT /oil-productions/{id}
```

Payload boleh parsial. Contoh selesai produksi:

```json
{
  "status": "selesai",
  "aktual_tanggal_akhir": "2026-05-20",
  "berat_kering_bahan": 1000,
  "aktual_hasil_minyak": 25
}
```

Response `200 OK` sama seperti object produksi minyak. `redaman` akan dihitung ulang oleh backend.

### Hapus Produksi Minyak

```txt
DELETE /oil-productions/{id}
```

Response `200 OK`:

```json
{
  "status": "success",
  "message": "Data produksi minyak berhasil dihapus",
  "data": null
}
```

### TypeScript Produksi Minyak

```ts
export type OilProductionStatus = "rencana" | "berjalan" | "selesai";

export interface OilProduction {
  id: string;
  kode: string;
  tanggal_mulai: string;
  tanggal_akhir: string | null;
  aktual_tanggal_akhir: string | null;
  berat_kering_bahan: number | null;
  hasil_minyak: number | null;
  aktual_hasil_minyak: number | null;
  redaman: number | null;
  petani_id: string;
  lahan_id: string | null;
  status: OilProductionStatus;
  user_update_id: string | null;
  petani: {
    id: string;
    nama: string;
    nik: string;
    hp: string | null;
  } | null;
  lahan: {
    id: string;
    kode: string;
    luas: number;
    elevasi: number | null;
  } | null;
  user_update: {
    id: string;
    name: string | null;
    email: string | null;
  } | null;
}

export interface OilProductionCreatePayload {
  kode: string;
  tanggal_mulai: string;
  tanggal_akhir?: string | null;
  aktual_tanggal_akhir?: string | null;
  berat_kering_bahan?: number | null;
  hasil_minyak?: number | null;
  aktual_hasil_minyak?: number | null;
  petani_id: string;
  lahan_id?: string | null;
  status: OilProductionStatus;
  user_update_id?: string | null;
}

export type OilProductionUpdatePayload = Partial<OilProductionCreatePayload>;
```

## Catatan Produksi

Catatan produksi tersedia untuk produksi tanam dan produksi minyak. Field `kode_produksi` berisi UUID produksi terkait.

### Object Catatan Produksi

```json
{
  "id": "f1ab774f-710a-456d-9f7d-917163c80a37",
  "kode_produksi": "0dd9c084-4253-46d9-8660-6fa87736b8f2",
  "tanggal": "2026-05-19",
  "catatan": "Tanam selesai di blok A",
  "user_update_id": null,
  "user_update": null
}
```

Field:

```txt
kode_produksi   required, UUID produksi terkait
tanggal         required, format YYYY-MM-DD
catatan         required
user_update_id  optional, UUID user
```

### Catatan Produksi Tanam

```txt
GET    /planting-production-notes
GET    /planting-production-notes?kode_produksi={planting_production_uuid}
GET    /planting-production-notes/{id}
POST   /planting-production-notes
PUT    /planting-production-notes/{id}
DELETE /planting-production-notes/{id}
```

Payload create:

```json
{
  "kode_produksi": "0dd9c084-4253-46d9-8660-6fa87736b8f2",
  "tanggal": "2026-05-19",
  "catatan": "Tanam selesai di blok A",
  "user_update_id": null
}
```

Response `201 Created`:

```json
{
  "status": "success",
  "message": "Data catatan produksi tanam berhasil dibuat",
  "data": {
    "id": "f1ab774f-710a-456d-9f7d-917163c80a37",
    "kode_produksi": "0dd9c084-4253-46d9-8660-6fa87736b8f2",
    "tanggal": "2026-05-19",
    "catatan": "Tanam selesai di blok A",
    "user_update_id": null,
    "user_update": null
  }
}
```

Payload update boleh parsial:

```json
{
  "catatan": "Tanam selesai dan mulai monitoring pertumbuhan"
}
```

### Catatan Produksi Minyak

```txt
GET    /oil-production-notes
GET    /oil-production-notes?kode_produksi={oil_production_uuid}
GET    /oil-production-notes/{id}
POST   /oil-production-notes
PUT    /oil-production-notes/{id}
DELETE /oil-production-notes/{id}
```

Payload create:

```json
{
  "kode_produksi": "b4e8fa3e-4abd-4e04-9f9c-5c71ef6c8801",
  "tanggal": "2026-05-20",
  "catatan": "Penyulingan batch pertama",
  "user_update_id": null
}
```

Response `201 Created`:

```json
{
  "status": "success",
  "message": "Data catatan produksi minyak berhasil dibuat",
  "data": {
    "id": "84252656-4135-4ab7-a9e7-f4488996698a",
    "kode_produksi": "b4e8fa3e-4abd-4e04-9f9c-5c71ef6c8801",
    "tanggal": "2026-05-20",
    "catatan": "Penyulingan batch pertama",
    "user_update_id": null,
    "user_update": null
  }
}
```

### TypeScript Catatan Produksi

```ts
export interface ProductionNote {
  id: string;
  kode_produksi: string;
  tanggal: string;
  catatan: string;
  user_update_id: string | null;
  user_update: {
    id: string;
    name: string | null;
    email: string | null;
  } | null;
}

export interface ProductionNoteCreatePayload {
  kode_produksi: string;
  tanggal: string;
  catatan: string;
  user_update_id?: string | null;
}

export type ProductionNoteUpdatePayload = Partial<ProductionNoteCreatePayload>;
```

## Pembiayaan

Modul pembiayaan terdiri dari master produk pembiayaan dan transaksi pembiayaan. Transaksi bisa dihubungkan ke petani, produksi tanam, atau produksi minyak sehingga frontend dapat menghitung biaya dan keuntungan bersih per periode produksi.

### Produk Pembiayaan

Endpoint:

```txt
GET    /financing-products
GET    /financing-products?search=pupuk
GET    /financing-products/{id}
POST   /financing-products
PUT    /financing-products/{id}
DELETE /financing-products/{id}
```

Payload create:

```json
{
  "nama": "Pupuk Organik",
  "harga": 25000,
  "satuan": "kg",
  "deskripsi": "Biaya pupuk organik"
}
```

Response:

```json
{
  "status": "success",
  "message": "Data produk pembiayaan berhasil dibuat",
  "data": {
    "id": "7c0b606e-69cc-4070-8d54-48855f5c0223",
    "nama": "Pupuk Organik",
    "harga": 25000,
    "satuan": "kg",
    "deskripsi": "Biaya pupuk organik"
  }
}
```

Field produk pembiayaan:

```txt
nama        required
harga       required, angka >= 0
satuan      required
deskripsi   optional
```

Produk pembiayaan yang sudah digunakan transaksi tidak bisa dihapus.

### Object Pembiayaan

```json
{
  "id": "823cf9c7-3e99-448f-bc4d-5e0d4c2dbbe7",
  "nama": "Pembelian pupuk awal",
  "tanggal": "2026-05-19",
  "deskripsi": "Pupuk untuk masa tanam awal",
  "produk_id": "7c0b606e-69cc-4070-8d54-48855f5c0223",
  "harga": 25000,
  "quantity": 4,
  "petani_id": "243b7917-8586-432e-9199-47bcedd8f2f9",
  "planting_production_id": "0dd9c084-4253-46d9-8660-6fa87736b8f2",
  "oil_production_id": null,
  "sub_total": 100000,
  "user_update_id": null,
  "produk": {
    "id": "7c0b606e-69cc-4070-8d54-48855f5c0223",
    "nama": "Pupuk Organik",
    "harga": 25000,
    "satuan": "kg",
    "deskripsi": "Biaya pupuk organik"
  },
  "petani": {
    "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
    "nama": "Budi Santoso",
    "nik": "1234567890123456",
    "hp": "08123456789"
  },
  "planting_production": {
    "id": "0dd9c084-4253-46d9-8660-6fa87736b8f2",
    "kode": "PT-001"
  },
  "oil_production": null,
  "user_update": null
}
```

Field:

```txt
nama                    required
tanggal                 required, format YYYY-MM-DD
deskripsi               optional
produk_id               required, UUID financing_products
harga                   required, angka >= 0
quantity                required, angka > 0
petani_id               required, UUID petani
planting_production_id  optional, UUID produksi tanam
oil_production_id       optional, UUID produksi minyak
partner_id              optional, UUID partner
paid_by                 optional, nama pihak pembayar
sub_total               dihitung backend = harga * quantity
user_update_id          optional, UUID user
```

### List Pembiayaan

```txt
GET /financings
GET /financings?search=pupuk
GET /financings?petani_id=243b7917-8586-432e-9199-47bcedd8f2f9
GET /financings?partner_id=8f34c2cf-9804-4de1-9dd3-37609073a052
GET /financings?produk_id=7c0b606e-69cc-4070-8d54-48855f5c0223
GET /financings?planting_production_id=0dd9c084-4253-46d9-8660-6fa87736b8f2
GET /financings?oil_production_id=b4e8fa3e-4abd-4e04-9f9c-5c71ef6c8801
GET /financings?tanggal_mulai=2026-05-01&tanggal_akhir=2026-05-31
```

Response `200 OK`:

```json
{
  "status": "success",
  "message": "Data pembiayaan berhasil diambil",
  "data": {
    "items": [],
    "total_sub_total": 0
  }
}
```

Gunakan `total_sub_total` sebagai total biaya dari filter yang sedang aktif.

### Buat Pembiayaan

```txt
POST /financings
```

Payload:

```json
{
  "nama": "Pembelian pupuk awal",
  "tanggal": "2026-05-19",
  "deskripsi": "Pupuk untuk masa tanam awal",
  "produk_id": "7c0b606e-69cc-4070-8d54-48855f5c0223",
  "harga": 25000,
  "quantity": 4,
  "petani_id": "243b7917-8586-432e-9199-47bcedd8f2f9",
  "partner_id": "8f34c2cf-9804-4de1-9dd3-37609073a052",
  "planting_production_id": "0dd9c084-4253-46d9-8660-6fa87736b8f2",
  "oil_production_id": null,
  "paid_by": "Koperasi Mitra",
  "user_update_id": null
}
```

Response `201 Created` sama seperti object pembiayaan.

Catatan validasi:

```txt
Jika planting_production_id diisi, produksi tanam harus milik petani yang sama.
Jika oil_production_id diisi, produksi minyak harus milik petani yang sama.
sub_total selalu dihitung backend.
Jika partner_id tidak diisi dan paid_by tidak diisi, backend otomatis mengisi paid_by = "Pembiayaan Sendiri".
```

### Update Pembiayaan

```txt
PUT /financings/{id}
```

Payload boleh parsial. Contoh:

```json
{
  "harga": 30000,
  "quantity": 5
}
```

Response `200 OK` sama seperti object pembiayaan, dengan `sub_total` dihitung ulang.

### Hapus Pembiayaan

```txt
DELETE /financings/{id}
```

Response:

```json
{
  "status": "success",
  "message": "Data pembiayaan berhasil dihapus",
  "data": null
}
```

### TypeScript Pembiayaan

```ts
export interface FinancingProduct {
  id: string;
  nama: string;
  harga: number;
  satuan: string;
  deskripsi: string | null;
}

export interface Financing {
  id: string;
  nama: string;
  tanggal: string;
  deskripsi: string | null;
  produk_id: string;
  harga: number;
  quantity: number;
  petani_id: string;
  partner_id: string | null;
  planting_production_id: string | null;
  oil_production_id: string | null;
  paid_by: string | null;
  sub_total: number;
  user_update_id: string | null;
  produk: FinancingProduct | null;
  petani: {
    id: string;
    nama: string;
    nik: string;
    hp: string | null;
  } | null;
  partner: {
    id: string;
    nama: string;
    pic: string | null;
  } | null;
  planting_production: {
    id: string;
    kode: string;
  } | null;
  oil_production: {
    id: string;
    kode: string;
  } | null;
  user_update: {
    id: string;
    name: string | null;
    email: string | null;
  } | null;
}

export interface FinancingCreatePayload {
  nama: string;
  tanggal: string;
  deskripsi?: string | null;
  produk_id: string;
  harga: number;
  quantity: number;
  petani_id: string;
  partner_id?: string | null;
  planting_production_id?: string | null;
  oil_production_id?: string | null;
  paid_by?: string | null;
  user_update_id?: string | null;
}

export type FinancingUpdatePayload = Partial<FinancingCreatePayload>;
```

## Penjualan

### Produk Penjualan

```txt
GET    /sales-products
GET    /sales-products?search=daun
GET    /sales-products?jenis=barang
GET    /sales-products?jenis=jasa
GET    /sales-products/{id}
POST   /sales-products
PUT    /sales-products/{id}
DELETE /sales-products/{id}
```

Field produk penjualan:

```txt
nama        required
jenis       required, pilihan: jasa | barang
harga       required, angka >= 0
satuan      required
deskripsi   optional
```

Contoh payload POST /sales-products:

```json
{
  "nama": "Jasa Pengeringan",
  "jenis": "jasa",
  "harga": 15000,
  "satuan": "kg",
  "deskripsi": "Biaya jasa pengeringan daun nilam"
}
```

### Transaksi Penjualan

```txt
GET /sales
GET /sales?search=panen
GET /sales?penjual_id=243b7917-8586-432e-9199-47bcedd8f2f9
GET /sales?pembeli_id=8f34c2cf-9804-4de1-9dd3-37609073a052
GET /sales?produk_penjualan_id=7c0b606e-69cc-4070-8d54-48855f5c0223
GET /sales?tanggal_mulai=2026-05-01&tanggal_akhir=2026-05-31
GET /sales/{id}
POST /sales
PUT /sales/{id}
DELETE /sales/{id}
```

Field transaksi:

```txt
nama                 required
tanggal              required, format YYYY-MM-DD
deskripsi            optional
produk_penjualan_id  required, UUID sales_products
quantity             required, angka > 0
harga                required, angka >= 0
penjual_id           required, UUID petani
pembeli_id           required, UUID partner
sub_total            dihitung backend = harga * quantity
```

Contoh payload POST /sales:

```json
{
  "nama": "Penjualan panen Mei",
  "tanggal": "2026-05-20",
  "deskripsi": "Penjualan daun nilam kering",
  "produk_penjualan_id": "7c0b606e-69cc-4070-8d54-48855f5c0223",
  "quantity": 120,
  "harga": 55000,
  "penjual_id": "243b7917-8586-432e-9199-47bcedd8f2f9",
  "pembeli_id": "8f34c2cf-9804-4de1-9dd3-37609073a052"
}
```

### TypeScript Penjualan

```ts
export interface SalesProduct {
  id: string;
  nama: string;
  jenis: "jasa" | "barang";
  harga: number;
  satuan: string;
  deskripsi: string | null;
}

export interface Sale {
  id: string;
  nama: string;
  tanggal: string;
  deskripsi: string | null;
  produk_penjualan_id: string;
  quantity: number;
  harga: number;
  penjual_id: string;
  pembeli_id: string;
  sub_total: number;
  produk_penjualan: SalesProduct | null;
  penjual: {
    id: string;
    nama: string;
    nik: string;
    hp: string | null;
  } | null;
  pembeli: {
    id: string;
    nama: string;
    pic: string | null;
    hp: string | null;
    email: string | null;
  } | null;
}

export interface SaleCreatePayload {
  nama: string;
  tanggal: string;
  deskripsi?: string | null;
  produk_penjualan_id: string;
  quantity: number;
  harga: number;
  penjual_id: string;
  pembeli_id: string;
}

export type SaleUpdatePayload = Partial<SaleCreatePayload>;
```

## Dashboard

Endpoint dashboard menyediakan data agregat untuk grafik dan tabel performa. Semua response tetap memakai wrapper standar:

```json
{
  "status": "success",
  "message": "Pesan response",
  "data": []
}
```

Filter umum:

```txt
tanggal_mulai  optional, format YYYY-MM-DD
tanggal_akhir  optional, format YYYY-MM-DD
petani_id      optional, UUID petani untuk endpoint yang mendukung filter petani
status         optional, untuk endpoint produksi: rencana | berjalan | selesai
```

Contoh pemakaian filter tanggal:

```txt
GET /dashboard/sales/monthly?tanggal_mulai=2026-01-01&tanggal_akhir=2026-12-31
```

Catatan perhitungan:

```txt
total_penjualan  = sum sales.sub_total
total_expense    = sum financings.sub_total
net_profit       = total_penjualan - total_expense
bulan            = format YYYY-MM
```

### Report Penjualan Bulan ke Bulan

```txt
GET /dashboard/sales/monthly
GET /dashboard/sales/monthly?tanggal_mulai=2026-01-01&tanggal_akhir=2026-12-31
GET /dashboard/sales/monthly?petani_id=243b7917-8586-432e-9199-47bcedd8f2f9
```

Response `data`:

```json
[
  {
    "bulan": "2026-05",
    "tahun": 2026,
    "bulan_ke": 5,
    "total_penjualan": 6600000,
    "jumlah_transaksi": 3
  }
]
```

### Report Expense Bulan ke Bulan

```txt
GET /dashboard/expenses/monthly
GET /dashboard/expenses/monthly?tanggal_mulai=2026-01-01&tanggal_akhir=2026-12-31
GET /dashboard/expenses/monthly?petani_id=243b7917-8586-432e-9199-47bcedd8f2f9
```

Response `data`:

```json
[
  {
    "bulan": "2026-05",
    "tahun": 2026,
    "bulan_ke": 5,
    "total_expense": 1200000,
    "jumlah_transaksi": 4
  }
]
```

### Report Produksi Tanam Bulan ke Bulan

```txt
GET /dashboard/planting-productions/monthly
GET /dashboard/planting-productions/monthly?status=selesai
GET /dashboard/planting-productions/monthly?petani_id=243b7917-8586-432e-9199-47bcedd8f2f9
```

Agregasi memakai `tanggal_mulai` produksi tanam.

Response `data`:

```json
[
  {
    "bulan": "2026-05",
    "tahun": 2026,
    "bulan_ke": 5,
    "jumlah_produksi": 2,
    "total_luas_garapan": 2.5,
    "total_jumlah_batang": 12000,
    "total_rencana_hasil_basah": 1500,
    "total_aktual_hasil_basah": 1450,
    "total_aktual_hasil_kering": 420
  }
]
```

### Report Produksi Minyak Bulan ke Bulan

```txt
GET /dashboard/oil-productions/monthly
GET /dashboard/oil-productions/monthly?status=selesai
GET /dashboard/oil-productions/monthly?petani_id=243b7917-8586-432e-9199-47bcedd8f2f9
```

Agregasi memakai `tanggal_mulai` produksi minyak.

Response `data`:

```json
[
  {
    "bulan": "2026-05",
    "tahun": 2026,
    "bulan_ke": 5,
    "jumlah_produksi": 2,
    "total_berat_kering_bahan": 1000,
    "total_rencana_hasil_minyak": 24,
    "total_aktual_hasil_minyak": 25,
    "redaman_rata_rata": 0.025
  }
]
```

### Total Penjualan Berdasarkan Petani

```txt
GET /dashboard/sales/by-farmer
GET /dashboard/sales/by-farmer?tanggal_mulai=2026-01-01&tanggal_akhir=2026-12-31
```

Response `data`:

```json
[
  {
    "petani": {
      "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
      "nama": "Budi Santoso",
      "nik": "1234567890123456",
      "hp": "08123456789"
    },
    "total_penjualan": 6600000,
    "jumlah_transaksi": 3
  }
]
```

### Total Penjualan Berdasarkan Kabupaten Petani

```txt
GET /dashboard/sales/by-farmer-regency
GET /dashboard/sales/by-farmer-regency?tanggal_mulai=2026-01-01&tanggal_akhir=2026-12-31
```

Endpoint ini cocok untuk pie chart distribusi penjualan berdasarkan `kabupaten_kota_kode` dari data petani penjual. Field `persentase` dihitung dari total penjualan seluruh kabupaten pada filter yang sama.

Response `data`:

```json
[
  {
    "kabupaten_kota_kode": "7171",
    "kabupaten_kota": "KOTA MANADO",
    "total_penjualan": 6600000,
    "jumlah_transaksi": 3,
    "jumlah_petani": 2,
    "persentase": 62.5
  }
]
```

### Penjualan Bulan ke Bulan Berdasarkan Petani

```txt
GET /dashboard/sales/monthly-by-farmer
GET /dashboard/sales/monthly-by-farmer?petani_id=243b7917-8586-432e-9199-47bcedd8f2f9
GET /dashboard/sales/monthly-by-farmer?tanggal_mulai=2026-01-01&tanggal_akhir=2026-12-31
```

Response `data`:

```json
[
  {
    "bulan": "2026-05",
    "tahun": 2026,
    "bulan_ke": 5,
    "petani": {
      "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
      "nama": "Budi Santoso",
      "nik": "1234567890123456",
      "hp": "08123456789"
    },
    "total_penjualan": 6600000,
    "jumlah_transaksi": 3
  }
]
```

### Expense Bulan ke Bulan Berdasarkan Petani

```txt
GET /dashboard/expenses/monthly-by-farmer
GET /dashboard/expenses/monthly-by-farmer?petani_id=243b7917-8586-432e-9199-47bcedd8f2f9
GET /dashboard/expenses/monthly-by-farmer?tanggal_mulai=2026-01-01&tanggal_akhir=2026-12-31
```

Response `data`:

```json
[
  {
    "bulan": "2026-05",
    "tahun": 2026,
    "bulan_ke": 5,
    "petani": {
      "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
      "nama": "Budi Santoso",
      "nik": "1234567890123456",
      "hp": "08123456789"
    },
    "total_expense": 1200000,
    "jumlah_transaksi": 4
  }
]
```

### Penjualan vs Expense Bulan ke Bulan

```txt
GET /dashboard/sales-vs-expenses/monthly
GET /dashboard/sales-vs-expenses/monthly?petani_id=243b7917-8586-432e-9199-47bcedd8f2f9
GET /dashboard/sales-vs-expenses/monthly?tanggal_mulai=2026-01-01&tanggal_akhir=2026-12-31
```

Response `data`:

```json
[
  {
    "bulan": "2026-05",
    "tahun": 2026,
    "bulan_ke": 5,
    "total_penjualan": 6600000,
    "total_expense": 1200000,
    "net_profit": 5400000
  }
]
```

### Penjualan vs Expense Berdasarkan Petani

```txt
GET /dashboard/sales-vs-expenses/by-farmer
GET /dashboard/sales-vs-expenses/by-farmer?tanggal_mulai=2026-01-01&tanggal_akhir=2026-12-31
```

Response `data`:

```json
[
  {
    "petani": {
      "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
      "nama": "Budi Santoso",
      "nik": "1234567890123456",
      "hp": "08123456789"
    },
    "total_penjualan": 6600000,
    "total_expense": 1200000,
    "net_profit": 5400000
  }
]
```

### Net Profit Performance Petani

```txt
GET /dashboard/farmer-net-profit
GET /dashboard/farmer-net-profit?tanggal_mulai=2026-01-01&tanggal_akhir=2026-12-31
```

Endpoint ini mengembalikan format yang sama dengan `/dashboard/sales-vs-expenses/by-farmer`, diurutkan dari `net_profit` terbesar ke terkecil.

Response `data`:

```json
[
  {
    "petani": {
      "id": "243b7917-8586-432e-9199-47bcedd8f2f9",
      "nama": "Budi Santoso",
      "nik": "1234567890123456",
      "hp": "08123456789"
    },
    "total_penjualan": 6600000,
    "total_expense": 1200000,
    "net_profit": 5400000
  }
]
```

### TypeScript Dashboard

```ts
export interface DashboardFarmer {
  id: string;
  nama: string;
  nik: string;
  hp: string | null;
}

export interface MonthlySalesReport {
  bulan: string;
  tahun: number;
  bulan_ke: number;
  total_penjualan: number;
  jumlah_transaksi: number;
}

export interface MonthlyExpenseReport {
  bulan: string;
  tahun: number;
  bulan_ke: number;
  total_expense: number;
  jumlah_transaksi: number;
}

export interface MonthlyPlantingProductionReport {
  bulan: string;
  tahun: number;
  bulan_ke: number;
  jumlah_produksi: number;
  total_luas_garapan: number;
  total_jumlah_batang: number;
  total_rencana_hasil_basah: number;
  total_aktual_hasil_basah: number;
  total_aktual_hasil_kering: number;
}

export interface MonthlyOilProductionReport {
  bulan: string;
  tahun: number;
  bulan_ke: number;
  jumlah_produksi: number;
  total_berat_kering_bahan: number;
  total_rencana_hasil_minyak: number;
  total_aktual_hasil_minyak: number;
  redaman_rata_rata: number | null;
}

export interface FarmerSalesReport {
  petani: DashboardFarmer | null;
  total_penjualan: number;
  jumlah_transaksi: number;
}

export interface RegencySalesReport {
  kabupaten_kota_kode: string;
  kabupaten_kota: string | null;
  total_penjualan: number;
  jumlah_transaksi: number;
  jumlah_petani: number;
  persentase: number;
}

export interface MonthlyFarmerSalesReport extends MonthlySalesReport {
  petani: DashboardFarmer | null;
}

export interface MonthlyFarmerExpenseReport extends MonthlyExpenseReport {
  petani: DashboardFarmer | null;
}

export interface SalesVsExpenseReport {
  total_penjualan: number;
  total_expense: number;
  net_profit: number;
}

export interface MonthlySalesVsExpenseReport extends SalesVsExpenseReport {
  bulan: string;
  tahun: number;
  bulan_ke: number;
}

export interface FarmerNetProfitReport extends SalesVsExpenseReport {
  petani: DashboardFarmer | null;
}
```

## Partner

Master partner dipakai untuk perusahaan/lembaga/perorangan yang berelasi dengan operasional.

### Struktur Data Partner

```txt
nama                    required
alamat                  required
hp                      optional
email                   optional
pic                     optional, nama orang PIC
web                     optional
provinsi_kode           required, kode wilayah level provinsi
kabupaten_kota_kode     required, kode wilayah level kabupaten_kota
kecamatan_kode          required, kode wilayah level kecamatan
```

Validasi wilayah:

```txt
kabupaten_kota_kode harus berada di bawah provinsi_kode.
kecamatan_kode harus berada di bawah kabupaten_kota_kode.
```

### List Partner

```txt
GET /partners
GET /partners?search=mitra
GET /partners?provinsi_kode=71
GET /partners?kabupaten_kota_kode=7171
GET /partners?kecamatan_kode=7171010
```

### Detail Partner

```txt
GET /partners/{id}
```

### Buat Partner

```txt
POST /partners
```

Payload:

```json
{
  "nama": "PT Nilam Sejahtera",
  "alamat": "Jl. Sudirman No. 10",
  "hp": "08123456789",
  "email": "info@nilamsejahtera.co.id",
  "pic": "Budi Santoso",
  "web": "https://nilamsejahtera.co.id",
  "provinsi_kode": "71",
  "kabupaten_kota_kode": "7171",
  "kecamatan_kode": "7171010"
}
```

### Update Partner

```txt
PUT /partners/{id}
```

Payload boleh parsial.

### Hapus Partner

```txt
DELETE /partners/{id}
```

### TypeScript Partner

```ts
export interface Partner {
  id: string;
  nama: string;
  alamat: string;
  hp: string | null;
  email: string | null;
  pic: string | null;
  web: string | null;
  provinsi_kode: string;
  kabupaten_kota_kode: string;
  kecamatan_kode: string;
  provinsi: string | null;
  kabupaten_kota: string | null;
  kecamatan: string | null;
}

export interface PartnerCreatePayload {
  nama: string;
  alamat: string;
  hp?: string | null;
  email?: string | null;
  pic?: string | null;
  web?: string | null;
  provinsi_kode: string;
  kabupaten_kota_kode: string;
  kecamatan_kode: string;
}

export type PartnerUpdatePayload = Partial<PartnerCreatePayload>;
```
