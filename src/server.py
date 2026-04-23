"""
doubaoime-asr-server
OpenAI-compatible /v1/audio/transcriptions endpoint
backed by 豆包输入法 ASR (doubaoime-asr)
"""

import os
import sys

# 让 opuslib 能找到打包在一起的 opus.dll
# PyInstaller 打包后 sys._MEIPASS 是解压临时目录
if hasattr(sys, '_MEIPASS'):
    _bundle_dir = sys._MEIPASS
else:
    _bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Windows: 把 bundle 目录加到 DLL 搜索路径
if sys.platform == 'win32':
    os.add_dll_directory(_bundle_dir)
    # 同时设置环境变量，opuslib 会读这个
    os.environ['PATH'] = _bundle_dir + os.pathsep + os.environ.get('PATH', '')
    
import asyncio
import json
import logging
import os
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("asr-server")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
HOST = os.environ.get("ASR_HOST", "127.0.0.1")
PORT = int(os.environ.get("ASR_PORT", "5050"))
CREDENTIAL_PATH = os.environ.get(
    "ASR_CREDENTIAL_PATH",
    str(Path.home() / ".config" / "doubaoime-asr" / "credentials.json"),
)

# ---------------------------------------------------------------------------
# Lazy-import doubaoime_asr so startup errors are surfaced clearly
# ---------------------------------------------------------------------------
try:
    from doubaoime_asr import ASRConfig, transcribe  # type: ignore
    ASR_AVAILABLE = True
except ImportError as _e:
    ASR_AVAILABLE = False
    _IMPORT_ERROR = str(_e)


def _ensure_credential_dir():
    Path(CREDENTIAL_PATH).parent.mkdir(parents=True, exist_ok=True)


def _run_transcribe(audio_bytes: bytes, suffix: str) -> str:
    """Write audio to a temp file and call doubaoime_asr.transcribe."""
    if not ASR_AVAILABLE:
        raise RuntimeError(f"doubaoime_asr not available: {_IMPORT_ERROR}")

    _ensure_credential_dir()
    config = ASRConfig(credential_path=CREDENTIAL_PATH)

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name

    try:
        result = asyncio.run(transcribe(tmp_path, config=config))
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    return result or ""


# ---------------------------------------------------------------------------
# Multipart form-data parser (minimal, no external deps)
# ---------------------------------------------------------------------------

def _parse_multipart(body: bytes, boundary: bytes):
    """
    Returns a dict mapping field names to (filename_or_None, bytes_value).
    """
    fields: dict[str, tuple[str | None, bytes]] = {}
    delimiter = b"--" + boundary
    parts = body.split(delimiter)
    for part in parts:
        if part in (b"", b"--\r\n", b"--"):
            continue
        if part.startswith(b"\r\n"):
            part = part[2:]
        if part.endswith(b"\r\n"):
            part = part[:-2]
        if b"\r\n\r\n" not in part:
            continue
        headers_raw, content = part.split(b"\r\n\r\n", 1)
        headers_text = headers_raw.decode("utf-8", errors="replace")

        name = None
        filename = None
        for line in headers_text.splitlines():
            if line.lower().startswith("content-disposition:"):
                for token in line.split(";"):
                    token = token.strip()
                    if token.startswith('name="'):
                        name = token[6:-1]
                    elif token.startswith('filename="'):
                        filename = token[10:-1]

        if name:
            fields[name] = (filename, content)

    return fields


# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------

class ASRHandler(BaseHTTPRequestHandler):
    server_version = "doubaoime-asr-server/1.0"

    def log_message(self, fmt, *args):  # suppress default access log
        log.debug(fmt, *args)

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------

    def do_GET(self):
        if self.path in ("/", "/health"):
            self._send_json(200, {"status": "ok", "asr_available": ASR_AVAILABLE})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path.rstrip("/") == "/v1/audio/transcriptions":
            self._handle_transcription()
        else:
            self._send_json(404, {"error": "not found"})

    # ------------------------------------------------------------------
    # Transcription handler
    # ------------------------------------------------------------------

    def _handle_transcription(self):
        content_type = self.headers.get("Content-Type", "")
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        # Parse boundary
        boundary = None
        for part in content_type.split(";"):
            part = part.strip()
            if part.startswith("boundary="):
                boundary = part[9:].strip('"').encode()
                break

        if boundary is None:
            self._send_json(400, {"error": {"message": "Expected multipart/form-data"}})
            return

        fields = _parse_multipart(body, boundary)

        if "file" not in fields:
            self._send_json(400, {"error": {"message": "Missing 'file' field"}})
            return

        filename, audio_bytes = fields["file"]
        suffix = Path(filename).suffix if filename else ".wav"

        log.info("Received audio: %s bytes  file=%s", len(audio_bytes), filename)
        t0 = time.time()

        try:
            text = _run_transcribe(audio_bytes, suffix)
        except Exception as exc:
            log.exception("ASR failed: %s", exc)
            self._send_json(500, {"error": {"message": str(exc)}})
            return

        elapsed = time.time() - t0
        log.info("Transcribed in %.2fs: %s", elapsed, text[:80])

        # OpenAI-compatible response
        self._send_json(200, {"text": text})

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _send_json(self, code: int, data: dict):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if not ASR_AVAILABLE:
        log.error("doubaoime_asr import failed: %s", _IMPORT_ERROR)
        log.error("Make sure doubaoime-asr is installed correctly.")
        sys.exit(1)

    server = HTTPServer((HOST, PORT), ASRHandler)
    log.info("=" * 56)
    log.info(" doubaoime-asr-server  (OpenAI-compatible ASR)")
    log.info(" Listening on  http://%s:%d", HOST, PORT)
    log.info(" Endpoint      POST /v1/audio/transcriptions")
    log.info(" Credentials   %s", CREDENTIAL_PATH)
    log.info("=" * 56)
    log.info("LazyTyper settings:")
    log.info("  Model name : FunAudioLLM/SenseVoiceSmall  (or anything)")
    log.info("  API Endpoint: http://%s:%d/v1/audio/transcriptions", HOST, PORT)
    log.info("  API Key    : any-non-empty-string")
    log.info("=" * 56)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Shutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
