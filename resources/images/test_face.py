import dlib


win = dlib.image_window()
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("./../dats/shape_predictor_68_face_landmarks.dat")

im = dlib.load_rgb_image("face.jpeg")
dets = detector(im, 1)
win.clear_overlay()
win.set_image(im)

for index, d in enumerate(dets):
    print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
        index, d.left(), d.top(), d.right(), d.bottom()))
    shape = predictor(im, d)
    print("Part 0: {}, Part 1: {} ...".format(shape.part(0),
                                              shape.part(1)))
    # Draw the face landmarks on the screen.
    win.add_overlay(shape)

