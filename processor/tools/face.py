from processor.tools.basetool import BaseTool
import pygame
import dlib
import cv2
import numpy as np


class Face(BaseTool):
    def __init__(self):
        super().__init__()
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("resources/dats/shape_predictor_68_face_landmarks.dat")

    def process(self, processor, event: pygame.event):
        focus = processor.focus
        raw_data = focus.raw_data
        pixel_array = raw_data[:, :, :3]
        pixel_array = np.swapaxes(pixel_array, 0, 1)
        pixel_bgr = cv2.cvtColor(pixel_array, cv2.COLOR_RGB2BGR)
        dets = self.detector(pixel_bgr, 1)
        shape = None

        for index, d in enumerate(dets):
            shape = self.predictor(pixel_bgr, d)

        xys = []
        for i in range(0, 68):
            xys.append((shape.part(i).x, shape.part(i).y))

        outline = xys[:17]
        l_eyebrow = xys[17:22]
        r_eyebrow = xys[22:27]
        nose = xys[27:28] + xys[31:36]
        l_eye = xys[36:42]
        r_eye = xys[42:48]
        mouth = xys[48:68]
        nose_mask = self.get_mask(nose, pixel_bgr)

        # get front head ellipse
        center = np.mean((outline[0], outline[-1]), axis=0)
        center = (int(center[0]), int(center[1]))
        comp = np.complex(*np.subtract(outline[0], outline[-1]))
        diameter = np.abs(comp)
        angle = np.angle(comp) / np.pi * 180
        minor = int(diameter / 2)
        major = int(np.linalg.norm(np.subtract(center, outline[8])))
        fronthead = self.get_zeros(pixel_bgr)
        cv2.ellipse(img=fronthead, center=center, axes=(minor, major),
                    angle=angle, startAngle=0, endAngle=180, color=(0, 0, 255), thickness=-1)
        # get front head mask
        low, up = self.get_bound(pixel_bgr[nose_mask], 1.5)
        color_mask = (pixel_bgr[:, :, :] >= low) * (pixel_bgr[:, :, :] <= up)
        color_mask = np.mean(color_mask, 2) > 0
        fronthead_mask = (fronthead[:, :, 2] == 255) * color_mask
        fronthead = self.get_zeros(pixel_bgr)
        fronthead[fronthead_mask] = (0, 0, 255)
        Y, Cr, Cb = cv2.split(cv2.cvtColor(fronthead, cv2.COLOR_BGR2YCR_CB))
        ksize = self.get_ksize(pixel_bgr.shape[:2], 20)
        Y = cv2.blur(Y, ksize)
        ret, thresh = cv2.threshold(Y, 45, 255, 0)
        points = np.array(np.where(thresh > 0), dtype=np.int32).transpose()
        landmark = cv2.convexHull(points).squeeze()
        contour = self.get_zeros(pixel_bgr)
        contour = cv2.fillConvexPoly(contour, np.flip(landmark, 1), (0, 0, 255))
        # get organ mask
        outline_mask = self.get_mask(outline, pixel_bgr)
        l_eyebrow_mask = self.get_mask(l_eyebrow, pixel_bgr)
        r_eyebrow_mask = self.get_mask(r_eyebrow, pixel_bgr)
        l_eye_mask = self.get_mask(l_eye, pixel_bgr)
        r_eye_mask = self.get_mask(r_eye, pixel_bgr)
        mouth_mask = self.get_mask(mouth, pixel_bgr)
        face_mask = (contour[:, :, 2] == 255) | (outline_mask)
        face_mask = face_mask & (~ l_eyebrow_mask) & (~ r_eyebrow_mask) & (~ l_eye_mask) & \
                    (~ r_eye_mask) & (~ mouth_mask)
        # whiten
        enhanced = pixel_bgr.copy()
        blurred_mask = cv2.blur(np.float32(face_mask), ksize)
        enhanced = (enhanced + blurred_mask[:, :, None] * np.ones(enhanced.shape) * 10).astype(np.int32)
        enhanced = np.clip(enhanced, 0, 255)
        # eye
        blurred_mask = cv2.blur(np.array(l_eye_mask | r_eye_mask, dtype=np.float32), ksize)
        H, S, V = cv2.split(cv2.cvtColor(np.float32(enhanced), cv2.COLOR_BGR2HSV))
        V = (V + blurred_mask * np.ones(enhanced.shape[:2]) * 30)
        V = np.clip(V, 0, 255).astype(np.float32)
        enhanced = cv2.cvtColor(np.float32(cv2.merge((H, S, V))), cv2.COLOR_HSV2BGR)
        # mouth
        mouth_ksize = self.get_ksize(pixel_bgr.shape[:2], 50)
        blurred_mask = cv2.blur(np.array(mouth_mask, dtype=np.float32), mouth_ksize)
        H, S, V = cv2.split(cv2.cvtColor(np.float32(enhanced), cv2.COLOR_BGR2HSV))
        S = (S + blurred_mask * np.ones(enhanced.shape[:2]) * 0.3)
        S = np.clip(S, 0, 255).astype(np.float32)
        enhanced = cv2.cvtColor(np.float32(cv2.merge((H, S, V))), cv2.COLOR_HSV2BGR)
        # smooth
        blurred_mask = cv2.blur(np.array(face_mask, dtype=np.float32), ksize)[:, :, None]
        if ksize[0] > 5:
            blurred = cv2.medianBlur(np.uint8(enhanced), ksize[0])
        else:
            blurred = cv2.medianBlur(np.float32(enhanced), ksize[0])
        enhanced = enhanced * (1 - blurred_mask * 0.5) + blurred * blurred_mask * 0.5
        enhanced = np.clip(enhanced, 0, 255).astype(np.int32)
        enhanced = cv2.cvtColor(np.float32(enhanced), cv2.COLOR_BGR2RGB)

        raw_data[:, :, :3] = np.swapaxes(enhanced, 0, 1)
        focus.raw_data = raw_data
        focus.construct_surface()
        processor.REFRESH = True
        processor.PROCESS = False

    def get_zeros(self, array):

        return np.zeros(array.shape, array.dtype)

    def get_mask(self, points, array):
        zeros = self.get_zeros(array)
        cv2.fillPoly(zeros, np.int32([points]), (0, 0, 255))
        mask = zeros[:, :, 2] > 0

        return mask

    def get_bound(self, data, tolerance):
        mean = np.mean(data, 0)
        std = np.std(data, 0)
        return mean - tolerance * std, mean + tolerance * std

    def get_ksize(self, shape, factor):
        ksize = (np.array(shape) / factor).astype(np.int32)
        ksize = tuple([k if k % 2 == 1 else k+1 for k in ksize])
        return ksize
