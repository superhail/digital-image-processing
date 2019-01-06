import dlib
import numpy as np
from PIL import Image
import cv2


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("./../dats/shape_predictor_68_face_landmarks.dat")

im = Image.open("face.jpg")
pixel_array = np.array(im)
dets = detector(pixel_array, 1)
shape = None


def get_zeros(array):
    return np.zeros(array.shape, array.dtype)


def get_mask(points, array):
    zeros = get_zeros(array)
    cv2.fillPoly(zeros, np.int32([points]), (0, 0, 255))
    mask = zeros[:, :, 2] > 0

    return mask


for index, d in enumerate(dets):
    shape = predictor(pixel_array, d)

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

pixel_bgr_ori = cv2.cvtColor(pixel_array, cv2.COLOR_RGB2BGR)
pixel_bgr = pixel_bgr_ori.copy()
for xy in xys:
    cv2.circle(pixel_bgr, xy, 1, (0, 0, 255))
cv2.imwrite("../saved/landmark.jpg", pixel_bgr)

center = np.mean((outline[0], outline[-1]), axis=0)
center = (int(center[0]), int(center[1]))
comp = np.complex(*np.subtract(outline[0], outline[-1]))
diameter = np.abs(comp)
angle = np.angle(comp) / np.pi * 180
minor = int(diameter / 2)
major = int(np.linalg.norm(np.subtract(center, outline[8])))
fronthead = get_zeros(pixel_bgr)
cv2.ellipse(img=fronthead, center=center, axes=(minor, major),
            angle=angle, startAngle=0, endAngle=180, color=(0, 0, 255), thickness=-1)
nose_mask = get_mask(nose, pixel_bgr)
mean = np.mean(pixel_bgr_ori[nose_mask], 0)
std = np.std(pixel_bgr_ori[nose_mask], 0)
low = mean - 1.5 * std
up = mean + 1.5 * std
color_mask = (pixel_bgr_ori[:, :, :] >= low) * (pixel_bgr_ori[:, :, :] <= up)
color_mask = np.mean(color_mask, 2) > 0
fronthead_mask = (fronthead[:, :, 2] == 255) * color_mask
fronthead = get_zeros(pixel_bgr)
fronthead[fronthead_mask] = (0, 0, 255)
Y, Cr, Cb = cv2.split(cv2.cvtColor(fronthead, cv2.COLOR_BGR2YCR_CB))
Y = cv2.blur(Y, (15, 15))
ret, thresh = cv2.threshold(Y, 45, 255, 0)
points = np.array(np.where(thresh > 0), dtype=np.int32).transpose()
landmark = cv2.convexHull(points).squeeze()
image = get_zeros(pixel_bgr_ori)
image = cv2.fillConvexPoly(image, np.flip(landmark, 1), (0, 0, 255))
cv2.imwrite("../saved/contour.jpg", fronthead)

outline_mask = get_mask(outline, pixel_bgr)
l_eyebrow_mask = get_mask(l_eyebrow, pixel_bgr)
r_eyebrow_mask = get_mask(r_eyebrow, pixel_bgr)
l_eye_mask = get_mask(l_eye, pixel_bgr)
r_eye_mask = get_mask(r_eye, pixel_bgr)
mouth_mask = get_mask(mouth, pixel_bgr)
face_mask = (image[:, :, 2] == 255) | (outline_mask)
face_mask = face_mask & (~ l_eyebrow_mask) & (~ r_eyebrow_mask) & (~ l_eye_mask) & \
            (~ r_eye_mask) & (~ mouth_mask) & (~ nose_mask)
# whiten
enhanced = pixel_bgr_ori.copy()
# TODO ksize
ksize = (np.array(enhanced.shape[:2]) / 20).astype(np.int32)
ksize = (ksize[0] if ksize[0] % 2 == 1 else ksize[0] + 1,
         ksize[1] if ksize[1] % 2 == 1 else ksize[1] + 1)
blurred_mask = cv2.blur(np.array(face_mask | nose_mask, dtype=np.float32), ksize)
enhanced = (enhanced + blurred_mask[:, :, None] * np.ones(enhanced.shape) * 10).astype(np.int32)
enhanced = np.clip(enhanced, 0, 255).astype(np.int32)

# eye
blurred_mask = cv2.blur(np.array(l_eye_mask | r_eye_mask, dtype=np.float32), ksize)
H, S, V = cv2.split(cv2.cvtColor(np.float32(enhanced), cv2.COLOR_BGR2HSV))
V = (V + blurred_mask * np.ones(enhanced.shape[:2]) * 30)
V = np.clip(V, 0, 255).astype(np.float32)
enhanced = cv2.cvtColor(np.float32(cv2.merge((H, S, V))), cv2.COLOR_HSV2BGR)
# mouth
blurred_mask = cv2.blur(np.array(mouth_mask, dtype=np.float32), (5, 5))
H, S, V = cv2.split(cv2.cvtColor(np.float32(enhanced), cv2.COLOR_BGR2HSV))
S = (S + blurred_mask * np.ones(enhanced.shape[:2]) * 0.3)
S = np.clip(S, 0, 255).astype(np.float32)
enhanced = cv2.cvtColor(np.float32(cv2.merge((H, S, V))), cv2.COLOR_HSV2BGR)
# smooth
blurred_mask = cv2.blur(np.array(face_mask | nose_mask, dtype=np.float32), ksize)[:, :, None]
blurred = cv2.medianBlur(np.uint8(enhanced), ksize[0])
enhanced = enhanced * (1 - blurred_mask * 0.5) + blurred * blurred_mask * 0.5
enhanced = np.clip(enhanced, 0, 255).astype(np.int32)

cv2.imwrite("../saved/enhanced.jpg", enhanced)

