"""
engine/sfx.py
Pure mathematical audio synthesis of UI sound effects inspired by latent-spaces/brag.
Generates crisp, platform-ready WAV sound effects (whoosh, pop, counter ticks, chime)
without requiring external sound files or internet downloads.
"""

import math
import struct
import wave
import os

def _write_wav(filename: str, samples: list, sample_rate: int = 44100):
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    with wave.open(filename, 'wb') as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        
        raw_data = bytearray()
        for s in samples:
            # Clamp between -1.0 and 1.0
            val = max(-1.0, min(1.0, s))
            int_val = int(val * 32767.0)
            raw_data.extend(struct.pack('<h', int_val))
            
        wav.writeframes(raw_data)
    return filename

def generate_whoosh(filename: str, duration: float = 0.35, sample_rate: int = 44100):
    """Generates a filtered frequency-sweep cinematic whoosh."""
    num_samples = int(duration * sample_rate)
    samples = []
    
    for i in range(num_samples):
        t = i / float(num_samples)
        # Hann window envelope
        env = 0.5 * (1.0 - math.cos(2.0 * math.pi * t))
        # Swept frequency: 150 Hz -> 650 Hz -> 200 Hz
        freq = 150.0 + 500.0 * math.sin(math.pi * t)
        phase = 2.0 * math.pi * freq * (i / sample_rate)
        # White noise blended with sine sweep
        noise = (math.sin(i * 12.9898) * 43758.5453) % 2.0 - 1.0
        val = (math.sin(phase) * 0.6 + noise * 0.4) * env * 0.7
        samples.append(val)
        
    return _write_wav(filename, samples, sample_rate)

def generate_pop(filename: str, duration: float = 0.08, sample_rate: int = 44100):
    """Generates a crisp, subtle UI pop / card entry sound."""
    num_samples = int(duration * sample_rate)
    samples = []
    
    for i in range(num_samples):
        t = i / float(num_samples)
        env = math.exp(-25.0 * t)  # Fast decay
        freq = 880.0 - 400.0 * t
        val = math.sin(2.0 * math.pi * freq * (i / sample_rate)) * env * 0.8
        samples.append(val)
        
    return _write_wav(filename, samples, sample_rate)

def generate_chime(filename: str, duration: float = 0.4, sample_rate: int = 44100):
    """Generates a harmonious high-frequency victory / benchmark chime."""
    num_samples = int(duration * sample_rate)
    samples = []
    
    # 2 chord frequencies (E6 + B6)
    f1 = 1318.5
    f2 = 1975.5
    
    for i in range(num_samples):
        t = i / float(num_samples)
        env = math.exp(-8.0 * t)
        val = (math.sin(2 * math.pi * f1 * (i / sample_rate)) * 0.5 +
               math.sin(2 * math.pi * f2 * (i / sample_rate)) * 0.4) * env * 0.7
        samples.append(val)
        
    return _write_wav(filename, samples, sample_rate)

def build_default_sfx_library(output_dir: str = "/tmp/video_assets/sfx") -> dict:
    """Generates the full core SFX library into output_dir."""
    os.makedirs(output_dir, exist_ok=True)
    paths = {
        "whoosh": generate_whoosh(os.path.join(output_dir, "ui_whoosh.wav")),
        "pop": generate_pop(os.path.join(output_dir, "ui_pop.wav")),
        "chime": generate_chime(os.path.join(output_dir, "ui_chime.wav"))
    }
    return paths
