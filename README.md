# GeneLab - Full-Stack Bioinformatics Platform

A full-stack web application designed for genomic data processing, DNA sequence analysis, and bioinformatics virtualization. 

## 🚀 Key Features
* *Asynchronous FASTA Parsing:* Uses Biopython core to efficiently read and handle genomic data sequences.
* *Background Processing Workers:* Offloads heavy sequence parsing tasks via FastAPI BackgroundTasks ensuring 100% server uptime.
* *Bioinformatic Metrics:* Computes essential sequence markers including precise Sequence Length and exact *GC-Content* percentage.
* *Secure Authentication System:* Implements secure user onboard processing with robust password hashing algorithms.

## 🛠️ Tech Stack
* *Backend:* Python 3.13, FastAPI, SQLAlchemy, Uvicorn
* *Bioinformatics:* Biopython, NumPy, Pandas
* *Database:* SQLite
* *Frontend:* React, TypeScript, Vite, TailwindCSS