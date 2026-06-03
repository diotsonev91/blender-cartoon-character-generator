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
    parts["legs"] = legs

    return parts