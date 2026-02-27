from uuid import UUID

from app.celery_app import celery_app
from app.db.schema import Machine
from app.db.session import SessionLocal
from app.services import anomaly_service


@celery_app.task(name="anomaly.detect_machine")
def detect_machine_anomalies(machine_id: str) -> dict:
    """
    Celery task: run anomaly detection for a single machine.
    Called per-machine by the beat schedule.
    """
    with SessionLocal() as db:
        saved = anomaly_service.detect_and_save(db, UUID(machine_id))
    return {"machine_id": machine_id, "anomalies_saved": saved}


@celery_app.task(name="anomaly.detect_all")
def detect_all_machines() -> dict:
    """
    Celery beat entry point: fans out per-machine tasks for all active machines.
    """
    with SessionLocal() as db:
        machine_ids = [str(m.id) for m in db.query(Machine.id).all()]

    for m_id in machine_ids:
        detect_machine_anomalies.delay(m_id)

    return {"machines_dispatched": len(machine_ids)}
