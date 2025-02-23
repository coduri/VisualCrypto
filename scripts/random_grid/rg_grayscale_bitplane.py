import numpy as np
from PIL import Image
from scripts.random_grid.rg_grayscale_halftone import create_first_random_grid, create_second_random_grid


# Returns a dictionary containing function mappings and metadata for the algorithm (used by the web interface).
def get_config():
    return {
        "name": "RG - Grayscale Bitplane",
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
            "parameters": {
                "bitplanes": {
                    "type": "number",
                    "default": 3,
                    "label": "Number of Most Significant Bit Planes to use:"
                }
            }
        },
        "decryption": {
            "num_images": 2,
            "parameters": {}  # No extra parameters needed
        }
    }


# Returns a dictionary containing the description and reference links for the algorithm.
def get_description():
    return {
        "text": "This (2,2) Visual Secret Sharing Scheme, inspired by the paper by Vahidi et al., handles grayscale images and is based on the concept of bitplanes. "
                "It is possible to indicate the number of desired bitplanes in the form.",
        "links": [
            {"text": "Kafri & Keren",
             "url": "https://doi.org/10.1364/ol.12.000377"},
            {"text": "Vahidi et al.",
             "url": "https://www.researchgate.net/profile/Javad-Vahidi/publication/279916654_A_new_approach_for_gray_scale_image_encryption_by_random_grids/links/559e19d208aeb45d1715ed4c/A-new-approach-for-gray-scale-image-encryption-by-random-grids.pdf"},

        ]
    }


# Function to extract bitplanes from an image
def extract_bitplanes(image_array, num_planes=8):
    """
    Extracts the specified number of bitplanes from a grayscale image.

    Parameters:
    image_array (numpy.ndarray): The input grayscale image as a numpy array.
    num_planes (int): The number of bitplanes to extract, starting from the most significant bit (MSB).

    Returns:
    list: A list of numpy arrays, where each array corresponds to a bitplane.
    """
    bit_planes = []

    for i in range(num_planes - 1, -1, -1):  # From MSB to LSB
        # Extract the i-th bit and add it to the bitplane
        bit_i = (image_array >> i) & 1
        bit_planes.append(bit_i)

    return bit_planes


# Function to save individual bitplanes as images
def save_bitplanes(bit_planes, output_path='./'):
    """
    Saves each bitplane in the bit_planes list as an image.

    Parameters:
    bit_planes (list): A list of numpy arrays representing bitplanes.
    output_path (str): The directory path where images should be saved.
    """
    for i, bit_plane in enumerate(bit_planes):
        # Multiply by 255 to make the bit values visible as 0 (black) or 255 (white)
        bit_plane_image = Image.fromarray((bit_plane * 255).astype(np.uint8))

        # Save the bitplane image
        path = f'{output_path}bitplane{i}.png'
        bit_plane_image.save(path)
        print(f'Saved: {path}')


# Function to generate RG1_final and RG2_final by combining random grids from bitplanes
def generate_final_random_grids(bit_planes, number_of_MSBP, output_path='./'):
    """
    Generates the final combined RG1_final and RG2_final by creating random grids from the most significant bitplanes.

    Parameters:
    bit_planes (list): A list of bitplanes.
    number_of_MSBP (int): The number of most significant bitplanes to use.
    output_path (str): The directory path where RG images should be saved.

    Returns:
    numpy.ndarray, numpy.ndarray: The combined RG1_final and RG2_final images.
    """
    height, width = bit_planes[0].shape
    RG1_final = np.zeros((height, width), dtype=np.uint8)  # For RG1 in grayscale
    RG2_final = np.zeros((height, width), dtype=np.uint8)  # For RG2 in grayscale

    # ENCRYPT: Generate and save random grids (RGs) from the most significant bitplanes
    for i in range(number_of_MSBP):  # Iterate over the indices of the most significant bitplanes
        # Create the first and second random grids for the current bitplane
        rg1 = create_first_random_grid(bit_planes[i].shape)
        rg2 = create_second_random_grid(bit_planes[i], rg1)

        # Add the current random grids into the final RG1 and RG2 by shifting
        RG1_final += (rg1 * (1 << (7 - i))).astype(np.uint8)  # Shift bits to the correct grayscale position
        RG2_final += (rg2 * (1 << (7 - i))).astype(np.uint8)  # Shift bits to the correct grayscale position

        # Save individual bitplane RG images
        # image_rg1 = Image.fromarray((rg1 * 255).astype(np.uint8))  # Convert to binary image for visualization
        # image_rg1.save(output_path + f"bitplane_{i}_RG1.png")
        # print(f"Saved: RG1 for bitplane {i}")

        # image_rg2 = Image.fromarray((rg2 * 255).astype(np.uint8))  # Convert to binary image for visualization
        # image_rg2.save(output_path + f"bitplane_{i}_RG2.png")
        # print(f"Saved: RG2 for bitplane {i}")

    # Return the combined RG1 and RG2 as final images
    return RG1_final, RG2_final


