"""
audio_model - 索克生活项目模块
"""

from ..config.settings import get_settings
from ..models.accessibility import AudioAnalysis
from datasets import load_dataset
from transformers import (
from typing import Dict, List, Optional, Tuple, Any, Union
import asyncio
import io
import librosa
import logging
import numpy as np
import torch
import torchaudio
import wave

"""
Audio AI model for accessibility analysis.
Provides speech recognition, synthesis, and audio processing capabilities.
"""

    WhisperProcessor, WhisperForConditionalGeneration,
    SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan,
    pipeline
)


logger = logging.getLogger(__name__)


class AudioModel:
    """
    Advanced audio AI model for accessibility analysis.
    
    Provides:
    - Speech recognition (ASR)
    - Text-to-speech synthesis (TTS)
    - Audio quality analysis
    - Sound event detection
    - Real-time audio processing
    - Multi-language support
    """
    
    def __init__(self):
        """Initialize the audio model."""
        self.settings = get_settings()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Model components
        self.speech_recognition_model = None
        self.speech_recognition_processor = None
        self.text_to_speech_model = None
        self.text_to_speech_processor = None
        self.text_to_speech_vocoder = None
        self.speaker_embeddings = None
        self.sound_classification_pipeline = None
        
        # Model configurations
        self.asr_model_name = "openai/whisper-base"
        self.tts_model_name = "microsoft/speecht5_tts"
        self.tts_vocoder_name = "microsoft/speecht5_hifigan"
        
        # Audio processing parameters
        self.sample_rate = 16000
        self.chunk_duration = 30  # seconds
        self.overlap_duration = 5  # seconds
        
        # Supported languages for speech recognition
        self.supported_languages = {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese",
            "ar": "Arabic",
            "hi": "Hindi",
            "th": "Thai",
            "vi": "Vietnamese",
            "nl": "Dutch",
            "pl": "Polish",
            "tr": "Turkish",
            "sv": "Swedish",
            "da": "Danish",
            "no": "Norwegian",
            "fi": "Finnish",
            "cs": "Czech",
            "sk": "Slovak",
            "hu": "Hungarian",
            "ro": "Romanian"
        }
        
        # Audio accessibility features
        self.accessibility_features = {
            "volume_normalization": True,
            "noise_reduction": True,
            "speech_enhancement": True,
            "frequency_adjustment": True,
            "speed_control": True,
            "pitch_adjustment": True
        }
        
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all audio models."""
        if self._initialized:
            return
        
        logger.info("Initializing audio AI models...")
        
        try:
            # Initialize speech recognition
            await self._initialize_speech_recognition()
            
            # Initialize text-to-speech
            await self._initialize_text_to_speech()
            
            # Initialize sound classification
            await self._initialize_sound_classification()
            
            # Load speaker embeddings for TTS
            await self._load_speaker_embeddings()
            
            self._initialized = True
            logger.info("Audio AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize audio models: {e}")
            raise
    
    async def _initialize_speech_recognition(self) -> None:
        """Initialize speech recognition model."""
        try:
            self.speech_recognition_processor = WhisperProcessor.from_pretrained(
                self.asr_model_name
            )
            self.speech_recognition_model = WhisperForConditionalGeneration.from_pretrained(
                self.asr_model_name
            ).to(self.device)
            logger.info("Speech recognition model loaded")
        except Exception as e:
            logger.error(f"Failed to load speech recognition model: {e}")
            self.speech_recognition_model = None
            self.speech_recognition_processor = None
    
    async def _initialize_text_to_speech(self) -> None:
        """Initialize text-to-speech model."""
        try:
            self.text_to_speech_processor = SpeechT5Processor.from_pretrained(
                self.tts_model_name
            )
            self.text_to_speech_model = SpeechT5ForTextToSpeech.from_pretrained(
                self.tts_model_name
            ).to(self.device)
            self.text_to_speech_vocoder = SpeechT5HifiGan.from_pretrained(
                self.tts_vocoder_name
            ).to(self.device)
            logger.info("Text-to-speech model loaded")
        except Exception as e:
            logger.error(f"Failed to load text-to-speech model: {e}")
            self.text_to_speech_model = None
            self.text_to_speech_processor = None
            self.text_to_speech_vocoder = None
    
    async def _initialize_sound_classification(self) -> None:
        """Initialize sound classification pipeline."""
        try:
            self.sound_classification_pipeline = pipeline(
                "audio-classification",
                model="MIT/ast-finetuned-audioset-10-10-0.4593",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Sound classification pipeline loaded")
        except Exception as e:
            logger.error(f"Failed to load sound classification pipeline: {e}")
            self.sound_classification_pipeline = None
    
    async def _load_speaker_embeddings(self) -> None:
        """Load speaker embeddings for TTS."""
        try:
            # Load default speaker embeddings
            embeddings_dataset = load_dataset(
                "Matthijs/cmu-arctic-xvectors", 
                split="validation"
            )
            self.speaker_embeddings = torch.tensor(
                embeddings_dataset[7306]["xvector"]
            ).unsqueeze(0).to(self.device)
            logger.info("Speaker embeddings loaded")
        except Exception as e:
            logger.error(f"Failed to load speaker embeddings: {e}")
            self.speaker_embeddings = None
    
    async def recognize_speech(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recognize speech from audio data.
        
        Args:
            audio_data: Raw audio data
            language: Target language code
            user_preferences: User accessibility preferences
            
        Returns:
            Speech recognition results
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.speech_recognition_model:
            return {
                "success": False,
                "text": "",
                "confidence": 0.0,
                "language": language or "unknown",
                "error": "Speech recognition model not available"
            }
        
        try:
            # Convert audio data to tensor
            audio_tensor = self._bytes_to_audio_tensor(audio_data)
            
            # Preprocess audio for better recognition
            audio_tensor = self._preprocess_audio(audio_tensor, user_preferences)
            
            # Prepare inputs for the model
            inputs = self.speech_recognition_processor(
                audio_tensor,
                sampling_rate=self.sample_rate,
                return_tensors="pt"
            ).to(self.device)
            
            # Generate transcription
            with torch.no_grad():
                if language and language in self.supported_languages:
                    # Force language if specified
                    forced_decoder_ids = self.speech_recognition_processor.get_decoder_prompt_ids(
                        language=language, task="transcribe"
                    )
                    predicted_ids = self.speech_recognition_model.generate(
                        inputs["input_features"],
                        forced_decoder_ids=forced_decoder_ids
                    )
                else:
                    # Auto-detect language
                    predicted_ids = self.speech_recognition_model.generate(
                        inputs["input_features"]
                    )
            
            # Decode the transcription
            transcription = self.speech_recognition_processor.batch_decode(
                predicted_ids, skip_special_tokens=True
            )[0]
            
            # Calculate confidence score (simplified)
            confidence = self._calculate_transcription_confidence(
                inputs["input_features"], predicted_ids
            )
            
            # Detect language if not specified
            detected_language = self._detect_language(transcription) if not language else language
            
            return {
                "success": True,
                "text": transcription,
                "confidence": confidence,
                "language": detected_language,
                "supported_language": detected_language in self.supported_languages,
                "audio_quality": self._analyze_audio_quality(audio_tensor),
                "processing_time": 0.0  # Would be calculated in real implementation
            }
            
        except Exception as e:
            logger.error(f"Speech recognition failed: {e}")
            return {
                "success": False,
                "text": "",
                "confidence": 0.0,
                "language": language or "unknown",
                "error": str(e)
            }
    
    async def synthesize_speech(
        self,
        text: str,
        language: str = "en",
        voice_settings: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            language: Target language
            voice_settings: Voice configuration
            user_preferences: User accessibility preferences
            
        Returns:
            Speech synthesis results
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.text_to_speech_model or not self.speaker_embeddings:
            return {
                "success": False,
                "audio_data": b"",
                "error": "Text-to-speech model not available"
            }
        
        try:
            # Apply voice settings and user preferences
            processed_text = self._preprocess_text_for_tts(text, voice_settings, user_preferences)
            
            # Prepare inputs
            inputs = self.text_to_speech_processor(
                text=processed_text,
                return_tensors="pt"
            ).to(self.device)
            
            # Generate speech
            with torch.no_grad():
                speech = self.text_to_speech_model.generate_speech(
                    inputs["input_ids"],
                    self.speaker_embeddings,
                    vocoder=self.text_to_speech_vocoder
                )
            
            # Apply accessibility enhancements
            enhanced_speech = self._enhance_speech_for_accessibility(
                speech, voice_settings, user_preferences
            )
            
            # Convert to bytes
            audio_bytes = self._audio_tensor_to_bytes(enhanced_speech)
            
            return {
                "success": True,
                "audio_data": audio_bytes,
                "sample_rate": self.sample_rate,
                "duration": len(enhanced_speech) / self.sample_rate,
                "language": language,
                "voice_settings": voice_settings or {},
                "accessibility_enhancements": self._get_applied_enhancements(user_preferences)
            }
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return {
                "success": False,
                "audio_data": b"",
                "error": str(e)
            }
    
    async def analyze_audio(
        self,
        audio_data: bytes,
        analysis_type: str = "comprehensive",
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> AudioAnalysis:
        """
        Perform comprehensive audio analysis.
        
        Args:
            audio_data: Raw audio data
            analysis_type: Type of analysis to perform
            user_preferences: User accessibility preferences
            
        Returns:
            Audio analysis results
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Convert audio data to tensor
            audio_tensor = self._bytes_to_audio_tensor(audio_data)
            
            # Perform different types of analysis
            if analysis_type == "speech_quality":
                return await self._analyze_speech_quality(audio_tensor, user_preferences)
            elif analysis_type == "sound_events":
                return await self._analyze_sound_events(audio_tensor, user_preferences)
            elif analysis_type == "accessibility":
                return await self._analyze_audio_accessibility(audio_tensor, user_preferences)
            else:
                return await self._comprehensive_audio_analysis(audio_tensor, user_preferences)
                
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return AudioAnalysis(
                accessibility_score=0.0,
                issues=["Audio analysis failed"],
                recommendations=["Please try again with different audio"],
                speech_clarity=0.0,
                background_noise_level=1.0,
                volume_level=0.0,
                frequency_analysis={},
                detected_sounds=[],
                language_detected="unknown"
            )
    
    async def _comprehensive_audio_analysis(
        self,
        audio_tensor: torch.Tensor,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> AudioAnalysis:
        """Perform comprehensive audio analysis."""
        # Run all analysis components in parallel
        results = await asyncio.gather(
            self._analyze_speech_content(audio_tensor),
            self._analyze_audio_quality(audio_tensor),
            self._detect_sound_events(audio_tensor),
            self._analyze_frequency_spectrum(audio_tensor),
            self._detect_background_noise(audio_tensor),
            return_exceptions=True
        )
        
        speech_content, quality_metrics, sound_events, frequency_analysis, noise_analysis = results
        
        # Handle exceptions in results
        speech_content = speech_content if not isinstance(speech_content, Exception) else {}
        quality_metrics = quality_metrics if not isinstance(quality_metrics, Exception) else {}
        sound_events = sound_events if not isinstance(sound_events, Exception) else []
        frequency_analysis = frequency_analysis if not isinstance(frequency_analysis, Exception) else {}
        noise_analysis = noise_analysis if not isinstance(noise_analysis, Exception) else {}
        
        # Calculate accessibility score
        accessibility_score = self._calculate_audio_accessibility_score(
            quality_metrics, noise_analysis, speech_content, user_preferences
        )
        
        # Generate recommendations
        recommendations = self._generate_audio_recommendations(
            quality_metrics, noise_analysis, speech_content, user_preferences
        )
        
        # Identify issues
        issues = self._identify_audio_issues(
            quality_metrics, noise_analysis, speech_content
        )
        
        return AudioAnalysis(
            accessibility_score=accessibility_score,
            issues=issues,
            recommendations=recommendations,
            speech_clarity=quality_metrics.get("clarity", 0.0),
            background_noise_level=noise_analysis.get("noise_level", 0.0),
            volume_level=quality_metrics.get("volume", 0.0),
            frequency_analysis=frequency_analysis,
            detected_sounds=sound_events,
            language_detected=speech_content.get("language", "unknown"),
            speech_content=speech_content.get("text", ""),
            audio_quality_metrics=quality_metrics
        )
    
    async def _analyze_speech_content(self, audio_tensor: torch.Tensor) -> Dict[str, Any]:
        """Analyze speech content in audio."""
        try:
            # Convert tensor to bytes for speech recognition
            audio_bytes = self._audio_tensor_to_bytes(audio_tensor)
            
            # Recognize speech
            speech_result = await self.recognize_speech(audio_bytes)
            
            return {
                "text": speech_result.get("text", ""),
                "language": speech_result.get("language", "unknown"),
                "confidence": speech_result.get("confidence", 0.0),
                "has_speech": len(speech_result.get("text", "")) > 0
            }
            
        except Exception as e:
            logger.error(f"Speech content analysis failed: {e}")
            return {"text": "", "language": "unknown", "confidence": 0.0, "has_speech": False}
    
    def _analyze_audio_quality(self, audio_tensor: torch.Tensor) -> Dict[str, Any]:
        """Analyze audio quality metrics."""
        try:
            audio_np = audio_tensor.cpu().numpy()
            
            # Calculate volume/amplitude metrics
            rms = np.sqrt(np.mean(audio_np**2))
            peak = np.max(np.abs(audio_np))
            
            # Calculate dynamic range
            dynamic_range = 20 * np.log10(peak / (rms + 1e-10))
            
            # Calculate zero crossing rate (indicator of speech clarity)
            zero_crossings = np.sum(np.diff(np.sign(audio_np)) != 0)
            zcr = zero_crossings / len(audio_np)
            
            # Calculate spectral centroid (brightness)
            stft = np.abs(librosa.stft(audio_np))
            freqs = librosa.fft_frequencies(sr=self.sample_rate)
            spectral_centroid = np.sum(freqs[:, np.newaxis] * stft, axis=0) / np.sum(stft, axis=0)
            
            # Calculate clarity score based on multiple factors
            clarity = self._calculate_speech_clarity(audio_np)
            
            return {
                "volume": float(rms),
                "peak_amplitude": float(peak),
                "dynamic_range": float(dynamic_range),
                "zero_crossing_rate": float(zcr),
                "spectral_centroid": float(np.mean(spectral_centroid)),
                "clarity": clarity,
                "is_clipped": peak > 0.95,
                "is_too_quiet": rms < 0.01
            }
            
        except Exception as e:
            logger.error(f"Audio quality analysis failed: {e}")
            return {"volume": 0.0, "clarity": 0.0}
    
    async def _detect_sound_events(self, audio_tensor: torch.Tensor) -> List[Dict[str, Any]]:
        """Detect sound events in audio."""
        if not self.sound_classification_pipeline:
            return []
        
        try:
            # Convert tensor to numpy for pipeline
            audio_np = audio_tensor.cpu().numpy()
            
            # Classify sounds
            results = self.sound_classification_pipeline(audio_np)
            
            # Process results
            sound_events = []
            for result in results[:5]:  # Top 5 detected sounds
                sound_events.append({
                    "label": result["label"],
                    "confidence": result["score"],
                    "accessibility_relevant": self._is_accessibility_relevant_sound(result["label"])
                })
            
            return sound_events
            
        except Exception as e:
            logger.error(f"Sound event detection failed: {e}")
            return []
    
    def _analyze_frequency_spectrum(self, audio_tensor: torch.Tensor) -> Dict[str, Any]:
        """Analyze frequency spectrum of audio."""
        try:
            audio_np = audio_tensor.cpu().numpy()
            
            # Compute FFT
            fft = np.fft.fft(audio_np)
            freqs = np.fft.fftfreq(len(fft), 1/self.sample_rate)
            magnitude = np.abs(fft)
            
            # Analyze frequency bands
            low_freq = np.sum(magnitude[(freqs >= 20) & (freqs < 250)])
            mid_freq = np.sum(magnitude[(freqs >= 250) & (freqs < 4000)])
            high_freq = np.sum(magnitude[(freqs >= 4000) & (freqs < 8000)])
            
            total_energy = low_freq + mid_freq + high_freq
            
            return {
                "low_frequency_energy": float(low_freq / (total_energy + 1e-10)),
                "mid_frequency_energy": float(mid_freq / (total_energy + 1e-10)),
                "high_frequency_energy": float(high_freq / (total_energy + 1e-10)),
                "dominant_frequency": float(freqs[np.argmax(magnitude[:len(freqs)//2])]),
                "frequency_range": {
                    "min": float(np.min(freqs[magnitude > np.max(magnitude) * 0.1])),
                    "max": float(np.max(freqs[magnitude > np.max(magnitude) * 0.1]))
                }
            }
            
        except Exception as e:
            logger.error(f"Frequency analysis failed: {e}")
            return {}
    
    def _detect_background_noise(self, audio_tensor: torch.Tensor) -> Dict[str, Any]:
        """Detect and analyze background noise."""
        try:
            audio_np = audio_tensor.cpu().numpy()
            
            # Simple noise detection using energy in quiet segments
            # Split audio into segments
            segment_length = self.sample_rate // 10  # 100ms segments
            segments = [audio_np[i:i+segment_length] for i in range(0, len(audio_np), segment_length)]
            
            # Calculate energy for each segment
            energies = [np.mean(segment**2) for segment in segments if len(segment) == segment_length]
            
            if not energies:
                return {"noise_level": 0.0, "snr": float('inf')}
            
            # Estimate noise floor (bottom 25% of energies)
            sorted_energies = sorted(energies)
            noise_floor = np.mean(sorted_energies[:len(sorted_energies)//4])
            
            # Estimate signal level (top 25% of energies)
            signal_level = np.mean(sorted_energies[3*len(sorted_energies)//4:])
            
            # Calculate SNR
            snr = 10 * np.log10((signal_level + 1e-10) / (noise_floor + 1e-10))
            
            return {
                "noise_level": float(noise_floor),
                "signal_level": float(signal_level),
                "snr": float(snr),
                "is_noisy": snr < 10  # SNR below 10dB is considered noisy
            }
            
        except Exception as e:
            logger.error(f"Background noise analysis failed: {e}")
            return {"noise_level": 0.0, "snr": 0.0}
    
    def _calculate_speech_clarity(self, audio_np: np.ndarray) -> float:
        """Calculate speech clarity score."""
        try:
            # Use multiple indicators for speech clarity
            
            # 1. Spectral clarity (energy distribution)
            stft = np.abs(librosa.stft(audio_np))
            spectral_rolloff = librosa.feature.spectral_rolloff(S=stft, sr=self.sample_rate)[0]
            clarity_spectral = np.mean(spectral_rolloff) / (self.sample_rate / 2)
            
            # 2. Temporal clarity (consistency)
            rms_frames = librosa.feature.rms(y=audio_np, frame_length=2048, hop_length=512)[0]
            clarity_temporal = 1.0 - np.std(rms_frames) / (np.mean(rms_frames) + 1e-10)
            
            # 3. Harmonic clarity
            harmonic, percussive = librosa.effects.hpss(audio_np)
            harmonic_ratio = np.sum(harmonic**2) / (np.sum(audio_np**2) + 1e-10)
            
            # Combine metrics
            clarity = (clarity_spectral + clarity_temporal + harmonic_ratio) / 3
            return max(0.0, min(1.0, clarity))
            
        except Exception as e:
            logger.error(f"Speech clarity calculation failed: {e}")
            return 0.5
    
    def _calculate_audio_accessibility_score(
        self,
        quality_metrics: Dict[str, Any],
        noise_analysis: Dict[str, Any],
        speech_content: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate overall audio accessibility score."""
        base_score = 1.0
        
        # Quality factors
        clarity = quality_metrics.get("clarity", 0.5)
        base_score *= clarity
        
        # Noise factors
        snr = noise_analysis.get("snr", 0)
        if snr < 10:
            base_score *= 0.7  # Penalty for noisy audio
        elif snr > 20:
            base_score *= 1.1  # Bonus for clean audio
        
        # Volume factors
        volume = quality_metrics.get("volume", 0.0)
        if volume < 0.01:
            base_score *= 0.5  # Penalty for too quiet
        elif volume > 0.8:
            base_score *= 0.8  # Penalty for too loud
        
        # Speech content factors
        if speech_content.get("has_speech"):
            base_score *= 1.2  # Bonus for having speech
            confidence = speech_content.get("confidence", 0.0)
            base_score *= (0.5 + 0.5 * confidence)  # Adjust by recognition confidence
        
        # User preference adjustments
        if user_preferences:
            if user_preferences.get("hearing_impairment"):
                # More stringent requirements for hearing impaired users
                if clarity < 0.8:
                    base_score *= 0.6
                if snr < 15:
                    base_score *= 0.5
        
        return max(0.0, min(1.0, base_score))
    
    def _generate_audio_recommendations(
        self,
        quality_metrics: Dict[str, Any],
        noise_analysis: Dict[str, Any],
        speech_content: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate audio accessibility recommendations."""
        recommendations = []
        
        # Quality-based recommendations
        clarity = quality_metrics.get("clarity", 0.5)
        if clarity < 0.6:
            recommendations.append("Audio clarity is low - consider noise reduction")
        
        volume = quality_metrics.get("volume", 0.0)
        if volume < 0.01:
            recommendations.append("Audio volume is too low - increase volume")
        elif volume > 0.8:
            recommendations.append("Audio volume is too high - reduce volume to prevent distortion")
        
        # Noise-based recommendations
        snr = noise_analysis.get("snr", 0)
        if snr < 10:
            recommendations.append("High background noise detected - use noise cancellation")
        
        # Speech-based recommendations
        if not speech_content.get("has_speech"):
            recommendations.append("No speech detected - ensure microphone is working")
        elif speech_content.get("confidence", 0.0) < 0.7:
            recommendations.append("Speech recognition confidence is low - speak more clearly")
        
        # User preference-based recommendations
        if user_preferences:
            if user_preferences.get("hearing_impairment"):
                recommendations.append("Enable visual captions for better accessibility")
                recommendations.append("Use frequency enhancement for better speech clarity")
            
            if user_preferences.get("cognitive_impairment"):
                recommendations.append("Use slower speech rate for better comprehension")
        
        return recommendations
    
    def _identify_audio_issues(
        self,
        quality_metrics: Dict[str, Any],
        noise_analysis: Dict[str, Any],
        speech_content: Dict[str, Any]
    ) -> List[str]:
        """Identify audio accessibility issues."""
        issues = []
        
        # Quality issues
        if quality_metrics.get("is_clipped", False):
            issues.append("Audio clipping detected")
        
        if quality_metrics.get("is_too_quiet", False):
            issues.append("Audio volume too low")
        
        clarity = quality_metrics.get("clarity", 0.5)
        if clarity < 0.4:
            issues.append("Poor speech clarity")
        
        # Noise issues
        if noise_analysis.get("is_noisy", False):
            issues.append("High background noise")
        
        # Speech issues
        if not speech_content.get("has_speech"):
            issues.append("No speech content detected")
        
        confidence = speech_content.get("confidence", 0.0)
        if confidence < 0.5:
            issues.append("Low speech recognition confidence")
        
        return issues
    
    def _preprocess_audio(
        self,
        audio_tensor: torch.Tensor,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> torch.Tensor:
        """Preprocess audio for better recognition."""
        audio_np = audio_tensor.cpu().numpy()
        
        try:
            # Normalize volume
            if self.accessibility_features["volume_normalization"]:
                audio_np = librosa.util.normalize(audio_np)
            
            # Noise reduction
            if self.accessibility_features["noise_reduction"]:
                audio_np = self._apply_noise_reduction(audio_np)
            
            # Speech enhancement
            if self.accessibility_features["speech_enhancement"]:
                audio_np = self._enhance_speech(audio_np)
            
            # User preference adjustments
            if user_preferences:
                if user_preferences.get("hearing_impairment"):
                    # Apply frequency enhancement
                    audio_np = self._apply_frequency_enhancement(audio_np)
        
        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
        
        return torch.tensor(audio_np, dtype=audio_tensor.dtype, device=audio_tensor.device)
    
    def _apply_noise_reduction(self, audio_np: np.ndarray) -> np.ndarray:
        """Apply basic noise reduction."""
        try:
            # Simple spectral subtraction
            stft = librosa.stft(audio_np)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise from first 0.5 seconds
            noise_frames = int(0.5 * self.sample_rate / 512)
            noise_spectrum = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
            
            # Subtract noise
            clean_magnitude = magnitude - 0.5 * noise_spectrum
            clean_magnitude = np.maximum(clean_magnitude, 0.1 * magnitude)
            
            # Reconstruct audio
            clean_stft = clean_magnitude * np.exp(1j * phase)
            clean_audio = librosa.istft(clean_stft)
            
            return clean_audio
            
        except Exception as e:
            logger.error(f"Noise reduction failed: {e}")
            return audio_np
    
    def _enhance_speech(self, audio_np: np.ndarray) -> np.ndarray:
        """Enhance speech clarity."""
        try:
            # Apply pre-emphasis filter
            pre_emphasis = 0.97
            emphasized = np.append(audio_np[0], audio_np[1:] - pre_emphasis * audio_np[:-1])
            
            # Apply mild compression
            compressed = np.sign(emphasized) * np.power(np.abs(emphasized), 0.8)
            
            return compressed
            
        except Exception as e:
            logger.error(f"Speech enhancement failed: {e}")
            return audio_np
    
    def _apply_frequency_enhancement(self, audio_np: np.ndarray) -> np.ndarray:
        """Apply frequency enhancement for hearing impaired users."""
        try:
            # Boost mid-frequencies (speech range)
            stft = librosa.stft(audio_np)
            freqs = librosa.fft_frequencies(sr=self.sample_rate)
            
            # Create frequency boost filter
            boost = np.ones_like(freqs)
            speech_range = (freqs >= 300) & (freqs <= 3400)
            boost[speech_range] = 1.5  # 3dB boost
            
            # Apply boost
            enhanced_stft = stft * boost[:, np.newaxis]
            enhanced_audio = librosa.istft(enhanced_stft)
            
            return enhanced_audio
            
        except Exception as e:
            logger.error(f"Frequency enhancement failed: {e}")
            return audio_np
    
    def _preprocess_text_for_tts(
        self,
        text: str,
        voice_settings: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> str:
        """Preprocess text for better TTS output."""
        processed_text = text
        
        # Apply user preferences
        if user_preferences:
            if user_preferences.get("cognitive_impairment"):
                # Simplify text structure
                processed_text = self._simplify_text(processed_text)
        
        # Apply voice settings
        if voice_settings:
            speed = voice_settings.get("speed", 1.0)
            if speed != 1.0:
                # Add pauses for slower speech
                if speed < 1.0:
                    processed_text = processed_text.replace(". ", ". ... ")
                    processed_text = processed_text.replace(", ", ", .. ")
        
        return processed_text
    
    def _simplify_text(self, text: str) -> str:
        """Simplify text for cognitive accessibility."""
        # Basic text simplification
        simplified = text.replace(";", ".")  # Replace semicolons with periods
        simplified = simplified.replace(" - ", ". ")  # Replace dashes with periods
        
        # Add pauses after sentences
        simplified = simplified.replace(". ", ". ... ")
        
        return simplified
    
    def _enhance_speech_for_accessibility(
        self,
        speech_tensor: torch.Tensor,
        voice_settings: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> torch.Tensor:
        """Enhance synthesized speech for accessibility."""
        speech_np = speech_tensor.cpu().numpy()
        
        try:
            # Apply voice settings
            if voice_settings:
                speed = voice_settings.get("speed", 1.0)
                pitch = voice_settings.get("pitch", 1.0)
                
                # Speed adjustment
                if speed != 1.0:
                    speech_np = librosa.effects.time_stretch(speech_np, rate=speed)
                
                # Pitch adjustment
                if pitch != 1.0:
                    speech_np = librosa.effects.pitch_shift(
                        speech_np, sr=self.sample_rate, n_steps=12 * np.log2(pitch)
                    )
            
            # Apply user preference enhancements
            if user_preferences:
                if user_preferences.get("hearing_impairment"):
                    # Enhance clarity
                    speech_np = self._enhance_speech(speech_np)
                    # Boost volume slightly
                    speech_np = speech_np * 1.2
                
                if user_preferences.get("cognitive_impairment"):
                    # Add slight pauses between words
                    speech_np = self._add_word_pauses(speech_np)
        
        except Exception as e:
            logger.error(f"Speech enhancement failed: {e}")
        
        return torch.tensor(speech_np, dtype=speech_tensor.dtype, device=speech_tensor.device)
    
    def _add_word_pauses(self, speech_np: np.ndarray) -> np.ndarray:
        """Add slight pauses between words for cognitive accessibility."""
        try:
            # Simple implementation: detect word boundaries and add pauses
            # This is a simplified version - real implementation would be more sophisticated
            
            # Detect silence periods (word boundaries)
            frame_length = 2048
            hop_length = 512
            rms = librosa.feature.rms(y=speech_np, frame_length=frame_length, hop_length=hop_length)[0]
            
            # Find silence frames
            silence_threshold = np.mean(rms) * 0.1
            silence_frames = rms < silence_threshold
            
            # Extend silence periods slightly
            extended_speech = []
            frame_samples = hop_length
            
            for i, frame in enumerate(silence_frames):
                start_sample = i * frame_samples
                end_sample = min((i + 1) * frame_samples, len(speech_np))
                frame_audio = speech_np[start_sample:end_sample]
                
                extended_speech.append(frame_audio)
                
                # Add extra silence if this is a silence frame
                if frame and i < len(silence_frames) - 1:
                    pause_length = int(0.1 * self.sample_rate)  # 100ms pause
                    extended_speech.append(np.zeros(pause_length))
            
            return np.concatenate(extended_speech)
            
        except Exception as e:
            logger.error(f"Adding word pauses failed: {e}")
            return speech_np
    
    def _get_applied_enhancements(self, user_preferences: Optional[Dict[str, Any]] = None) -> List[str]:
        """Get list of applied accessibility enhancements."""
        enhancements = []
        
        if self.accessibility_features["volume_normalization"]:
            enhancements.append("Volume normalization")
        
        if self.accessibility_features["noise_reduction"]:
            enhancements.append("Noise reduction")
        
        if self.accessibility_features["speech_enhancement"]:
            enhancements.append("Speech enhancement")
        
        if user_preferences:
            if user_preferences.get("hearing_impairment"):
                enhancements.append("Frequency enhancement for hearing impairment")
            
            if user_preferences.get("cognitive_impairment"):
                enhancements.append("Cognitive accessibility enhancements")
        
        return enhancements
    
    def _calculate_transcription_confidence(
        self,
        input_features: torch.Tensor,
        predicted_ids: torch.Tensor
    ) -> float:
        """Calculate confidence score for transcription (simplified)."""
        try:
            # This is a simplified confidence calculation
            # Real implementation would use model probabilities
            
            # Use input signal quality as a proxy for confidence
            signal_energy = torch.mean(input_features**2).item()
            
            # Normalize to 0-1 range
            confidence = min(1.0, signal_energy * 10)
            
            return confidence
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5
    
    def _detect_language(self, text: str) -> str:
        """Detect language from transcribed text (simplified)."""
        # This is a very basic language detection
        # Real implementation would use proper language detection models
        
        if not text:
            return "unknown"
        
        # Simple heuristics based on common words
        text_lower = text.lower()
        
        english_indicators = ["the", "and", "is", "in", "to", "of", "a", "that", "it", "with"]
        spanish_indicators = ["el", "la", "de", "que", "y", "en", "un", "es", "se", "no"]
        french_indicators = ["le", "de", "et", "à", "un", "il", "être", "et", "en", "avoir"]
        
        english_score = sum(1 for word in english_indicators if word in text_lower)
        spanish_score = sum(1 for word in spanish_indicators if word in text_lower)
        french_score = sum(1 for word in french_indicators if word in text_lower)
        
        scores = {"en": english_score, "es": spanish_score, "fr": french_score}
        detected_lang = max(scores, key=scores.get)
        
        return detected_lang if scores[detected_lang] > 0 else "unknown"
    
    def _is_accessibility_relevant_sound(self, sound_label: str) -> bool:
        """Check if detected sound is relevant for accessibility."""
        accessibility_relevant_sounds = [
            "speech", "music", "alarm", "siren", "doorbell", "phone",
            "car", "traffic", "footsteps", "applause", "crying", "laughter",
            "coughing", "sneezing", "typing", "clicking", "beeping"
        ]
        
        return any(relevant in sound_label.lower() for relevant in accessibility_relevant_sounds)
    
    def _bytes_to_audio_tensor(self, audio_data: bytes) -> torch.Tensor:
        """Convert audio bytes to tensor."""
        try:
            # Try to load as WAV first
            audio_io = io.BytesIO(audio_data)
            with wave.open(audio_io, 'rb') as wav_file:
                frames = wav_file.readframes(-1)
                audio_np = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Resample if necessary
                original_sr = wav_file.getframerate()
                if original_sr != self.sample_rate:
                    audio_np = librosa.resample(audio_np, orig_sr=original_sr, target_sr=self.sample_rate)
                
                return torch.tensor(audio_np, dtype=torch.float32)
        
        except Exception:
            # Fallback: try to interpret as raw audio data
            try:
                audio_np = np.frombuffer(audio_data, dtype=np.float32)
                return torch.tensor(audio_np, dtype=torch.float32)
            except Exception as e:
                logger.error(f"Failed to convert audio bytes to tensor: {e}")
                # Return empty tensor
                return torch.zeros(self.sample_rate, dtype=torch.float32)
    
    def _audio_tensor_to_bytes(self, audio_tensor: torch.Tensor) -> bytes:
        """Convert audio tensor to bytes."""
        try:
            # Convert to numpy and scale to int16 range
            audio_np = audio_tensor.cpu().numpy()
            audio_int16 = (audio_np * 32767).astype(np.int16)
            
            # Create WAV file in memory
            audio_io = io.BytesIO()
            with wave.open(audio_io, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_int16.tobytes())
            
            return audio_io.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to convert audio tensor to bytes: {e}")
            return b""
    
    async def shutdown(self) -> None:
        """Shutdown the audio model and free resources."""
        logger.info("Shutting down audio model...")
        
        # Clear model references
        if self.speech_recognition_model:
            del self.speech_recognition_model
            self.speech_recognition_model = None
        
        if self.text_to_speech_model:
            del self.text_to_speech_model
            self.text_to_speech_model = None
        
        if self.text_to_speech_vocoder:
            del self.text_to_speech_vocoder
            self.text_to_speech_vocoder = None
        
        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self._initialized = False
        logger.info("Audio model shutdown complete")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models."""
        return {
            "speech_recognition": {
                "model": self.asr_model_name,
                "loaded": self.speech_recognition_model is not None,
                "supported_languages": list(self.supported_languages.keys())
            },
            "text_to_speech": {
                "model": self.tts_model_name,
                "loaded": self.text_to_speech_model is not None,
                "vocoder": self.tts_vocoder_name
            },
            "sound_classification": {
                "loaded": self.sound_classification_pipeline is not None
            },
            "accessibility_features": self.accessibility_features,
            "device": str(self.device),
            "sample_rate": self.sample_rate,
            "initialized": self._initialized
        } 