import base64
import shutil
import subprocess
import tempfile
import threading
import wave
from pathlib import Path

_speech_lock = threading.Lock()
_voice_model_name = "en_US-joe-medium"
_voice_model_path = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "voices"
    / f"{_voice_model_name}.onnx"
)
_piper_voice = None


def speak(text):
    message = text.strip()
    if not message:
        return

    with _speech_lock:
        if _voice_model_path.is_file():
            try:
                _speak_with_piper(message)
                return
            except ImportError:
                # Keep speech available if the optional local voice is missing.
                pass
        _speak_with_windows(message)


def _speak_with_piper(message):
    global _piper_voice
    from piper import PiperVoice, SynthesisConfig

    if _piper_voice is None:
        _piper_voice = PiperVoice.load(str(_voice_model_path))

    import winsound

    with tempfile.TemporaryDirectory(prefix="jarvis-voice-") as temporary_directory:
        audio_path = Path(temporary_directory) / "reply.wav"
        synthesis = SynthesisConfig(length_scale=1.05)
        with wave.open(str(audio_path), "wb") as audio_file:
            _piper_voice.synthesize_wav(message, audio_file, syn_config=synthesis)
        winsound.PlaySound(str(audio_path), winsound.SND_FILENAME)


def _speak_with_windows(message):
    powershell = shutil.which("powershell.exe")
    if powershell is None:
        raise RuntimeError("Windows PowerShell could not be found.")

    message_data = base64.b64encode(message.encode("utf-16le")).decode("ascii")
    script = f"""
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$messageBytes = [Convert]::FromBase64String('{message_data}')
$message = [System.Text.Encoding]::Unicode.GetString($messageBytes)
$speaker = [System.Speech.Synthesis.SpeechSynthesizer]::new()
$speaker.Rate = -1
$speaker.Speak($message)
$speaker.Dispose()
"""
    encoded_script = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    result = subprocess.run(
        [powershell, "-NoLogo", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded_script],
        capture_output=True,
        text=True,
        timeout=60,
        creationflags=creation_flags,
    )

    if result.returncode != 0:
        detail = result.stderr.strip() or "The Windows speech engine could not speak."
        raise RuntimeError(detail)
