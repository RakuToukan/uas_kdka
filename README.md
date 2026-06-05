# Photomosaic API

Layanan backend untuk menghasilkan photomosaic dari gambar target. Proyek ini menggabungkan server HTTP ditulis dengan Go (Gin) yang memanggil skrip Python untuk melakukan pemrosesan gambar (Pillow, NumPy).

Base URL default: http://localhost:8080

## Endpoints

 - GET /categories
  - Mengembalikan daftar kategori tile yang tersedia.
  - Response: JSON berisi array kategori, mis. ["building", "cloud", "forest", "mountain"].

- POST /mosaic
  - Mengunggah gambar target dan memulai proses pembuatan photomosaic secara asinkron.
  - Request: multipart/form-data dengan field berikut:
    - `image` (file) — gambar target (JPG/PNG).
    - `category` (string) — salah satu kategori tile: `building`, `cloud`, `forest`, `mountain`.
    - `distance` (string, optional) — rumus jarak yang digunakan untuk mencocokkan warna. Nilai yang didukung oleh API: `euclidean`, `minkowski`, `manhattan`. Default: `euclidean`.
  - Response saat diterima: status HTTP 202 dan body JSON berisi `job_id` dan status awal (`pending`).
  - Validasi input: server mengembalikan error jika field wajib hilang atau kategori tidak valid.

- GET /status/:id
  - Mengecek status job berdasarkan `job_id`.
  - Jika job belum selesai: response JSON dengan `job_id` dan `status` (mis. `pending` atau `processing`).
  - Jika job gagal: response JSON memberi `status: "failed"` dan field `error` berisi pesan kesalahan.
  - Jika job selesai: response berupa binary image (Content-Type: `image/jpeg`) — bukan JSON.
  - Jika `job_id` tidak ditemukan: HTTP 404 dengan pesan error.

## Cara Penggunaan (ringkas)

1. Ambil daftar kategori dari `GET /categories`.
2. Ambil daftar rumus distance dari `GET /distance`.
3. Unggah gambar ke `POST /mosaic` dengan field `image` dan `category` untuk memulai job; catat `job_id` dari respons.
4. Lakukan polling ke `GET /status/:id` setiap 2–3 detik untuk memeriksa progres:
   - `pending` — job belum mulai
   - `processing` — pemrosesan sedang berjalan
   - `failed` — pemrosesan gagal (periksa pesan `error`)
   - Jika response berisi header `Content-Type: image/jpeg`, job selesai dan body adalah file gambar hasil mosaic.

## Catatan untuk Frontend

- Gunakan polling dengan interval minimal 2 detik.
- Jangan hanya mengandalkan field JSON `status: "done"` untuk mendeteksi hasil jadi — periksa `Content-Type` pada respons. Response bertipe `image/jpeg` berarti hasil sudah siap.
- Job disimpan di memori proses server. Jika server di-restart, semua job hilang; jangan mengandalkan `job_id` bersifat persisten lintas sesi.

## Menjalankan Server

Persyaratan lingkungan:
- Go 1.21+
- Python 3.9+ beserta dependensi Python: Pillow dan NumPy
- Dataset tile tersedia di folder `assets/` di root proyek

Menjalankan server (dijalankan dari root proyek):

```bash
go run main.go
```

Server akan berjalan pada http://localhost:8080 secara default.

## Penggunaan Manual (Python)

Jika ingin menjalankan proses langsung tanpa melalui API, skrip Python `main.py` menerima argumen berikut: `target_image`, `category`, `distance`, `output_path`. Opsi `distance` yang didukung: `euclidean`, `minkowski`, `manhattan` (default `euclidean`).