import dlib
import numpy as np
from PIL import Image
import cv2

def get_landmarks(image, detector, predictor):
    dets = detector(image)
    shape = None
    for index, d in enumerate(dets):
        shape = predictor(image, d)
    xys = []
    for i in range(0, 68):
        xys.append((np.clip(shape.part(i).x, None, image.shape[1]-1), np.clip(shape.part(i).y, None, image.shape[0]-1)))

    shape = image.shape[:2]

    return xys

def get_face_landmarks(image, detector, predictor):
    dets = detector(image)
    shape = None
    for index, d in enumerate(dets):
        shape = predictor(image, d)
    xys = []
    for i in range(0, 68):
        xys.append((np.clip(shape.part(i).x, None, image.shape[1]-1), np.clip(shape.part(i).y, None, image.shape[0]-1)))

    return xys

def draw_delaunay(img, triangleList, delaunay_color):
    size = img.shape
    r = (0, 0, size[1], size[0])
    for index, t in enumerate(triangleList):
        pt1 = t[0]
        pt2 = t[1]
        pt3 = t[2]
        if index == 0:
            cv2.fillConvexPoly(img, np.int32(t), (255, 255, 0))
        cv2.line(img, pt1, pt2, delaunay_color, 1)
        cv2.line(img, pt2, pt3, delaunay_color, 1)
        cv2.line(img, pt3, pt1, delaunay_color, 1)
    return img


def get_delaunay(img, points):
    subdiv = cv2.Subdiv2D((0, 0, img.shape[1], img.shape[0]))
    for p in points:
        subdiv.insert(p)
    triangleList = subdiv.getTriangleList()

    delaunayTri = []
    pt = []
    for t in triangleList:
        pt.append((t[0], t[1]))
        pt.append((t[2], t[3]))
        pt.append((t[4], t[5]))

        ind = []
        # Get face-points (from 68 face detector) by coordinates
        for j in range(0, 3):
            for k in range(0, len(points)):
                if (abs(pt[j][0] - points[k][0]) < 1.0 and abs(pt[j][1] - points[k][1]) < 1.0):
                    ind.append(k)
                    # Three points form a triangle. Triangle array corresponds to the file tri.txt in FaceMorph
        if len(ind) == 3:
            delaunayTri.append((ind[0], ind[1], ind[2]))

        pt = []

    return delaunayTri


def face_swap(triangles_1, triangles_2, pic_1, pic_2, face_2_points):
    new_pic = np.zeros(pic_2.shape, pic_2.dtype)
    for triangle_1, triangle_2 in zip(triangles_1, triangles_2):
        rect_1 = cv2.boundingRect(np.array(triangle_1))
        rect_2 = cv2.boundingRect(np.array(triangle_2))
        tri_1_cropped = np.array([(p[0]-rect_1[0], p[1]-rect_1[1]) for p in triangle_1], dtype=np.float32)
        tri_2_cropped = np.array([(p[0]-rect_2[0], p[1]-rect_2[1]) for p in triangle_2], dtype=np.float32)
        pic_1_cropped = pic_1[rect_1[1]:rect_1[1]+rect_1[3], rect_1[0]:rect_1[0]+rect_1[2], :]
        warp_mat = cv2.getAffineTransform(tri_1_cropped, tri_2_cropped)
        pic_2_cropped = cv2.warpAffine(pic_1_cropped, warp_mat, (rect_2[2], rect_2[3]), None,
                                       flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
        mask = np.zeros((rect_2[3], rect_2[2], 3), dtype=np.float32)
        mask = cv2.fillConvexPoly(mask, np.int32(tri_2_cropped), (1.0, 1.0, 1.0))
        new_pic[rect_2[1]:rect_2[1]+rect_2[3], rect_2[0]:rect_2[0]+rect_2[2]] = \
            new_pic[rect_2[1]:rect_2[1]+rect_2[3], rect_2[0]:rect_2[0]+rect_2[2]] * ( - mask + (1.0, 1.0, 1.0)) + \
            pic_2_cropped * mask

    points = face_2_points
    hullIndex = cv2.convexHull(np.array(points, dtype=np.int32), returnPoints=False)
    hull2 = [points[int(index)] for index in hullIndex]
    hull8U = [(hull2[i][0], hull2[i][1]) for i in range(len(hull2))]
    mask = np.zeros(pic_2.shape, dtype=pic_2.dtype)
    cv2.fillConvexPoly(mask, np.int32(hull8U), (255, 255, 255))
    r = cv2.boundingRect(np.float32([hull2]))
    center = ((r[0]+int(r[2]/2), r[1]+int(r[3]/2)))
    seamless = cv2.seamlessClone(new_pic, pic_2, mask, center, cv2.NORMAL_CLONE)
    ksize = (mask.shape[0]//10, mask.shape[1]//10)
    ksize = (ksize[0] if ksize[0]%2==1 else ksize[0],
             ksize[1] if ksize[1]%2==1 else ksize[1])
    mask = cv2.blur(mask, ksize) / 255

    output = seamless * mask + pic_2 * (1-mask)
    output = np.uint8(output)

    return output


if __name__ == "__main__":
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("./../dats/shape_predictor_68_face_landmarks.dat")
    pic_1 = cv2.imread("trump.jpg")
    pic_2 = cv2.imread("hilary.jpg")
    points_1 = get_face_landmarks(pic_1, detector, predictor)
    points_2 = get_face_landmarks(pic_2, detector, predictor)
    triangle_index_list = get_delaunay(pic_1, points_1)
    triangles_1 = [(points_1[indexs[0]], points_1[indexs[1]], points_1[indexs[2]]) for indexs in triangle_index_list]
    triangles_2 = [(points_2[indexs[0]], points_2[indexs[1]], points_2[indexs[2]]) for indexs in triangle_index_list]
    new_pic = face_swap(triangles_1, triangles_2, pic_1, pic_2, get_face_landmarks(pic_2, detector, predictor))
    cv2.imwrite("new_pic.jpg", new_pic)

