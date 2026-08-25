import hashlib
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.dataset import Dataset
from backend.app.models.project import Project
from backend.app.models.user import User
from backend.app.schemas.dataset import DatasetResponse
from backend.app.schemas.project import ProjectCreate, ProjectResponse
from backend.app.workers.tasks import process_dataset


router = APIRouter(tags=["projects"])
STORAGE_ROOT = Path(__file__).resolve().parents[3] / "storage" / "raw"
CHUNK_SIZE = 1024 * 1024


@router.get("/projects", response_model=list[ProjectResponse])
def list_projects(owner_id: str | None = None, db: Session = Depends(get_db)) -> list[Project]:
    query = select(Project).order_by(Project.created_at.desc())
    if owner_id:
        query = query.where(Project.owner_id == owner_id)
    return list(db.scalars(query).all())


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)) -> Project:
    project = db.scalar(select(Project).where(Project.id == project_id))
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.get("/projects/{project_id}/datasets", response_model=list[DatasetResponse])
def list_datasets(project_id: str, db: Session = Depends(get_db)) -> list[Dataset]:
    project = db.scalar(select(Project).where(Project.id == project_id))
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    query = select(Dataset).where(Dataset.project_id == project_id).order_by(Dataset.created_at.desc())
    return list(db.scalars(query).all())


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> Project:
    owner = db.scalar(select(User).where(User.id == payload.owner_id))
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project owner not found",
        )

    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.post(
    "/projects/{project_id}/datasets",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_dataset(
    project_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dataset:
    project = db.scalar(select(Project).where(Project.id == project_id))
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    original_name = Path(file.filename or "").name
    if Path(original_name).suffix.lower() != ".fasta":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .fasta files are supported",
        )

    STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4()}.fasta"
    destination = STORAGE_ROOT / stored_name
    checksum = hashlib.sha256()
    file_size = 0

    try:
        with destination.open("wb") as output_file:
            while chunk := await file.read(CHUNK_SIZE):
                output_file.write(chunk)
                checksum.update(chunk)
                file_size += len(chunk)
    except OSError as error:
        destination.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save the uploaded file",
        ) from error
    finally:
        await file.close()

    dataset = Dataset(
        project_id=project.id,
        name=Path(original_name).stem,
        file_name=original_name,
        file_path=str(destination.relative_to(STORAGE_ROOT.parent.parent)),
        file_size=file_size,
        checksum=checksum.hexdigest(),
        status="processing",
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    background_tasks.add_task(process_dataset, dataset.id)
    return dataset