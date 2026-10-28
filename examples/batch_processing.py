#!/usr/bin/env python3
"""
Batch processing example for YouTube Watcher.
Processes multiple YouTube videos from a file or list.
"""

import os
import sys
import json
import time
from pathlib import Path


def batch_process_videos(url_list, output_dir="output"):
    """
    Process multiple YouTube videos in batch.
    
    Args:
        url_list: List of YouTube URLs
        output_dir: Directory to save outputs
    
    Returns:
        Dictionary with results for each video
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    
    for i, url in enumerate(url_list, 1):
        print(f"\n{'='*60}")
        print(f"Processing video {i}/{len(url_list)}: {url}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Download audio
            from youtube_watcher import download_audio
            audio_path = download_audio(url, output_dir)
            
            if not audio_path:
                results[url] = {
                    "success": False,
                    "error": "Failed to download audio"
                }
                continue
            
            # Transcribe audio
            from youtube_watcher import transcribe_audio
            transcript_path = transcribe_audio(audio_path, output_dir)
            
            # Save results
            results[url] = {
                "success": True,
                "audio_file": Path(audio_path).name,
                "transcript_file": Path(transcript_path).name,
                "duration": time.time() - start_time,
            }
            
            print(f"✓ Completed in {results[url]['duration']:.1f}s")
            
        except Exception as e:
            results[url] = {
                "success": False,
                "error": str(e)
            }
            print(f"✗ Error: {e}")
    
    # Save summary JSON
    summary_file = Path(output_dir) / "batch_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Batch processing complete!")
    print(f"Results saved to: {summary_file}")
    print(f"{'='*60}")
    
    return results


def main():
    """Main entry point for batch processing."""
    # Default URLs (replace with your videos)
    urls = [
        "https://youtu.be/Bvucb9BpJ1U",  # Example video 1
        # "https://youtu.be/VIDEO_ID_2",  # Add more videos
    ]
    
    output_dir = "batch_output"
    
    print("YouTube Watcher - Batch Processing")
    print("=" * 60)
    print(f"Videos to process: {len(urls)}")
    print(f"Output directory: {output_dir}")
    print()
    
    results = batch_process_videos(urls, output_dir)
    
    # Print summary
    success_count = sum(1 for r in results.values() if r.get('success'))
    print(f"\nSummary: {success_count}/{len(urls)} videos processed successfully")
    
    return 0 if success_count == len(urls) else 1


if __name__ == "__main__":
    sys.exit(main())
