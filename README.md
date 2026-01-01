# Google Drive File Downloader

This project provides a tool to recursively download files from a Google Drive folder. It is designed to handle videos and PDFs, but can be extended for other file types. The script preserves the original folder structure from Google Drive, making it easy to mirror a directory to your local machine.

## Features

*   **Recursive Download**: Scans a specified folder and all its subfolders.
*   **Handles Shortcuts**: Correctly resolves shortcuts to files and folders.
*   **Preserves Structure**: Re-creates the Google Drive folder hierarchy on your local disk, starting with a root folder named after the target Drive folder.
*   **File Type Filtering**: Downloads videos and PDFs by default.
*   **Videos-Only Mode**: Option to download only video files.
*   **Progress Bars**: Displays a progress bar for each download.
*   **Error Handling**: Reports failed downloads in red text.
*   **Download Summary**: Provides a summary at the end, showing the number of successful downloads for each file type.

## Prerequisites

1.  **Python 3.6+**
2.  **Google Cloud Project & Credentials:**
    *   Enable the **Google Drive API** in your Google Cloud project.
    *   Create an OAuth 2.0 Client ID and download the credentials JSON file.
    *   Save the file as `credentials.json` in the same directory as the script.
    *   For a guide, see: [Google Drive API Python Quickstart](https://developers.google.com/drive/api/v3/quickstart/python)
3.  **Dependencies:**
    Install the required Python packages using `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The primary script for downloading is `gdrive_video_download.py`.
### 1. Download a Single Video

Use `gdrive_videoloader.py` to download a specific video using its Video ID. 

```bash
python gdrive_video_download.py <FOLDER_ID> [options]
```
> VIDEO_ID: https://drive.google.com/file/d/<VIDEO_ID>/view?t=3
> Open video in new window or tab

### Options

*   `folder_id`: **(Required)** The ID of the Google Drive folder you want to download. This is the last part of the folder's URL.
*   `--videos-only`: (Optional) If specified, the script will only download video files and ignore PDFs.
*   `-v`, `--verbose`: (Optional) Enables detailed debug logging, showing the full scanning and download process.

### Examples

**1. Download All Videos and PDFs**

This command will scan the specified folder and download all supported files, creating a local directory named after the Google Drive folder.

```bash
python gdrive_video_download.py 1HFkHQYetpcNnyQoqvTxX1I1TAcF6Q0us
```

**2. Download Only Videos**

Use the `--videos-only` flag to restrict downloads to video files.

```bash
python gdrive_video_download.py 1HFkHQYetpcNnyQoqvTxX1I1TAcF6Q0us --videos-only
```
> FOLDER_ID: https://drive.google.com/drive/folders/<FOLDER_ID>

## Authentication

The first time you run the script, a browser window will open asking you to log in to your Google Account and grant permission. After you approve, a `token.pickle` file is created. This file stores your authentication token so you don't have to log in every time you run the script. If you change the API scopes, you will need to delete this file to re-authenticate.
