import cv2
import numpy as np
import easyocr
from flask import Flask, render_template, jsonify

# Initialize Flask app
app = Flask(__name__)

# Initialize EasyOCR
reader = easyocr.Reader(['en'])

# Canvas settings
canvas_width, canvas_height = 800, 400
canvas = np.ones((canvas_height, canvas_width), dtype=np.uint8) * 255
recognized_texts = []

# Mouse drawing variables
drawing = False
prev_x, prev_y = None, None

# Mouse callback function
def draw_with_mouse(event, x, y, flags, param):
    global drawing, prev_x, prev_y, canvas

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        prev_x, prev_y = x, y

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        cv2.line(canvas, (prev_x, prev_y), (x, y), (0, 0, 0), thickness=5)
        prev_x, prev_y = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

# Recognize handwriting and update for webpage
def recognize_handwriting():
    global recognized_texts

    gray = cv2.bitwise_not(canvas)  # Invert colors
    cv2.imwrite("temp.png", gray)  # Save for OCR

    result = reader.readtext("temp.png")

    if result:
        words = " ".join([res[1] for res in result])
        recognized_texts.append(words)

        # Save recognized text for webpage
        with open("recognized_text.txt", "w", encoding="utf-8") as file:
            file.write(" ".join(recognized_texts))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recognized_text")
def get_recognized_text():
    try:
        with open("recognized_text.txt", "r", encoding="utf-8") as file:
            return jsonify({"text": file.read()})
    except FileNotFoundError:
        return jsonify({"text": "No text recognized yet."})

if __name__ == "__main__":
    # Run Flask server in a separate thread
    import threading
    threading.Thread(target=lambda: app.run(debug=True, port=5000, use_reloader=False)).start()

    cv2.namedWindow("Handwriting Pad")
    cv2.setMouseCallback("Handwriting Pad", draw_with_mouse)

    while True:
        cv2.imshow("Handwriting Pad", canvas)

        key = cv2.waitKey(1) & 0xFF  # Real-time drawing

        if key == ord('s'):  # Recognize handwriting
            recognize_handwriting()

        elif key == ord('c'):  # Clear canvas
            canvas[:] = 255

        elif key == ord('q'):  # Quit
            break

    cv2.destroyAllWindows()
