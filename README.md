# YouTube Watcher Skill

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Hermes Agent](https://img.shields.io/badge/Hermes-1.17.0%2B-orange)](https://github.com/nousresearch/hermes-agent)

**Download, transcribe, and summarize YouTube videos using local tools — no cloud APIs required.**

</div>

---

## Overview

This skill enables AI agents (Hermes, AutoGPT, LangChain, etc.) to watch, transcribe, and summarize YouTube videos entirely locally. No OpenAI API keys, no cloud transcription services — just your machine and open-source tools.

### Features
- ✅ **Audio extraction** via `yt-dlp` (handles YouTube, Vimeo, TikTok, etc.)
- ✅ **Speech-to-text** via `faster-whisper` (OpenAI's whisper model, optimized for speed)
- ✅ **Summarization** via local Qwen model (or any local LLM)
- ✅ **No cloud dependencies** — everything runs on your hardware
- ✅ **Extensible** — swap whisper models, LLM backends, or extractors

---

## Hardware Requirements

| Component | Minimum | Recommended | Ideal |
|-----------|---------|-------------|-------|
| **CPU** | Quad-core (Intel i5 / AMD Ryzen 5) | 8-core (Intel i7 / AMD Ryzen 7) | Apple M3/M4 Max (16+ cores) |
| **RAM** | 16 GB | 32 GB | 64 GB+ |
| **GPU** | None (CPU-only) | Apple Silicon (M1/M2/M3) | Apple M4 Max with 64GB+ unified memory |
| **Storage** | 10 GB free | 50 GB free | 100 GB+ (for multiple models) |
| **Network** | For initial download only | — | — |

### Performance Estimates (Apple M4 Max, 64GB RAM)
| Video Duration | Audio Size | Transcription Time | Quality |
|---------------|------------|-------------------|---------|
| 5 minutes | ~50 MB | ~30 seconds | Excellent |
| 15 minutes | ~150 MB | ~90 seconds | Excellent |
| 60 minutes | ~600 MB | ~5 minutes | Very Good |
| 2 hours | ~1.2 GB | ~10 minutes | Good |

### Notes
- **Apple Silicon (M1/M2/M3/M4)**: Optimal — uses Metal backend for GPU acceleration
- **Intel/AMD**: CPU-only fallback, slower but functional (int8 quantization helps)
- **RAM**: Whisper's `medium.en` model needs ~2GB RAM during inference
- **Storage**: Models take ~1-2GB each; cache stores audio/transcripts

---

## Quick Start

### Prerequisites
```bash
# Required tools (already in hermes-agent venv)
yt-dlp --version    # Should be 2023.06.22+
faster-whisper       # Should be 1.0.0+
python3 --version   # Should be 3.11+
```

### Installation
```bash
# 1. Clone the skill into your skills directory
git clone https://github.com/amiu888/youtube-watcher.git
cd youtube-watcher

# 2. Install dependencies (if not in hermes-agent venv)
pip install yt-dlp faster-whisper

# 3. Verify installation
python youtube_watcher.py --help
```

### Basic Usage
```bash
# Watch a single video
python youtube_watcher.py --url "https://youtu.be/VIDEO_ID"

# Watch multiple videos
python youtube_watcher.py --urls file.txt  # One URL per line

# Skip transcription (just download)
python youtube_watcher.py --url "..." --no-transcript

# Skip LLM summarization (just transcript)
python youtube_watcher.py --url "..." --no-summary
```

---

## Configuration

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `YT_WORKSPACE` | `~/.hermes/cache/browser-use/workspace/youtube_watcher_workspace/` | Output directory |
| `WHISPER_MODEL` | `medium.en` | Whisper model (tiny, base, small, medium, medium.en) |
| `LLM_MODEL_PATH` | `~/.local/share/qwen36-moe-mlx/model` | Path to local LLM |
| `LLM_PROVIDER` | `auto` | LLM backend: `auto`, `transformers`, `ollama` |

### Model Selection
| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `tiny.en` | 39 MB | Very Fast | Fair | Short clips, simple speech |
| `base.en` | 74 MB | Fast | Good | General purpose (English) |
| `small.en` | 244 MB | Moderate | Very Good | Best for most use cases |
| `medium.en` | 769 MB | Slow | Excellent | Professional grade |
| `large-v3` | 1.5 GB | Very Slow | Best | Maximum accuracy |

---

## File Structure

```
youtube-watcher/
├── README.md              # This file
├── SKILL.md              # Skill manifest for agent platforms
├── LICENSE               # MIT License
├── INSTALL.md            # Detailed installation guide
├── youtube_watcher.py    # Main script (entry point)
├── examples/
│   ├── basic_usage.py    # Simple example
│   └── batch_processing.py # Multiple videos
└── tests/
    └── test_watcher.py   # Unit tests
```

---

## API Reference

### `download_audio(video_url, output_dir)`
Downloads audio from YouTube video.

**Parameters:**
- `video_url` (str): YouTube URL
- `output_dir` (str): Directory to save audio

**Returns:** Path to downloaded audio file, or `None` on failure

### `transcribe_audio(audio_path, output_dir, model="medium.en")`
Transcribes audio to text.

**Parameters:**
- `audio_path` (str): Path to downloaded audio
- `output_dir` (str): Directory to save transcript
- `model` (str): Whisper model size (default: `medium.en`)

**Returns:** Path to transcript file

### `summarize_with_local_llm(transcript_path, output_dir)`
Summarizes transcript using local LLM.

**Parameters:**
- `transcript_path` (str): Path to transcript file
- `output_dir` (str): Directory to save summary

**Returns:** Summary text

---

## Integration Examples

### With Hermes Agent
Place this skill in `~/.hermes/skills/` and reference it in your agent config:

```yaml
skills:
  - name: youtube-watcher
    path: ~/.hermes/skills/youtube-watcher
```

### With LangChain
```python
from youtube_watcher import download_audio, transcribe_audio

audio = download_audio("https://youtu.be/VIDEO_ID", "/tmp")
transcript = transcribe_audio(audio, "/tmp")
```

### With AutoGPT
Create a plugin that calls `youtube_watcher.py` as a subprocess.

---

## Troubleshooting

### "Could not download audio"
- Check internet connection
- Verify URL format: `https://youtu.be/VIDEO_ID` or `https://youtube.com/watch?v=VIDEO_ID`
- Some videos may be region-locked or private

### "Transcription failed"
- Ensure `faster-whisper` is installed: `pip install faster-whisper`
- Check disk space (models need ~1-2GB)
- Try smaller model: set `WHISPER_MODEL=small.en`

### "LLM summary failed"
- Verify Qwen model is at `~/.local/share/qwen36-moe-mlx/model`
- Ensure 16GB+ RAM is available
- Try using `--no-summary` to skip LLM step

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Submit a pull request

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/amiu888/youtube-watcher/issues)
- **Documentation**: This README
- **Updates**: Star this repo for notifications

---

*Built for agents that need eyes and ears — locally, privately, affordably.*
