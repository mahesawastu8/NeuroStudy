# 🧠 NeuroStudy

> **Clinical Neuroscience & Evidence-Based Medical Learning Platform**

NeuroStudy adalah platform belajar kedokteran bertenaga AI yang dirancang berdasarkan literatur neurosains kognitif (*Ebbinghaus Forgetting Curve*, *SuperMemo SM-2 Spaced Repetition*, *Testing Effect / Active Recall*, *Cognitive Load Theory*, dan *Feynman Technique*).

---

## ✨ Fitur Utama
1. **🏛️ Sistem Pareto 80/20 (Zero-PPT Standard):**
   - **Catatan Master Klinis:** Rangkuman substansi level textbook (Harrison & Robbins), tabel perbandingan obat, dan diagram kaskade sinyal molekuler.
   - **Active Recall Socratic:** 3 pertanyaan penguji penalaran kausalitas sebelum membuka materi.
   - **Simulasi Ujian Blok (C1–C6):** 10 soal klinis vignette standar UKMPPD/USMLE lengkap dengan bedah distractor & rasionalisasi.
2. **🗂️ Pusat Latihan Memori Jangka Panjang:**
   - Flashcards interaktif berbasis algoritma pengulangan berjarak **SuperMemo SM-2**.
   - Ekspor deck flashcards standar **Anki (.tsv)** sekali klik.
   - Sinkronisasi kalender belajar otomatis (**Google Calendar & format .ics** untuk Apple/Outlook).
3. **⚙️ Dewan Dokter Spesialis AI & Cloud Sync:**
   - Multi-Agent AI Council: Dr. Marcus Vance, Sp.FK (Farmakologi), Dr. Aris Thorne, Sp.PD (Penyakit Dalam), Dr. Elena Rostova, Sp.A (Pediatri & Tumbuh Kembang), dan Dr. Hiroshi Tanaka, Sp.BS (Neurosains).
   - Sinkronisasi Google Drive 208 Modul Kuliah otomatis.

---

## 🚀 Cara Menjalankan Secara Lokal

```bash
# 1. Clone repository
git clone https://github.com/<username>/NeuroStudy.git
cd NeuroStudy

# 2. Buat virtual environment & install dependensi
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Jalankan aplikasi Streamlit
streamlit run app.py
```

---

## ☁️ Deploy ke Streamlit Community Cloud (Gratis & 24/7)

1. Fork / Push repositori ini ke akun GitHub Anda.
2. Buka [share.streamlit.io](https://share.streamlit.io).
3. Pilih repository `NeuroStudy`, branch `main`, dan file `app.py`.
4. Di bagian **Advanced Settings -> Secrets**, masukkan Gemini API Key Anda:
   ```toml
   GEMINI_API_KEY = "AIzaSy..."
   ```
5. Klik **Deploy**! Aplikasi Anda akan aktif 24 jam nonstop secara permanen.
