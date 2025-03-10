import cv2
import numpy as np
import easyocr

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Initialize drawing canvas
canvas_width, canvas_height = 800, 400
canvas = np.ones((canvas_height, canvas_width), dtype=np.uint8) * 255
drawing = False
prev_point = None
recognized_text = ""

# Mouse callback function
def draw(event, x, y, flags, param):
    global drawing, prev_point, canvas

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        prev_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        if prev_point:
            cv2.line(canvas, prev_point, (x, y), (0, 0, 0), thickness=5)
            prev_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

# Recognize text using EasyOCR
def recognize_handwriting():
    global recognized_text

    # Preprocessing: Convert to grayscale and invert colors
    gray = cv2.bitwise_not(canvas)
    cv2.imwrite("temp.png", gray)  # Save the image for OCR

    # Use EasyOCR to recognize handwriting
    result = reader.readtext("temp.png")
    recognized_text = " ".join([res[1] for res in result])  # Extract detected words

# Create window and set mouse callback
cv2.namedWindow("Handwriting Pad")
cv2.setMouseCallback("Handwriting Pad", draw)

while True:
    cv2.imshow("Handwriting Pad", canvas)

    # Display recognized text
    text_display = np.ones((100, canvas_width), dtype=np.uint8) * 255
    cv2.putText(text_display, f"Recognized: {recognized_text}", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

    cv2.imshow("Recognized Text", text_display)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):  # Press 's' to process handwriting into text
        recognize_handwriting()

    elif key == ord('c'):  # Press 'c' to clear canvas
        canvas[:] = 255
        recognized_text = ""

    elif key == ord('q'):  # Press 'q' to quit
        break

cv2.destroyAllWindows()
