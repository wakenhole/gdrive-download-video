import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
import argparse
import gdrive_single_video_downloader

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class bcolors:
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def get_folder_name(service, folder_id):
    """Gets the name of a Google Drive folder."""
    try:
        file = service.files().get(fileId=folder_id, fields='name', supportsAllDrives=True).execute()
        return file.get('name')
    except Exception as e:
        print(f"An error occurred while fetching folder name: {e}")
        return None

def get_file_ids_in_folder(folder_id, verbose=False, videos_only=False):
    """Lists all video and PDF IDs in a specified Google Drive folder and its subfolders."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    file_ids = []
    folders_stack = [(folder_id, "")]

    while folders_stack:
        current_folder_id, current_path = folders_stack.pop()
        if verbose:
            print(f"[DEBUG] Processing folder: {current_folder_id}")
        page_token = None

        # Query to search for files within the specific folder
        file_types_query = "mimeType contains 'video'"
        if not videos_only:
            file_types_query += " or mimeType = 'application/pdf'"

        query = f"'{current_folder_id}' in parents and ({file_types_query} or mimeType = 'application/vnd.google-apps.folder' or mimeType = 'application/vnd.google-apps.shortcut') and trashed=false"
        if verbose:
            print(f"[DEBUG] Query: {query}")

        while True:
            response = service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType, shortcutDetails)',
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()

            files = response.get('files', [])
            if verbose:
                print(f"[DEBUG] Found {len(files)} items in response.")
            for file in files:
                if verbose:
                    print(f"[DEBUG] Item: {file.get('name')} | Type: {file.get('mimeType')}")
                if file.get('mimeType') == 'application/vnd.google-apps.folder':
                    if verbose:
                        print(f"[DEBUG] -> Adding subfolder to stack: {file.get('name')}")
                    new_path = os.path.join(current_path, file.get('name'))
                    folders_stack.append((file.get('id'), new_path))
                elif file.get('mimeType') == 'application/vnd.google-apps.shortcut':
                    shortcut_details = file.get('shortcutDetails')
                    if shortcut_details:
                        target_mime_type = shortcut_details.get('targetMimeType')
                        target_id = shortcut_details.get('targetId')
                        if target_mime_type == 'application/vnd.google-apps.folder':
                            if verbose:
                                print(f"[DEBUG] -> Found shortcut to folder. Adding target to stack: {file.get('name')} ({target_id})")
                            new_path = os.path.join(current_path, file.get('name'))
                            folders_stack.append((target_id, new_path))
                        elif target_mime_type and ('video' in target_mime_type or 'pdf' in target_mime_type):
                            print(f"Found shortcut to file: {file.get('name')} ({target_id})")
                            file_ids.append({'id': target_id, 'name': file.get('name'), 'path': current_path})
                else:
                    print(f"Found file: {file.get('name')} ({file.get('id')})")
                    file_ids.append({'id': file.get('id'), 'name': file.get('name'), 'path': current_path})

            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    return file_ids

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download files from a Google Drive folder.")
    parser.add_argument("folder_id", type=str, help="The Google Drive folder ID to scan for files.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    parser.add_argument("--videos-only", "--videos_only", dest="videos_only", action="store_true", help="Limit scanning to video files only (default scans videos + PDFs; downloads are always videos only).")
    args = parser.parse_args()

    target_folder_id = args.folder_id
    
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    root_folder_name = get_folder_name(service, target_folder_id)

    if not root_folder_name:
        print("Could not retrieve the root folder name. Exiting.")
        exit()

    all_files = get_file_ids_in_folder(target_folder_id, verbose=args.verbose, videos_only=args.videos_only)
    print(f"\nTotal files found: {len(all_files)}")

    total_counts = {}
    success_counts = {}

    for file_data in all_files:
        ext = os.path.splitext(file_data['name'])[1].lower()
        if not ext:
            ext = 'no_extension'
        total_counts[ext] = total_counts.get(ext, 0) + 1
        if ext not in success_counts:
            success_counts[ext] = 0

    for file_data in all_files:
        output_dir = os.path.join(root_folder_name, file_data['path'])
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        full_output_path = os.path.join(output_dir, file_data['name'])
        
        if os.path.exists(full_output_path):
            print(f"\nFile {full_output_path} already exists. Skipping download.")
            ext = os.path.splitext(file_data['name'])[1].lower()
            if not ext:
                ext = 'no_extension'
            success_counts[ext] = success_counts.get(ext, 0) + 1
            continue

        try:
            # Use the single-video downloader that is known to work
            gdrive_single_video_downloader.main(file_data['id'], output_file=full_output_path, verbose=args.verbose)
            was_success = True
        except Exception as e:
            print(f"\n{bcolors.FAIL}Download failed for {file_data['name']}: {e}{bcolors.ENDC}")
            if os.path.exists(full_output_path):
                print(f"Cleaning up incomplete download: {full_output_path}")
                os.remove(full_output_path)

    print("\n--- Download Summary ---")
    for ext, total in total_counts.items():
        success = success_counts.get(ext, 0)
        print(f"{ext}: {success} / {total}")

