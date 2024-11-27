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

    # Step 10: Remove small noise using contour filtering
    contours, _ = cv2.findContours(cleaned_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 50:  # Threshold for small noise (adjust based on your image)
            cv2.drawContours(cleaned_binary, [contour], -1, 0, -1)  # Remove the contour by filling it with black

    # Step 11: Restore handwriting onto a white background
    handwriting_mask = cleaned_binary > 0
    output = np.ones_like(image) * 255  # Create a white background
    output[handwriting_mask] = image[handwriting_mask]

    # Convert the result to a PIL image
    result_image = Image.fromarray(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))

    # Save the result
    save_image(result_image, output_path, output_name)
    return output


def detect_skew(image):
    """
    Detect the angle of skew in the image using the Hough Line Transform.

    Args:
        image (numpy.ndarray): The preprocessed image.

    Returns:
        float: The angle by which the image is skewed.
    """
    # Convert to grayscale and invert colors
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Detect edges
    edges = cv2.Canny(binary, 50, 150, apertureSize=3)

    # Perform Hough Line Transform
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    # Calculate the angle of the lines
    angles = []
    if lines is not None:
        for rho, theta in lines[:, 0]:
            angle = np.rad2deg(theta) - 90
            angles.append(angle)

    # Calculate the median angle
    if angles:
        return np.median(angles)
    return 0.0  # Assume no rotation if no lines are detected


def rotate_image(image, angle):
    """
    Rotate the image to correct the skew.

    Args:
        image (numpy.ndarray): The image to rotate.
        angle (float): The angle to rotate the image.

    Returns:
        numpy.ndarray: The rotated image.
    """
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    # Calculate the rotation matrix
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Perform the rotation
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

# def crop_lines(image, output_path, padding=5):
#     """
#     Crop the text lines from the given image and save each line as a separate image,
#     with adjustments to include letter tails and caps.
#
#     Args:
#         image (numpy.ndarray): The input image with text on a white background.
#         output_path (str): The directory to save the cropped line images.
#         padding (int): Number of pixels to extend above and below detected lines.
#     """
#     # Convert to grayscale
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#
#     # Invert colors to make text white on black background
#     inverted = cv2.bitwise_not(gray)
#
#     # Apply horizontal projection to detect text lines
#     projection = np.sum(inverted, axis=1)
#
#     # Threshold to detect significant text regions
#     threshold = np.max(projection) * 0.1  # 10% of the maximum projection value
#     line_regions = projection > threshold
#
#     # Detect line start and end indices
#     line_indices = []
#     start = None
#     for i, val in enumerate(line_regions):
#         if val and start is None:
#             start = i
#         elif not val and start is not None:
#             line_indices.append((start, i))
#             start = None
#
#     # Handle case where the last line reaches the image bottom
#     if start is not None:
#         line_indices.append((start, len(line_regions)))
#
#     # Expand lines to include letter caps/tails and merge overlapping regions
#     expanded_indices = []
#     for start, end in line_indices:
#         start = max(0, start - padding)
#         end = min(image.shape[0], end + padding)
#         if expanded_indices and expanded_indices[-1][1] >= start:  # Merge overlapping lines
#             expanded_indices[-1] = (expanded_indices[-1][0], end)
#         else:
#             expanded_indices.append((start, end))
#
#     # Create output directory if not exists
#     os.makedirs(output_path, exist_ok=True)
#
#     # Crop and save each line
#     for i, (start, end) in enumerate(expanded_indices):
#         cropped_line = image[start:end, :]  # Crop the entire width
#         line_image_path = os.path.join(output_path, f"line_{i + 1}.png")
#         cv2.imwrite(line_image_path, cropped_line)
#         print(f"Saved: {line_image_path}")

# Example usage
# image = cv2.imread('path_to_image.png')
# crop_lines(image, 'output_directory')


def crop_lines(image, output_path, padding=5, margin=10):
    """
    Crop the text lines from the given image, considering letter tails and caps,
    and add a white margin around each line.

    Args:
        image (numpy.ndarray): The input image with text on a white background.
        output_path (str): The directory to save the cropped line images.
        padding (int): Number of pixels to extend above and below detected lines.
        margin (int): White space to add above and below each cropped line.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Invert colors to make text white on black background
    inverted = cv2.bitwise_not(gray)

    # Apply horizontal projection to detect text lines
    projection = np.sum(inverted, axis=1)

    # Threshold to detect significant text regions
    threshold = np.max(projection) * 0.10  # 10% of the maximum projection value
    line_regions = projection > threshold

    # Detect line start and end indices
    line_indices = []
    start = None
    for i, val in enumerate(line_regions):
        if val and start is None:
            start = i
        elif not val and start is not None:
            line_indices.append((start, i))
            start = None

    # Handle case where the last line reaches the image bottom
    if start is not None:
        line_indices.append((start, len(line_regions)))

    # Expand lines to include letter caps/tails and add white margin
    expanded_indices = []
    for start, end in line_indices:
        # Expand by padding
        start = max(0, start - padding)
        end = min(image.shape[0], end + padding)

        # Detect the maximum vertical extent within the line
        line_slice = inverted[start:end, :]
        vertical_projection = np.sum(line_slice, axis=0)
        top_tail = np.where(vertical_projection > 0)[0]
        if len(top_tail) > 0:
            line_min = max(0, np.min(top_tail))
            line_max = min(image.shape[1], np.max(top_tail))
        else:
            line_min, line_max = 0, image.shape[1]

        # Merge overlapping lines
        if expanded_indices and expanded_indices[-1][1] >= start:
            expanded_indices[-1] = (
                expanded_indices[-1][0],
                end,
                expanded_indices[-1][2],
                expanded_indices[-1][3],
            )
        else:
            expanded_indices.append((start, end, line_min, line_max))

    # Create output directory if not exists
    os.makedirs(output_path, exist_ok=True)

    # Crop and save each line
    for i, (start, end, min_x, max_x) in enumerate(expanded_indices):
        # Add white margin
        start = max(0, start - margin)
        end = min(image.shape[0], end + margin)
        cropped_line = image[start:end, :]  # Crop the entire width

        # Add horizontal margin
        horizontal_margin = 10  # Adjust margin on both sides
        cropped_line = cv2.copyMakeBorder(
            cropped_line,
            top=horizontal_margin,
            bottom=horizontal_margin,
            left=0,
            right=0,
            borderType=cv2.BORDER_CONSTANT,
            value=[255, 255, 255],  # White margin
        )

        # Save the cropped line
        line_image_path = os.path.join(output_path, f"line_{i + 1}.png")
        cv2.imwrite(line_image_path, cropped_line)
        print(f"Saved: {line_image_path}")



# Example usage
output = remove_background("tests", "test_many_lines.jpg", "output_crop", "output_many_lines.png")
crop_lines(output, "output_crop/cropped")
