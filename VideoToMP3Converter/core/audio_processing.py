# In core/audio_processing.py
class AudioEnhancer:
    @staticmethod
    def normalize_audio(audio_clip, target_dBFS=-20.0):
        """Normalize audio to target volume"""
        change_in_dB = target_dBFS - audio_clip.max_volume()
        return audio_clip.volumex(10**(change_in_dB/20))

    @staticmethod
    def remove_silence(audio_clip, threshold=0.02):
        """Remove silent portions from audio"""
        return audio_clip.without_audio(
            lambda t: np.abs(audio_clip.to_soundarray()[t]) < threshold
        )