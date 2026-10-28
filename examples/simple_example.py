#!/usr/bin/env python3
"""
Simple example: Download and transcribe a single YouTube video.
"""

import os
import sys
from pathlib import Path


def main():
    """Watch a single YouTube video."""
    # Default video (change this)
    video_url = "https://youtu.be/Bvucb9BpJ1U"
    output_dir = "/tmp"
    
    print(f"Watching: {video_url}")
    print(f"Output directory: {output_dir}\n")
    
    # Download audio
    from youtube_watcher import download_audio
    audio_path = download_audio(video_url, output_dir)
    
    if not audio_path:
        print("ERROR: Failed to download audio.")
        return 1
    
    print(f"\nAudio downloaded: {audio_path}\n")
    
    # Transcribe audio
    from youtube_watcher import transcribe_audio
    transcript_path = transcribe_audio(audio_path, output_dir)
    
    print(f"\nTranscript saved: {transcript_path}")
    print(f"\nTranscript preview (first 500 chars):")
    print("=" * 60)
    
    with open(transcript_path, 'r') as f:
        print(f.read()[:500])
    
    print(f"...\n(See full transcript: {transcript_path})")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
