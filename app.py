import streamlit as st
from PIL import Image
import numpy as np
import os
import io
import tempfile

# Import semua fungsi dari main.py 
from main import (
    get_folder_avg_rgb,
    get_avg_rgb_per_grid,
    knn_euclidean,
    knn_minkowski,
    knn_manhattan,
    mosaic,
    FOLDER_CATEGORY,
)

# Page Config
st.set_page_config(
    page_title="Photomosaic Generator",
    page_icon="🖼️",
    layout="centered",
)

# Title
st.title("🖼️ Photomosaic Art Generator")
st.write("Upload gambar referensi, pilih kategori tile dan metode jarak, lalu generate mosaik!")

st.divider()

# Upload Image
st.subheader("1. Upload Gambar Referensi")
uploaded_file = st.file_uploader(
    "Pilih gambar (JPG / PNG)",
    type=["jpg", "jpeg", "png"],
)

if uploaded_file:
    preview_img = Image.open(uploaded_file)
    st.image(preview_img, caption="Gambar referensi", use_container_width=True)

st.divider()

# Category Selection
st.subheader("2. Pilih Kategori Tile")

CATEGORY_LABELS = {
    "building": "🏢 Bangunan",
    "cloud":    "☁️ Awan",
    "forest":   "🌲 Hutan",
    "mountain": "⛰️ Gunung",
}

category_options = list(FOLDER_CATEGORY.keys())
category_labels  = [CATEGORY_LABELS.get(c, c.capitalize()) for c in category_options]

selected_label    = st.radio(
    "Kategori",
    options=category_labels,
    horizontal=True,
    label_visibility="collapsed",
)
selected_category = category_options[category_labels.index(selected_label)]

st.divider()

# Distance Selection
st.subheader("3. Pilih Metode Jarak KNN")

DISTANCE_OPTIONS = {
    "Euclidean":        "euclidean",
    "Minkowski (p=3)":  "minkowski",
    "Manhattan":        "manhattan",
}

selected_distance_label = st.radio(
    "Metode Jarak",
    options=list(DISTANCE_OPTIONS.keys()),
    horizontal=True,
    label_visibility="collapsed",
)
selected_distance = DISTANCE_OPTIONS[selected_distance_label]

st.divider()

# Grid Size
st.subheader("4. Ukuran Grid")
col_m, col_n = st.columns(2)
with col_m:
    grid_m = st.slider("Kolom (m)", min_value=16, max_value=256, value=64, step=8)
with col_n:
    grid_n = st.slider("Baris (n)",  min_value=16, max_value=256, value=64, step=8)

st.divider()

# Generate Button
generate_btn = st.button(
    "✨ Generate Mosaik",
    type="primary",
    use_container_width=True,
    disabled=(uploaded_file is None),
)

if uploaded_file is None:
    st.caption("⬆️ Upload gambar terlebih dahulu untuk mengaktifkan tombol generate.")

# Proses
if generate_btn and uploaded_file:

    folder = FOLDER_CATEGORY.get(selected_category)
    if not os.path.isdir(folder):
        st.error(f"Folder asset tidak ditemukan: `{folder}`\nPastikan folder assets ada di direktori yang sama dengan app.py.")
        st.stop()

    # Simpan file upload ke tempfile agar bisa dibaca PIL via path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        # Progress bar
        progress = st.progress(0, text="Memulai proses...")

        # Step 1: Load / cache dataset
        cache_dir  = "cache"
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, f"{selected_category}_avg.npz")

        if os.path.exists(cache_path):
            progress.progress(15, text="📦 Memuat cache dataset...")
            data      = np.load(cache_path, allow_pickle=True)
            avg_rgb   = data["avg_rgb"]
            img_paths = list(data["paths"])
        else:
            progress.progress(10, text="🔍 Membaca dataset tile...")
            avg_rgb, img_paths = get_folder_avg_rgb(folder)
            np.savez(cache_path, avg_rgb=avg_rgb, paths=np.array(img_paths))
            progress.progress(25, text="✅ Dataset dimuat & cache disimpan.")

        if len(img_paths) == 0:
            st.error(f"Tidak ada gambar ditemukan di folder `{folder}`.")
            st.stop()

        # Hitung avg RGB per grid
        progress.progress(35, text="🎨 Menghitung warna rata-rata per grid...")
        avg_color_pixel, width, height, grid_w, grid_h = get_avg_rgb_per_grid(
            tmp_path, grid_m, grid_n
        )

        # KNN matching
        progress.progress(50, text=f"🔎 Mencocokkan tile ({selected_distance_label})...")
        if selected_distance == "euclidean":
            nearest = knn_euclidean(avg_color_pixel, avg_rgb)
        elif selected_distance == "minkowski":
            nearest = knn_minkowski(avg_color_pixel, avg_rgb, p=3)
        else:
            nearest = knn_manhattan(avg_color_pixel, avg_rgb)

        # Susun mosaik
        progress.progress(85, text="🖼️ Menyusun mosaik...")
        result_img = mosaic(nearest, img_paths, width, height, grid_w, grid_h)

        progress.progress(100, text="✅ Selesai!")

        # Tampilkan hasil
        st.success("Mosaik berhasil dibuat!")
        st.image(result_img, caption="Hasil Photomosaic", use_container_width=True)

        # Tombol download
        buf = io.BytesIO()
        result_img.save(buf, format="JPEG", quality=90)
        st.download_button(
            label="⬇️ Download Hasil Mosaik",
            data=buf.getvalue(),
            file_name="mosaic.jpg",
            mime="image/jpeg",
            use_container_width=True,
        )

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

    finally:
        os.unlink(tmp_path)