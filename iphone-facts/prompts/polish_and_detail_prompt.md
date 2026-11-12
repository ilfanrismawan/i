# Prompt: polishing dan detailing aset 3D

Tempel bagian "PROMPT" di bawah ke Claude Code atau Codex yang sudah memasang skill
`educational-3d-director`, dari folder repo ini. Ganti `<PROYEK>` dengan salah satu folder proyek.
Kerjakan satu proyek per sesi supaya hasilnya bisa diperiksa sebelum lanjut.

Proyek yang tersedia: `iphone-crash-detection`, `iphone-duo-fold`, `iphone-vapor-chamber`,
`iphone-quad-pixel`, `iphone-camera-control`, `iphone-printed-port`.

---

## PROMPT

Gunakan skill educational-3d-director dalam mode `repair` + `asset`. Proyek: `<PROYEK>`.

**Tujuan:** naikkan kualitas visual aset yang SUDAH ADA (polishing dan detailing) tanpa membuat ulang,
tanpa mengubah cara aset itu dikendalikan, dan tanpa menambah klaim fakta baru.

### Langkah wajib sebelum mengubah apa pun
1. Baca `<PROYEK>/asset_manifest.json`, laporan di `<PROYEK>/reports/` (atau `iphone-facts/reports/`),
   skrip pembuat yang disebut di kolom `generator`, dan `iphone-crash-detection/scripts/asset_lib.py`.
2. Buka setiap `.blend` secara headless dan catat: daftar objek, nama root, anchor, properti kontrol,
   driver, shape key, ukuran bounding box. Simpan sebagai `reports/polish_baseline.json`.
3. Render ulang pratinjau yang ada ke `previews/polish_before/` dengan kamera yang sama, lalu LIHAT
   gambarnya. Tulis daftar kekurangan per aset sebelum mulai bekerja.

### Aturan yang tidak boleh dilanggar
- Jangan menimpa file `.blend` asal. Simpan hasil sebagai `assets/<nama>_v2.blend` dan tambahkan entri
  baru di manifest (`phase: "polish"`, `supersedes: "<id lama>"`). Entri lama tidak dihapus.
- Nama collection, root, anchor, dan properti kontrol beserta rentang nilainya HARUS sama persis.
  Semua uji kontrol di laporan lama harus tetap lolos dengan angka yang sama pada file v2.
- Jangan membuat ulang aset yang tercantum di `reuse_do_not_recreate`, termasuk model milik pengguna
  di `Asset/`. Pakai lewat link atau append.
- Eevee saja. Tanpa teks, label, panah penjelas, logo, atau watermark di dalam Blender. UI diegetik
  di layar ponsel boleh, tetapi tetap ikon tanpa tulisan.
- Semua aset mekanisme adalah ilustrasi konseptual. Jangan menambah detail yang mengesankan bentuk
  asli komponen Apple, jangan menulis angka ukuran, dan jangan menambah klaim di luar `sourced_facts`
  atau `research/claims.json`. Jika sebuah detail butuh fakta baru, berhenti dan laporkan.
- Tidak ada animasi shot, kamera final, naskah, atau render final di tahap ini.

### Yang dikerjakan (urutan prioritas)
1. **Bentuk dan siluet:** bevel yang konsisten, tepi tajam hanya bila disengaja, tidak ada permukaan
   saling tembus atau z-fighting, normal benar, shading halus tanpa artefak.
2. **Material:** ganti warna polos dengan material berlapis yang tetap ringan untuk Eevee: variasi
   roughness, sedikit noise/bump prosedural, logam sikat untuk aluminium/titanium, kaca dengan
   pantulan terbaca, serbuk/karet/plastik yang bisa dibedakan. Emisi tetap dikendalikan driver lama.
3. **Detail sekunder yang membantu pemahaman:** sekrup, alur, kabel lentur, bantalan, celah perakitan,
   tepi potongan yang jelas pada aset cutaway. Setiap detail harus mendukung mekanisme yang diceritakan;
   detail hiasan yang mengganggu pembacaan dibuang.
