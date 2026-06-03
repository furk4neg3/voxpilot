"""
VoxPilot API — TTS / Voice AI Studio PoC.

FastAPI application providing TTS synthesis, voice management,
metrics tracking, run history, and feedback collection.
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import (
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Query,
    Request,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.config import Settings, get_settings
from app.logging_config import setup_logging
from app.schemas import (
    ErrorResponse,
    FeedbackRequest,
    FeedbackResponse,
    FeedbackSummaryResponse,
    HealthResponse,
    MetricsResponse,
    SynthesizeResponse,
    VoicesResponse,
)
from app.services.cache_service import CacheService
from app.services.metrics_service import MetricsService
from app.services.synthesis_service import SynthesisService
from app.storage.database import Database
from app.storage.models import FeedbackRecord
from app.storage.repository import RunRepository
from app.tts import TTSEngine, create_engine
from app.tts.fake_engine import FakeTTSEngine

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # ── Settings ─────────────────────────────────────────────────────────
    settings: Settings = get_settings()

    # ── Logging ──────────────────────────────────────────────────────────
    setup_logging(settings.log_level)
    logger.info("Starting VoxPilot API")

    # ── Data directories ─────────────────────────────────────────────────
    audio_dir = Path(settings.audio_dir)
    audio_dir.mkdir(parents=True, exist_ok=True)
    logger.info(
        "Data directories ready",
        extra={"audio_dir": str(audio_dir)},
    )

    # ── Database ─────────────────────────────────────────────────────────
    database = Database(settings.db_path)
    database.init_db()
    logger.info("Database initialised", extra={"db_path": settings.db_path})

    # ── TTS engine ───────────────────────────────────────────────────────
    try:
        engine: TTSEngine = create_engine(settings.engine)
        logger.info(
            "TTS engine created",
            extra={"engine": engine.get_engine_name()},
        )
    except Exception as exc:
        logger.warning(
            "Failed to create requested TTS engine, falling back to FakeTTSEngine",
            extra={"requested_engine": settings.engine, "error": str(exc)},
        )
        engine = FakeTTSEngine()

    # ── Services ─────────────────────────────────────────────────────────
    cache_service = CacheService(str(audio_dir))
    metrics_service = MetricsService()
    run_repository = RunRepository(database)
    synthesis_service = SynthesisService(
        engine=engine,
        cache=cache_service,
        metrics=metrics_service,
        repository=run_repository,
        settings=settings,
    )

    # ── Attach to app state ──────────────────────────────────────────────
    app.state.settings = settings
    app.state.engine = engine
    app.state.cache_service = cache_service
    app.state.metrics_service = metrics_service
    app.state.run_repository = run_repository
    app.state.synthesis_service = synthesis_service

    logger.info(
        "VoxPilot API ready",
        extra={
            "engine": engine.get_engine_name(),
            "version": settings.app_version,
            "host": settings.host,
            "port": settings.port,
        },
    )

    yield  # ── Application runs here ─────────────────────────────────────

    # ── Shutdown ─────────────────────────────────────────────────────────
    logger.info("Shutting down VoxPilot API")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="VoxPilot API",
    description=(
        "Production-oriented TTS / Voice AI Studio PoC with synthesis, "
        "run history, caching, latency metrics, and feedback collection."
    ),
    version=get_settings().app_version,
    lifespan=lifespan,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)

# ── CORS (allow all origins for demo) ────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Normalize synthesis form validation errors to the app's 400 contract."""
    if request.url.path == "/synthesize":
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid synthesis request.", "errors": exc.errors()},
        )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


# ---------------------------------------------------------------------------
# Dependency injection helpers
# ---------------------------------------------------------------------------

def get_engine(request: Request) -> TTSEngine:
    """Return the active TTS engine from application state."""
    return request.app.state.engine


def get_synthesis_service(request: Request) -> SynthesisService:
    """Return the synthesis service from application state."""
    return request.app.state.synthesis_service


def get_metrics_service(request: Request) -> MetricsService:
    """Return the metrics service from application state."""
    return request.app.state.metrics_service


def get_run_repository(request: Request) -> RunRepository:
    """Return the run repository from application state."""
    return request.app.state.run_repository


