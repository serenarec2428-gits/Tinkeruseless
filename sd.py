"""
Object Shape Detector (no hand tracking)
-----------------------------------------
Detects the largest object in front of the camera and classifies its shape
(circle, square, rectangle, triangle, pentagon, polygon).

Install requirements:
    pip install opencv-python numpy
"""

import cv2
import numpy as np

# Set this to True to deliberately mislabel every detected shape (troll/testing
# mode). Set it back to False to get correct labels again.
WRONG_MODE = True

# Maps each real shape name to whatever it should be reported as instead.
# Edit this freely to change which shape gets swapped for which.
WRONG_LABELS = {
    "Circle": "Square",
    "Square": "Circle",
    "Triangle": "Pentagon",
    "Rectangle": "Triangle",
    "Pentagon": "Rectangle",
    "Polygon/Round object": "Triangle",
    "Unknown": "Unknown",
}


def classify_shape(contour):
    """Classify a contour as triangle / rectangle / circle / polygon based on
    the number of vertices after polygon approximation and circularity."""
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.03 * perimeter, True)
    vertices = len(approx)

    area = cv2.contourArea(contour)
    circularity = 0
    if perimeter > 0:
        circularity = 4 * np.pi * (area / (perimeter * perimeter))

    if circularity > 0.80:
        real_shape = "Circle"
    elif vertices == 3:
        real_shape = "Triangle"
    elif vertices == 4:
        x, y, w, h = cv2.boundingRect(approx)
        aspect_ratio = w / float(h)
        real_shape = "Square" if 0.90 <= aspect_ratio <= 1.10 else "Rectangle"
    elif vertices == 5:
        real_shape = "Pentagon"
    elif vertices >= 6:
        real_shape = "Polygon/Round object"
    else:
        real_shape = "Unknown"

    if WRONG_MODE:
        return WRONG_LABELS.get(real_shape, real_shape)
    return real_shape


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera could not be opened")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Could not read camera")
            break

        frame = cv2.resize(frame, (800, 600))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)

        # Auto-threshold (Otsu) instead of a fixed value, so it adapts to
        # different lighting conditions.
        _, thresh = cv2.threshold(
            blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        biggest = None
        biggest_area = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000 and area > biggest_area:
                biggest_area = area
                biggest = contour

        if biggest is not None:
            x, y, w, h = cv2.boundingRect(biggest)
            shape_name = classify_shape(biggest)

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.drawContours(frame, [biggest], -1, (0, 255, 0), 2)

            cv2.putText(
                frame,
                f"Shape: {shape_name}",
                (x, max(y - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )
        else:
            cv2.putText(
                frame,
                "No object detected",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )

        cv2.imshow("Shape Detector", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()