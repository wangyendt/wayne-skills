"""Reference invariants shared by SQLite and PostgreSQL ledgers."""


def check_references(event, get_event, topic_exists, error):
    data = event["data"]
    if event["kind"] not in {"topic", "delete"} and not topic_exists(event["topic"]):
        raise error("Unknown topic; create or fetch it first")
    if event["kind"] == "assessment":
        user_found, sessions = False, set()
        for eid in data["evidence"]:
            ref = get_event(eid)
            if not ref:
                raise error("Evidence is absent; synchronize or hydrate first")
            if ref["kind"] != "message" or ref["topic"] != event["topic"]:
                raise error("Evidence must be a message in the same topic")
            sessions.add(ref["session"])
            user_found |= ref["data"]["role"] == "user"
        if not user_found:
            raise error("Assessment needs the learner's own answer")
        if len(sessions) != 1:
            raise error("One assessment evaluates one source session; keep independent attempts separate")
        for eid in data.get("supersedes", []):
            ref = get_event(eid)
            if not ref or ref["kind"] != "assessment" or ref["topic"] != event["topic"] or any(ref["data"][k] != data[k] for k in ("concept", "dimension")):
                raise error("Correction must refer to an existing assessment of the same concept/dimension")
    if event["kind"] == "checkpoint":
        for eid in data["parents"]:
            ref = get_event(eid)
            if not ref or ref["topic"] != event["topic"] or ref["kind"] != "checkpoint":
                raise error("Checkpoint parent is absent or belongs to another topic")
