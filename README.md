# Google Drive Video Downloader

Recursively scan a Google Drive folder (including subfolders and shortcuts) and download its video files while preserving the original folder structure locally. The folder name from Drive becomes the local root, and existing files are skipped.

## Features

- Recursively scans folders and shortcuts; works with shared drives.
- Recreates the Drive folder tree locally under the Drive folder name.
- Downloads only video files (uses `gdrive_single_video_downloader.py` for reliable downloading). Non-video files are currently skipped; default scan includes PDFs, but `--videos-only` can restrict scanning to videos.
- Skips files that already exist at the target path.
- Verbose mode to see Drive queries and traversal details.

## Prerequisites

1) Python 3.6+
2) Google Drive API enabled + OAuth 2.0 Client ID JSON saved as `credentials.json` next to the scripts. Guide: https://developers.google.com/drive/api/v3/quickstart/python  
3) Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Download videos from a folder (current behavior)
```bash
python gdrive_download.py <FOLDER_ID> [--videos-only] [-v]
```
- `FOLDER_ID` is the last segment of the Drive folder URL (https://drive.google.com/drive/folders/<FOLDER_ID>).
- `-v` shows detailed traversal logs.
- `--videos-only` (or `--videos_only`): Restrict scanning to video files only (default scan includes videos + PDFs; downloads are always videos).

The script will create a local directory named after the Drive folder and mirror its subfolders, downloading videos into their respective paths. Non-video files (e.g., PDFs) are detected but skipped.

### Download a single video by ID
If you already know a specific video ID, you can directly call:
```bash
python gdrive_single_video_downloader.py <VIDEO_ID> [-o OUTPUT] [-c CHUNK] [-v] [--version]
```
Options for single-video downloads:
- `-o, --output`: Custom output filename (default: video title from Drive).
- `-c, --chunk_size`: Chunk size in bytes for HTTP streaming; default `1024`.
- `-v, --verbose`: Verbose logging.
- `--version`: Show script version and exit.

## Authentication

On first run, a browser window opens for Google login and consent. A `token.pickle` file is saved for reuse. Delete it if you change scopes or need to re-authenticate.
