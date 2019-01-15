from processor.tools.basetool import BaseTool
import pygame
import cv2
import numpy as np
import matplotlib.pyplot as plt


class Snitch(BaseTool):
    def __init__(self):
        super().__init__()
        self.sift = cv2.xfeatures2d.SIFT_create()
        self.matcher = cv2.BFMatcher()
        self.thresh = 4
        self.sender_focus = None
        self.receiver_focus = None

    def process(self, processor, event: pygame.event):
        focus = processor.focus
        if not processor.process_initialized:
            processor.process_initialized = True
            self.sender_focus = focus
            self.receiver_focus = None
        if focus != self.sender_focus and self.receiver_focus is None:
            self.receiver_focus = focus

        if processor.confirm:
            if self.receiver_focus is not None:
                img1 = np.swapaxes(self.sender_focus.raw_data[:, :, :3], 0, 1)
                img2 = np.swapaxes(self.receiver_focus.raw_data[:, :, :3], 0, 1)
                kp1s, feature1s = self.detect_and_describe(img1, self.sift)
                kp2s, feature2s = self.detect_and_describe(img2, self.sift)
                matches = self.matcher.knnMatch(feature1s, feature2s, k=2)
                matches = self.ratio_test(matches, 0.75)
                ptsA = np.float32([kp1s[i] for (i, _) in matches])
                ptsB = np.float32([kp2s[i] for (_, i) in matches])
                result = self.stitch_image(img1, img2, ptsA, ptsB, self.thresh)
                plt.imshow(result)
                plt.show()

            processor.REFRESH = True
            processor.PROCESS = False

        if processor.cancel:
            processor.PROCESS = False

    def ratio_test(self, raw_matches, ratio):
        # ratio test
        matches = []
        for m in raw_matches:
            if len(m)==2 and m[0].distance < ratio * m[1].distance:
                matches.append((m[0].queryIdx, m[0].trainIdx))

        return matches

    def detect_and_describe(self, image, descriptor):
        kps, features = descriptor.detectAndCompute(image, None)
        kps = np.float32([kp.pt for kp in kps])

        return kps, features

    def get_smooth_mask(self, shape):
        mask = np.zeros(shape)
        mat = np.eye(shape[0])
        mat[:, 0] = 1
        mask[0, :shape[1]] = np.linspace(0, 1, shape[1])
        mask = np.matmul(mat, mask)

        return mask

    def stitch_image(self, imageA, imageB, ptsA, ptsB, thresh):
        (H, status) = cv2.findHomography(ptsB, ptsA, cv2.RANSAC, thresh)
        imageBwarped = cv2.warpPerspective(imageB, H, (imageA.shape[1] + imageB.shape[1], imageA.shape[0]))
        mask = np.ones(imageBwarped.shape[:2], dtype=np.float32)
        mask[:, :imageA.shape[1]] = 0
        smooth_lim = imageA.shape[1] // 10
        mask[:, imageA.shape[1]-smooth_lim:imageA.shape[1]] = self.get_smooth_mask((imageA.shape[0], smooth_lim))
        mask = mask * (imageBwarped[:, :, 0] != 0)
        result = imageBwarped.copy()
        result[:imageA.shape[0], :imageA.shape[1]] = imageA * (1-mask[:, :imageA.shape[1], None]) + \
                                                     (imageBwarped * mask[:, :, None])[:, :imageA.shape[1], :]

        return result

