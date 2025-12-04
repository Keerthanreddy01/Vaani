"""
VAANI Helper Utilities
Common utility functions used across the VAANI project.
"""

import os
import json
import csv
from pathlib import Path
from datetime import datetime
import hashlib


def load_json(filepath):
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, filepath, indent=2):
    """Save data to JSON file."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_csv(filepath):
    """Load CSV file as list of dictionaries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save_csv(data, filepath, fieldnames=None):
    """Save list of dictionaries to CSV file."""
    if not data:
        return
    
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    if fieldnames is None:
        fieldnames = list(data[0].keys())
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def ensure_dir(directory):
    """Ensure directory exists."""
    Path(directory).mkdir(parents=True, exist_ok=True)
    return directory


def get_timestamp(format='%Y%m%d_%H%M%S'):
    """Get current timestamp as string."""
    return datetime.now().strftime(format)


def get_file_hash(filepath, algorithm='md5'):
    """Calculate file hash."""
    hash_func = hashlib.new(algorithm)
    
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def format_duration(seconds):
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_size(bytes):
    """Format file size in bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} PB"


def normalize_text(text):
    """Normalize text for processing."""
    import re
    # Convert to lowercase
    text = text.lower()
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove special characters (keep alphanumeric and spaces)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text


def split_list(lst, n):
    """Split list into n roughly equal parts."""
    k, m = divmod(len(lst), n)
    return [lst[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]


def batch_iterator(iterable, batch_size):
    """Iterate over items in batches."""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers, returning default if denominator is zero."""
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return default


def merge_dicts(*dicts):
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def flatten_list(nested_list):
    """Flatten a nested list."""
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def get_project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


def get_data_dir():
    """Get data directory."""
    return get_project_root() / 'data'


def get_models_dir():
    """Get models directory."""
    return get_project_root() / 'models'


def get_logs_dir():
    """Get logs directory."""
    return get_project_root() / 'logs'


class Timer:
    """Simple timer context manager."""
    
    def __init__(self, name="Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, *args):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        print(f"{self.name} took {format_duration(duration)}")
    
    @property
    def elapsed(self):
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()


# Example usage
if __name__ == "__main__":
    print("🛠️  VAANI Helper Utilities Demo\n")
    
    # Test timer
    with Timer("Test operation"):
        import time
        time.sleep(1)
    
    # Test text normalization
    text = "Hello, World! This is a TEST."
    print(f"Original: {text}")
    print(f"Normalized: {normalize_text(text)}")
    
    # Test duration formatting
    print(f"\n30 seconds: {format_duration(30)}")
    print(f"90 seconds: {format_duration(90)}")
    print(f"3600 seconds: {format_duration(3600)}")
    
    # Test size formatting
    print(f"\n1024 bytes: {format_size(1024)}")
    print(f"1048576 bytes: {format_size(1048576)}")
    
    # Test batch iterator
    print(f"\nBatch iterator:")
    items = list(range(10))
    for batch in batch_iterator(items, 3):
        print(f"  Batch: {batch}")

