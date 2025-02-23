from PIL import Image
import random
import copy


# Returns a dictionary containing function mappings and metadata for the algorithm (used by the web interface).
def get_config():
    return {
        "name": "VC - Grayscale Halftone",
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
        "text": "This (2,2) Visual Cryptography Scheme is one of the simplest implementations of a VC scheme. This script allows for the encryption and decryption of binary images (composed of black and white pixels) as well as grayscale images. In the case of grayscale images, they are first converted into binary images using the Floyd-Steinberg dithering process before applying the classic VC scheme.",
        "links": [
            {"text": "Adi Shamir",
             "url": "https://doi.org/10.1145/359168.359176"},
            {"text": "Naor, Moni & Shamir",
             "url": "https://doi.org/10.1007/BFb0053419"},
            {"text": "Weir & Yan",
             "url": "https://doi.org/10.1007/978-3-642-14298-7_5"},
            {"text": "Bhosale & Patil",
             "url": "https://doi.org/10.1109/ICICT48043.2020.9112420"}
        ]
    }


# Matrices for visual cryptography (VC) encoding of black and white pixels
white_matrix = [[1, 1, 0, 0], [1, 1, 0, 0]]
black_matrix = [[1, 1, 0, 0], [0, 0, 1, 1]]


# Function to map a pixel value from RGB encoding (0 = black, 1 = white) to VC encoding
def map_rgb_to_bit(rgb_value):
    """
    Maps the pixel value from RGB encoding to visual cryptography (VC) encoding.
    In this mapping, a pixel value of 0 (black) is converted to 1, and any non-zero value (white) is converted to 0.

    Parameters:
    rgb_value (int): The pixel value in RGB format (0 for black, 255 for white).

    Returns:
    int: 1 for black, 0 for white (VC encoding).
    """
    return 1 if rgb_value == 0 else 0


# Function to map a pixel value from VC encoding to RGB encoding
def map_bit_to_rgb(vc_value):
    """
    Maps the VC encoding value (1 = black, 0 = white) back to RGB encoding.
    In this mapping, a VC value of 1 (black) is converted to RGB value 0 (black),
    and a VC value of 0 (white) is converted to RGB value 255 (white).

    Parameters:
    vc_value (int): The pixel value in VC encoding (1 for black, 0 for white).

    Returns:
    int: 0 for black, 255 for white (RGB encoding).
    """
    return 0 if vc_value == 1 else 255


# Function to randomly permute the columns of a matrix
def random_col_permutation(matrix):
    """
    Randomly permutes the columns of a given matrix.

    Parameters:
    matrix (list of lists): A 2D matrix to be permuted.

    Returns:
    list of lists: A new matrix with columns permuted randomly.
    """
    n_rows = len(matrix)
    n_cols = len(matrix[0])
    new_matrix = copy.deepcopy(matrix)

    # Generate a random permutation of column indices
    col_indices = list(range(n_cols))
    random.shuffle(col_indices)

    # Apply the column permutation to the matrix
    for i in range(n_rows):
        for j in range(n_cols):
            new_matrix[i][j] = matrix[i][col_indices[j]]

    return new_matrix


# Function to populate the subpixels for both shares based on the matrix
def populate_subpixels(share1, share2, i, j, matrix):
    """
    Populates the subpixels for two shares based on a given 2x2 matrix.
    Each share's corresponding pixels are set according to the values in the matrix.

    Parameters:
    share1 (PIL.Image.Image): The first share image.
    share2 (PIL.Image.Image): The second share image.
    i (int): The x-coordinate of the pixel.
    j (int): The y-coordinate of the pixel.
    matrix (list of lists): A 2x2 matrix containing pixel values for the subpixels.
    """
    # Populate subpixels for Share1
    share1.putpixel((i * 2, j * 2), matrix[0][0])
    share1.putpixel((i * 2, j * 2 + 1), matrix[0][1])
    share1.putpixel((i * 2 + 1, j * 2), matrix[0][2])
    share1.putpixel((i * 2 + 1, j * 2 + 1), matrix[0][3])

    # Populate subpixels for Share2
    share2.putpixel((i * 2, j * 2), matrix[1][0])
    share2.putpixel((i * 2, j * 2 + 1), matrix[1][1])
    share2.putpixel((i * 2 + 1, j * 2), matrix[1][2])
    share2.putpixel((i * 2 + 1, j * 2 + 1), matrix[1][3])


# Function to encrypt the image into two shares
def encrypt(image):
    """
    Encrypts the input image using visual cryptography, generating two shares.

    The image is processed pixel by pixel, and each pixel is encoded using either a white or black matrix,
    which is then randomly permuted. The resulting subpixels are placed into two separate share images.

    Parameters:
    image (PIL.Image.Image): The input image to be encrypted (must be black and white).

    Returns:
    tuple: A tuple containing two share images (share1, share2).
    """
    share1 = Image.new("1", (image.size[0] * 2, image.size[1] * 2))
    share2 = Image.new("1", (image.size[0] * 2, image.size[1] * 2))

    for i in range(image.size[0]):
        for j in range(image.size[1]):
            # Get the pixel value and map it to VC encoding
            source_pixel_rgb = image.getpixel((i, j))
            source_pixel_vc = map_rgb_to_bit(source_pixel_rgb)

            # For white pixels
            if source_pixel_vc == 0:
                random_white_matrix = random_col_permutation(white_matrix)
                populate_subpixels(share1, share2, i, j, random_white_matrix)

            # For black pixels
            else:
                random_black_matrix = random_col_permutation(black_matrix)
                populate_subpixels(share1, share2, i, j, random_black_matrix)

    return share1, share2


# Function to decrypt the shares and reconstruct the original image
def decrypt(share1, share2):
    """
    Decrypts the two shares using the OR operation to reconstruct the original image.

    Parameters:
    share1 (PIL.Image.Image): The first share image.
    share2 (PIL.Image.Image): The second share image.

    Returns:
    PIL.Image.Image: The decrypted image, reconstructed from the two shares.
    """
    out = Image.new("1", (share1.size[0], share1.size[1]))

    for i in range(share1.size[0]):
        for j in range(share1.size[1]):
            # Overlay shares using OR operation
            share1_vc_value = map_rgb_to_bit(share1.getpixel((i, j)))
            share2_vc_value = map_rgb_to_bit(share2.getpixel((i, j)))
            out_vc_value = share1_vc_value | share2_vc_value

            # Map VC encoding back to RGB
            share1.putpixel((i, j), map_bit_to_rgb(share1_vc_value))
            share2.putpixel((i, j), map_bit_to_rgb(share2_vc_value))
            out.putpixel((i, j), map_bit_to_rgb(out_vc_value))

    return out


if __name__ == "__main__":
    image_path = '../images/test.png'
    output_path = '../images/output/'

    # Load and convert the input image to binary
    image = Image.open(image_path).convert('1')
    image.save(output_path + "halftoned.png")

    # ENCRYPT: Generate shares
    share1, share2 = encrypt(image)
    share1.save(output_path + "share1.png")
    share2.save(output_path + "share2.png")

    # DECRYPT: Overlay shares to reconstruct the image
    img_share1 = Image.open(output_path + "share1.png")
    img_share2 = Image.open(output_path + "share2.png")

    out = decrypt(img_share1, img_share2)
    out.save(output_path + "overlap.png")
