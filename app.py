from flask import Flask, request, jsonify, render_template

import numpy as np
import cv2

app = Flask(__name__)

# Canvas settings
canvas_width, canvas_height = 800, 400
canvas = np.ones((canvas_height, canvas_width), dtype=np.uint8) * 255
prev_x, prev_y = canvas_width // 2, canvas_height // 2

def draw_with_web(x, y):
    global prev_x, prev_y, canvas

    # Convert mouse positions to screen coordinates
    new_x = int(x)
    new_y = int(y)

    # Keep movements within the canvas
    new_x = max(0, min(new_x, canvas_width - 1))
    new_y = max(0, min(new_y, canvas_height - 1))

    # Draw movement on canvas
    cv2.line(canvas, (prev_x, prev_y), (new_x, new_y), (0, 0, 0), thickness=5)
    prev_x, prev_y = new_x, new_y

@app.route('/update', methods=['POST'])
def update_position():
    data = request.json
    x, y = data.get('x', 0), data.get('y', 0)
    draw_with_web(x, y)
    return jsonify({"status": "success"})

@app.route('/canvas')
def show_canvas():
    cv2.imshow("Handwriting Pad", canvas)
    cv2.waitKey(1)
    return jsonify({"status": "displaying"})
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
