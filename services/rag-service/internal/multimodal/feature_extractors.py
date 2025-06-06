"""
feature_extractors - 索克生活项目模块
"""

    import cv2
    import easyocr
    import tempfile
    import whisper
from PIL import Image
from typing import List, Optional
import io


# 图片OCR
try:
    _ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
except ImportError:
    _ocr_reader = None

def extract_image_text(image_bytes: bytes) -> str:
    if not _ocr_reader:
        return "[OCR模块未安装]"
    image = Image.open(io.BytesIO(image_bytes))
    result = _ocr_reader.readtext(np.array(image), detail=0)
    return '\n'.join(result)

# 音频ASR
try:
    _asr_model = whisper.load_model('base')
except ImportError:
    _asr_model = None

def extract_audio_text(audio_bytes: bytes) -> str:
    if not _asr_model:
        return "[ASR模块未安装]"
    with tempfile.NamedTemporaryFile(suffix='.wav') as f:
        f.write(audio_bytes)
        f.flush()
        result = _asr_model.transcribe(f.name)
    return result.get('text', '')

# 视频帧抽取
try:
except ImportError:
    cv2 = None

def extract_video_keyframes(video_bytes: bytes, max_frames: int = 3) -> List[bytes]:
    if not cv2:
        return []
    frames = []
    with tempfile.NamedTemporaryFile(suffix='.mp4') as f:
        f.write(video_bytes)
        f.flush()
        cap = cv2.VideoCapture(f.name)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        idxs = np.linspace(0, total-1, min(max_frames, total)).astype(int)
        for idx in idxs:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                _, buf = cv2.imencode('.jpg', frame)
                frames.append(buf.tobytes())
        cap.release()
    return frames 