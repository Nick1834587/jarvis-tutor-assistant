import json
import queue
import time
from pathlib import Path

MODEL_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "models"
    / "vosk-model-small-en-us-0.15"
)

_model = None


def listen_once(max_seconds=10):
    global _model
    import sounddevice as sd
    from vosk import KaldiRecognizer, Model

    if not MODEL_DIR.exists():
        raise RuntimeError(
            "The local English speech model is missing from data/models."
        )

    if _model is None:
        _model = Model(str(MODEL_DIR))

    device_info = sd.query_devices(kind="input")
    sample_rate = int(device_info["default_samplerate"])
    recognizer = KaldiRecognizer(_model, sample_rate)
    audio_queue = queue.Queue()

    def audio_callback(indata, frames, time_info, status):
        audio_queue.put(bytes(indata))

    deadline = time.monotonic() + max_seconds
    with sd.RawInputStream(
        samplerate=sample_rate,
        blocksize=8000,
        channels=1,
        dtype="int16",
        callback=audio_callback,
    ):
        while time.monotonic() < deadline:
            try:
                audio = audio_queue.get(timeout=0.25)
            except queue.Empty:
                continue
            if recognizer.AcceptWaveform(audio):
                recognized = json.loads(recognizer.Result()).get("text", "").strip()
                if recognized:
                    return recognized

    return json.loads(recognizer.FinalResult()).get("text", "").strip()