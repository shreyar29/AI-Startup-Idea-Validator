from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    tier = Column(String, default="free") # free, premium, enterprise
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    reports = relationship("Report", back_populates="owner", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="owner", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")

class Report(Base):
    __tablename__ = "reports"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    startup_idea = Column(String, nullable=False)
    analysis_payload = Column(JSON, nullable=False)
    validation_score = Column(Integer, default=0)
    version = Column(Integer, default=1)
    parent_report_id = Column(String, ForeignKey("reports.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    owner = relationship("User", back_populates="reports")
    chat_sessions = relationship("ChatSession", back_populates="report")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    report_id = Column(String, ForeignKey("reports.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    owner = relationship("User", back_populates="chat_sessions")
    report = relationship("Report", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False) # user, vera, system
    content = Column(String, nullable=False)
    token_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    session = relationship("ChatSession", back_populates="messages")

class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"
    id = Column(String, primary_key=True, default=generate_uuid)
    request_id = Column(String, nullable=True, index=True)
    report_id = Column(String, ForeignKey("reports.id"), nullable=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=True)
    agent_name = Column(String, nullable=False, index=True)
    latency_seconds = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    failure_reason = Column(String, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

class Project(Base):
    """
    A Founder Workspace Project.
    """
    __tablename__ = "projects"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    report_id = Column(String, ForeignKey("reports.id"), nullable=True) # Linked validation report
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

class Task(Base):
    """
    Actionable task within a Project.
    """
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="Todo", index=True) # Todo, In Progress, Blocked, Done
    priority = Column(String, default="Medium") # Low, Medium, High, Critical
    assigned_to = Column(String, nullable=True) # Support future assignment
    due_date = Column(DateTime, nullable=True)
    source_metadata = Column(JSON, nullable=True) # E.g. {"agent": "swot", "module": "tows"}
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="tasks")

