from PIL import Image
import numpy as np

im = Image.open("transform.jpg")
im = im.convert("RGBA")
pixels = np.array(im)
print(pixels[:, 1, :])
pixels[pixels[:, :, 0]<240] = [0, 0, 0, 255]
pixels[pixels[:, :, 0]>=240] = [0, 0, 0 , 0]
print()
print(pixels[:, 1, :])
im = Image.fromarray(pixels, "RGBA")
im.save("transform.png")
