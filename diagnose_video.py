"""Standalone visual diagnostic. Does not record participant data.
Usage: .venv\Scripts\python.exe diagnose_video.py "path\to\video.mp4"
"""
import sys
import cv2
import numpy as np
from psychopy import visual, core, event


def main(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []
    while True:
        ok, bgr = cap.read()
        if not ok:
            break
        frames.append(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
    cap.release()
    if not frames or fps <= 0:
        raise RuntimeError('Video has no decodable frames or invalid FPS')
    h, w = frames[0].shape[:2]
    win = visual.Window(fullscr=True, color=(-1, -1, -1), units='height', waitBlanking=True)
    try:
        sw, sh = win.size
        scale = min(.9*sw/w, .9*sh/h)
        stim = visual.ImageStim(win, image=frames[0], size=(w*scale/sh, h*scale/sh),
                                units='height', interpolate=False)
        label = visual.TextStim(win, text='', color='white', height=.025,
                                pos=(0, -.47), units='height')
        def present(msg, seconds):
            label.text = msg
            stim.draw()
            label.draw()
            win.flip(clearBuffer=True)
            core.wait(seconds)
        print(f'Video: {w}x{h}, {fps:.3f} fps, {len(frames)} frames; display: {sw}x{sh}')
        present('TEST 1: STILL FRAME — dots should have no trails', 4)
        label.text = ''
        clock = core.Clock()
        start = None
        flips = []
        for i, frame in enumerate(frames):
            if event.getKeys(keyList=['escape']):
                return
            if start is not None:
                while clock.getTime() < start + i/fps - .003:
                    core.wait(.001)
            stim.image = frame
            stim.draw()
            win.flip(clearBuffer=True)
            flips.append(clock.getTime())
            if start is None:
                start = flips[0]
        # Clear the final frame immediately after nominal video duration.
        while clock.getTime() < start + len(frames)/fps:
            core.wait(.001)
        win.flip(clearBuffer=True)
        core.wait(.5)
        print(f'Presented {len(frames)} frames; elapsed between first and last flip: {flips[-1]-flips[0]:.3f}s')
        print('Expected first-to-last interval:', round((len(frames)-1)/fps, 3), 's')
        print('This diagnostic does not prove frame-accurate timing.')
    finally:
        win.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: .venv\\Scripts\\python.exe diagnose_video.py "C:\\path\\to\\video.mp4"')
        sys.exit(2)
    main(sys.argv[1])
