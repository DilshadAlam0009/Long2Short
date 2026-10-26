from datetime import datetime, timezone


sessions = {}


def create_session(session_id: str):

    sessions[session_id] = {
        "history": [],
        "last_activity": datetime.now(timezone.utc)
    }


def get_history(session_id: str, limit: int = 20):

    session = sessions.get(session_id)

    if not session:
        return []

    return session["history"][-limit:]


def add_message(session_id: str, message):

    if session_id not in sessions:
        create_session(session_id)

    sessions[session_id]["history"].append(message)

    # Reset the 5-minute timer
    sessions[session_id]["last_activity"] = datetime.now(timezone.utc)


def session_exists(session_id: str):

    return session_id in sessions


def get_sessions():

    return sessions


def delete_session(session_id: str):

    sessions.pop(session_id, None)