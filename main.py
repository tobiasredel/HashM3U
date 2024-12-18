import logging
import os
import requests
import hashlib
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, RedirectResponse, JSONResponse
import io
from typing import Dict
import re
import uvicorn


# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
scheduler = BackgroundScheduler()

MAPPINGS: Dict[str, Dict] = {}
M3U_URL = os.getenv("M3U_SOURCE_URL", "http://example.com/playlist.m3u")
M3U_HOSTPORT = os.getenv("M3U_HOSTPORT", "localhost:8000")
M3U_UPDATEHOURS = os.getenv("M3U_UPDATEHOURS", 2)


def generate_hash(name: str) -> str:
    return hashlib.sha256(name.encode()).hexdigest()[:16]


def download_m3u(url: str) -> str:
    logger.info(f"Downloading M3U from {url}...")
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def update_mapping(m3u_url: str):
    global MAPPINGS
    logger.info("Updating M3U mappings...")
    m3u_content = download_m3u(m3u_url)
    new_mappings = {}

    lines = m3u_content.splitlines()
    line_iter = iter(lines)

    for line in line_iter:
        if line.startswith("#EXTINF"):
            metadata = line
            tvg_name = get_tvg_name(metadata)
            stream_url = next(line_iter, "").strip()

            if tvg_name and stream_url:
                unique_hash = generate_hash(tvg_name)
                new_mappings[unique_hash] = {
                    "url": stream_url,
                    "tvg_name": tvg_name,
                    "metadata": metadata,
                }
                logger.debug(f"Added mapping: {tvg_name} -> {unique_hash}")

    MAPPINGS = new_mappings
    logger.info(f"{len(MAPPINGS)} mappings updated successfully.")


def get_tvg_name(line: str) -> str:
    match = re.search(r'tvg-name="([^"]+)"', line)
    if match:
        return match.group(1)  # Gibt den gesamten TVG-Namen zurück
    return None

def generate_proxified_m3u() -> str:
    logger.info("Generating proxified M3U...")
    proxified_content = "#EXTM3U\n"
    for hash, data in MAPPINGS.items():
        metadata = data["metadata"]

        # Stelle sicher, dass die Anführungszeichen korrekt bleiben und nicht escaped werden
        proxified_content += f'{metadata}\n'
        proxified_content += f'http://{M3U_HOSTPORT}/proxy/{hash}\n'
    return proxified_content

@app.get("/playlist.m3u")
def serve_proxified_playlist():
    # Erstelle die M3U-Datei als String
    playlist_content = generate_proxified_m3u()

    # Konvertiere den Inhalt in ein BytesIO-Objekt (das wie eine Datei funktioniert)
    playlist_io = io.BytesIO(playlist_content.encode('utf-8'))

    # Setze den HTTP-Header für den Dateidownload
    return StreamingResponse(playlist_io, media_type="application/x-mpegURL", headers={
        "Content-Disposition": "attachment; filename=playlist.m3u"
    })

@app.get("/proxy/{hash_id}")
def proxy_stream(hash_id: str):
    mapping = MAPPINGS.get(hash_id)
    if mapping:
        logger.info(f"Proxying stream for hash: {hash_id} -> {mapping['url']}")

        return RedirectResponse(url=mapping['url'])

    logger.warning(f"Stream not found for hash: {hash_id}")
    return {"error": "Stream not found"}

def schedule_mapping_update():
    scheduler.add_job(update_mapping, "interval", hours=int(M3U_UPDATEHOURS), args=[M3U_URL])
    scheduler.start()

# FastAPI-Endpunkt (zum Testen)
@app.get("/")
def read_root():
    info = {
        "mappings": len(MAPPINGS),
        "next_refresh": f'{scheduler.get_jobs()[0].next_run_time:%Y-%m-%d %H:%M:%S}'
    }
    return JSONResponse(content=info)


if __name__ == "__main__":
    # Direktes Update beim Starten
    logger.info("Performing initial update of mappings...")
    update_mapping(M3U_URL)  # Initiales Update
    logger.info("Initial mapping update complete.")

    # Planung der Aktualisierung alle 2 Stunden
    schedule_mapping_update()

    # Starte FastAPI-Server
    uvicorn.run(app, host="0.0.0.0", port=8000)
