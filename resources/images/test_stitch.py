import cv2
import numpy as np


def ratio_test(raw_matches, ratio):
    # ratio test
    matches = []
    for m in raw_matches:
        if len(m)==2 and m[0].distance < ratio * m[1].distance:
            matches.append((m[0].queryIdx, m[0].trainIdx))

    return matches


def detect_and_describe(image, descriptor):
    kps, features = descriptor.detectAndCompute(image, None)
    kps = np.float32([kp.pt for kp in kps])

    return kps, features


def get_smooth_mask(shape):
    mask = np.zeros(shape)
    mat = np.eye(shape[0])
    mat[:, 0] = 1
    mask[0, :shape[1]] = np.linspace(0, 1, shape[1])
    mask = np.matmul(mat, mask)

    return mask


def stitch_image(imageA, imageB, ptsA, ptsB, thresh):
    (H, status) = cv2.findHomography(ptsB, ptsA, cv2.RANSAC, thresh)
    imageBwarped = cv2.warpPerspective(imageB, H, (imageA.shape[1] + imageB.shape[1], imageA.shape[0]))
    mask = np.ones(imageBwarped.shape[:2], dtype=np.float32)
    mask[:, :imageA.shape[1]] = 0
    smooth_lim = imageA.shape[1] // 10
    mask[:, imageA.shape[1]-smooth_lim:imageA.shape[1]] = get_smooth_mask((imageA.shape[0], smooth_lim))
    mask = mask * (imageBwarped[:, :, 0] != 0)
    result = imageBwarped.copy()
    result[:imageA.shape[0], :imageA.shape[1]] = imageA * (1-mask[:, :imageA.shape[1], None]) + \
                                                 (imageBwarped * mask[:, :, None])[:, :imageA.shape[1], :]

    return result


if __name__ == "__main__":
    thresh = 4
    img1 = cv2.imread("left.jpg")
    img2 = cv2.imread("right.jpg")
    sift = cv2.xfeatures2d.SIFT_create()
    kp1s, feature1s = detect_and_describe(img1, sift)
    kp2s, feature2s = detect_and_describe(img2, sift)
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(feature1s, feature2s, k=2)
    matches = ratio_test(matches, 0.75)
    ptsA = np.float32([kp1s[i] for (i, _) in matches])
    ptsB = np.float32([kp2s[i] for (_, i) in matches])
    result = stitch_image(img1, img2, ptsA, ptsB, thresh)

    cv2.imwrite("result.jpg", result)