4. **Keterbacaan di layar ponsel 9:16:** bagian yang bergerak harus kontras terhadap latar dan bagian
   diam; gerakannya harus terlihat jelas antara nilai kontrol 0 dan 1.
5. **Pencahayaan pratinjau:** satu rig tiga lampu + world gelap netral yang sama untuk semua aset
   mekanisme, disimpan sebagai `assets/preview_lighting.blend` supaya bisa dipakai ulang. Hindari
   emisi yang membuat warna menjadi putih terbakar.

### Kekurangan yang sudah diketahui (perbaiki bila proyeknya sesuai)
- `iphone-crash-detection`: ikon gagang telepon di layar panggilan mirip headphone; titik merah
  "berhenti" jejak GPS tertutup mobil; lendutan selaput sensor tekanan kurang terbaca dari sudut
  tinggi; dasbor terlalu polos; warna pratinjau aset utama pucat; bantalan emas sensor nyaris tak
  terlihat.
- `iphone-duo-fold`: layar dalam terbakar putih saat `inner_glow` bawaan; tidak ada strip layar di
  atas engsel (ada celah di antara dua paruh layar); susunan lapisan terlihat kecil di bingkai dan
  lapisan perekat sulit dibedakan saat rata; gigi roda engsel kotak-kotak dan belum jelas saling
  mengait; pembingkaian pratinjau engsel miring.
- `iphone-vapor-chamber`: tetes air dan uap berupa cakram/kubus seragam; ujung panas dan dingin
  belum terbaca tanpa nyala; panah aliran panas berbentuk segitiga polos.
- `iphone-quad-pixel`: bingkai potong tengah tetap terlihat putih saat `crop_glow` = 0 (seharusnya
  tersembunyi); tutup piksel gabungan menutupi lensa mikro sepenuhnya; warna terlalu pastel.
- `iphone-camera-control`: penanda jari berupa gumpalan; kubah sakelar terlihat datar dari samping;
  sambungan plunger ke balok dan ke kubah belum rapat; pengukur regangan nyaris tak terlihat.
- `iphone-printed-port`: tabung port terbaca sebagai balok padat dari atas (pastikan berongga);
  sinar laser menembus ke atas kepala laser; lapisan cetak tidak terlihat sebagai lapisan; serbuk
  berupa balok rata tanpa butiran.

### Bukti selesai (wajib ada sebelum berhenti)
- `previews/polish_after/` berisi render dengan kamera yang sama seperti `polish_before/`, minimal
  posisi kontrol 0, 0.5, dan 1 untuk setiap kontrol gerak, resolusi 540x960, Eevee.
- `reports/polish_validation.json`: hasil ulang semua uji kontrol lama (harus identik), daftar
  anchor/kontrol yang dibandingkan dengan baseline, jumlah objek dan segitiga sebelum/sesudah.
- `asset_manifest.json` lolos `scripts/validate_manifest.py --check-hashes` dari skill.
- Ringkasan per aset: apa yang berubah, apa yang sengaja tidak diubah, dan kekurangan yang tersisa.
  Lihat sendiri gambar `polish_after`; jangan menyatakan lolos hanya dari angka.

### Berhenti dan tanyakan bila
- sebuah perbaikan mengharuskan mengganti nama/rentang kontrol atau anchor;
- sebuah detail membutuhkan fakta yang belum ada di sumber;
- jumlah segitiga satu aset melewati sekitar 300 ribu atau render pratinjau menjadi lebih dari
  sekitar 20 detik per gambar.

Setelah satu proyek selesai: BERHENTI. Jangan lanjut ke proyek lain, jangan commit atau push kecuali
diminta.

---

## Catatan pemakaian

- Jalankan Blender headless: `blender --background --python <skrip> -- <folder>`.
- Skrip pembuat lama boleh dijadikan acuan atau diimpor, tetapi jangan dijalankan ulang ke file asal.
- Urutan yang disarankan: `iphone-duo-fold` (topik berikutnya), lalu `iphone-crash-detection`.
