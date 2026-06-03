import os
import cv2
import numpy as np


def analyze_body_mask(mask):
    h, w = mask.shape

    profile = []

    for y in range(h):
        xs = np.where(mask[y] > 0)[0]

        if len(xs) == 0:
            profile.append({
                "y": y,
                "left": None,
                "right": None,
                "width": 0
            })
        else:
            profile.append({
                "y": y,
                "left": int(xs.min()),
                "right": int(xs.max()),
                "width": int(xs.max() - xs.min())
            })

    return profile


def find_body_landmarks(mask):
    profile = analyze_body_mask(mask)

    h, w = mask.shape

    widths = np.array([row["width"] for row in profile])

    # smooth profile
    kernel_size = max(5, h // 80)
    kernel = np.ones(kernel_size) / kernel_size
    smooth = np.convolve(widths, kernel, mode="same")

    nonzero = np.where(smooth > 5)[0]

    if len(nonzero) == 0:
        raise RuntimeError("Empty silhouette")

    top = int(nonzero[0])
    bottom = int(nonzero[-1])

    body_height = bottom - top

    # approximate regions
    head_start = top
    head_end = top + int(body_height * 0.30)

    torso_start = top + int(body_height * 0.28)
    torso_end = top + int(body_height * 0.58)

    legs_start = top + int(body_height * 0.55)
    legs_end = bottom

    # neck = narrowest part between head and torso
    neck_search_start = top + int(body_height * 0.20)
    neck_search_end = top + int(body_height * 0.40)

    neck_region = smooth[neck_search_start:neck_search_end]
    neck_y = neck_search_start + int(np.argmin(neck_region))

    # crotch = narrow point between legs
    crotch_search_start = top + int(body_height * 0.55)
    crotch_search_end = top + int(body_height * 0.75)

    crotch_region = smooth[crotch_search_start:crotch_search_end]
    crotch_y = crotch_search_start + int(np.argmin(crotch_region))

    landmarks = {
        "top": top,
        "bottom": bottom,
        "head_start": head_start,
        "head_end": head_end,
        "neck_y": neck_y,
        "torso_start": torso_start,
        "torso_end": torso_end,
        "crotch_y": crotch_y,
        "legs_start": legs_start,
        "legs_end": legs_end,
    }

    print("=== BODY LANDMARKS ===")
    for k, v in landmarks.items():
        print(k, v)

    return landmarks



def split_body_masks(mask, landmarks):
    parts = {}

    h, w = mask.shape

    head = np.zeros_like(mask)
    torso = np.zeros_like(mask)
    legs = np.zeros_like(mask)

    head[
        landmarks["head_start"]:landmarks["neck_y"],
        :
    ] = mask[
        landmarks["head_start"]:landmarks["neck_y"],
        :
    ]

    torso[
        landmarks["neck_y"]:landmarks["crotch_y"],
        :
    ] = mask[
        landmarks["neck_y"]:landmarks["crotch_y"],
        :
    ]

    legs[
        landmarks["crotch_y"]:landmarks["legs_end"],
        :
    ] = mask[
        landmarks["crotch_y"]:landmarks["legs_end"],
        :
    ]

    parts["head"] = head
    parts["torso"] = torso

    leg_components = get_connected_components(legs, min_area=1000)

    if len(leg_components) >= 2:
        for i, comp in enumerate(leg_components[:3]):
            parts[f"leg_component_{i}"] = comp["mask"]
    else:
        mid_x = find_leg_split_x(legs, landmarks)
        print("Using leg split x:", mid_x)

        left_leg = np.zeros_like(mask)
        right_leg = np.zeros_like(mask)

        left_leg[:, :mid_x] = legs[:, :mid_x]
        right_leg[:, mid_x:] = legs[:, mid_x:]

        parts["left_leg"] = left_leg
        parts["right_leg"] = right_leg

    return parts

def save_landmark_debug_image(mask, landmarks, image_path):
    debug = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    h, w = mask.shape

    lines = [
        ("top", landmarks["top"], (255, 255, 0)),
        ("head_end", landmarks["head_end"], (0, 255, 0)),
        ("neck_y", landmarks["neck_y"], (0, 0, 255)),
        ("torso_end", landmarks["torso_end"], (255, 0, 255)),
        ("crotch_y", landmarks["crotch_y"], (255, 0, 0)),
        ("bottom", landmarks["bottom"], (0, 255, 255)),
    ]

    for name, y, color in lines:
        cv2.line(debug, (0, y), (w - 1, y), color, 2)
        cv2.putText(
            debug,
            name,
            (10, max(20, y - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

    output_path = os.path.join(
        os.path.dirname(image_path),
        "DEBUG_LANDMARKS.png"
    )

    cv2.imwrite(output_path, debug)

    print("Saved landmark debug image:", output_path)

    return output_path


def get_connected_components(mask, min_area=500):
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        mask,
        connectivity=8
    )

    components = []

    for label in range(1, num_labels):
        x, y, w, h, area = stats[label]

        if area < min_area:
            continue

        component_mask = np.zeros_like(mask)
        component_mask[labels == label] = 255

        components.append({
            "label": label,
            "mask": component_mask,
            "bbox": (x, y, w, h),
            "area": area,
            "centroid": centroids[label],
        })

    components.sort(key=lambda c: c["area"], reverse=True)

    return components


def find_leg_split_x(legs_mask, landmarks=None, max_search_height=220, min_gap=20):
    h, w = legs_mask.shape

    nonzero_rows = np.where(np.sum(legs_mask > 0, axis=1) > 0)[0]

    if len(nonzero_rows) == 0:
        return w // 2

    start_y = int(nonzero_rows[0])
    end_y = min(h, start_y + max_search_height)

    best_gap = 0
    best_split_x = w // 2
    best_y = start_y

    for y in range(start_y, end_y):
        xs = np.where(legs_mask[y] > 0)[0]

        if len(xs) < 2:
            continue

        gaps = np.diff(xs)
        max_gap_index = int(np.argmax(gaps))
        max_gap = int(gaps[max_gap_index])

        if max_gap > best_gap:
            left_edge = int(xs[max_gap_index])
            right_edge = int(xs[max_gap_index + 1])

            best_gap = max_gap
            best_split_x = (left_edge + right_edge) // 2
            best_y = y

    print("Best leg gap:", best_gap)
    print("Best leg gap y:", best_y)
    print("Leg split x:", best_split_x)

    if best_gap < min_gap:
        print("No clear leg gap found, using image center")
        return w // 2

    return best_split_x