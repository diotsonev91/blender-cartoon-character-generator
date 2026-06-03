import cv2
import numpy as np
import os


def extract_mask(image_path: str):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    if image is None:
        raise RuntimeError(f"Could not load image: {image_path}")

    print("Image shape:", image.shape)

    if len(image.shape) == 3 and image.shape[2] == 4:
        alpha = image[:, :, 3]

        print("Alpha min/max:", alpha.min(), alpha.max())

        mask = (alpha > 5).astype(np.uint8) * 255

        debug_path = os.path.join(os.path.dirname(image_path), "DEBUG_MASK.png")
        cv2.imwrite(debug_path, mask)
        print("Saved debug mask:", debug_path)

        return mask

    raise RuntimeError("MVP expects PNG with transparent background / alpha channel")