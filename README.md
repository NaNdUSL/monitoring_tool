# Directory Synchronization Tool

A Python-based tool that synchronizes a source directory with a replica directory. It continuously monitors the source directory for changes (additions, updates, deletions) and applies those changes to the replica directory. All operations are logged with detailed information, including timestamps.

## Features

- **Real-Time Monitoring**: The tool runs in a separate thread to monitor the source directory continuously.
- **Automatic Synchronization**: The tool will:
  - **Copy new files** from the source to the replica.
  - **Update files** in the replica if the source file is changed or has a different size.
  - **Delete files or directories** in the replica that no longer exist in the source.
- **Logging**: Logs every file operation (copy, update, delete) with timestamps for tracking.
- **Configurable Interval**: The monitoring interval is configurable (default is 1 second).

## Requirements

- Python 3.x or higher
- No additional dependencies are required beyond Python's standard library.

## Usage

To start the directory synchronization, run the following command:

```bash
python src.py <source_dir> <target_dir> <log_file>