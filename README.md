<div align="center">

# 🧠 NeuroAI-ADHD

### fMRI-Based ADHD Detection using BiLSTM-Transformer Ensemble with Explainable AI

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?style=flat-square&logo=pytorch)](https://pytorch.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)](https://reactjs.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13%2B-FF6F00?style=flat-square&logo=tensorflow)](https://www.tensorflow.org/)
[![Anna University](https://img.shields.io/badge/Anna%20University-Final%20Year%20Project-maroon?style=flat-square)](https://www.annauniv.edu/)

**B.E. Artificial Intelligence & Data Science — Final Year Capstone Project**  
United Institute of Technology (UIT), Coimbatore | Anna University Affiliation  
**2025–2026**

</div>

---

## 📌 Problem Statement

Attention Deficit Hyperactivity Disorder (ADHD) affects approximately **5–10% of children** and **2–5% of adults** worldwide, yet clinical diagnosis remains **largely subjective** — relying on behavioral questionnaires and clinician observation without objective neurobiological markers. 

This project proposes an **automated, objective, neuroimaging-based detection system** using resting-state functional Magnetic Resonance Imaging (fMRI), deep learning, and explainable AI to:
- **Assist clinicians** in making faster, data-driven ADHD diagnoses
- **Reduce diagnostic bias** with objective neurobiological evidence
- **Improve patient outcomes** through early detection and intervention
- **Provide interpretable results** — clinicians see *why* the model predicts ADHD (which brain regions are affected)

---

## 🏗️ System Architecture

```
📥 fMRI Input (NIfTI Format)
       │
       ▼
┌─────────────────────────────────┐
│  PREPROCESSING & NORMALIZATION  │
│  • Skull stripping (FSL BET)    │
│  • Motion correction            │
│  • MNI space registration       │
│  • Quality checks               │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│   FEATURE EXTRACTION            │
│  • ROI extraction (AAL atlas)   │
│  • Mean BOLD signal/ROI (116)   │
│  • Functional connectivity      │
│  • Matrix computation (pearson) │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│   DEEP LEARNING ENSEMBLE PREDICTION        │
│  ┌──────────────┐    ┌──────────────────┐  │
│  │   BiLSTM     │    │  Transformer     │  │
│  │ • Temporal   │ +  │ • Self-attention │  │
│  │   patterns   │    │ • ROI interactions  │
│  └──────────────┘    └──────────────────┘  │
│         │                    │              │
│         └────────┬───────────┘              │
│          Soft Voting Ensemble              │
│          (Confidence Score)                │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│   EXPLAINABILITY (XAI)          │
│  • SHAP feature importance      │
│  • Attention maps               │
│  • Brain region heatmaps        │
│  • Clinical interpretation      │
└─────────────┬───────────────────┘
              │
              ▼
    🎯 ADHD Classification + Confidence + Brain Regions
```

---

## 🧬 Dataset & Preprocessing

| Property | Details |
|---|---|
| **Source** | [ADHD-200 Global Competition](http://fcon_1000.projects.nitrc.org/indi/adhd200/) |
| **Type** | Resting-state fMRI (rs-fMRI) |
| **Subjects** | ~973 subjects (ADHD + Typically Developing Controls) |
| **Acquisition Sites** | 8 international research centers (NYU, Peking, Kennedy Krieger, etc.) |
| **File Format** | NIfTI (.nii.gz) — 4D volumetric time series |
| **Atlas Used** | AAL (Automated Anatomical Labeling) — 116 brain regions |
| **Processing** | FSL pipelines for preprocessing; nilearn for feature extraction |

> ⚠️ **Data Note:** Raw fMRI data is **not included** in this repository due to licensing. Download from [NITRC ADHD-200](http://fcon_1000.projects.nitrc.org/indi/adhd200/) and place in `data/raw/`. Processed connectivity matrices are available upon request.

---

## 📊 Model Performance

| Model | Accuracy | Sensitivity | Specificity | AUC-ROC | Precision |
|---|---|---|---|---|---|
| SVM (Baseline) | 62.4% | 58.1% | 66.7% | 0.64 | 0.61 |
| LSTM | 71.3% | 69.5% | 73.1% | 0.74 | 0.70 |
| Transformer | 74.8% | 72.6% | 76.9% | 0.78 | 0.75 |
| **BiLSTM-Transformer Ensemble** | **79.6%** | **77.4%** | **81.8%** | **0.83** | **0.81** |

**Evaluation Protocol:**
- Subject-level predictions (not slice-level)
- 5-fold stratified cross-validation
- Held-out test set (80/20 split)
- Balanced dataset handling for class imbalance

---

## 🛠️ Technology Stack

### Backend & API
- **Framework**: FastAPI (async Python web framework)
- **Authentication**: JWT tokens with role-based access control
- **Database**: SQLite + SQLAlchemy ORM
- **Task Queue**: Celery + Redis (async fMRI processing)

### Machine Learning
- **Deep Learning**: TensorFlow/Keras + PyTorch
- **Neuroimaging**: Nibabel, nilearn, FSL Python
- **Explainability**: SHAP, Grad-CAM, attention mechanisms
- **Preprocessing**: scikit-image, scipy, numpy

### Frontend
- **UI Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **HTTP Client**: Axios

### Data & Visualization
- **Vector Store**: ChromaDB (for embeddings, if needed)
- **Visualization**: Plotly, Matplotlib, nilearn plotting
- **Data Processing**: Pandas, NumPy

---

## 📁 Repository Structure

```
NeuroAI-ADHD/
│
├── backend/                          # FastAPI backend application
│   ├── app/
│   │   ├── main.py                   # FastAPI app initialization
│   │   ├── auth.py                   # JWT authentication
│   │   ├── database.py               # SQLAlchemy setup
│   │   ├── models.py                 # Database models
│   │   ├── schemas.py                # Pydantic request/response schemas
│   │   ├── utils.py                  # Helper functions
│   │   └── routes/
│   │       ├── auth_routes.py        # Login, register, token refresh
│   │       ├── patient_routes.py     # Patient CRUD operations
│   │       ├── assessment_routes.py  # ADHD assessment endpoints
│   │       ├── dashboard_routes.py   # Analytics & statistics
│   │       └── report_routes.py      # Report generation
│   │
│   ├── ml/                           # ML pipeline
│   │   ├── model_loader.py           # Load trained ensemble
│   │   ├── predictor.py              # Inference logic
│   │   ├── preprocess.py             # fMRI preprocessing
│   │   ├── explainability.py         # XAI visualizations
│   │   └── scan_preview.py           # PNG rendering
│   │
│   ├── uploads/                      # User-uploaded fMRI scans
│   │   ├── *.nii.gz                  # Brain scan files
│   │   └── previews/                 # Generated PNG previews
│   │
│   ├── reports/                      # Generated clinical reports
│   ├── requirements.txt
│   ├── run.py                        # Entry point
│   ├── .env                          # Configuration (git-ignored)
│   └── README.md                     # Backend-specific docs
│
├── frontend/                         # React UI application
│   ├── src/
│   │   ├── components/               # Reusable React components
│   │   ├── pages/                    # Page-level components
│   │   │   ├── Upload.tsx            # Scan upload interface
│   │   │   ├── Results.tsx           # Prediction results display
│   │   │   └── Dashboard.tsx         # Admin analytics
│   │   ├── api/                      # API client (Axios)
│   │   └── App.tsx
│   ├── package.json
│   └── README.md                     # Frontend-specific docs
│
├── ml/                               # Standalone ML training code
│   ├── preprocessing/
│   │   ├── skull_strip.py            # Brain extraction (FSL)
│   │   ├── motion_correction.py      # fMRI motion correction
│   │   ├── normalize.py              # MNI registration
│   │   └── extract_rois.py           # ROI signal extraction
│   │
│   ├── features/
│   │   └── connectivity.py           # Functional connectivity matrix
│   │
│   ├── models/
│   │   ├── bilstm.py                 # BiLSTM architecture
│   │   ├── transformer.py            # Transformer encoder
│   │   ├── ensemble.py               # Ensemble logic
│   │   ├── train.py                  # Training script
│   │   └── evaluate.py               # Model evaluation
│   │
│   ├── xai/
│   │   ├── shap_explainer.py         # SHAP explanations
│   │   └── gradcam.py                # Spatial attention maps
│   │
│   └── notebooks/
│       └── EDA_Visualization.ipynb    # Exploratory data analysis
│
├── data/
│   ├── raw/                          # Raw NIfTI files (add manually)
│   ├── processed/                    # Connectivity matrices
│   └── phenotypic/                   # Subject metadata
│
├── docs/
│   ├── NeuroAI_ADHD_Report.pdf       # Full project report
│   ├── ARCHITECTURE.md               # Detailed system design
│   └── DEPLOYMENT.md                 # Deployment guide
│
├── requirements.txt                  # Python dependencies (root)
├── environment.yml                   # Conda environment
├── README.md                         # This file
└── LICENSE
```

---

## ⚙️ Quick Start Guide

### Prerequisites
- **Python 3.10+** — [Download](https://www.python.org/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **Git** — Version control
- **FSL (optional)** — For preprocessing; instructions [here](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)
- **GPU (recommended)** — CUDA-capable device for training

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/<your-username>/NeuroAI-ADHD.git
cd NeuroAI-ADHD
```

### 2️⃣ Backend Setup

```bash
cd backend

# Create and activate Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (database, JWT secret, etc.)

# Initialize database
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Run development server
python run.py
```

API will be available at `http://localhost:8000`  
Swagger Docs: `http://localhost:8000/docs`

### 3️⃣ Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### 4️⃣ (Optional) Train ML Model

```bash
cd ml

# Preprocess fMRI data
python preprocessing/skull_strip.py
python preprocessing/normalize.py
python preprocessing/extract_rois.py

# Train ensemble model
python models/train.py --epochs 100 --batch-size 32 --lr 0.0001
```

---

## 🔍 Key Features

### ✅ Clinical Assessment
- **Patient Management**: Create and manage patient records with demographics
- **Standardized Assessments**: ADHD questionnaire integration
- **Scan Upload**: Secure NIfTI file upload with progress tracking
- **Role-Based Access**: Different permissions for clinicians, admins, and researchers

### ✅ Machine Learning
- **Automated Prediction**: BiLSTM-Transformer ensemble for ADHD classification
- **Confidence Scores**: Probability-based predictions with uncertainty
- **Cross-Validation**: 5-fold evaluation to prevent overfitting
- **GPU Acceleration**: CUDA support for fast inference

### ✅ Explainability (XAI)
- **Brain Region Attribution**: SHAP values identify which regions influenced prediction
- **Heatmaps**: Gradient-weighted activation maps overlaid on brain scans
- **Clinical Report**: Automated generation with interpretation and recommendations
- **Attention Visualization**: Model attention weights across brain regions

### ✅ Dashboard & Analytics
- **Real-time Statistics**: Patient demographics, diagnosis rates, trends
- **Model Performance**: Accuracy, sensitivity, specificity tracking
- **Report History**: Access previous assessments and predictions

---

## 🔐 Security & Privacy

- **JWT Authentication**: Token-based stateless auth
- **Password Hashing**: bcrypt for secure storage
- **RBAC**: Role-based access control (Clinician, Admin, Researcher)
- **HIPAA Compliance**: Patient data encryption at rest
- **CORS Configuration**: Restricted cross-origin requests
- **Rate Limiting**: API abuse prevention
- **Environment Secrets**: Sensitive data in `.env` (not in repo)

---

## 📚 Documentation

- **[Backend README](./backend/README.md)** — API endpoints, deployment, troubleshooting
- **[Frontend README](./frontend/README.md)** — Component structure, styling guide
- **[Architecture Guide](./docs/ARCHITECTURE.md)** — System design, data flow
- **[Deployment Guide](./docs/DEPLOYMENT.md)** — Production setup (Docker, cloud)
- **[Full Project Report](./docs/NeuroAI_ADHD_Report.pdf)** — Literature survey, methodology, results

---

## 👥 Team & Supervision

| Role | Name |
|---|---|
| **Lead Developer & ML Engineering** | Elan |
| **Data Processing & Feature Engineering** | [Team Member 2] |
| **Frontend Development & UI/UX** | [Team Member 3] |
| **Testing, Evaluation & Documentation** | [Team Member 4] |
| **Project Supervisor** | **Ms. Subathra C, M.E.** |

**Institution:** United Institute of Technology (UIT), Coimbatore  
**Affiliation:** Anna University, Chennai  
**Project Period:** 2025–2026 (Final Year)

---

## 📊 Project Status

- ✅ **Data Preprocessing**: Complete
- ✅ **Model Training**: Complete (BiLSTM-Transformer ensemble)
- ✅ **Backend API**: Complete
- ✅ **Frontend UI**: In Progress
- ✅ **XAI Module**: Complete
- 🔄 **Clinical Validation**: Planned
- 🔄 **Deployment**: In Progress

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the [MIT License](LICENSE) — free to use for academic and research purposes with attribution.

---

## 🙏 Acknowledgements

- [ADHD-200 Consortium](http://fcon_1000.projects.nitrc.org/indi/adhd200/) for the publicly available neuroimaging dataset
- [nilearn](https://nilearn.github.io/) — Neuroimaging analysis in Python
- [FastAPI](https://fastapi.tiangolo.com/) — Modern web framework
- [PyTorch](https://pytorch.org/) & [TensorFlow](https://www.tensorflow.org/) — Deep learning frameworks
- Open-source neuroimaging and ML community

---

## 📞 Support & Contact

For questions, issues, or inquiries:
- 📧 Contact project supervisor: **Ms. Subathra C**
- 🐛 Report bugs via GitHub Issues
- 💬 Discussions available for feature requests

---

<div align="center">

### Made with ❤️ as a Final Year Engineering Capstone
**United Institute of Technology, Coimbatore | Anna University | 2026**

[![Stars](https://img.shields.io/github/stars/<your-username>/NeuroAI-ADHD?style=social)](https://github.com/<your-username>/NeuroAI-ADHD)
[![Forks](https://img.shields.io/github/forks/<your-username>/NeuroAI-ADHD?style=social)](https://github.com/<your-username>/NeuroAI-ADHD)

</div>
