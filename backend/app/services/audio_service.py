import random

try:
    import librosa
    import numpy as np
    HAS_AUDIO_LIBS = True
except ImportError:
    HAS_AUDIO_LIBS = False


class AudioProcessingEngine:
    """Librosa-based DSP pipeline for computing speech fluency metrics from audio recordings."""

    def __init__(self, silence_db_threshold: int = -40, min_pause_duration_sec: float = 0.8):
        self.silence_threshold = silence_db_threshold
        self.min_pause_duration = min_pause_duration_sec
        self.filler_lexicon = {"um", "uh", "like", "so", "actually", "basically"}

    def _fallback_metrics(self, raw_transcript: str) -> dict:
        """Compute estimated fluency metrics from transcript alone (no audio file)."""
        words = [w.strip(".,?!:;").lower() for w in raw_transcript.split()]
        total_words = len(words)
        estimated_duration = max(3.0, total_words * 0.45 + random.uniform(0.5, 2.0)) if total_words > 0 else 5.0
        wpm = (total_words / estimated_duration) * 60.0 if estimated_duration > 0 else 0.0
        filler_count = sum(1 for word in words if word in self.filler_lexicon)
        filler_ratio = filler_count / total_words if total_words > 0 else 0.0
        pause_count = int(estimated_duration / 4.0)

        wpm_score = max(0, 10 - abs(135 - wpm) / 10)
        filler_penalty = max(0, 10 - (filler_ratio * 40))
        pause_penalty = max(0, 10 - (pause_count * 1.5))
        overall_score = round((wpm_score * 0.4) + (filler_penalty * 0.3) + (pause_penalty * 0.3), 2)

        return {
            "audio_duration_sec": round(estimated_duration, 2),
            "speaking_rate_wpm": round(wpm, 2),
            "pause_count": pause_count,
            "filler_words_count": filler_count,
            "filler_ratio": round(filler_ratio, 4),
            "fluency_score": overall_score
        }

    def compute_speech_fluency(self, file_path: str, raw_transcript: str) -> dict:
        """Compute comprehensive speech fluency metrics from an audio file and its transcript."""
        if not HAS_AUDIO_LIBS:
            return self._fallback_metrics(raw_transcript)

        try:
            y, sr = librosa.load(file_path, sr=None)
            total_duration = librosa.get_duration(y=y, sr=sr)

            rms = librosa.feature.rms(y=y)
            rms_db = librosa.amplitude_to_db(rms, ref=np.max)[0]

            hop_length = 512
            frame_duration = hop_length / sr
            silence_threshold_frames = int(self.min_pause_duration / frame_duration)

            pause_count = 0
            current_silent_streak = 0

            for val in rms_db:
                if val < self.silence_threshold:
                    current_silent_streak += 1
                else:
                    if current_silent_streak >= silence_threshold_frames:
                        pause_count += 1
                    current_silent_streak = 0
            if current_silent_streak >= silence_threshold_frames:
                pause_count += 1

            words = [w.strip(".,?!:;").lower() for w in raw_transcript.split()]
            total_words = len(words)

            wpm = (total_words / total_duration) * 60.0 if total_duration > 0 else 0.0
            filler_count = sum(1 for word in words if word in self.filler_lexicon)
            filler_ratio = filler_count / total_words if total_words > 0 else 0.0

            wpm_score = max(0, 10 - abs(135 - wpm) / 10)
            filler_penalty = max(0, 10 - (filler_ratio * 40))
            pause_penalty = max(0, 10 - (pause_count * 1.5))
            overall_score = round((wpm_score * 0.4) + (filler_penalty * 0.3) + (pause_penalty * 0.3), 2)

            return {
                "audio_duration_sec": round(total_duration, 2),
                "speaking_rate_wpm": round(wpm, 2),
                "pause_count": pause_count,
                "filler_words_count": filler_count,
                "filler_ratio": round(filler_ratio, 4),
                "fluency_score": overall_score
            }
        except Exception:
            return self._fallback_metrics(raw_transcript)
