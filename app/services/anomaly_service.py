from datetime import datetime, timedelta, timezone
from uuid import UUID

import pandas as pd
from adtk.data import validate_series
from adtk.detector import InterQuartileRangeAD, PersistAD
from sqlalchemy.orm import Session

from app.db.schema import AnomalyEvent, MeasurementEvent

DETECTORS = {"iqr": InterQuartileRangeAD(c=1.5), "persist": PersistAD(c=3.0, side="both")}


METRICS = ["voltage", "current", "rpm", "torque"]


def detect_and_save(db: Session, machine_id: UUID, lookback_hours: int = 1) -> int:
    """
    Run anomaly detection on recent measurements for a machine.
    Returns the number of anomalies saved.
    """
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=lookback_hours)

    rows = (
        db.query(MeasurementEvent)
        .filter(
            MeasurementEvent.machine_id == machine_id,
            MeasurementEvent.timestamp >= start_time,
            MeasurementEvent.timestamp <= end_time,
        )
        .order_by(MeasurementEvent.timestamp.asc())
        .all()
    )

    if len(rows) < 10:  # Minimum 10 data points guard prevents ADTK from crashing on sparse data
        return 0

    df = pd.DataFrame(
        [
            {
                "timestamp": r.timestamp,
                "voltage": r.voltage,
                "current": r.current,
                "rpm": r.rpm,
                "torque": r.torque,
            }
            for r in rows
        ]
    ).set_index("timestamp")
    df.index = pd.to_datetime(df.index, utc=True)

    saved = 0
    for metric in METRICS:
        series = df[metric].dropna()
        if len(series) < 10:
            continue

        series = validate_series(series)

        for detector_name, detector in DETECTORS.items():
            try:
                anomalies = detector.fit_detect(series)
            except Exception:
                continue

            for ts, is_anomaly in anomalies.items():
                if not is_anomaly:
                    continue
                value = series.get(ts)
                if value is None:
                    continue
                event = AnomalyEvent(
                    machine_id=machine_id,
                    timestamp=ts.to_pydatetime(),
                    metric=metric,
                    value=float(value),
                    score=1.0,
                    detector=detector_name,
                )
                db.merge(
                    event
                )  # used to not re-run detection over the same window and won't crate duplicates
                saved += 1

    if saved:
        db.commit()

    return saved


def get_anomalies(
    db: Session,
    machine_id: UUID,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = 100,
) -> list[AnomalyEvent]:
    """
    Query stored anomaly events for a machine
    """

    query = db.query(AnomalyEvent).filter(AnomalyEvent.machine_id == machine_id)

    if start_time:
        query = query.filter(AnomalyEvent.timestamp >= start_time)

    if end_time:
        query = query.filter(AnomalyEvent.timestamp <= end_time)

    return query.order_by(AnomalyEvent.timestamp.desc()).limit(limit).all()
