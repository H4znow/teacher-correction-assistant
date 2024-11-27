import os

import cv2
import numpy as np
from PIL import Image


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def save_image(image, path, file_name):
    full_dir_path = os.path.join(ROOT_DIR, path)
    os.makedirs(full_dir_path, exist_ok=True)  # Create only the directory
    full_file_path = os.path.join(full_dir_path, file_name)
    image.save(full_file_path)


def load_image_as_bytes(path, file_name):
    full_path = os.path.join(ROOT_DIR, path, file_name)
    if os.path.exists(full_path):
        return cv2.imread(full_path)
    else:
        raise FileNotFoundError(f"The file does not exist: {full_path}")


def remove_background(input_path, input_name, output_path, output_name):
    # Step 1: Read the image
    image = load_image_as_bytes(input_path, input_name)

    # Step 2: Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Step 3: Apply Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Step 4: Apply adaptive thresholding to binarize the image
    binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Step 5: Detect horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # Step 6: Detect vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    # Step 7: Combine horizontal and vertical lines into one mask
    grid_mask = cv2.add(horizontal_lines, vertical_lines)

    # Step 8: Invert the grid mask
    grid_removed = cv2.bitwise_not(grid_mask)

    # Step 9: Remove the grid from the original binary image
    cleaned_binary = cv2.bitwise_and(binary, binary, mask=grid_removed)

    # Step 10: Restore handwriting onto a white background
    handwriting_mask = cleaned_binary > 0
    output = np.ones_like(image) * 255  # Create a white background
    output[handwriting_mask] = image[handwriting_mask]

    # Convert the result to a PIL image
    result_image = Image.fromarray(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))

    # Save the result
    save_image(result_image, output_path, output_name)


# Example usage
remove_background("", "test1.jpg", "output", "output_image1.png")
