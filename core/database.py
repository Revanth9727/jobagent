"""Database module — SQLAlchemy, SQLite, three tables: Observation, Company, Job."""

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional, Tuple

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = "sqlite:///data/jobs.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Observation(Base):
    """Append-only log of every sighting of a company or job."""

    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[Optional[str]] = mapped_column(String)
    source: Mapped[Optional[str]] = mapped_column(String)
    source_type: Mapped[Optional[str]] = mapped_column(String)
    company_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("companies.id"), nullable=True
    )
    job_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("jobs.id"), nullable=True
    )
    raw_url: Mapped[Optional[str]] = mapped_column(String)
    raw_title: Mapped[Optional[str]] = mapped_column(String)
    raw_company: Mapped[Optional[str]] = mapped_column(String)
    raw_location: Mapped[Optional[str]] = mapped_column(String)
    raw_payload: Mapped[Optional[Dict]] = mapped_column(JSON)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )


class Company(Base):
    """Company registry — tracks ATS type, promotion tier, sighting history."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    canonical_name: Mapped[Optional[str]] = mapped_column(String)
    careers_url: Mapped[Optional[str]] = mapped_column(String)
    ats_type: Mapped[str] = mapped_column(String, default="unknown")
    ats_board_url: Mapped[Optional[str]] = mapped_column(String)
    ats_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    discovery_source: Mapped[Optional[str]] = mapped_column(String)
    tracking_status: Mapped[str] = mapped_column(String, default="candidate")
    first_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    times_seen: Mapped[int] = mapped_column(Integer, default=1)
    best_role_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    roles_above_75: Mapped[int] = mapped_column(Integer, default=0)
    ignored_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reactivated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)


class Job(Base):
    """Canonical job records — one per unique posting."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id"), nullable=False
    )
    canonical_url: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    normalized_hash: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String)
    location: Mapped[Optional[str]] = mapped_column(String)
    country: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    first_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    age_days: Mapped[Optional[int]] = mapped_column(Integer)
    is_repost: Mapped[bool] = mapped_column(Boolean, default=False)
    source_type: Mapped[Optional[str]] = mapped_column(String)
    source_confidence: Mapped[Optional[str]] = mapped_column(String)
    hard_filtered: Mapped[bool] = mapped_column(Boolean, default=False)
    hard_filter_reason: Mapped[Optional[str]] = mapped_column(String)
    source_deduped: Mapped[bool] = mapped_column(Boolean, default=False)
    history_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    score_reason: Mapped[Optional[str]] = mapped_column(Text)
    key_matches: Mapped[Optional[List]] = mapped_column(JSON)
    red_flags: Mapped[Optional[List]] = mapped_column(JSON)
    talking_points: Mapped[Optional[List]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String, default="scraped")
    ats_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    route: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    resume_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cover_letter_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    applied_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    telegram_message_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)


def init_db() -> None:
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Context manager that yields a database session and handles cleanup."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_observation(
    session: Session,
    run_id: str,
    source: str,
    source_type: str,
    raw_data: Dict[str, Any],
) -> Observation:
    """Insert a new observation row and return it.

    Args:
        session: Active SQLAlchemy session.
        run_id: Identifier for this pipeline run.
        source: Where the data came from (e.g. "greenhouse").
        source_type: Category of source (e.g. "ats_api").
        raw_data: Dict with optional keys: url, title, company, location, payload,
                  company_id, job_id.

    Returns:
        The newly created Observation instance.
    """
    obs = Observation(
        run_id=run_id,
        source=source,
        source_type=source_type,
        company_id=raw_data.get("company_id"),
        job_id=raw_data.get("job_id"),
        raw_url=raw_data.get("url"),
        raw_title=raw_data.get("title"),
        raw_company=raw_data.get("company"),
        raw_location=raw_data.get("location"),
        raw_payload=raw_data.get("payload"),
    )
    session.add(obs)
    session.flush()
    return obs


def upsert_company(
    session: Session,
    name: str,
    discovery_source: str,
) -> Tuple["Company", bool]:
    """Find or create a company by name.

    Args:
        session: Active SQLAlchemy session.
        name: Company name (case-sensitive lookup).
        discovery_source: How we found this company.

    Returns:
        Tuple of (Company, created) where created=True if newly inserted.
    """
    company = session.query(Company).filter_by(name=name).first()
    if company:
        company.last_seen_at = _utcnow()
        company.times_seen = (company.times_seen or 0) + 1
        return company, False

    now = _utcnow()
    company = Company(
        name=name,
        canonical_name=name.lower().strip(),
        discovery_source=discovery_source,
        first_seen_at=now,
        last_seen_at=now,
    )
    session.add(company)
    session.flush()
    return company, True


def upsert_job(
    session: Session,
    canonical_url: str,
    company_id: int,
    data: Dict[str, Any],
) -> Tuple["Job", bool]:
    """Find or create a job by canonical URL.

    Args:
        session: Active SQLAlchemy session.
        canonical_url: Unique URL for this job posting.
        company_id: FK to the owning Company.
        data: Dict of job fields to set on creation or update last_seen_at on match.
              Expected keys match Job column names.

    Returns:
        Tuple of (Job, created) where created=True if newly inserted.
    """
    job = session.query(Job).filter_by(canonical_url=canonical_url).first()
    if job:
        job.last_seen_at = _utcnow()
        return job, False

    now = _utcnow()
    job = Job(
        canonical_url=canonical_url,
        company_id=company_id,
        normalized_hash=data.get("normalized_hash", ""),
        title=data.get("title"),
        location=data.get("location"),
        country=data.get("country"),
        description=data.get("description"),
        posted_at=data.get("posted_at"),
        first_seen_at=now,
        last_seen_at=now,
        age_days=data.get("age_days"),
        source_type=data.get("source_type"),
        source_confidence=data.get("source_confidence"),
        ats_type=data.get("ats_type"),
    )
    session.add(job)
    session.flush()
    return job, True


def get_jobs_for_scoring(session: Session) -> List["Job"]:
    """Return jobs ready to be scored: status='scraped', not hard-filtered, no score yet.

    Args:
        session: Active SQLAlchemy session.

    Returns:
        List of Job instances awaiting scoring.
    """
    return (
        session.query(Job)
        .filter(
            Job.status == "scraped",
            Job.hard_filtered.is_(False),
            Job.score.is_(None),
        )
        .all()
    )


def update_job_status(
    session: Session,
    job_id: int,
    status: str,
    **kwargs: Any,
) -> None:
    """Update a job's status and any additional fields.

    Args:
        session: Active SQLAlchemy session.
        job_id: Primary key of the job to update.
        status: New status string.
        **kwargs: Additional Job column values to set.
    """
    job = session.query(Job).filter_by(id=job_id).first()
    if not job:
        raise ValueError(f"Job {job_id} not found")
    job.status = status
    for key, value in kwargs.items():
        setattr(job, key, value)
    session.flush()
