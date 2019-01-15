from processor.tools.basetool import BaseTool
import pygame
import numpy as np
import dlib
import cv2


class Combine(BaseTool):
    def __init__(self, detector, predictor):
        super().__init__()
        self.detector = detector
        self.predictor = predictor
        self.pre_pos = None
        self.sender_focus = None
        self.receiver_focus = None
        self.marker = (8, 8)
        self.sender_points = None
        self.receiver_points = None
        self.scale = None

    def process(self, processor, event: pygame.event):
        focus = processor.focus
        if not processor.process_initialized:
            processor.process_initialized = True
            self.sender_focus = focus
            self.receiver_focus = None
            self.pre_pos = None
            self.sender_points = None
            self.receiver_points = None
            self.scale = None
        if focus != self.sender_focus and self.receiver_focus is None:
            self.receiver_focus = focus
            raw_data = self.sender_focus.raw_data
            rgb_data = raw_data[:, :, :3]
            dets = self.detector(np.swapaxes(rgb_data, 0, 1), 1)
            shape = None

            for index, d in enumerate(dets):
                shape = self.predictor(rgb_data, d)

            xys = []
            for i in range(0, 68):
                xys.append((shape.part(i).y, shape.part(i).x))
            self.sender_points = xys

        if processor.confirm:
            if self.receiver_focus is not None:
                raw_data_1 = np.swapaxes(self.sender_focus.raw_data[:, :, :3], 0, 1)
                raw_data_2 = np.swapaxes(self.receiver_focus.raw_data[:, :, :3], 0, 1)
                points_1 = self.get_face_landmarks(raw_data_1, self.detector, self.predictor)
                points_2 = self.get_face_landmarks(raw_data_2, self.detector, self.predictor)
                triangle_index_list = self.get_delaunay(raw_data_1, points_1)
                triangles_1 = [(points_1[indexs[0]], points_1[indexs[1]], points_1[indexs[2]]) for indexs in triangle_index_list]
                triangles_2 = [(points_2[indexs[0]], points_2[indexs[1]], points_2[indexs[2]]) for indexs in triangle_index_list]
                new_pic = self.face_swap(triangles_1, triangles_2, raw_data_1, raw_data_2,
                                         self.get_face_landmarks(raw_data_2, self.detector, self.predictor))
                self.receiver_focus.raw_data[:, :, :3] = np.swapaxes(new_pic, 0, 1)
                self.receiver_focus.construct_surface()
            processor.REFRESH = True
            processor.PROCESS = False

        if processor.cancel:
            processor.PROCESS = False

    def get_delaunay(self, img, points):
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

    def face_swap(self, triangles_1, triangles_2, pic_1, pic_2, face_2_points):
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
        # blur the boundary
        ksize = (mask.shape[0]//10, mask.shape[1]//10)
        ksize = (ksize[0] if ksize[0]%2==1 else ksize[0],
                 ksize[1] if ksize[1]%2==1 else ksize[1])
        mask = cv2.blur(mask, ksize) / 255

        output = seamless * mask + pic_2 * (1-mask)
        output = np.uint8(output)

        return output

    def get_face_landmarks(self, image, detector, predictor):
        dets = detector(image)
        shape = None
        for index, d in enumerate(dets):
            shape = predictor(image, d)
        xys = []
        for i in range(0, 68):
            xys.append((np.clip(shape.part(i).x, None, image.shape[1] - 1),
                        np.clip(shape.part(i).y, None, image.shape[0] - 1)))

        return xys