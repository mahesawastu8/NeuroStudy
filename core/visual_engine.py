"""
NeuroStudy Multimodal Clinical Visual Engine (Integrated Dual Coding)
Ensures medical students master visual diagnostic competencies (Histology, ECG, Radiology).
"""
import os
import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VISUAL_DIR = BASE_DIR / "data" / "visual_atlas"
VISUAL_DIR.mkdir(parents=True, exist_ok=True)

# High-yield verified diagnostic visual maps for medical blocks
DIAGNOSTIC_VISUAL_ATLAS = {
    "ECG": {
        "title": "⚡ Atlas EKG Klinis & Jalur Konduksi Jantung",
        "category": "Elektrokardiografi (EKG)",
        "clinical_pearl": "Wajib identifikasi Segmen ST (STEMI vs NSTEMI), kompleks QRS (>120ms = Bundle Branch Block), dan Interval PR (AV Block derajat 1-3).",
        "schematic": """
  ┌────────────────────────────────────────────────────────┐
  │ 🫀 EKG 12-LEAD DIAGNOSTIC GRID                         │
  │ Leads II, III, aVF    → Dinding Inferior (RCA)         │
  │ Leads V1 - V2         → Septal (LAD cabang septal)     │
  │ Leads V3 - V4         → Anterior (LAD)                 │
  │ Leads I, aVL, V5 - V6 → Dinding Lateral (LCx / Diag LAD)│
  └────────────────────────────────────────────────────────┘
"""
    },
    "HISTO": {
        "title": "🔬 Preparat Histopatologi Pewarnaan H&E Khas",
        "category": "Histopatologi & Jejas Sel (Robbins 10th)",
        "clinical_pearl": "Diferensiasi nekrosis koagulatif (infark organ padat), nekrosis likuefaktif (otak & abses), dan nekrosis kaseosa (tuberkulosis dengan sel datia Langhans).",
        "schematic": """
  ┌────────────────────────────────────────────────────────┐
  │ 🔬 HISTOPATOLOGI PEMBEDA (Robbins 10th Ed)              │
  │ • Koagulatif   : Ghost cells, arsitektur jaringan awet │
  │ • Kaseosa      : Massa aseluler amorf merah muda + Langhans │
  │ • Likuefaktif  : Degenerasi kistik penuh pus netrofil  │
  │ • Fibrinoid    : Kompleks imun dinding vaskulitis      │
  └────────────────────────────────────────────────────────┘
"""
    },
    "RADIO": {
        "title": "🩻 Interpretasi Radiologi Toraks & Abdomen",
        "category": "Radiologi Diagnostik",
        "clinical_pearl": "Baca dengan algoritma ABCDE: Airway (deviasi trakea), Breathing (corakan bronkovaskular & infiltrat), Cardiac (CTR > 50%), Diaphragm (sudut kostofrenikus tajam), Everything else (fraktur kosta).",
        "schematic": """
  ┌────────────────────────────────────────────────────────┐
  │ 🩻 RADIOLOGI TORAKS KRITIS                             │
  │ • Pneumotoraks : Garis pleural line + avaskuler perifer│
  │ • Efusi Pleura : Meniscus sign / sudut kostofrenikus tumpul │
  │ • Edema Paru   : Bat-wing appearance + Kerley B lines  │
  │ • Ileus Obstruktif: Multiple air-fluid levels bertingkat│
  └────────────────────────────────────────────────────────┘
"""
    },
    "REASONING": {
        "title": "🧠 Diagram Alur Penalaran Klinis (Dual-Process Theory)",
        "category": "Proses Klinis & Clinical Decision Making",
        "clinical_pearl": "Sistem 1 (Pattern recognition / Heuristik cepat) harus selalu diverifikasi dengan Sistem 2 (Hypothetico-deductive terstruktur) untuk mencegah premature closure.",
        "schematic": """
  ┌────────────────────────────────────────────────────────┐
  │ 🧭 ALUR PENALARAN KLINIS (Norman & Eva, NEJM 2006)     │
  │ Pasien Datang → Chief Complaint → Semantic Qualifiers  │
  │        ↓                                                │
  │ [Sistem 1: Heuristik] ──→ Hipotesis Kerja Dini         │
  │        ↓                                                │
  │ [Sistem 2: Verifikasi] ─→ Likelihood Ratio Penunjang    │
  │        ↓                                                │
  │ Diagnosis Definitif ───→ Terapi Rasional Berbasis EBM   │
  └────────────────────────────────────────────────────────┘
"""
    }
}

def get_module_visual_atlas(module_title):
    """
    Detects relevant clinical diagnostic visual modalities for any medical module.
    """
    title_lower = module_title.lower()
    selected = []
    
    if any(k in title_lower for k in ["kardio", "jantung", "cardio", "vaskular", "ekg", "ecg", "aritmia"]):
        selected.append(DIAGNOSTIC_VISUAL_ATLAS["ECG"])
    if any(k in title_lower for k in ["histo", "patologi", "sel", "jaringan", "tumor", "inflamasi"]):
        selected.append(DIAGNOSTIC_VISUAL_ATLAS["HISTO"])
    if any(k in title_lower for k in ["respirasi", "paru", "thorax", "dada", "toraks", "pneumo"]):
        selected.append(DIAGNOSTIC_VISUAL_ATLAS["RADIO"])
    if any(k in title_lower for k in ["clinical", "process", "penalaran", "anamnesis", "bdt", "diagnosis"]):
        selected.append(DIAGNOSTIC_VISUAL_ATLAS["REASONING"])
        
    # Default fallback: always provide at least reasoning + pathology
    if not selected:
        selected.append(DIAGNOSTIC_VISUAL_ATLAS["REASONING"])
        selected.append(DIAGNOSTIC_VISUAL_ATLAS["HISTO"])
        
    return selected
