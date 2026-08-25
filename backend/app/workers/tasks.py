from pathlib import Path

from sqlalchemy import select

from backend.app.core.database import PROJECT_ROOT, SessionLocal
from backend.app.models.dataset import Dataset
from backend.app.services.dna_service import analyze_fasta


def process_dataset(dataset_id: str) -> None:
    db = SessionLocal()
    try:
        dataset = db.scalar(select(Dataset).where(Dataset.id == dataset_id))
        if dataset is None:
            return

        dataset.status = "processing"
        db.commit()

        try:
            analysis = analyze_fasta(PROJECT_ROOT / Path(dataset.file_path))
            dataset.sequence_length = analysis.sequence_length
            dataset.gc_content = analysis.gc_content
            dataset.status = "completed"
            dataset.error_message = None
        except Exception as error:
            dataset.status = "error"
            dataset.error_message = str(error)[:1024]

        db.commit()
    finally:
        db.close()