"""Text-to-Speech Generator Module

Responsible for converting Tamil text to speech using AI4Bharat Indic-TTS.
Supports multiple TTS backends including Coqui TTS and gTTS as fallback.
"""

import os
import warnings
from typing import Optional
from pathlib import Path

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    warnings.warn("Coqui TTS not installed. TTS features will be limited.")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False


class TTSGenerator:
    """
    Text-to-Speech generator for Tamil language.
    Supports AI4Bharat Indic-TTS via Coqui TTS or gTTS as fallback.
    """
    
    def __init__(self, backend: str = "coqui", device: str = "cpu"):
        """
        Initialize TTS generator.
        
        Args:
            backend: TTS backend to use ('coqui' or 'gtts')
            device: Device for inference ('cpu' or 'cuda')
        """
        self.backend = backend
        self.device = device
        self.tts_model = None
        self._is_initialized = False
        
        # Model cache directory
        self.cache_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'tts')
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def initialize(self):
        """Lazy load the TTS model."""
        if self._is_initialized:
            return
        
        if self.backend == "coqui":
            self._initialize_coqui()
        elif self.backend == "gtts":
            self._initialize_gtts()
        else:
            raise ValueError(f"Unknown TTS backend: {self.backend}")
        
        self._is_initialized = True
    
    def _initialize_coqui(self):
        """Initialize Coqui TTS with Indic-TTS model."""
        if not TTS_AVAILABLE:
            raise ImportError(
                "Coqui TTS not installed. Install with: pip install TTS"
            )
        
        print("Loading Indic-TTS model...")
        print("This may take a few minutes on first run...")
        
        try:
            # List available models
            # For Tamil, we can use multilingual models or specific Indic models
            # Options:
            # 1. "tts_models/multilingual/multi-dataset/your_tts"
            # 2. Custom AI4Bharat model if available
            
            # Using a multilingual model that supports Tamil
            model_name = "tts_models/multilingual/multi-dataset/your_tts"
            
            self.tts_model = TTS(
                model_name=model_name,
                progress_bar=True,
                gpu=(self.device == "cuda")
            )
            
            print(f"✓ TTS model loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"Warning: Failed to load Coqui TTS: {str(e)}")
            print("Falling back to gTTS...")
            self.backend = "gtts"
            self._initialize_gtts()
    
    def _initialize_gtts(self):
        """Initialize gTTS (fallback option)."""
        if not GTTS_AVAILABLE:
            raise ImportError(
                "gTTS not installed. Install with: pip install gtts"
            )
        
        print("✓ Using gTTS for Tamil text-to-speech")
    
    def generate(self, text: str, output_path: str, language: str = "ta") -> str:
        """
        Generate speech audio from text.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            language: Language code (default: 'ta' for Tamil)
            
        Returns:
            str: Path to the saved audio file
        """
        if not self._is_initialized:
            self.initialize()
        
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Ensure output path has .wav extension
        if not output_path.endswith('.wav') and not output_path.endswith('.mp3'):
            output_path += '.wav'
        
        try:
            if self.backend == "coqui":
                self._generate_coqui(text, output_path, language)
            elif self.backend == "gtts":
                self._generate_gtts(text, output_path, language)
            
            # Verify file was created
            if not os.path.exists(output_path):
                raise RuntimeError("Audio file was not created")
            
            print(f"✓ Audio saved to: {output_path}")
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"TTS generation failed: {str(e)}")
    
    def _generate_coqui(self, text: str, output_path: str, language: str):
        """Generate audio using Coqui TTS."""
        try:
            # For multilingual models, specify speaker/language
            self.tts_model.tts_to_file(
                text=text,
                file_path=output_path,
                language=language
            )
        except Exception as e:
            # Try without language parameter
            try:
                self.tts_model.tts_to_file(
                    text=text,
                    file_path=output_path
                )
            except Exception as e2:
                raise RuntimeError(f"Coqui TTS failed: {str(e2)}")
    
    def _generate_gtts(self, text: str, output_path: str, language: str):
        """Generate audio using gTTS."""
        try:
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(output_path)
        except Exception as e:
            raise RuntimeError(f"gTTS failed: {str(e)}")


# Global TTS generator instance
_tts_generator_instance: Optional[TTSGenerator] = None


def get_tts_generator(backend: str = "gtts", device: str = "cpu") -> TTSGenerator:
    """
    Get or create a global TTS generator instance.
    
    Args:
        backend: TTS backend ('coqui' or 'gtts')
        device: Device to use ('cpu' or 'cuda')
        
    Returns:
        TTSGenerator: Global TTS generator instance
    """
    global _tts_generator_instance
    
    if _tts_generator_instance is None:
        _tts_generator_instance = TTSGenerator(backend=backend, device=device)
    
    return _tts_generator_instance


