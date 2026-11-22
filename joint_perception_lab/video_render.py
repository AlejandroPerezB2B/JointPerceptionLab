"""Pixel-faithful image transfer utilities for biological-motion videos.

OpenCV decodes BGR uint8 frames. PsychoPy ImageStim accepts float arrays in
[-1, 1]; we convert explicitly, and present in *pixel* units. This avoids
ambiguous dtype/range interpretation and unintentional display enlargement.
"""
from __future__ import annotations
import numpy as np


def bgr_to_psychopy(bgr: np.ndarray) -> np.ndarray:
    if bgr.dtype != np.uint8 or bgr.ndim != 3 or bgr.shape[2] != 3:
        raise ValueError('Expected OpenCV BGR uint8 image with three channels')
    rgb = bgr[:, :, ::-1]
    # Contiguous float32 avoids negative strides and ambiguous unsigned image ranges.
    return np.ascontiguousarray(rgb, dtype=np.float32) / 127.5 - 1.0


def display_size(source_width: int, source_height: int,
                 screen_width: int, screen_height: int, mode='native') -> tuple[int, int]:
    if mode == 'native':
        if source_width > screen_width or source_height > screen_height:
            raise ValueError('Native-size video exceeds display resolution; use fit mode')
        return source_width, source_height
    if mode == 'fit':
        scale = min(screen_width / source_width, screen_height / source_height, 1.0)
        return round(source_width * scale), round(source_height * scale)
    raise ValueError(f'Unknown video display mode: {mode}')


def decode_video(path):
    import cv2
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f'Cannot open video: {path}')
    try:
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        frames = []
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frames.append(frame)
    finally:
        cap.release()
    if not frames or not (0 < fps < 1000):
        raise RuntimeError(f'Video contains no frames or has invalid FPS: {path}')
    return frames, fps
