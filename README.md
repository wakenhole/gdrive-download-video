# Google Drive Video Downloader

This project provides tools to download videos from Google Drive. It supports downloading individual videos by ID or scanning a folder (including subfolders and shortcuts) to download all videos while preserving the directory structure.

## Prerequisites

1.  **Python 3.6+**
2.  **Google Cloud Project & Credentials:**
    *   Enable the **Google Drive API**.
    *   Download the OAuth 2.0 Client ID JSON file and save it as `credentials.json` in the project directory.
    *   Reference: [Google Drive API Python Quickstart](https://ai.google.dev/palm_docs/oauth_quickstart?hl=ko)
3.  **Dependencies:**
    Install the required Python packages using `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
    Or install them manually:
    ```bash
    pip install google-api-python-client google-auth-oauthlib requests tqdm
    ```

## Usage

### 1. Download a Single Video

Use `gdrive_videoloader.py` to download a specific video using its Video ID. 

```bash
python gdrive_videoloader.py <VIDEO_ID> [options]
```
> VIDEO_ID: https://drive.google.com/file/d/<VIDEO_ID>/view?t=3
> Open video in new window or tab

**Options:**
*   `video_id`: The ID of the video file on Google Drive.
*   `-o`, `--output`: (Optional) Output filename. Defaults to the video title from Drive.
*   `-c`, `--chunk_size`: (Optional) Download chunk size in bytes. Default is 1024.
*   `-v`, `--verbose`: Enable verbose logging.

**Example:**
```bash
python gdrive_videoloader.py 1HFkHQYetpcNnyQoxxxxxX1I1TAcF6Q0us -o my_video.mp4 -v
```

### 2. Download All Videos from a Folder

Use `gdrive_video_download.py` to recursively scan a Google Drive folder and download all videos.

*   Scans subfolders and shortcuts.
*   Preserves the folder structure locally.
*   Skips non-video files.

```bash
python gdrive_video_download.py <FOLDER_ID> [options]
```

**Options:**
*   `folder_id`: The ID of the Google Drive folder to scan. ()
*   `-v`, `--verbose`: Enable debug logging to see the scanning process.

**Example:**
```bash
python gdrive_video_download.py 1HFkHQYetpcNnyQoxxxxxX1I1TAcF6Q0us -v
```
> FOLDER_ID: https://drive.google.com/drive/folders/<FOLDER_ID>

## Authentication

On the first run, a browser window will open to authenticate with your Google account. A `token.pickle` file will be created to store your access token for future runs.
