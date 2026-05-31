from __future__ import annotations

import json
import mimetypes
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pandas as pd

from src.backtest.backtest import run_backtest


ROOT = Path(__file__).resolve().parent
OUTPUT_CSV = ROOT / "output" / "lsi_output.csv"
WEB_ROOT = ROOT / "web"

MODULES = [
    {
        "id": "m1",
        "title": "M1 Усреднение резервов",
        "signal": "m1_signal",
        "description": "Обязательные резервы и RUONIA",
    },
    {
        "id": "m2",
        "title": "M2 Репо ЦБ",
        "signal": "flag_demand",
        "description": "Спрос на рефинансирование и ставка",
    },
    {
        "id": "m3",
        "title": "M3 ОФЗ",
        "signal": "m3_signal",
        "description": "Аукционы федерального займа",
    },
    {
        "id": "m4",
        "title": "M4 Налоги",
        "signal": "m4_signal",
        "description": "Налоговые даты и сезонность",
    },
    {
        "id": "m5",
        "title": "M5 Казначейство",
        "signal": "m5_signal",
        "description": "Операции федерального казначейства",
    },
]


def _read_data() -> pd.DataFrame:
    if not OUTPUT_CSV.exists():
        return pd.DataFrame()

    df = pd.read_csv(OUTPUT_CSV, parse_dates=["date"])
    if "date" in df.columns:
        df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    return df


def _json_safe(value):
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value


def _records(df: pd.DataFrame) -> list[dict]:
    rows = []
    for row in df.to_dict(orient="records"):
        rows.append({key: _json_safe(value) for key, value in row.items()})
    return rows


def _status_bucket(status: str | None, lsi: float | None) -> str:
    text = (status or "").lower()
    if "positive" in text:
        return "watch"
    if "negative" in text:
        return "calm"
    if lsi is None:
        return "unknown"
    if lsi >= 0.6:
        return "watch"
    if lsi <= 0.4:
        return "calm"
    return "neutral"


def _latest_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "available": False,
            "message": "Нет данных. Запустите pipeline.py или POST /api/recalculate.",
        }

    latest = df.iloc[-1]
    lsi = _json_safe(latest.get("lsi"))
    lsi_smooth = _json_safe(latest.get("lsi_smooth"))
    quality = _json_safe(latest.get("data_quality"))
    status = _json_safe(latest.get("status"))

    return {
        "available": True,
        "date": _json_safe(latest.get("date")),
        "lsi": lsi,
        "lsi_smooth": lsi_smooth,
        "status": status,
        "status_bucket": _status_bucket(status, lsi_smooth if lsi_smooth is not None else lsi),
        "data_quality": quality,
        "data_quality_score": _json_safe(latest.get("data_quality_score")),
        "rows": int(len(df)),
        "range": {
            "start": _json_safe(df["date"].min()) if "date" in df else None,
            "end": _json_safe(df["date"].max()) if "date" in df else None,
        },
        "mean_lsi": _json_safe(df["lsi"].mean()) if "lsi" in df else None,
        "max_lsi": _json_safe(df["lsi"].max()) if "lsi" in df else None,
    }


def _module_summary(df: pd.DataFrame) -> list[dict]:
    items = []
    latest = df.iloc[-1] if not df.empty else pd.Series(dtype=object)

    for module in MODULES:
        col = module["signal"]
        series = pd.to_numeric(df[col], errors="coerce") if col in df else pd.Series(dtype=float)
        latest_value = _json_safe(latest.get(col)) if col in latest else None
        coverage = float(series.notna().mean()) if len(df) else 0.0

        items.append(
            {
                **module,
                "latest_value": latest_value,
                "coverage": coverage,
                "active": latest_value is not None,
                "mean": _json_safe(series.mean()) if not series.dropna().empty else None,
                "max": _json_safe(series.max()) if not series.dropna().empty else None,
            }
        )

    return items


def _api_response(path: str, query: dict[str, list[str]]) -> tuple[int, dict | list]:
    df = _read_data()

    if path == "/api/health":
        return 200, {"ok": True, "csv_exists": OUTPUT_CSV.exists(), "rows": int(len(df))}

    if path == "/api/summary":
        return 200, _latest_summary(df)

    if path == "/api/modules":
        return 200, _module_summary(df)

    if path == "/api/series":
        limit = int(query.get("limit", ["500"])[0])
        return 200, _records(df.tail(limit))

    if path == "/api/backtest":
        if df.empty:
            return 200, []
        result = run_backtest(df.copy())
        return 200, _records(result)

    return 404, {"error": "Unknown API endpoint"}


def _run_pipeline() -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "pipeline.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    return (
        200 if proc.returncode == 0 else 500,
        {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-4000:],
        },
    )


class AppHandler(BaseHTTPRequestHandler):
    server_version = "LiquiditySentinel/1.0"

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            status, payload = _api_response(path, parse_qs(parsed.query))
            self._send_json(status, payload)
            return

        self._send_static(path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/recalculate":
            status, payload = _run_pipeline()
            self._send_json(status, payload)
            return
        self._send_json(404, {"error": "Unknown API endpoint"})

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))

    def _send_json(self, status: int, payload: dict | list):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_static(self, path: str):
        rel = "index.html" if path in ("", "/") else path.lstrip("/")
        target = (WEB_ROOT / rel).resolve()

        if not str(target).startswith(str(WEB_ROOT.resolve())) or not target.exists() or target.is_dir():
            self.send_error(404)
            return

        content = target.read_bytes()
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if target.suffix in (".html", ".css", ".js"):
            ctype += "; charset=utf-8"

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main():
    host = "127.0.0.1"
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f"RU Liquidity Sentinel demo: http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
