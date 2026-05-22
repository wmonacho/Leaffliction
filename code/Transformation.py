import sys
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import plantcv.plantcv as pcv
from skimage.morphology import remove_small_objects


def analyze_step(img, mask):
    labeled_mask, _ = pcv.create_labels(mask=mask)
    pcv.params.line_thickness = 1
    return pcv.analyze.size(img=img, labeled_mask=labeled_mask)


def roi_step(img, mask):
    h, w = img.shape[:2]
    margin = int(min(h, w) * 0.05)
    roi = pcv.roi.rectangle(img=img, x=margin, y=margin, h=h - 2 * margin, w=w - 2 * margin)
    filtered_mask = pcv.roi.filter(mask=mask, roi=roi, roi_type='partial')

    green_overlay = np.zeros_like(img)
    green_overlay[filtered_mask > 0] = (0, 255, 0)
    roi_img = np.where(filtered_mask[:, :, np.newaxis] > 0,
                       cv2.addWeighted(img, 0.4, green_overlay, 0.6, 0),
                       img)
    cv2.rectangle(roi_img, (margin, margin), (w - margin, h - margin), (255, 0, 0), 2)

    return filtered_mask, roi_img


def create_mask_step(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    s_channel = hsv[:, :, 1]
    mask = pcv.threshold.binary(gray_img=s_channel, threshold=50, object_type='light')
    mask_clean = remove_small_objects(mask.astype(bool), max_size=300)
    return mask_clean.astype(np.uint8) * 255


def mask_step(img, mask):
    return pcv.apply_mask(img=img, mask=mask, mask_color='white')


def pseudolandmarks_step(img, mask):
    top, bottom, center_v = pcv.homology.x_axis_pseudolandmarks(img=img, mask=mask)
    left, right, center_h = pcv.homology.y_axis_pseudolandmarks(img=img, mask=mask)
    landmark_img = img.copy()
    groups = [
        (top,      (255,   0,   0)),
        (bottom,   (  0, 255,   0)),
        (center_v, (  0,   0, 255)),
        (left,     (255, 255,   0)),
        (right,    (  0, 255, 255)),
        (center_h, (255,   0, 255)),
    ]
    for pts, color in groups:
        for pt in pts:
            pt = np.array(pt).flatten()
            cv2.circle(landmark_img, (int(pt[0]), int(pt[1])), 3, color, -1)
    return landmark_img



def display_all(original, mask, masked_img, roi_img, roi_mask, analyze_img, landmark_img):
    fig = plt.figure(figsize=(20, 10))
    fig.suptitle("Transformations PlantCV", fontsize=16)

    steps = [
        ("Original",        original,    False),
        ("Mask",            mask,        True),
        ("Masked",          masked_img,  False),
        ("ROI Objects",     roi_img,     False),
        ("Analyze Object",  analyze_img, False),
        ("Pseudolandmarks", landmark_img,False),
    ]

    positions = [(i // 4, i % 4) for i in range(len(steps))]
    for (row, col), (title, img, is_gray) in zip(positions, steps):
        ax = plt.subplot2grid((2, 4), (row, col), fig=fig)
        if is_gray:
            ax.imshow(img, cmap='gray')
        else:
            ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        ax.set_title(title, fontsize=11)
        ax.axis('off')

    ax_hist = plt.subplot2grid((2, 4), (1, 2), colspan=2, fig=fig)
    for ch, color, name in zip(range(3), ['blue', 'green', 'red'], ['B', 'G', 'R']):
        hist = cv2.calcHist([original], [ch], roi_mask, [256], [0, 256])
        ax_hist.plot(hist, color=color, label=name)
    ax_hist.set_title("Color Histogram", fontsize=11)
    ax_hist.legend(fontsize=8)

    plt.tight_layout()
    plt.show()


def process_single_image(image_path):
    pcv.params.debug = None

    img, _, _ = pcv.readimage(filename=image_path)
    mask = create_mask_step(img)
    masked_img = mask_step(img, mask)
    roi_mask, roi_img = roi_step(img, mask)
    analyze_img = analyze_step(img, roi_mask)
    landmark_img = pseudolandmarks_step(img, roi_mask)

    display_all(img, mask, masked_img, roi_img, roi_mask, analyze_img, landmark_img)


def main():
    if len(sys.argv) != 2:
        print("Usage: python Transformation.py <image>")
        return

    target = sys.argv[1]
    if os.path.isfile(target):
        process_single_image(target)
    elif os.path.isdit(target):
        return
    else:
        print(f"Erreur : '{target}' n'est pas un fichier ou un dossier valide.")
        return

    


if __name__ == "__main__":
    main()
