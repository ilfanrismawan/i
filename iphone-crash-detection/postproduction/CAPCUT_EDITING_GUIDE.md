# Panduan Lengkap Editing CapCut Pro — iPhone Crash Detection

Panduan ini disusun sesuai standar **Educational 3D Director v5.0 (CapCut-First Workflow)**. Semua materi telah dirender secara terpisah (*clean render*, tanpa overlay teks bakar), diverifikasi pada format **1080×1920 (9:16 portrait) @ 30 FPS**, dan siap disusun di CapCut Pro.

---

## 📁 Lokasi File Siap Impor

Folder paket lengkap:
`c:\Users\HOG-PC001\Documents\i\iphone-crash-detection\postproduction\capcut_import_package\`

Isi paket:
1. **18 Video Shot**: `01_shot_01.mp4` s/d `18_shot_18.mp4`
2. **Audio Voice-Over**: `voice_over.mp3` (durasi 68.911 detik)
3. **Subtitel Kalimat**: `captions.srt` (per kalimat/klausa)
4. **Subtitel Dinamis (Word-by-word)**: `word_captions.srt` (per kata untuk efek kinetic captions)

---

## 🛠️ Langkah-Langkah Setup Timeline di CapCut Desktop

### 1. Buat Project Baru & Pengaturan Rasio
- Buka CapCut Desktop (`C:\Users\HOG-PC001\AppData\Local\CapCut\Apps\CapCut.exe`).
- Klik **New Project**.
- Pada menu **Ratio** di bawah preview player, pilih **9:16** (Portrait / TikTok / Reels).
- Pada menu **Settings** project, pastikan Frame Rate diatur ke **30 fps**.

### 2. Impor Media
- Drag seluruh file dari folder `postproduction/capcut_import_package/` ke tab **Media / Local Import**:
  - `01_shot_01.mp4` sampai `18_shot_18.mp4`
  - `voice_over.mp3`
  - `captions.srt` atau `word_captions.srt`

### 3. Penataan Track pada Timeline
Susun layer timeline dari atas ke bawah:
- **Track 1 (Paling Atas - Teks)**: Subtitle Track (`word_captions.srt` atau `captions.srt`)
- **Track 2 (Video Utama)**: Letakkan berurutan `01_shot_01.mp4` s/d `18_shot_18.mp4`
- **Track 3 (Audio VO)**: Letakkan `voice_over.mp3` mulai dari detik `00:00.000`
- **Track 4 (SFX Transisi)**: Efek suara transisi (Whoosh, Swish, Glitch, Thud)
- **Track 5 (Scene SFX)**: Efek suara diegetik (Mesin mobil, dentuman, alarm darurat, klik MEMS, pop tekanan, sinyal radio)
- **Track 6 (BGM / Musik Latar)**: Musik ambience synth / subtle tech beat

---

## 📋 Matriks Editorial & Desain Suara per Shot (Shot 01 – Shot 18)

| Shot ID | Waktu In - Out | Durasi | Teks Narasi / Subtitle | Jenis Transisi CapCut | SFX Transisi | Scene SFX (Cari di CapCut Sound) |
|---|---|---|---|---|---|---|
| **SHOT_01** | `00:00.00` - `00:02.37` | 2.37s | *ipon ieu sedang ikut naik mobil.* | **Fade In / Hard Cut** | - | **Car Driving / Engine Low Hum** |
| **SHOT_02** | `00:02.37` - `00:07.23` | 4.87s | *Tiba-tiba, INNAMMAA SYUDUDUU!! mobilnya menabrak dengan keras.* | **Hard Cut on Impact** | - | **Brake Screech** + **Dull Car Crash / Impact Thud** |
| **SHOT_03** | `00:07.23` - `00:10.53` | 3.30s | *Tak lama kemudian, si ipon menelepon bantuan sendiri.* | **Push / Zoom In** (0.2s) | **Fast Whoosh** | **Soft Beep / iOS Alert Ringtone** |
| **SHOT_04** | `00:10.53` - `00:12.77` | 2.23s | *Kok bisa ipon nyaho ada tabrakan?* | **Glitch Cut / White Flash** | **Camera Shutter / Glitch SFX** | **Ambient Silence / Deep Bass Drop** |
| **SHOT_05** | `00:12.77` - `00:17.30` | 4.53s | *Di dalam ipon 14 dan yang lebih baru, ada beberapa alat perasa kecil.* | **Spin / Orbit Zoom** | **Air Swish Soft** | **Sci-Fi Hologram Hum / X-Ray Sheen** |
| **SHOT_06** | `00:17.30` - `00:21.13` | 3.83s | *Yang pertama Innammaaqolli innammaa qollaa, merasakan hentakan.* | **Macro Snap / Pull In** | **Fast Swoosh** | **Mechanical Micro-Click / Spring Snap** |
| **SHOT_07** | `00:21.13` - `00:26.37` | 5.23s | *Saat mobil berhenti mendadak, ia merasakan dorongan yang sangat kuat.* | **Match Cut** (searah dorongan) | **Subtle Whoosh** | **Heavy G-Force Whine / Sudden Halting Thud** |
| **SHOT_08** | `00:26.37` - `00:31.27` | 4.90s | *Yang kedua merasakan putaran. Ia tahu kalau mobil berputar atau terguling.* | **Clockwise Rotate / Whirl** | **Spinning Air Whoosh** | **Gyroscope Whir / Whistle Spin** |
| **SHOT_09** | `00:31.27` - `00:35.30` | 4.03s | *Yang ketiga, DUARR MÉMÉKK!!* | **Quick Zoom In** | **Bass Thump** | **Air Pressure Pop / Balloon Burst Soft** |
| **SHOT_10** | `00:35.30` - `00:38.83` | 3.53s | *merasakan tekanan udara. Saat tabrakan, udara di dalam mobil bisa berubah tiba-tiba.* | **Wipe Left / Slide** | **Air Wave Rush** | **Cabin Air Shockwave / Sub Woofer Pulse** |
| **SHOT_11** | `00:38.83` - `00:41.30` | 2.47s | *Mikrofon mendengar suara yang sangat keras.* | **Punch In to Mic Hole** | **Snap In** | **Muffled Acoustic Boom / Mic Feedback Clip** |
| **SHOT_12** | `00:41.30` - `00:45.60` | 4.30s | *Dan GPS tahu, mobil yang tadi melaju sekarang tiba-tiba berhenti.* | **Top-Down Fade / Drop** | **Paper Flip / Digital Ping** | **Sequential Sonar Beeps (4x) then Silence** |
| **SHOT_13** | `00:45.60` - `00:48.07` | 2.47s | *si ipon menggabungkan semua tanda itu.* | **Converge / Light Streak** | **Data Riser** | **Electronic Synth Arpeggio / Data Fusion Pulse** |
| **SHOT_14** | `00:48.07` - `00:52.67` | 4.60s | *Ia sudah belajar dari lebih dari satu juta jam data berkendara dan tabrakan.* | **Pull Back Dolly** | **Reverse Whoosh** | **High-Speed AI Processing / Computer Churn** |
| **SHOT_15** | `00:52.67` - `00:56.40` | 3.73s | *Kalau tandanya cocok, iPhone membunyikan alarm dan bertanya dulu.* | **Hard Cut to Dash** | - | **Urgent Siren / iOS Emergency SOS Alert Tone** |
| **SHOT_16** | `00:56.40` - `01:00.60` | 4.20s | *Kalau tidak ada yang menjawab, iPhone menelepon bantuan dan memberi tahu lokasimu.* | **Crane Up / Sky Tilt** | **Rising Wind Swell** | **Satellite Beacon Chime / Phone Ringing Out** |
| **SHOT_17** | `01:00.60` - `01:03.63` | 3.03s | *Tapi si ipon teu bisa mengenali semua tabrakan.* | **Clean Hard Cut** | - | **Peaceful Country Road Ambience / Gentle Breeze** |
| **SHOT_18** | `01:03.63` - `01:08.91` | 5.27s | *Jadi, alat-alat kecil itu bekerja sama untuk memanggil bantuan. DAMNNN BRUHH!!* | **Slow Zoom Out to Shell Close** | **Closing Swell** | **Power Down Sheen / Crisp Closing Bell Chime** |

---

## 🎨 Rekomendasi Styling Subtitel di CapCut (Word-by-word / Kinetic)

1. **Pilihan Impor**:
   - Jika ingin teks per-kalimat rapi: Impor `captions.srt`.
   - Jika ingin efek *kinetic word-highlight*: Impor `word_captions.srt`, atau gunakan fitur **Auto Captions** di CapCut dengan panduan teks yang sudah ada.
2. **Font & Warna**:
   - **Font**: *The Bold Font*, *Montserrat (Extra Bold)*, atau *Futura Bold*.
   - **Warna Teks Utama**: Putih (`#FFFFFF`) dengan Stroke Hitam tipis (`#000000`, 8%).
   - **Highlight Kata Kunci**: Kuning Emas (`#FFE500`) atau Neon Green (`#00FF88`) saat narator mengucapkan kata penting (misal: *"menabrak"*, *"alat perasa"*, *"tekanan udara"*, *"alarm"*).
   - **Posisi**: Letakkan di area tengah bawah (Y: -35% dari titik tengah) agar tidak tertutup tombol UI TikTok/Reels di sebelah kanan atau caption akun di bawah.

---

## 🎵 Pengaturan Musik Latar (BGM) & Audio Ducking

1. **Pilihan Musik**:
   - Cari di CapCut Audio: Kategori **Tech / Beats / Minimal Corporate** (tempo sedang 110-120 BPM, tanpa vokal).
2. **Audio Ducking**:
   - Aktifkan fitur **Audio Ducking** pada track BGM di CapCut.
   - Atur level ducking ke **-18 dB s/d -22 dB** saat narasi terdengar.
   - Saat narasi jeda (misalnya pada efek tabrakan SHOT_02 dan alarm SHOT_15), BGM otomatis naik perlahan untuk memberi dampak emosional.

---

## 📤 Langkah Ekspor Akhir

Setelah penyesuaian di CapCut selesai:
1. Klik **Export** di pojok kanan atas CapCut.
2. Resolusi: **1080p (1080 × 1920)**.
3. Bitrate: **Recommended (Higher / ~15-20 Mbps)**.
4. Codec: **H.264**.
5. Format: **MP4**.
6. Frame rate: **30 fps**.