def generate_tts(text: str, output_path: str, language: str = "ta", backend: str = "gtts", device: str = "cpu") -> str:
    """
    Generate Tamil text-to-speech audio.
    
    Args:
        text: Tamil text to convert to speech
        output_path: Path to save the audio file (.wav or .mp3)
        language: Language code (default: 'ta' for Tamil)
        backend: TTS backend to use ('coqui' or 'gtts', default: 'gtts')
        device: Device to use ('cpu' or 'cuda')
        
    Returns:
        str: Path to the saved audio file
        
    Example:
        >>> audio_path = generate_tts(
        ...     "இது அரசாங்க சுற்றறிக்கை.",
        ...     "output.wav"
        ... )
        >>> print(f"Audio saved to: {audio_path}")
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    # Get TTS generator
    generator = get_tts_generator(backend=backend, device=device)
    
    # Generate audio
    audio_path = generator.generate(text, output_path, language)
    
    return audio_path


def generate_tts_tamil(text: str, output_path: str, backend: str = "gtts") -> str:
    """
    Convenience function for Tamil TTS generation.
    
    Args:
        text: Tamil text to convert to speech
        output_path: Path to save the audio file
        backend: TTS backend to use (default: 'gtts' for reliability)
        
    Returns:
        str: Path to the saved audio file
    """
    return generate_tts(text, output_path, language="ta", backend=backend)


def split_text_for_tts(text: str, max_chars: int = 5000) -> list:
    """
    Split long text into chunks suitable for TTS.
    gTTS has a limit of ~5000 characters per request.
    
    Args:
        text: Long text to split
        max_chars: Maximum characters per chunk
        
    Returns:
        list: List of text chunks
    """
    if len(text) <= max_chars:
        return [text]
    
    # Split by sentences (basic)
    sentences = text.replace('।', '.').split('.')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Check if adding this sentence exceeds limit
        if len(current_chunk) + len(sentence) + 1 <= max_chars:
            current_chunk += sentence + ". "
        else:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def generate_tts_long_text(text: str, output_path: str, backend: str = "gtts") -> list:
    """
    Generate TTS for long text by splitting into chunks.
    
    Args:
        text: Long text to convert
        output_path: Base path for output files (will add _part1, _part2, etc.)
        backend: TTS backend to use
        
    Returns:
        list: List of generated audio file paths
    """
    chunks = split_text_for_tts(text)
    
    if len(chunks) == 1:
        # Single file
        return [generate_tts(text, output_path, backend=backend)]
    
    # Multiple files
    audio_paths = []
    base_path = Path(output_path)
    base_name = base_path.stem
    extension = base_path.suffix or '.wav'
    output_dir = base_path.parent
    
    for i, chunk in enumerate(chunks, 1):
        part_path = output_dir / f"{base_name}_part{i}{extension}"
        print(f"Generating audio part {i}/{len(chunks)}...")
        audio_path = generate_tts(chunk, str(part_path), backend=backend)
        audio_paths.append(audio_path)
    
    return audio_paths


def check_tts_available() -> dict:
    """
    Check which TTS backends are available.
    
    Returns:
        dict: Status of each backend
    """
    return {
        'coqui': TTS_AVAILABLE,
        'gtts': GTTS_AVAILABLE,
        'any_available': TTS_AVAILABLE or GTTS_AVAILABLE
    }


if __name__ == "__main__":
    # Test the module
    import sys
    
    print("Testing TTS Generator Module")
    print("=" * 60)
    
    # Check availability
    status = check_tts_available()
    print("TTS Backend Availability:")
    print(f"  Coqui TTS: {'✓' if status['coqui'] else '✗'}")
    print(f"  gTTS: {'✓' if status['gtts'] else '✗'}")
    print()
    
    if not status['any_available']:
        print("❌ No TTS backend available. Please install:")
        print("   pip install gtts")
        print("   OR")
        print("   pip install TTS")
        exit(1)
    
    # Test text
    tamil_text = "இது ஒரு சோதனை. இது தமிழ் உரையிலிருந்து பேச்சு உருவாக்கம்."
    
    # Determine output path
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'temp_audio')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'test_output.wav')
    
    print(f"Tamil Text: {tamil_text}")
    print(f"Output File: {output_file}")
    print()
    
    # Try gTTS first (more reliable)
    if status['gtts']:
        print("Test 1: Using gTTS")
        print("-" * 60)
        try:
            audio_path = generate_tts_tamil(tamil_text, output_file, backend="gtts")
            file_size = os.path.getsize(audio_path)
            print(f"✓ Success! Audio file created: {audio_path}")
            print(f"  File size: {file_size} bytes")
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
    
    # Try Coqui TTS if available
    if status['coqui']:
        print("\nTest 2: Using Coqui TTS")
        print("-" * 60)
        output_file2 = os.path.join(output_dir, 'test_output_coqui.wav')
        try:
            audio_path = generate_tts_tamil(tamil_text, output_file2, backend="coqui")
            file_size = os.path.getsize(audio_path)
            print(f"✓ Success! Audio file created: {audio_path}")
            print(f"  File size: {file_size} bytes")
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
