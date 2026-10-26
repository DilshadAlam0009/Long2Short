from datetime import datetime, timezone, timedelta
from config import settings
from services.session import get_sessions, delete_session
from services.chroma import delete_session_documents

from fastapi import Path

SESSION_TIMEOUT = timedelta(minutes=1)


def cleanup_expired_sessions():

    now = datetime.now(timezone.utc)

    expired_sessions = []

    for session_id, session in list(get_sessions().items()):

        last_activity = session["last_activity"]

        if now - last_activity >= SESSION_TIMEOUT:

            expired_sessions.append(session_id)

    for session_id in expired_sessions:

        # Delete only this session's vectors
        delete_session_documents(session_id)

        # Delete uploaded PDF
        pdf_path = Path(settings.UPLOAD_PATH) / f"{session_id}.pdf"

        if pdf_path.exists():
            pdf_path.unlink()

        # Delete chat history and session
        delete_session(session_id)