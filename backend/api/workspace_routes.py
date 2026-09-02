from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from database.database import get_db
from database.models import Project, Task
from auth.jwt_manager import get_current_user

router = APIRouter(prefix="/api/workspace", tags=["workspace"])

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    report_id: Optional[str] = None

class TaskCreate(BaseModel):
    project_id: str
    title: str
    description: Optional[str] = None
    status: Optional[str] = "Todo"
    priority: Optional[str] = "Medium"
    source_metadata: Optional[Dict[str, Any]] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None

# --- PROJECTS ---

@router.get("/projects")
async def get_projects(db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.user_id == "guest").order_by(Project.created_at.desc())
    result = await db.execute(stmt)
    projects = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "report_id": p.report_id,
            "created_at": p.created_at
        }
        for p in projects
    ]

@router.post("/projects")
async def create_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db)):
    new_project = Project(
        user_id="guest",
        name=payload.name,
        description=payload.description,
        report_id=payload.report_id
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return {"id": new_project.id, "message": "Project created successfully"}

# --- TASKS ---

@router.get("/projects/{project_id}/tasks")
async def get_tasks(project_id: str, db: AsyncSession = Depends(get_db)):
    # Verify ownership
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    stmt = select(Task).where(Task.project_id == project_id).order_by(Task.created_at.desc())
    result = await db.execute(stmt)
    tasks = result.scalars().all()
    
    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "assigned_to": t.assigned_to,
            "source_metadata": t.source_metadata,
            "created_at": t.created_at
        }
        for t in tasks
    ]

@router.post("/tasks")
async def create_task(payload: TaskCreate, db: AsyncSession = Depends(get_db)):
    # Verify ownership of project
    stmt = select(Project).where(Project.id == payload.project_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    new_task = Task(
        project_id=payload.project_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        source_metadata=payload.source_metadata
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return {"id": new_task.id, "message": "Task created successfully"}

@router.patch("/tasks/{task_id}")
async def update_task(task_id: str, payload: TaskUpdate, db: AsyncSession = Depends(get_db)):
    # Verify ownership through JOIN
    stmt = select(Task).join(Project).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
        
    await db.commit()
    return {"message": "Task updated successfully"}
