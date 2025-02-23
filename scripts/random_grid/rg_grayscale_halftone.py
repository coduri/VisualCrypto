from PIL import Image
import numpy as np


# Returns a dictionary containing function mappings and metadata for the algorithm (used by the web interface).
def get_config():
    return {
        "name": "RG - Grayscale Halftone",
        "description": get_description(),
        "requirements": get_requirements(),
        "encrypt": encrypt,
        "decrypt": decrypt,
        "extension": "png",
        "image_type": "1"
    }


# Defines the expected inputs for encryption/decryption (number of images and additional parameters)
def get_requirements():
    return {
        "encryption": {
            "num_images": 1,
            "parameters": {}  # No additional parameters needed
        },
        "decryption": {
            "num_images": 2,
            "parameters": {
                "xor_or": {
                    "type": "select",
                    "options": ["OR", "XOR"],
                    "default": "OR",
                    "label": "Choose whether to decrypt using OR or XOR:"
                }
            }
        }
    }


# Returns a dictionary containing the description and reference links for the algorithm.
def get_description():
    return {
        "text": "This (2,2) Visual Secret Sharing Scheme is similar to the vc_grayscale_halftone approach, where a black or grayscale image can be used for encryption. "
                "The Steinberg dithering process is applied to convert the image into binary, and then the typical random grid approach by Kafri and Keren is implemented. "
                "Decryption can be performed using the OR operation (a classic approach, but with lower quality) or the XOR operation (to recover the exact image as after dithering).",
        "links": [
            {"text": "Kafri & Keren",
             "url": "https://doi.org/10.1364/ol.12.000377"},
            {"text": "Kumar & Sharma",
             "url": "https://web.iitd.ac.in/~rksharma/Research%20Publications/Journal/Paper50.pdf"}
        ]
    }


# Function to generate the first random binary grid for encryption
def create_first_random_grid(size):
    """
    Generates a random binary grid of specified dimensions.

    Parameters:
    size (tuple): The dimensions of the grid (height, width).

    Returns:
    numpy.ndarray: A random binary grid (0s and 1s) of the specified size.
    """
    grid = np.random.randint(2, size=size)
    return grid


# Function to generate the second random binary grid based on the first one
def create_second_random_grid(image, grid):
    """
    Modifies the first random grid using the halftoned image, based on the Kafri and Keren equation.

    Parameters:
    image (numpy.ndarray): The binary halftoned image used to modify the grid.
    grid (numpy.ndarray): The first random binary grid to be transformed.

    Returns:
    numpy.ndarray: A transformed random binary grid, modified by the halftoned image.
    """
    transformed_grid = np.where(image == 0, grid, 1 - grid)
    return transformed_grid


# Function to combine two binary images using the XOR operation
def decrypt_with_XOR(image1, image2):
    """
    Combines two binary images using the XOR operation.

    Parameters:
    image1 (PIL.Image.Image): The first binary image (PIL Image).
    image2 (PIL.Image.Image): The second binary image (PIL Image).

    Returns:
    PIL.Image.Image: The result of the XOR operation applied to the two input images, with values inverted to black and white.
    """
    # Convert PIL images to numpy arrays
    img1_array = np.array(image1.convert('1'))  # Convert to binary (1-bit) image
    img2_array = np.array(image2.convert('1'))  # Convert to binary (1-bit) image

    # Perform the XOR operation
    overlaid_image = np.bitwise_xor(img1_array, img2_array)
    overlaid_image = 1 - overlaid_image  # Invert the image to get black and white

    # Convert back to PIL image and return
    return Image.fromarray(overlaid_image.astype(np.uint8) * 255)


# Function to combine two binary images using the OR operation
def decrypt_with_OR(image1, image2):
    """
    Combines two binary images using the OR operation.

    Parameters:
    image1 (PIL.Image.Image): The first binary image (PIL Image).
    image2 (PIL.Image.Image): The second binary image (PIL Image).

    Returns:
    PIL.Image.Image: The result of the OR operation applied to the two input images, with values inverted to black and white.
    """
    # Convert PIL images to numpy arrays
    img1_array = np.array(image1.convert('1'))  # Convert to binary (1-bit) image
    img2_array = np.array(image2.convert('1'))  # Convert to binary (1-bit) image

    # Perform the OR operation
    overlaid_image = np.bitwise_or(img1_array, img2_array)
    overlaid_image = 1 - overlaid_image  # Invert the image to get black and white

    # Convert back to PIL image and return
    return Image.fromarray(overlaid_image.astype(np.uint8) * 255)


def decrypt(image1, image2, operation):
    """
    Decrypts two binary images using the specified operation (XOR or OR).

    Parameters:
    image1 (PIL.Image.Image): The first binary image (PIL Image).
    image2 (PIL.Image.Image): The second binary image (PIL Image).
    operation (str): The operation to use for decryption ("XOR" or "OR").

    Returns:
    PIL.Image.Image: The result of the selected decryption operation applied to the two input images.
    """
    if operation.upper() == "XOR":
        return decrypt_with_XOR(image1, image2)
    elif operation.upper() == "OR":
        return decrypt_with_OR(image1, image2)
    else:
        raise ValueError(f"Invalid decryption operation: {operation}. Choose 'XOR' or 'OR'.")


def encrypt(image):
    """
    Encrypts an image by applying a binary inversion and creating two random grids
    based on the binary representation of the image. The random grids are generated
    in such a way that they can later be combined to reveal the original image.

    Parameters:
    image (PIL.Image.Image): The input image to be encrypted. It will be processed in its binary form.

    Returns:
    tuple: A tuple containing two PIL images (image_rg1 and image_rg2), which are the
           generated random grids used in the encryption process.
    """
    image_array = 1 - np.array(image).astype(int)

    # Create the first and second random grids
    rg1 = create_first_random_grid(image_array.shape)
    rg2 = create_second_random_grid(image_array, rg1)

    image_rg1 = Image.fromarray(rg1.astype(np.uint8) * 255)
    image_rg2 = Image.fromarray(rg2.astype(np.uint8) * 255)

    return image_rg1, image_rg2


if __name__ == "__main__":
    image_path = '../images/test.png'
    output_path = '../images/output/'

    # Load and convert the input image to binary
    image = Image.open(image_path).convert('1')
    image.save(output_path + "halftoned.png")

    # ENCRYPT: Generate shares
    share1, share2 = encrypt(image)
    share1.save(output_path + "RG1.png")
    share2.save(output_path + "RG2.png")

    # DECRYPT: Overlay the grids using OR and XOR
    img_share1 = Image.open(output_path + "RG1.png")
    img_share2 = Image.open(output_path + "RG2.png")

    out = decrypt_with_OR(img_share1, img_share2)
    # out = decrypt(img_share1, img_share2, "OR")
    out.save(output_path + "overlap_OR.png")

    out = decrypt_with_XOR(img_share1, img_share2)
    # out = decrypt(img_share1, img_share2, "XOR")
    out.save(output_path + "overlap_XOR.png")
