# Installation Guide for YouTube Watcher Skill

## Prerequisites

### System Requirements

**Minimum Configuration:**
- macOS 13+ (Ventura) or Linux with Python 3.11+
- 16 GB RAM (32 GB recommended)
- 10 GB free disk space
- Internet connection (for initial download only)

**Recommended Configuration (Apple Silicon):**
- M1/M2/M3/M4 Mac with 16+ cores
- 32+ GB RAM
- 50 GB free disk space

**Intel/AMD Linux:**
- 8+ core CPU (Intel i7 or AMD Ryzen 7)
- 32 GB RAM
- Optional: NVIDIA GPU with CUDA (if available)

### Required Software

```bash
# Python 3.11+ (via pyenv recommended)
pyenv install 3.11.6
pyenv local 3.11.6

# yt-dlp (already in hermes-agent venv)
yt-dlp --version  # Should be 2023.06.22+

# faster-whisper (already in hermes-agent venv)
pip show faster-whisper  # Should be 1.0.0+

# Verify both are in your venv
source ~/.hermes/hermes-agent/venv/bin/activate
which yt-dlp
python3 -c "from faster_whisper import WhisperModel; print('OK')"
```

## Installation Steps

### Step 1: Clone the Repository

```bash
# Clone the skill to your local skills directory
git clone https://github.com/amiu888/youtube-watcher.git \
  ~/.hermes/skills/youtube-watcher
```

### Step 2: Verify Dependencies

```bash
source ~/.hermes/hermes-agent/venv/bin/activate

# Check yt-dlp
yt-dlp --version

# Check faster-whisper
python3 -c "from faster_whisper import WhisperModel; print('faster-whisper OK')"

# Check Python version
python3 --version
```

### Step 3: Download Whisper Model (First Run)

```bash
# The first run will automatically download the whisper model
# For medium.en model (~769 MB), ensure you have:
# - 1-2 GB free disk space
# - Stable internet connection

# Manual download (optional, skip if you want auto-download)
python3 -c "
from faster_whisper.utils import _MODELS
print('Available models:', list(_MODEDS.keys()))
"
```

### Step 4: Test Installation

```bash
# Test with a short YouTube video
python3 ~/.hermes/skills/youtube-watcher/youtube_watcher.py \
  --url "https://youtu.be/dQw4w9WgXcQ"

# Should output:
# 1. Downloaded audio file (.wav)
# 2. Transcript (.txt)
# 3. Summary (if LLM is available)
```

### Step 5: Configure for Your Environment

Edit `youtube_watcher.py` or set environment variables:

```bash
# Optional: Customize paths and models
export YT_WORKSPACE="/path/to/output/directory"
export WHISPER_MODEL="medium.en"  # or: tiny.en, base.en, small.en, medium.en
export LLM_MODEL_PATH="/path/to/qwen/model"
export LLM_PROVIDER="auto"  # or: transformers, ollama
```

## Troubleshooting

### Issue: "yt-dlp not found"
```bash
# Install yt-dlp
pip install yt-dlp

# Or use brew (macOS)
brew install yt-dlp
```

### Issue: "faster-whisper import error"
```bash
# Reinstall in your venv
source ~/.hermes/hermes-agent/venv/bin/activate
pip install --upgrade faster-whisper
```

### Issue: "Could not download audio"
- Check internet connection
- Verify video URL is public (not private/region-locked)
- Try a different video URL
- Ensure `node` is available for YouTube JS (already in system)

### Issue: "Transcription failed"
- Ensure sufficient disk space (whisper models need 1-2 GB)
- Try a smaller model: `WHISPER_MODEL=small.en`
- Check that `faster-whisper` is correctly installed

### Issue: "LLM summary failed"
- Ensure Qwen model exists at `~/.local/share/qwen36-moe-mlx/model`
- Verify 16+ GB RAM is available (no swapping)
- Use `--no-summary` flag to skip LLM step:
  ```bash
  python3 youtube_watcher.py --url "..." --no-summary
  ```

## Uninstallation

```bash
# Remove the skill directory
rm -rf ~/.hermes/skills/youtube-watcher

# Remove cached files (optional)
rm -rf ~/.hermes/cache/browser-use/workspace/youtube_watcher_workspace

# Remove whisper models (optional, saves ~1-2 GB)
rm -rf ~/.cache/huggingface/hub/  # Careful: other models too
```

## Updating

```bash
# Pull latest changes
cd ~/.hermes/skills/youtube-watcher
git pull origin main

# Update dependencies
source ~/.hermes/hermes-agent/venv/bin/activate
pip install --upgrade yt-dlp faster-whisper
```

---

*For support, see [README.md](README.md) or open an [Issue](https://github.com/amiu888/youtube-watcher/issues).*
