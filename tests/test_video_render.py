import unittest
import numpy as np
from joint_perception_lab.video_render import bgr_to_psychopy, display_size

class TestVideoRender(unittest.TestCase):
    def test_rgb_float_mapping(self):
        bgr = np.array([[[0,0,255], [255,0,0], [0,0,0], [255,255,255]]], dtype=np.uint8)
        out = bgr_to_psychopy(bgr)
        self.assertEqual(out.dtype, np.float32)
        self.assertTrue(out.flags.c_contiguous)
        np.testing.assert_allclose(out[0,0], [1,-1,-1])
        np.testing.assert_allclose(out[0,1], [-1,-1,1])
        np.testing.assert_allclose(out[0,2], [-1,-1,-1])
        np.testing.assert_allclose(out[0,3], [1,1,1])
    def test_native_size(self):
        self.assertEqual(display_size(1024,768,1920,1080), (1024,768))
    def test_reject_invalid(self):
        with self.assertRaises(ValueError):
            bgr_to_psychopy(np.zeros((2,2,3), dtype=np.float32))
if __name__ == '__main__': unittest.main()
