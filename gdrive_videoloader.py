from urllib.parse import unquote
import requests
import argparse
import sys
from tqdm import tqdm
import os

def get_video_url(page_content: str, verbose: bool) -> tuple[str, str]:
    """Extracts the video playback URL and title from the page content."""
    if verbose:
        print("[INFO] Parsing video playback URL and title.")
    contentList = page_content.split("&")
    video, title = None, None
    for content in contentList:
        if content.startswith('title=') and not title:
            title = unquote(content.split('=')[-1])
        elif "videoplayback" in content and not video:
            video = unquote(content).split("|")[-1]
        if video and title:
            break

    if verbose:
        print(f"[INFO] Video URL: {video}")
        print(f"[INFO] Video Title: {title}")
    return video, title

def download_file(url: str, cookies: dict, filename: str, chunk_size: int, verbose: bool) -> None:
    """Downloads the file from the given URL with provided cookies, supports resuming."""
    headers = {}
    file_mode = 'wb'
    is_resuming = False

    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        downloaded_size = os.path.getsize(filename)
        headers['Range'] = f"bytes={downloaded_size}-"
        file_mode = 'ab'
        is_resuming = True
    else:
        downloaded_size = 0

    if verbose:
        print(f"[INFO] Starting download from {url}")
        if is_resuming:
            print(f"[INFO] Resuming download from byte {downloaded_size}")

    try:
        response = requests.get(url, stream=True, cookies=cookies, headers=headers)
        
        if not (response.status_code == 200 or (is_resuming and response.status_code == 206)):
             print(f"Error downloading {filename}, status code: {response.status_code}")
             return

        total_size = int(response.headers.get('content-length', 0)) + downloaded_size
        
        with open(filename, file_mode) as file:
            with tqdm(total=total_size, initial=downloaded_size, unit='B', unit_scale=True, desc=filename, file=sys.stdout) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
                        pbar.update(len(chunk))
        
        if os.path.getsize(filename) < total_size:
            raise IOError("Download incomplete.")

        print(f"\n{filename} downloaded successfully.")

    except (Exception, KeyboardInterrupt) as e:
        print(f"\nDownload failed for {filename}: {e}")
        if os.path.exists(filename):
            print(f"Cleaning up incomplete download: {filename}")
            os.remove(filename)

def main(video_id: str, output_file: str = None, chunk_size: int = 1024, verbose: bool = False) -> None:
    """Main function to process video ID and download the video file."""
    drive_url = f'https://drive.google.com/u/0/get_video_info?docid={video_id}&drive_originator_app=303'
    
    if verbose:
        print(f"[INFO] Accessing {drive_url}")

    response = requests.get(drive_url)
    page_content = response.text
    cookies = response.cookies.get_dict()

    video, title = get_video_url(page_content, verbose)

    filename = output_file if output_file else title
    if video:
        download_file(video, cookies, filename, chunk_size, verbose)
    else:
        print("Unable to retrieve the video URL. Ensure the video ID is correct and accessible.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to download videos from Google Drive.")
    parser.add_argument("video_id", type=str, help="The video ID from Google Drive (e.g., 'abc-Qt12kjmS21kjDm2kjd').")
    parser.add_argument("-o", "--output", type=str, help="Optional output file name for the downloaded video (default: video name in gdrive).")
    parser.add_argument("-c", "--chunk_size", type=int, default=1024, help="Optional chunk size (in bytes) for downloading the video. Default is 1024 bytes.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode.")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    main(args.video_id, args.output, args.chunk_size, args.verbose)
