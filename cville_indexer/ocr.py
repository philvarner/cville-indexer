# import the necessary packages
from PIL import Image
import pytesseract
import cv2
import os
import np


def test():
    # load the example image and convert it to grayscale
    filename = '2105622.jpg'

    multiple = 4
    img = cv2.imread(filename)
    img = cv2.resize(img, None, fx=multiple, fy=multiple, interpolation=cv2.INTER_LANCZOS4)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Filter to remove noise
    # img = cv2.GaussianBlur(img, (5, 5), 0)
    # img = cv2.medianBlur(img,5)

    ## not bad with this
    kernel = np.ones((5, 5), np.uint8)
    # img = cv2.erode(img, kernel, iterations=1)
    # img = cv2.dilate(img, kernel, iterations=1)

    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    # img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    # img = cv2.bilateralFilter(img, 9, 75, 75)

    # Threshold
    # ret3, img = cv2.threshold(img, 25, 255, cv2.THRESH_OTSU)
    # img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 13, 2)

    # write the grayscale image to disk as a temporary file so we can apply OCR to it
    dst_filename = "pre_{}.png".format(os.getpid())

    cv2.imwrite(dst_filename, img)

    print(f"wrote {dst_filename}")

    # load the image as a PIL/Pillow image, apply OCR, and then delete
    # the temporary file
    text = pytesseract.image_to_string(Image.open(dst_filename))
    # os.remove(filename)
    dst_ocr_filename = "ocr_{}.txt".format(os.getpid())
    f = open(dst_ocr_filename, "w")
    f.write(text)
    f.close()

    # show the output images
    # cv2.imshow("Image", image)
    # cv2.imshow("Output", gray)
    # cv2.waitKey(0)

