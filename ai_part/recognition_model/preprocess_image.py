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


def apply_clean(image):
    """
    Applies Gaussian blur and adaptive thresholding to an image.

    Args:
        image (numpy.ndarray): The input grayscale image.

    Returns:
        numpy.ndarray: The binary image after thresholding.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply adaptive thresholding to binarize the image
    binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
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

    return output


def remove_background(input_path, input_name, output_path, output_name):
    # Step 1: Read the image
    image = load_image_as_bytes(input_path, input_name)

    # Step 2: Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply adaptive thresholding to binarize the image
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


def crop_horizontal_and_vertical(image):
    """
    Crop the image by removing white space on all sides (top, bottom, left, right).

    Args:
        image (numpy.ndarray): The input image with handwriting on a white background.

    Returns:
        numpy.ndarray: The cropped image.
    """
    # Convert to grayscale and threshold
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

    # Invert binary image
    binary_inv = cv2.bitwise_not(binary)

    # Find non-white region using contours
    coords = cv2.findNonZero(binary_inv)  # Get all non-zero points
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)  # Get bounding box
        cropped = image[y:y+h, x:x+w]  # Crop the region
        return cropped
    else:
        return image  # If no handwriting is found, return the original image


def crop_lines(image, output_path, padding=5, margin=10):
    """
    Crop the text lines from the given image, considering letter tails and caps,
    and add a white margin around each line, with additional processing to ignore
    and merge small lines.

    Args:
        image (numpy.ndarray): The input image with text on a white background.
        output_path (str): The directory to save the cropped line images.
        padding (int): Number of pixels to extend above and below detected lines.
        margin (int): White space to add above and below each cropped line.
    """
    # Convert to grayscale
    image = crop_horizontal_and_vertical(image)
    cv2.imwrite(f"{output_path}/initial_crop.png", image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Invert colors to make text white on black background
    # inverted = cv2.bitwise_not(gray)
    #
    # # Detect the global horizontal extent of text
    # vertical_projection = np.sum(inverted, axis=0)
    # text_x = np.where(vertical_projection > 0)[0]
    # if len(text_x) > 0:
    #     min_x = np.min(text_x)
    #     max_x = np.max(text_x)
    # else:
    #     min_x, max_x = 0, image.shape[1]
    #
    # # Expand text horizontally to the full extent
    # for i in range(inverted.shape[0]):
    #     if np.sum(inverted[i, :]) > 0:  # If there's text on this row
    #         inverted[i, min_x:max_x] = 255  # Ensure text spans the full width
    #
    # # Apply horizontal projection to detect text lines
    # projection = np.sum(inverted, axis=1)
    #
    # # Threshold to detect significant text regions
    # threshold = np.max(projection) * 0.10  # 10% of the maximum projection value
    # line_regions = projection > threshold

    # Apply horizontal projection to detect text lines
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

    # Calculate the average vertical size of lines
    line_heights = [end - start for start, end in line_indices]
    avg_height = np.mean(line_heights)

    # Filter out lines that are less than half the average height
    filtered_indices = []
    merge_previous_indices = None

    for i, (start, end) in enumerate(line_indices):
        line_height = end - start
        if line_height >= avg_height / 2:  # Keep lines that are not too small
            if merge_previous_indices and start - merge_previous_indices[1] < padding:
                # prev_start, prev_end = line_indices[i - 1]
                # next_start, next_end = line_indices[i]
                merged_start = merge_previous_indices[0]
                merged_end = end
                filtered_indices.append((merged_start, merged_end))
                merge_previous_indices = None
            else:
                filtered_indices.append((start, end))

        elif i > 0 and i < len(line_indices) - 1 and start - filtered_indices[len(filtered_indices) - 1][0] < padding:  # Merge with neighbors
            merged_start = filtered_indices[len(filtered_indices) - 1][0]
            merged_end = end
            filtered_indices[len(filtered_indices) - 1] = (merged_start, merged_end)
            merge_previous_indices = (start, end)

    # Expand lines to include letter caps/tails and add white margin
    expanded_indices = []
    for start, end in filtered_indices:
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

        expanded_indices.append((start, end, line_min, line_max))

    # Create output directory if not exists
    os.makedirs(output_path, exist_ok=True)

    # Crop and save each line
    for i, (start, end, min_x, max_x) in enumerate(expanded_indices):
        # Add white margin
        start = max(0, start - margin)
        end = min(image.shape[0], end + margin)
        cropped_line = image[start:end, :]  # Crop the entire width

        # ADD BACKGROUND REMOVAL
        cropped_line = apply_clean(cropped_line)
        cropped_line = crop_horizontal_and_vertical(cropped_line)

        # Add horizontal margin
        horizontal_margin = 10  # Adjust margin on both sides

        cropped_line = cv2.copyMakeBorder(
            cropped_line,
            top=horizontal_margin,
            bottom=horizontal_margin,
            left=padding,
            right=padding,
            borderType=cv2.BORDER_CONSTANT,
            value=[255, 255, 255],  # White margin
        )

        # Save the cropped line
        line_image_path = os.path.join(output_path, f"line_{i + 1}.png")


        cv2.imwrite(line_image_path, cropped_line)
        print(f"Saved: {line_image_path}")

# Example usage
# output = remove_background("tests", "test_many_lines_with_blank_black_white.jpg", "output_crop", "output_many_lines_with_blank_black_white.png")
# crop_lines(output, "output_crop/croppep6")
# output = remove_background("tests", "test_many_lines_with_blank_black_white.jpg", "output_crop", "output_many_lines_with_blank_black_white.png")
# crop_lines(output, "output_crop/croppep4")

# output = remove_background("tests", "test_many_lines.jpg", "output_crop", "output_many_lines.png")
# crop_lines(output, "output_crop/cropped")