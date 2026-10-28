# Examples for YouTube Watcher

## Basic Usage

### Watch a Single Video
```python
from youtube_watcher import download_audio, transcribe_audio

# Download and transcribe a video
audio_path = download_audio(
    video_url="https://youtu.be/Bvucb9BpJ1U",
    output_dir="/tmp"
)

if audio_path:
    transcript_path = transcribe_audio(
        audio_path=audio_path,
        output_dir="/tmp"
    )
    print(f"Transcript saved to: {transcript_path}")
```

### Watch Multiple Videos
```python
urls = [
    "https://youtu.be/VIDEO_ID_1",
    "https://youtu.be/VIDEO_ID_2",
    "https://youtu.be/VIDEO_ID_3",
]

for url in urls:
    audio = download_audio(url, "/tmp/output")
    if audio:
        transcribe_audio(audio, "/tmp/output")
```

## Command Line Usage

### Watch a Single Video
```bash
python youtube_watcher.py --url "https://youtu.be/VIDEO_ID"
```

### Watch Multiple Videos (from file)
```bash
# Create a file with one URL per line: videos.txt
echo "https://youtu.be/VIDEO1" > videos.txt
echo "https://youtu.be/VIDEO2" >> videos.txt

# Process all videos
python youtube_watcher.py --urls videos.txt
```

### Skip Transcription (Download Only)
```bash
python youtube_watcher.py --url "https://youtu.be/VIDEO_ID" --no-transcript
```

### Skip LLM Summary (Transcript Only)
```bash
python youtube_watcher.py --url "https://youtu.be/VIDEO_ID" --no-summary
```

### Use Different Whisper Model
```bash
# Use smaller model (faster, less accurate)
python youtube_watcher.py --url "https://youtu.be/VIDEO_ID" --whisper-model small.en

# Use larger model (slower, more accurate)
python youtube_watcher.py --url "https://youtu.be/VIDEO_ID" --whisper-model large-v3
```

## API Integration

### With LangChain
```python
from langchain_community.document_loaders import TextLoader
from youtube_watcher import download_audio, transcribe_audio

# Watch video and load transcript
audio = download_audio("https://youtu.be/VIDEO_ID", "/tmp")
transcript = transcribe_audio(audio, "/tmp")

# Load into LangChain
loader = TextLoader(transcript)
documents = loader.load()
```

### With LangChain Summarization
```python
from langchain.chains import MapReduceDocumentsChain
from langchain.prompts import PromptTemplate

# After getting transcript
prompt = PromptTemplate.from_template("""
Summarize the following video transcript:
{text}

Key points:
""")

# Use your preferred LLM
chain = MapReduceDocumentsChain(
    llm_chain=LLMChain(llm=OpenAI(), prompt=prompt),
    document_variable_name="text"
)
result = chain.run(documents)
print(result)
```

### With AutoGPT Plugin
```python
# Create a plugin that calls youtube_watcher.py
import subprocess

def watch_video(video_url: str) -> dict:
    """Watch a YouTube video and return transcript."""
    result = subprocess.run([
        "python3", "youtube_watcher.py",
        "--url", video_url,
        "--no-summary"  # Skip LLM if not needed
    ], capture_output=True, text=True)
    
    return {
        "success": result.returncode == 0,
        "transcript_path": result.stdout.strip()
    }
```

## Custom Workflow

### Batch Process with Progress Tracking
```python
from youtube_watcher import download_audio, transcribe_audio
import time

urls = [
    "https://youtu.be/VIDEO_ID_1",
    "https://youtu.be/VIDEO_ID_2",
    "https://youtu.be/VIDEO_ID_3",
]

output_dir = "/tmp/batch_output"
import os
os.makedirs(output_dir, exist_ok=True)

for i, url in enumerate(urls, 1):
    print(f"\nProcessing video {i}/{len(urls)}: {url}")
    start = time.time()
    
    audio = download_audio(url, output_dir)
    if not audio:
        print(f"  ⚠ Failed to download")
        continue
    
    transcript = transcribe_audio(audio, output_dir)
    print(f"  ✓ Completed in {time.time() - start:.1f}s")

print(f"\nAll done! Results in: {output_dir}")
```

### Extract Keywords from Transcript
```python
import re
from collections import Counter

def extract_keywords(transcript_path, top_n=20):
    """Extract top keywords from transcript."""
    with open(transcript_path, 'r') as f:
        text = f.read()
    
    # Simple keyword extraction (replace with NLTK/spacy for production)
    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to'}
    
    keywords = [w for w in words if w.isalpha() and w not in stopwords]
    return Counter(keywords).most_common(top_n)

# Usage
keywords = extract_keywords("/tmp/transcript.txt", top_n=20)
print("Top keywords:", keywords)
```

### Save Results as JSON
```python
import json
from pathlib import Path

def save_results(video_url, audio_path, transcript_path, summary_text):
    """Save all results as a JSON file."""
    metadata = {
        "video_url": video_url,
        "audio_file": Path(audio_path).name if audio_path else None,
        "transcript_file": Path(transcript_path).name if transcript_path else None,
        "summary": summary_text,
    }
    
    output_file = Path("/tmp") / f"{Path(video_url).name}_results.json"
    with open(output_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return output_file

# Usage
save_results(
    video_url="https://youtu.be/VIDEO_ID",
    audio_path="/tmp/video.wav",
    transcript_path="/tmp/transcript.txt",
    summary_text="Video is about..."
)
```

---

*For more examples, see the [examples/](examples/) directory.*
