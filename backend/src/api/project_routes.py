from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from src.database.connection import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/projects", tags=["projects"])

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    article_url: Optional[str] = None
    article_text: Optional[str] = None
    article_type: Optional[str] = "url"

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: str

    class Config:
        from_attributes = True

@router.post("", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project."""
    try:
        # Import here to avoid circular imports
        from src.database.models import Project

        new_project = Project(
            name=project.name,
            description=project.description or "",
            user_id=None  # No auth, so no user
        )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        return {
            "id": new_project.id,
            "name": new_project.name,
            "description": new_project.description,
            "created_at": new_project.created_at.isoformat() if hasattr(new_project, 'created_at') else ""
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@router.get("", response_model=List[ProjectResponse])
async def list_projects(db: Session = Depends(get_db)):
    """List all projects."""
    try:
        from src.database.models import Project
        projects = db.query(Project).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "created_at": p.created_at.isoformat() if hasattr(p, 'created_at') else ""
            }
            for p in projects
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project."""
    try:
        from src.database.models import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at.isoformat() if hasattr(project, 'created_at') else ""
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch project: {str(e)}")

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    """Update a project."""
    try:
        from src.database.models import Project
        db_project = db.query(Project).filter(Project.id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")

        if project.name:
            db_project.name = project.name
        if project.description is not None:
            db_project.description = project.description

        db.commit()
        db.refresh(db_project)

        return {
            "id": db_project.id,
            "name": db_project.name,
            "description": db_project.description,
            "created_at": db_project.created_at.isoformat() if hasattr(db_project, 'created_at') else ""
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")

@router.delete("/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project."""
    try:
        from src.database.models import Project
        db_project = db.query(Project).filter(Project.id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")

        db.delete(db_project)
        db.commit()

        return {"success": True, "message": f"Project {project_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")
