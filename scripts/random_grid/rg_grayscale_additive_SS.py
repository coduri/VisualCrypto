import numpy as np
from PIL import Image


# Returns a dictionary containing function mappings and metadata for the algorithm (used by the web interface).
def get_config():
    return {
        "name": "RG - Grayscale Additive Secret Sharing",
        "description": get_description(),
        "requirements": get_requirements(),
        "encrypt": encrypt,
        "decrypt": decrypt,
        "extension": "png",
        "image_type": "L"
    }


# Defines the expected inputs for encryption/decryption (number of images and additional parameters)
def get_requirements():
    return {
        "encryption": {
            "num_images": 1,
            "parameters": {}  # No extra parameters needed
        },
        "decryption": {
            "num_images": 2,
            "parameters": {}  # No extra parameters needed
        }
    }


# Returns a dictionary containing the description and reference links for the algorithm.
def get_description():
    return {
        "text": "This (2,2) Visual Secret Sharing Scheme is a straightforward additive VSS scheme that handles grayscale images.",
        "links": [
            {"text": "Kafri & Keren",
             "url": "https://doi.org/10.1364/ol.12.000377"}
        ]
    }


# Function to create a random grid with values in the range of 0-255
def create_random_grid(size):
    """
    Generates a random grid of the specified size, with values in the range 0 to 255.

    Parameters:
    size (tuple): The dimensions of the grid (height, width).

    Returns:
    numpy.ndarray: A grid filled with random integer values between 0 and 255.
    """
    grid = np.random.randint(0, 256, size=size)
    return grid


# Function to create a difference grid by subtracting the image from the random grid
def create_difference_grid(image, grid):
    """
    Creates a difference grid by subtracting the pixel values of the input image from the random grid.

    Parameters:
    image (numpy.ndarray): The binary image array (as a numpy array) to subtract from the grid.
    grid (numpy.ndarray): The random grid (as a numpy array) to be transformed by subtraction.

    Returns:
    numpy.ndarray: A grid where each value is the result of subtracting the corresponding image value from the grid.
    """
    transformed_grid = grid - image
    return transformed_grid


# Function to overlay two grids by performing subtraction
def decrypt(image1, image2):
    """
    Combines two grids by subtracting the second grid from the first.

    Parameters:
    image1 (PIL.Image.Image): The first image (PIL Image object), to be converted to numpy array and processed.
    image2 (PIL.Image.Image): The second image (PIL Image object), to be converted to numpy array and processed.

    Returns:
    PIL.Image.Image: The resulting image (PIL Image object) after subtracting the second grid from the first.
    """
    img1_array = np.array(image1.convert('L'))  # Convert PIL Image to numpy array (grayscale)
    img2_array = np.array(image2.convert('L'))  # Convert PIL Image to numpy array (grayscale)

    overlaid_image = img1_array - img2_array
    return Image.fromarray(overlaid_image.astype(np.uint8))  # Convert numpy array back to PIL Image


def encrypt(image):
    """
    Encrypts an image by generating two shares using random grids and difference grids.

    Parameters:
    image (PIL.Image.Image): The input image (PIL Image object) to be encrypted.

    Returns:
    tuple: A tuple containing two PIL.Image.Image objects (grid1_image and grid2_image),
           representing the encrypted shares of the original image.
    """
    img_array = np.array(image).astype(int)  # Convert PIL Image to numpy array and convert to int type

    # Create the first random grid
    grid1 = create_random_grid(img_array.shape)
    grid1_image = Image.fromarray(grid1.astype(np.uint8))  # Convert grid to PIL Image

    # Create the second grid (difference grid)
    grid2 = create_difference_grid(img_array, grid1)
    grid2_image = Image.fromarray(grid2.astype(np.uint8))  # Convert grid to PIL Image

    return grid1_image, grid2_image


if __name__ == '__main__':
    image_path = '../images/test.png'
    output_path = '../images/output/'

    # Load and convert the input image to grayscale
    image = Image.open(image_path).convert('L')  # PIL Image (grayscale)

    # ENCRYPT: Generate shares
    share1, share2 = encrypt(image)
    share1.save(output_path + "RG1.png")
    share2.save(output_path + "RG2.png")

    # DECRYPT: Overlay the grids
    img_share1 = Image.open(output_path + "RG1.png")  # PIL Image (grayscale)
    img_share2 = Image.open(output_path + "RG2.png")  # PIL Image (grayscale)

    out = decrypt(img_share1, img_share2)
    out.save(output_path + "decrypted_image.png")
