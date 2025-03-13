"""Tools for interacting with Dropbox API."""

import logging
import os
from pathlib import Path

import dropbox

logger = logging.getLogger(__name__)


class DropboxClient:
    """Client for interacting with Dropbox API."""

    def __init__(self):
        app_key = os.getenv("DROPBOX_APP_KEY")
        app_secret = os.getenv("DROPBOX_SECRET")
        refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")

        if not app_key or not app_secret or not refresh_token:
            raise EnvironmentError(
                "Missing one or more required Dropbox environment variables: "
                "DROPBOX_APP_KEY, DROPBOX_SECRET, DROPBOX_REFRESH_TOKEN"
            )

        self.dbx = dropbox.Dropbox(
            oauth2_refresh_token=refresh_token, app_key=app_key, app_secret=app_secret
        )

        logger.info("Dropbox client initialized")
        logger.info(self.dbx)

    def list_files_recursive(
        self,
        path="/Genealogy",
        file_extensions=None,
        keyword_filters=None,
        exclude_patterns=None,
    ):
        """
        Recursively list all files in a given Dropbox path with optional filtering:
        - By file extensions.
        - By keyword filters (matches full path, not just file name).
        - Excludes files/folders whose FULL PATH contains specific patterns.

        Returns a list of matching file paths.
        """
        found_files = []  # List to store matching file paths

        try:
            result = self.dbx.files_list_folder(path)

            for entry in result.entries:
                file_path = entry.path_display  # Full path (Dropbox-style)

                # Check if the full path should be excluded
                if exclude_patterns and any(
                    pattern.lower() in file_path.lower() for pattern in exclude_patterns
                ):
                    continue  # Skip this file/folder

                if isinstance(entry, dropbox.files.FileMetadata):
                    # Check file extension filter
                    if file_extensions and not file_path.lower().endswith(
                        tuple(file_extensions)
                    ):
                        continue

                    # ✅ Check keyword filter (case insensitive match in **full path**)
                    if keyword_filters and not any(
                        keyword.lower() in file_path.lower()
                        for keyword in keyword_filters
                    ):
                        continue

                    found_files.append(file_path)

                elif isinstance(entry, dropbox.files.FolderMetadata):
                    # print(f"Processing folder: {file_path}")
                    found_files.extend(
                        self.list_files_recursive(
                            entry.path_lower,
                            file_extensions,
                            keyword_filters,
                            exclude_patterns,
                        )
                    )

            # Fetch remaining results if needed
            while result.has_more:
                result = dropbox.files_list_folder_continue(result.cursor)
                for entry in result.entries:
                    file_path = entry.path_display  # Full file path

                    if exclude_patterns and any(
                        pattern.lower() in file_path.lower()
                        for pattern in exclude_patterns
                    ):
                        continue  # Skip this file/folder

                    if isinstance(entry, dropbox.files.FileMetadata):
                        if file_extensions and not file_path.lower().endswith(
                            tuple(file_extensions)
                        ):
                            continue
                        if keyword_filters and not any(
                            keyword.lower() in file_path.lower()
                            for keyword in keyword_filters
                        ):
                            continue

                        found_files.append(file_path)

                    elif isinstance(entry, dropbox.files.FolderMetadata):
                        # print(f"Processing folder: {file_path}")
                        found_files.extend(
                            self.list_files_recursive(
                                entry.path_lower,
                                file_extensions,
                                keyword_filters,
                                exclude_patterns,
                            )
                        )

        except dropbox.exceptions.ApiError as err:
            print(f"Failed to list folder {path}: {err}")

        return found_files  # Return the list of matching file paths

    def download_file(self, file_path, local_path, target_dir):
        """
        Download files from a list of file paths.
        """
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        local_file = Path(local_path)
        if local_file.exists():
            print(f"Skipping: {local_path} (already exists)")
            return

        metadata, res = self.dbx.files_download(file_path)
        target_path = Path(target_dir) / Path(local_path)
        with open(Path(target_dir) / Path(local_path), "wb") as f:
            print(file_path, "->", target_path)
            f.write(res.content)

    def download_all_files(self, file_paths, local_path):
        """
        Download all files from a list of file paths.
        """
        os.makedirs(local_path, exist_ok=True)
        os.chdir(local_path)
        try:
            for file_path in file_paths:
                try:
                    local_filename = self.get_local_filename(file_path)
                    self.download_file(file_path, local_filename, local_path)
                except Exception as err:
                    print("Failed to download file", file_path, ":", err)
        finally:
            os.chdir("/content")

    def get_local_filename(self, filename):
        """
        Get new, local filename for the Dropbox file.
        """
        return filename.replace("/Genealogy/", "").replace("/", " - ")

    def cache_files(self, file_list, cache_dir="cache"):
        """
        Cache files from Dropbox to a local directory.
        """
        os.makedirs(cache_dir, exist_ok=True)
        for file_path in file_list:
            print(f"Processing file: {file_path}")
            local_filename = self.get_local_filename(file_path)
            print(f"Local filename: {local_filename}")
            cached_file = Path(cache_dir) / local_filename
            print(f"Cached file: {cached_file}")
            if cached_file.exists():
                print("File exists in cache")
            else:
                print("Downloading file...")
                self.download_file(file_path, local_filename, cache_dir)
            print("")