def override_engine(engine: TTSEngine) -> None:
    """Override the TTS engine on the running app (useful for testing)."""
    app.state.engine = engine
    # Also update the synthesis service pointer so everything stays in sync.
    if hasattr(app.state, "synthesis_service"):
        app.state.synthesis_service.engine = engine
    logger.info(
        "TTS engine overridden",
        extra={"engine": engine.get_engine_name()},
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["System"],
)
async def health_check(
    engine: TTSEngine = Depends(get_engine),
) -> HealthResponse:
    """Return service health including engine status."""
    settings: Settings = get_settings()
    return HealthResponse(
        status="healthy",
        engine=engine.get_engine_name(),
        model_loaded=True,
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get(
    "/voices",
    response_model=VoicesResponse,
    summary="List available voices",
    tags=["Voices"],
)
async def list_voices(
    engine: TTSEngine = Depends(get_engine),
) -> VoicesResponse:
    """Return the list of voices supported by the active TTS engine."""
    voices = engine.get_voices()
    return VoicesResponse(
        voices=voices,
        engine=engine.get_engine_name(),
    )


@app.post(
    "/synthesize",
    response_model=SynthesizeResponse,
    summary="Synthesize speech from text",
    tags=["Synthesis"],
)
async def synthesize(
    request: Request,
    text: str = Form(..., description="Text to synthesize"),
    language: str = Form("en", description="Language code (BCP-47)"),
    voice: str = Form("default", description="Voice identifier"),
    style: Optional[str] = Form(None, description="Optional speaking style"),
    metadata: Optional[str] = Form(
        None,
        description="Optional JSON metadata string",
    ),
    synthesis_service: SynthesisService = Depends(get_synthesis_service),
) -> SynthesizeResponse:
    """Synthesize speech from text and persist generation metadata."""
    form = await request.form()
    if any(isinstance(value, StarletteUploadFile) for value in form.values()):
        raise HTTPException(
            status_code=400,
            detail="File uploads are not supported for speech generation.",
        )

    # ── Parse optional metadata ──────────────────────────────────────────
    parsed_metadata: Optional[dict] = None
    if metadata is not None:
        try:
            parsed_metadata = json.loads(metadata)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON in metadata field: {exc}",
            )

    # ── Synthesize ───────────────────────────────────────────────────────
    try:
        result: SynthesizeResponse = await synthesis_service.synthesize(
            text=text,
            voice=voice,
            language=language,
            metadata=parsed_metadata,
        )
        logger.info(
            "Synthesis completed",
            extra={
                "voice": voice,
                "language": language,
                "text_length": len(text),
            },
        )
        return result

    except ValueError as exc:
        logger.warning("Synthesis validation error", extra={"error": str(exc)})
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        logger.error(
            "Synthesis failed unexpectedly",
            extra={"error": str(exc)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Synthesis failed: {exc}",
        )


@app.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Get service metrics",
    tags=["Observability"],
)
async def get_metrics(
    engine: TTSEngine = Depends(get_engine),
    metrics_service: MetricsService = Depends(get_metrics_service),
    repository: RunRepository = Depends(get_run_repository),
) -> MetricsResponse:
    """Return aggregated service and feedback metrics."""
    metrics_data = metrics_service.get_metrics(engine.get_engine_name())
    metrics_data.update(repository.get_feedback_summary())
    return MetricsResponse(**metrics_data)


@app.post(
    "/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit generation feedback",
    tags=["Feedback"],
)
async def submit_feedback(
    feedback: FeedbackRequest,
    repository: RunRepository = Depends(get_run_repository),
) -> FeedbackResponse:
    """Persist quality feedback for a completed generation run."""
    if not repository.run_exists(feedback.run_id):
        raise HTTPException(
            status_code=404,
            detail=f"Generation run not found: {feedback.run_id}",
        )

    record = FeedbackRecord(
        run_id=feedback.run_id,
        rating=feedback.rating,
        naturalness=feedback.naturalness,
        clarity=feedback.clarity,
        latency_acceptability=feedback.latency_acceptability,
        comment=feedback.comment.strip() if feedback.comment else None,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    stored = repository.save_feedback(record)
    return FeedbackResponse(**stored)


@app.get(
    "/feedback/summary",
    response_model=FeedbackSummaryResponse,
    summary="Get feedback summary",
    tags=["Feedback"],
)
async def get_feedback_summary(
    repository: RunRepository = Depends(get_run_repository),
) -> FeedbackSummaryResponse:
    """Return aggregate quality feedback metrics."""
    return FeedbackSummaryResponse(**repository.get_feedback_summary())


@app.get(
    "/runs",
    summary="List synthesis runs",
    tags=["History"],
)
async def list_runs(
    limit: int = Query(50, ge=1, le=500, description="Max results to return"),
    status: Optional[str] = Query(None, description="Filter by run status"),
    voice: Optional[str] = Query(None, description="Filter by voice"),
    language: Optional[str] = Query(None, description="Filter by language"),
    cache_hit: Optional[bool] = Query(None, description="Filter by cache hit"),
    repository: RunRepository = Depends(get_run_repository),
) -> list[dict]:
    """Return a paginated list of synthesis run records."""
    try:
        runs = repository.get_runs(
            limit=limit,
            status=status,
            voice=voice,
            language=language,
            cache_hit=cache_hit,
        )
        return runs
    except Exception as exc:
        logger.error("Failed to fetch runs", extra={"error": str(exc)})
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve runs: {exc}",
        )


@app.get(
    "/audio/{filename}",
    summary="Serve synthesized audio file",
    tags=["Audio"],
)
async def serve_audio(
    filename: str,
    request: Request,
) -> FileResponse:
    """Serve a previously synthesized audio file from the audio directory."""
    settings: Settings = request.app.state.settings
    file_path = Path(settings.audio_dir) / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Audio file not found: {filename}",
        )

    # Basic path-traversal guard
    try:
        file_path.resolve().relative_to(Path(settings.audio_dir).resolve())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename",
        )

    return FileResponse(
        path=str(file_path),
        media_type="audio/wav",
        filename=filename,
    )