# Function to decrypt the final RG1_final and RG2_final images and reconstruct the original bitplanes
def decrypt(rg1_final, rg2_final, number_of_MSBP=8):
    """
    Decrypts the final combined RG1_final and RG2_final images to recover the original bitplanes.
    Then, it reconstructs the original grayscale image by combining the decrypted bitplanes.

    Parameters:
    rg1_final (PIL.Image.Image): The final RG1 image (after encryption) as a PIL Image.
    rg2_final (PIL.Image.Image): The final RG2 image (after encryption) as a PIL Image.
    number_of_MSBP (int): The number of most significant bitplanes to be overlapped.

    Returns:
    PIL.Image.Image: The decrypted grayscale image, reconstructed from the bitplanes.
                     The image is returned as a PIL Image object, ready for saving or display.
    """
    # Convert the PIL Image inputs to numpy arrays
    rg1_final_array = np.array(rg1_final)
    rg2_final_array = np.array(rg2_final)

    # Initialize an array to hold the final reconstructed grayscale image
    decrypted_image = np.zeros_like(rg1_final_array, dtype=np.uint8)

    # List to store the decrypted bitplanes
    decrypted_bitplanes = []

    # Loop over each of the most significant bitplanes
    for i in range(number_of_MSBP):
        # Extract the relevant bits for the i-th bitplane from RG1_final and RG2_final
        bitplane_rg1 = (rg1_final_array >> (7 - i)) & 1  # Extract the i-th bit from RG1_final
        bitplane_rg2 = (rg2_final_array >> (7 - i)) & 1  # Extract the i-th bit from RG2_final

        # Reconstruct the original bitplane by performing XOR operation on the extracted bits
        overlaid_image = np.bitwise_xor(bitplane_rg1, bitplane_rg2)
        overlaid_image = 1 - overlaid_image  # Invert the image to get black and white

        # Append the decrypted bitplane to the list
        decrypted_bitplanes.append(overlaid_image)

        # Shift each decrypted bitplane to its correct position and add it to the final image
        decrypted_image += decrypted_bitplanes[i] * (1 << (7 - i))  # Shift and combine

    # Return the final decrypted grayscale image
    return Image.fromarray(decrypted_image)


def encrypt(image, number_of_MSBP):
    """
    Encrypts a grayscale image by decomposing it into bitplanes, applying random grid-based encryption,
    and returning the final combined RG1 and RG2 images.

    Parameters:
    image (PIL.Image.Image): The input grayscale image to be encrypted.
    number_of_MSBP (int): The number of most significant bitplanes to be processed and encrypted.

    Returns:
    PIL.Image.Image: The encrypted RG1 image (final version after applying random grids).
    PIL.Image.Image: The encrypted RG2 image (final version after applying random grids).
    """
    image_array = 1 - np.array(image).astype(int)

    # Decompose the grayscale image into bitplanes
    bit_planes = extract_bitplanes(image_array)
    # save_bitplanes(bit_planes, output_path)

    # Generate final RG1 and RG2 images by combining the random grids for the most significant bitplanes
    RG1_final, RG2_final = generate_final_random_grids(bit_planes, number_of_MSBP)

    # Save the combined RG1 and RG2 images
    image_RG1_final = Image.fromarray(RG1_final)
    image_RG2_final = Image.fromarray(RG2_final)

    return image_RG1_final, image_RG2_final


if __name__ == "__main__":
    image_path = '../images/test.png'
    output_path = '../images/output/'
    number_of_MSBP = 3  # Number of most significant bitplanes to consider when enc/dec (8 for full bitplane)

    # Load the image and convert to grayscale ('L' mode for 8-bit grayscale)
    image = Image.open(image_path).convert('L')

    # ENCRYPT: Generate shares
    share1, share2 = encrypt(image, number_of_MSBP)
    share1.save(output_path + "RG1_final.png")
    share2.save(output_path + "RG2_final.png")

    # DECRYPT: Overlay the grids: RG1_final and RG2_final
    img_share1 = Image.open(output_path + "RG1_final.png")
    img_share2 = Image.open(output_path + "RG2_final.png")

    decrypted_image = decrypt(img_share1, img_share2)
    decrypted_image.save(output_path + "final_decrypted_image.png")
