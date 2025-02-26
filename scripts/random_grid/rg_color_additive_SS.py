import numpy as np
from PIL import Image
from scripts.random_grid.rg_grayscale_additive_SS import create_random_grid, create_difference_grid


# Returns a dictionary containing function mappings and metadata for the algorithm (used by the web interface).
def get_config():
    return {
        "name": "RG - Color (RGB) Additive Secret Sharing",
        "description": get_description(),
        "requirements": get_requirements(),
        "encrypt": encrypt,
        "decrypt": decrypt,
        "extension": "png",
        "image_type": "RGB"
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
        "text": "This (2,2) Visual Secret Sharing Scheme extends the general additive secret sharing scheme to handle RGB color images.",
        "links": [
            {"text": "Kafri & Keren",
             "url": "https://doi.org/10.1364/ol.12.000377"}
        ]
    }


# Function to encrypt an image by generating two shares using random grids and difference grids
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

    # Create the first random grid for each channel and stack them
    grid1 = np.stack([create_random_grid(img_array.shape[:2]) for _ in range(3)], axis=-1)
    grid1_image = Image.fromarray(grid1)

    # Create the second grid using modular subtraction
    grid2 = create_difference_grid(img_array, grid1)
    grid2_image = Image.fromarray(grid2.astype(np.uint8))

    return grid1_image, grid2_image


# Function to decrypt two images by overlaying the grids
def decrypt(image1, image2):
    """
    Combines two grids by adding the second grid to the first.

    Parameters:
    image1 (PIL.Image.Image): The first image (PIL Image object), to be converted to numpy array and processed.
    image2 (PIL.Image.Image): The second image (PIL Image object), to be converted to numpy array and processed.

    Returns:
    PIL.Image.Image: The resulting image (PIL Image object) after adding the two grids.
    """
    img1_array = np.array(image1.convert('RGB'))  # Convert PIL Image to numpy array (RGB)
    img2_array = np.array(image2.convert('RGB'))  # Convert PIL Image to numpy array (RGB)

    # Combine the grids using modular addition
    decrypted = img1_array + img2_array
    return Image.fromarray(decrypted.astype(np.uint8))  # Convert numpy array back to PIL Image


if __name__ == '__main__':
    image_path = '../images/test.png'
    output_path = '../images/output/'

    # Load and convert the input image to RGB
    image = Image.open(image_path).convert('RGB')

    # ENCRYPT: Generate shares
    share1, share2 = encrypt(image)
    share1.save(output_path + "RG1.png")
    share2.save(output_path + "RG2.png")

    # DECRYPT: Overlay the grids
    img_share1 = Image.open(output_path + "RG1.png")  # PIL Image (RGB)
    img_share2 = Image.open(output_path + "RG2.png")  # PIL Image (RGB)

    out = decrypt(img_share1, img_share2)
    out.save(output_path + "decrypted_image.png")
