#!/usr/bin/env python3
"""
YouTube Watcher - Downloads, transcribes, and summarizes YouTube videos using local tools.
Dependencies: yt-dlp, faster-whisper, local Qwen model
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path

def download_audio(video_url, output_dir):
    """Download audio from YouTube video using yt-dlp"""
    print("=== Downloading audio with yt-dlp ===")
    
    result = subprocess.run([
        'yt-dlp',
        '--js-runtimes', 'node',
        '-x',  # extract audio
        '--audio-format', 'wav',
        '-o', os.path.join(output_dir, 'video.%(ext)s'),
        '--no-playlist',
        '--no-warnings',
        video_url
    ], capture_output=True, text=True, timeout=300)
    
    if result.returncode == 0:
        # Find the downloaded file
        for f in os.listdir(output_dir):
            if f.endswith('.wav'):
                audio_path = os.path.join(output_dir, f)
                size_mb = os.path.getsize(audio_path) / (1024 * 1024)
                print(f"✓ Audio downloaded: {audio_path} ({size_mb:.1f} MB)")
                return audio_path
    else:
        print(f"✗ Download failed: {result.stderr[:300]}")
        return None

def transcribe_audio(audio_path, output_dir):
    """Transcribe audio using faster-whisper with fast-small model"""
    print("\n=== Transcribing with faster-whisper ===")
    
    from faster_whisper import WhisperModel
    
    # Load the fast-small model (good balance of speed/accuracy)
    model = WhisperModel("medium.en", device="cuda" if False else "cpu", compute_type="int8")
    
    # Transcribe
    segments, info = model.transcribe(audio_path, beam_size=5)
    
    print(f"Detected language: {info.language} ({info.language_probability:.2f})")
    print(f"Duration: {info.duration:.1f}s")
    
    # Save transcript
    transcript = ""
    for segment in segments:
        transcript += f"[{segment.start:.0f}s] {segment.text}\n"
    
    transcript_path = os.path.join(output_dir, 'transcript.txt')
    with open(transcript_path, 'w') as f:
        f.write(transcript)
    
    print(f"✓ Transcript saved: {transcript_path}")
    return transcript_path

def summarize_with_local_llm(transcript_path, output_dir):
    """Summarize transcript using local Qwen model"""
    print("\n=== Summarizing with local Qwen ===")
    
    with open(transcript_path, 'r') as f:
        transcript = f.read()
    
    # Create summary prompt
    prompt = f"""You are a helpful analyst. Summarize this video transcript and extract key information.

Video Transcript:
{transcript[:8000]}  # Use first 8000 chars to keep context manageable

Please provide:
1. Video title/topic (if discernible from content)
2. Main points discussed
3. Any specific topics, products, or concepts mentioned
4. Key takeaways or conclusions

Format your response clearly with headings."""

    # Use the local Qwen model via the existing endpoint
    llm_workspace = os.path.expanduser("~/.hermes/cache/browser-use/workspace")
    llm_script_path = os.path.join(llm_workspace, 'summarize_with_qwen.py')
    
    script_content = f'''
import subprocess
import os

transcript_path = "{transcript_path}"
output_dir = "{output_dir}"

with open(transcript_path, "r") as f:
    transcript = f.read()

# Create summary prompt  
prompt = """{prompt}"""

# Call local Qwen model (adjust path as needed)
model_path = "/Users/afonso/.local/share/qwen36-moe-mlx/model"

# Try using qwen36-moe command or similar
result = subprocess.run([
    "python", "-c", f"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_path = "{model_path}"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(
    model_path, 
    torch_dtype=torch.float16,
    device_map="auto"
)

messages = [{{"role": "user", "content": prompt}}]
input_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)
input_ids = torch.tensor(input_ids).unsqueeze(0).to("cuda" if torch.cuda.is_available() else "cpu")

outputs = model.generate(
    input_ids, 
    max_new_tokens=2000, 
    do_sample=True, 
    temperature=0.7, 
    top_p=0.95
)

response = outputs[0][input_ids.shape[1]:]
summary = tokenizer.decode(response, skip_special_tokens=True)
print(summary)
"""]
], capture_output=True, text=True, timeout=300)

if result.returncode == 0:
    summary = result.stdout.strip()
    summary_path = os.path.join(output_dir, 'summary.txt')
    with open(summary_path, 'w') as f:
        f.write(summary)
    print(f"✓ Summary saved: {summary_path}")
    print(f"Summary ({len(summary)} chars):\\n{summary[:500]}")
else:
    print(f"✗ LLM summary failed: {result.stderr[:300]}")
    # Fallback: just return the transcript
    return transcript

# Save metadata
metadata = {
    'video_url': 'https://youtu.be/Bvucb9BpJ1U',
    'audio_file': None,  # Will be filled in by download_audio
    'transcript_file': transcript_path,
    'summary_file': summary_path
}
'''
    
    with open(llm_script_path, 'w') as f:
        f.write(script_content)
    
    result = subprocess.run([
        'python', llm_script_path
    ], capture_output=True, text=True, timeout=300)
    
    print("LLM Summary Output:")
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr[:200]}")
    
    return result.stdout

def main():
    """Main workflow: download → transcribe → summarize"""
    video_url = "https://youtu.be/Bvucb9BpJ1U"
    workspace = os.path.expanduser("~/.hermes/cache/browser-use/workspace")
    output_dir = os.path.join(workspace, 'youtube_watcher_workspace')
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"YouTube Watcher - Processing: {video_url}")
    print(f"Output directory: {output_dir}\n")
    
    # Step 1: Download audio
    audio_path = download_audio(video_url, output_dir)
    if not audio_path:
        print("ERROR: Could not download audio. Please check your network or video URL.")
        return 1
    
    # Step 2: Transcribe audio
    transcript_path = transcribe_audio(audio_path, output_dir)
    
    # Step 3: Summarize with local LLM
    summarize_with_local_llm(transcript_path, output_dir)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
