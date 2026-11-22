"""Controlled same-frame display test. No participant data are recorded.

Usage: .venv\\Scripts\\python.exe diagnose_video_v2.py "path\\to\\S24L0.mp4"
Press SPACE to advance; ESC to quit. Tests use exactly the same first frame.
"""
from pathlib import Path
import sys
import tempfile
import cv2
import numpy as np
from psychopy import visual, core, event
from joint_perception_lab.video_render import bgr_to_psychopy, decode_video, display_size


def main(path):
    frames, fps = decode_video(path)
    h, w = frames[0].shape[:2]
    float_frame = bgr_to_psychopy(frames[0])
    rgb_uint8 = cv2.cvtColor(frames[0], cv2.COLOR_BGR2RGB)
    win = visual.Window(fullscr=True, units='pix', color=(-1,-1,-1),
                        allowGUI=False, waitBlanking=True)
    try:
        sw, sh = map(int, win.size)
        native = display_size(w, h, sw, sh, 'native')
        label = visual.TextStim(win, units='pix', pos=(0, -sh/2 + 42), height=20,
                                color='white', text='', wrapWidth=sw-80)
        stim = visual.ImageStim(win, units='pix', image=float_frame, size=native,
                                interpolate=True)
        print(f'Video: {path}; {w}x{h}, {fps:.6f} fps, {len(frames)} frames')
        print(f'Monitor: {sw}x{sh}; native displayed size: {native}')
        print('Press SPACE to advance between comparisons. ESC to quit.')

        with tempfile.TemporaryDirectory(prefix='jpl_video_') as temp:
            png = Path(temp) / 'exact_first_frame.png'
            cv2.imwrite(str(png), frames[0])
            tests = [
                ('A: PNG loaded from disk, native size, interpolation ON', str(png), True),
                ('B: OpenCV decoded as RGB float32, native size, interpolation ON', float_frame, True),
                ('C: OpenCV decoded as RGB float32, native size, interpolation OFF', float_frame, False),
                ('D: OpenCV decoded as RGB uint8, native size, interpolation ON', rgb_uint8, True),
            ]
            for title, frame, interpolate in tests:
                stim = visual.ImageStim(win, units='pix', image=frame, size=native,
                                        interpolate=interpolate)
                label.text = title + '   |   SPACE: next   ESC: quit'
                event.clearEvents()
                while True:
                    stim.draw(); label.draw(); win.flip(clearBuffer=True)
                    keys = event.getKeys(keyList=['space','escape'])
                    if 'escape' in keys:
                        return
                    if 'space' in keys:
                        break
                    core.wait(.01)

        label.text = 'E: Moving video, native size, RGB float32, interpolation ON   |   ESC: quit'
        stim = visual.ImageStim(win, units='pix', image=float_frame, size=native,
                                interpolate=True)
        clock = core.Clock()
        onset = None
        flips = []
        for i, bgr in enumerate(frames):
            if event.getKeys(keyList=['escape']):
                return
            if onset is not None:
                while clock.getTime() < onset + i/fps - .003:
                    core.wait(.001)
            stim.image = bgr_to_psychopy(bgr)
            stim.draw(); label.draw()
            win.flip(clearBuffer=True)
            t = clock.getTime()
            flips.append(t)
            if onset is None:
                onset = t
        while clock.getTime() < onset + len(frames)/fps:
            core.wait(.001)
        print('Actual first-to-last flip interval:', round(flips[-1]-flips[0],4), 's')
        print('Nominal first-to-last interval:', round((len(frames)-1)/fps,4), 's')
        print('Timing is not hardware-validated. Press SPACE to exit.')
        event.clearEvents()
        label.text = 'Test complete. Press SPACE to exit.'
        while True:
            label.draw(); win.flip(clearBuffer=True)
            if event.getKeys(keyList=['space','escape']):
                break
            core.wait(.01)
    finally:
        win.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: .venv\\Scripts\\python.exe diagnose_video_v2.py "path\\to\\S24L0.mp4"')
        sys.exit(2)
    main(sys.argv[1])
