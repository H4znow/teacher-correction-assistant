import io
import os

import cv2
import numpy as np
from rembg import remove
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
    # # Load the input image
    # input_image = load_image_as_bytes(input_path, input_name)
    #
    # # Remove background
    # output_image = remove(input_image)
    #
    # # Convert to a white background
    # with Image.open(io.BytesIO(output_image)) as img:
    #     # Ensure the image has an alpha channel
    #     img = img.convert("RGBA")
    #     white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    #     result = Image.alpha_composite(white_bg, img)
    #
    #     # Convert back to RGB (remove alpha channel)
    #     result = result.convert("RGB")
    #     save_image(result, output_path, output_name)

    # WORKING
    # Step 1: Read the image
    image = load_image_as_bytes(input_path, input_name)

    # Step 2: Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Step 3: Apply adaptive thresholding to binarize the image
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 10
    )

    # Step 4: Detect horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # Step 5: Detect vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    # Step 6: Combine horizontal and vertical lines into one mask
    grid_mask = cv2.add(horizontal_lines, vertical_lines)

    # Step 7: Invert the grid mask
    grid_removed = cv2.bitwise_not(grid_mask)

    # Step 8: Remove the grid from the original binary image
    cleaned_binary = cv2.bitwise_and(binary, binary, mask=grid_removed)

    # Step 9: Restore handwriting onto a white background
    handwriting_mask = cleaned_binary > 0
    output = np.ones_like(image) * 255  # Create a white background
    output[handwriting_mask] = image[handwriting_mask]

    # Convert the result to a PIL image
    result_image = Image.fromarray(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))

    # Save the result
    save_image(result_image, output_path, output_name)
    #################


# Example usage
remove_background("", "test_not_clean1.jpg", "output", "output_image2.png")
