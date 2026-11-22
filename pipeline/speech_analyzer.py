"""
pipeline/speech_analyzer.py
Analyzes raw footage audio:
- Detects silence boundaries (trims dead air at start/end)
- Transcribes speech using faster-whisper (supports Tamil, English, Hindi, etc.)
- Emits timestamped segments and word-level cues
"""

import subprocess
import re
import os
import sys
import numpy as np
from typing import Dict, Any, List, Tuple

def detect_speech_boundaries(video_path: str, noise_thresh_db: float = -30.0, min_silence_dur: float = 0.5) -> Tuple[float, float, float]:
    """
    Detects the first spoken word and final spoken word to trim dead air.
    Returns: (start_time, end_time, total_duration)
    """
    # Probe duration
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    total_dur = float(res.stdout.strip())
    
    # Run silencedetect
    cmd = [
        "ffmpeg", "-i", video_path,
        "-af", f"silencedetect=noise={noise_thresh_db}dB:d={min_silence_dur}",
        "-f", "null", "-"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stderr = proc.stderr
    
    # Check leading silence
    start_time = 0.0
    first_silence_end = re.search(r"silence_end:\s*([0-9.]+)", stderr)
    first_silence_start = re.search(r"silence_start:\s*([0-9.]+)", stderr)
    
    if first_silence_start and float(first_silence_start.group(1)) < 0.3:
        if first_silence_end:
            start_time = float(first_silence_end.group(1))
            
    # Check trailing silence
    end_time = total_dur
    silence_starts = re.findall(r"silence_start:\s*([0-9.]+)", stderr)
    if silence_starts:
        last_silence_start = float(silence_starts[-1])
        if total_dur - last_silence_start < 2.5 and last_silence_start > start_time:
            end_time = last_silence_start
            
    # Safety bounds
    start_time = max(0.0, min(start_time, 3.0))
    if end_time - start_time < 5.0:
        end_time = total_dur
        
    return start_time, end_time, total_dur

def transcribe_audio(
    video_path: str,
    start_time: float = 0.0,
    end_time: float = None,
    model_size: str = "base"
) -> Dict[str, Any]:
    """
    Transcribes audio within [start_time, end_time] using faster-whisper.
    Returns: {
        'language': str,
        'probability': float,
        'segments': [{'start': float, 'end': float, 'text': str, 'words': [...]}]
    }
    """
    from faster_whisper import WhisperModel
    
    # Extract audio slice to 16kHz mono PCM float32
    cmd = ["ffmpeg", "-y"]
    if start_time > 0:
        cmd.extend(["-ss", str(start_time)])
    cmd.extend(["-i", video_path])
    if end_time is not None:
        cmd.extend(["-to", str(end_time - start_time)])
    cmd.extend(["-f", "s16le", "-ac", "1", "-ar", "16000", "-"])
    
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    audio_np = np.frombuffer(proc.stdout, np.int16).flatten().astype(np.float32) / 32768.0
    
    # Look for cached models
    download_root = "/mnt/hdd/nvim/cache/huggingface/hub"
    if not os.path.exists(download_root):
        download_root = None
        
    model = WhisperModel(model_size, device="cpu", compute_type="int8", download_root=download_root)
    segments_raw, info = model.transcribe(audio_np, beam_size=5, word_timestamps=True)
    
    segments = []
    for s in segments_raw:
        words = []
        if s.words:
            for w in s.words:
                s_abs_start = round(start_time + w.start, 2)
                words.append({
                    "word": w.word,
                    "start": s_abs_start,
                    "end": round(start_time + w.end, 2),
                    "probability": round(w.probability, 2)
                })
        segments.append({
            "start": round(start_time + s.start, 2),
            "end": round(start_time + s.end, 2),
            "text": s.text.strip(),
            "words": words
        })
        
    return {
        "language": info.language,
        "language_probability": round(info.language_probability, 3),
        "segments": segments
    }
