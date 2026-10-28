---
name: youtube-watcher
description: Download YouTube videos, transcribe audio using faster-whisper, and summarize with local Qwen model
category: media
---

# YouTube Watcher Skill

## Overview
This skill enables the agent to watch, transcribe, and summarize YouTube videos using local tools only — no cloud APIs required.

## Workflow
1. User provides a YouTube video URL
2. Download audio using `yt-dlp` (extracted from venv)
3. Transcribe audio using `faster-whisper` (fast-small model, int8 quantization)
4. Summarize transcript using local Qwen model
5. Return summary + key points

## Prerequisites
- `yt-dlp` (already installed in hermes-agent venv)
- `faster-whisper` (already installed in hermes-agent venv)
- Local Qwen model at `~/.local/share/qwen36-moe-mlx/model`

## Core Commands
```python
# Download audio
yt-dlp --js-runtimes node -x --audio-format wav --no-playlist \
  -o '/path/output.%(ext)s' 'https://youtu.be/VIDEO_ID'

# Transcribe (using faster-whisper in hermes-agent venv)
from faster_whisper import WhisperModel
model = WhisperModel("medium.en", device="cpu", compute_type="int8")
segments, info = model.transcribe(audio_path, beam_size=5)

# Summarize with local LLM (if needed)
# Use transformers + local Qwen model
```

## File Locations
- Script: `~/.hermes/skills/youtube-watcher/youtube_watcher.py`
- Output workspace: `~/.hermes/cache/browser-use/workspace/youtube_watcher_workspace/`

## Error Handling
- If yt-dlp fails: check video URL, network connection
- If whisper fails: model may not be available, fall back to transcript API
- If LLM fails: return raw transcript instead of summary

## Notes
- Uses int8 quantization for faster inference on CPU
- fast-small model is ~142M parameters, good speed/accuracy tradeoff
- yt-dlp needs `--js-runtimes node` due to YouTube's JavaScript requirements
- Output workspace persists between runs for re-use
