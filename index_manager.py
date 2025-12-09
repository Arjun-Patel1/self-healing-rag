# index_manager.py
import os
import json
import time
import shutil
from pathlib import Path

INDEX_DIR = Path("index_versions")
MANIFEST = INDEX_DIR / "manifest.json"

INDEX_DIR.mkdir(exist_ok=True)

def _now_tag():
    return time.strftime("%Y%m%dT%H%M%S")

def save_version(index_path: str, metadata_path: str):
    """
    Atomically save a copy of the index and metadata to a new version folder.
    """
    tag = _now_tag()
    version_folder = INDEX_DIR / tag
    version_folder.mkdir(parents=True, exist_ok=False)
    shutil.copy2(index_path, version_folder / Path(index_path).name)
    shutil.copy2(metadata_path, version_folder / Path(metadata_path).name)

    manifest = {"versions": []}
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text())
    manifest["versions"].append({
        "tag": tag,
        "index_file": str(version_folder / Path(index_path).name),
        "meta_file": str(version_folder / Path(metadata_path).name),
        "ts": tag
    })
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(f"[index_manager] Saved version {tag}")
    return tag

def list_versions():
    if not MANIFEST.exists():
        return []
    manifest = json.loads(MANIFEST.read_text())
    return manifest.get("versions", [])

def rollback_to(tag: str, dest_index_path: str, dest_meta_path: str):
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    for v in manifest.get("versions", []):
        if v["tag"] == tag:
            shutil.copy2(v["index_file"], dest_index_path)
            shutil.copy2(v["meta_file"], dest_meta_path)
            print(f"[index_manager] Rolled back to {tag}")
            return True
    print(f"[index_manager] Tag {tag} not found")
    return False
