from PIL import Image
import numpy as np

# img = Image.open('rotate.jpg')
# img = img.convert("RGBA")
# img = img.resize([160, 160], Image.BICUBIC)
# datas = img.getdata()
#
# newData = []
# for item in datas:
#     if item[0] >= 240 and item[1] >= 240 and item[2] >= 240:
#         newData.append((255, 255, 255, 0))
#     else:
#         newData.append((0, 0, 0, 255))
#
# img.putdata(newData)
# img.save("rotate.png")

from PIL import Image
import numpy as np

img = Image.open('lena.jpg')
img = img.convert("RGBA")
img = img.rotate(45, expand=1, fillcolor=(80, 80, 80, 0))
img.convert("RGB").save("rotate1.jpg")
pixel_array = np.array(img)
img2 = Image.fromarray(pixel_array, "RGBA")
pixel_array = np.array(img2)[:, :, :3]
Image.fromarray(pixel_array).save("rotate2.jpg")
