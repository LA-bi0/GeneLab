# GeneLab - Full-Stack Bioinformatics Platform

A full-stack web application designed for genomic data processing, DNA sequence analysis, and bioinformatics workflows.

## ✨ Key Features

- *Asynchronous FASTA Parsing:* Uses Biopython to efficiently read and process genomic data sequences.
- *Background Processing:* Offloads sequence-analysis tasks using FastAPI BackgroundTasks.
- *Bioinformatics Metrics:* Calculates sequence length and GC-content percentage.
- *Secure Authentication System:* Implements user authentication with password hashing.

## 🛠️ Tech Stack

- *Backend:* Python 3.13, FastAPI, SQLAlchemy, SQLite, Uvicorn
- *Bioinformatics:* Biopython, NumPy, Pandas
- *Frontend:* React, TypeScript, Vite, TailwindCSS

## 🚀 Quick Start

### 1. Backend Setup

bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload


### 2. Frontend Setup

bash
cd frontend
npm install
npm run dev


The frontend will be available at the local address shown by Vite, usually: http://localhost:5173

## 🧬 Example Analysis

A test FASTA sequence was successfully processed during development.

- Sequence length: 180 nucleotides
- GC-content: 43.33%

## 📁 Project Structure

text
GeneLab/
├── backend/
│   └── app/
│       ├── core/
│       ├── models/
│       ├── schemas/
│       ├── api/
│       ├── services/
│       ├── workers/
│       └── main.py
├── frontend/
│   └── src/
├── storage/
├── README.md
└── requirements.txt


## 🔬 Project Purpose

GeneLab combines full-stack web development with computational biology. The project demonstrates how genomic sequence data can be uploaded through a web interface, processed by a Python backend, analyzed using bioinformatics tools, and stored as structured application data.

## 🚧 Current Scope

The current version focuses on fundamental DNA sequence analysis, including FASTA processing, sequence length calculation, and GC-content calculation.

Future development may include additional sequence-analysis tools, visualization, alignment, and more advanced computational biology workflows.