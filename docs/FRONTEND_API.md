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
    "id": 1,
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
  "id": 1,
  "nama": "Budi Santoso",
  "nik": "1234567890123456",
  "alamat": "Jl. Nilam No. 1",
  "hp": "08123456789",
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
    "id": 1,
    "nama": "Budi Santoso",
    "nik": "1234567890123456",
    "alamat": "Jl. Nilam No. 1",
    "hp": "08123456789",
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
GET /farmers/1
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
  "id": 1,
  "nama": "Budi Santoso",
  "nik": "1234567890123456",
  "alamat": "Jl. Nilam No. 1",
  "hp": "08123456789",
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

### Hapus Petani

```txt
DELETE /farmers/{id}
```

Response:

```txt
204 No Content
```

Tidak ada response body.

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
  id: number;
  nama: string;
  nik: string;
  alamat: string;
  hp: string | null;
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
  "id" | "desa_kelurahan" | "kecamatan" | "kabupaten_kota" | "provinsi"
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
