"""Bounded, credential-free image metadata shared by client and server."""
import base64
import hashlib
import json
import re
import unicodedata
import uuid

MAX_IMAGE = 25 * 1024 * 1024
MAX_WIRE = 36 * 1024 * 1024


class AssetError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def identity(value):
    try:
        if not isinstance(value, str) or str(uuid.UUID(value)) != value:
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise AssetError("Expected a canonical UUID") from None
    return value


def topic_id(profile, key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, profile + ":" + unicodedata.normalize("NFKC", key).strip().casefold()))


def metadata(value):
    if not isinstance(value, dict) or set(value) != {"asset_id", "profile", "topic_id", "topic_key", "session_id", "caption", "alt_text", "provenance", "sha256"}:
        raise AssetError("Invalid image metadata fields")
    for key, limit in (("profile", 200), ("topic_key", 500), ("caption", 8000), ("alt_text", 8000)):
        if not isinstance(value[key], str) or not value[key].strip() or len(value[key]) > limit:
            raise AssetError("Missing or oversized image description/identity")
    identity(value["asset_id"])
    identity(value["topic_id"])
    if value["session_id"] is not None:
        identity(value["session_id"])
    if value["topic_id"] != topic_id(value["profile"], value["topic_key"]):
        raise AssetError("Topic identity does not match profile/key")
    if not isinstance(value["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", value["sha256"]):
        raise AssetError("Invalid image SHA-256")
    if not isinstance(value["provenance"], dict):
        raise AssetError("Provenance must be an object")
    try:
        if len(canonical(value["provenance"]).encode()) > 16000:
            raise AssetError("Provenance exceeds 16 KB")
    except (ValueError, TypeError):
        raise AssetError("Provenance must be bounded finite JSON") from None
    return dict(value)


def decode_image(encoded, sha256):
    if not isinstance(encoded, str) or len(encoded) > (MAX_IMAGE + 2) // 3 * 4:
        raise AssetError("Image exceeds 25 MiB")
    try:
        data = base64.b64decode(encoded, validate=True)
    except (ValueError, __import__("binascii").Error):
        raise AssetError("Invalid image encoding") from None
    if not data or len(data) > MAX_IMAGE or hashlib.sha256(data).hexdigest() != sha256:
        raise AssetError("Image length or SHA-256 mismatch")
    return data


def object_key(prefix, profile, topic, asset_id, extension):
    if not re.fullmatch(r"[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_-]+)*/", prefix):
        raise AssetError("Invalid OSS root prefix")
    if extension not in {"png", "jpg", "webp"}:
        raise AssetError("Supported formats: PNG, JPEG, WebP")
    learner = hashlib.sha256(profile.encode()).hexdigest()[:20]
    return prefix + "assets/" + learner + "/" + identity(topic) + "/" + identity(asset_id) + "." + extension
