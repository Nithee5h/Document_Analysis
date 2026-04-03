import base64
import tempfile
from pathlib import Path


EXT_MAP = {
    "pdf": ".pdf",
    "docx": ".docx",
    "image": ".png",
}


def decode_base64_to_temp_file(file_base64: str, file_type: str) -> Path:
    raw = base64.b64decode(file_base64, validate=False)
    suffix = EXT_MAP[file_type]
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp.write(raw)
    temp.flush()
    temp.close()
    return Path(temp.name)


def get_file_size_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)