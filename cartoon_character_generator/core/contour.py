import cv2


def find_largest_contour(mask):
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE
    )

    if not contours:
        raise RuntimeError("No contour found")

    contour = max(contours, key=cv2.contourArea)

    print("Contour area:", cv2.contourArea(contour))

    return contour


def simplify_contour(contour, epsilon: float):
    simplified = cv2.approxPolyDP(contour, epsilon, True)

    print("Simplified with epsilon:", epsilon)

    return simplified