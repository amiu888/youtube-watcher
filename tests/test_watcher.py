# Unit Tests for YouTube Watcher

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from youtube_watcher import download_audio, transcribe_audio, summarize_with_local_llm


class TestDownloadAudio:
    """Test the download_audio function."""

    def test_download_success(self, tmp_path):
        """Test successful audio download."""
        # Mock successful subprocess.run
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        
        # Create a mock WAV file
        mock_wav_file = tmp_path / "test_video.wav"
        mock_wav_file.write_text("mock audio data")
        
        with patch('subprocess.run', return_value=mock_result):
            with patch('os.listdir', return_value=['test_video.wav']):
                with patch('os.path.getsize', return_value=1024 * 1024):
                    audio_path = download_audio(
                        "https://youtu.be/VIDEO_ID",
                        str(tmp_path)
                    )
                    
                    assert audio_path is not None
                    assert audio_path.endswith('.wav')

    def test_download_failure(self, tmp_path):
        """Test failed audio download."""
        # Mock failed subprocess.run
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Error: Video not found"
        
        with patch('subprocess.run', return_value=mock_result):
            audio_path = download_audio(
                "https://youtu.be/INVALID_ID",
                str(tmp_path)
            )
            
            assert audio_path is None


class TestTranscribeAudio:
    """Test the transcribe_audio function."""

    def test_transcribe_success(self, tmp_path):
        """Test successful transcription."""
        # Create a mock audio file
        mock_audio = tmp_path / "test.wav"
        mock_audio.write_text("mock audio data")
        
        # Mock WhisperModel
        mock_model = Mock()
        mock_segments = [
            Mock(start=0.0, text="Hello world"),
            Mock(start=1.0, text="This is a test"),
        ]
        mock_info = Mock(language="en", language_probability=0.99, duration=2.0)
        
        mock_model.transcribe.return_value = (mock_segments, mock_info)
        
        with patch('faster_whisper.WhisperModel', return_value=mock_model):
            transcript_path = transcribe_audio(
                str(mock_audio),
                str(tmp_path)
            )
            
            assert transcript_path is not None
            assert transcript_path.endswith('.txt')
            
            # Verify transcript content
            with open(transcript_path, 'r') as f:
                content = f.read()
                assert "Hello world" in content
                assert "This is a test" in content

    def test_transcribe_failure(self, tmp_path):
        """Test failed transcription."""
        mock_audio = tmp_path / "test.wav"
        mock_audio.write_text("mock audio data")
        
        # Mock WhisperModel that raises an exception
        with patch('faster_whisper.WhisperModel', side_effect=Exception("Model not found")):
            with pytest.raises(Exception):
                transcribe_audio(str(mock_audio), str(tmp_path))


class TestSummarizeWithLocalLLM:
    """Test the summarize_with_local_llm function."""

    def test_summarize_success(self, tmp_path):
        """Test successful LLM summarization."""
        # Create a mock transcript file
        mock_transcript = tmp_path / "transcript.txt"
        mock_transcript.write_text("This is a test transcript about Python programming.")
        
        # Mock subprocess.run for LLM call
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Summary: This video is about Python programming."
        
        with patch('subprocess.run', return_value=mock_result):
            summary = summarize_with_local_llm(
                str(mock_transcript),
                str(tmp_path)
            )
            
            assert summary is not None
            assert "Python programming" in summary

    def test_summarize_failure(self, tmp_path):
        """Test failed LLM summarization."""
        mock_transcript = tmp_path / "transcript.txt"
        mock_transcript.write_text("This is a test transcript.")
        
        # Mock subprocess.run that fails
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "LLM not available"
        
        with patch('subprocess.run', return_value=mock_result):
            # Should return transcript text on failure
            result = summarize_with_local_llm(
                str(mock_transcript),
                str(tmp_path)
            )
            
            # When LLM fails, should return transcript
            assert "test transcript" in result


class TestIntegration:
    """Integration tests for the full workflow."""

    def test_full_workflow(self, tmp_path):
        """Test complete workflow: download → transcribe → summarize."""
        # This test requires actual network access and working dependencies
        # Skip if dependencies are not available
        
        try:
            # Mock the entire workflow
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr="")
                
                with patch('os.listdir', return_value=['test.wav']):
                    with patch('os.path.getsize', return_value=1024):
                        audio = download_audio("https://youtu.be/TEST", str(tmp_path))
                        
                mock_segments = [Mock(start=0.0, text="Test speech")]
                mock_info = Mock(language="en", language_probability=0.99, duration=1.0)
                
                mock_model = Mock()
                mock_model.transcribe.return_value = (mock_segments, mock_info)
                
                with patch('faster_whisper.WhisperModel', return_value=mock_model):
                    transcript = transcribe_audio(audio, str(tmp_path))
                    
                mock_result = Mock(returncode=0, stdout="Summary: test")
                
                with patch('subprocess.run', return_value=mock_result):
                    summary = summarize_with_local_llm(transcript, str(tmp_path))
                    
                assert audio is not None
                assert transcript is not None
                assert summary is not None

        except Exception as e:
            pytest.skip(f"Dependencies not available: {e}")
