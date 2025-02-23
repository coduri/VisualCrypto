from PIL import Image
from scripts.visual_cryptography.vc_grayscale_halftone import encrypt as encrypt_bin_img, decrypt as decrypt_bin_img


# Returns a dictionary containing function mappings and metadata for the algorithm (used by the web interface).
def get_config():
    return {
        "name": "VC - Color CMYK",
        "description": get_description(),
        "requirements": get_requirements(),
        "encrypt": encrypt,
        "decrypt": decrypt,
        "extension": "tiff",
        "image_type": "CMYK"
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
        "text": "This (2,2) Visual Cryptography Scheme is inspired by the approach outlined in the paper by Qiao et al. The scheme utilizes CMYK images, designed to work with .TIFF image files. Additionally, the encoding process makes the image appear entirely white for code reuse purposes. For further details, refer to the script.",
        "links": [
            {"text": "Adi Shamir",
             "url": "https://doi.org/10.1145/359168.359176"},
            {"text": "Naor, Moni & Shamir",
             "url": "https://doi.org/10.1007/BFb0053419"},
            {"text": "Qiao et al.",
             "url": "https://doi.org/10.1109/ICMTMA.2009.294"},
            {"text": "Young-Chang Hou",
             "url": "https://doi.org/10.1016/S0031-3203(02)00258-3"}
        ]
    }


# Function to isolate a specific channel (Cyan, Magenta, or Yellow) from a CMYK image
def extract_cmyk_channel(image, channel):
    """
    Isolates a single channel (Cyan, Magenta, or Yellow) from a CMYK image.

    Parameters:
    image (PIL.Image.Image): The input CMYK image in PIL format.
    channel (int): Index of the channel to isolate (0 for Cyan, 1 for Magenta, 2 for Yellow, 3 for Black).

    Returns:
    PIL.Image.Image: A grayscale (mode "L") image representing the intensity of the isolated channel.
    """
    return image.split()[channel]


# Function to apply Floyd-Steinberg dithering to a grayscale image
def floyd_steinberg_dithering(img):
    """
    Applies Floyd-Steinberg dithering to a grayscale image. This technique diffuses
    the quantization error from each pixel to its neighboring pixels, creating a visually
    smoother binary image.

    Parameters:
    img (PIL.Image.Image): The input grayscale image (mode "L"), in this case it is a single CMYK channel.

    Returns:
    PIL.Image.Image: A new dithered grayscale image (mode "L").
    """
    dithered_image = Image.new("L", img.size)

    for y in range(img.size[1]):  # Loop through rows (image height)
        for x in range(img.size[0]):  # Loop through columns (image width)
            old_value = img.getpixel((x, y))  # Original pixel value
            new_value = 255 if old_value > 128 else 0  # Threshold for binary dithering
            dithered_image.putpixel((x, y), new_value)  # Set dithered pixel value

            quant_error = old_value - new_value  # Calculate quantization error

            # Diffuse quantization error to neighboring pixels
            if x < img.size[0] - 1:  # Right neighbor
                pixel = img.getpixel((x + 1, y))
                img.putpixel((x + 1, y), min(max(pixel + quant_error * 7 // 16, 0), 255))

                if y < img.size[1] - 1:  # Bottom-right neighbor
                    pixel = img.getpixel((x + 1, y + 1))
                    img.putpixel((x + 1, y + 1), min(max(pixel + quant_error * 1 // 16, 0), 255))

            if y < img.size[1] - 1:  # Bottom neighbor
                pixel = img.getpixel((x, y + 1))
                img.putpixel((x, y + 1), min(max(pixel + quant_error * 5 // 16, 0), 255))

                if x > 0:  # Bottom-left neighbor
                    pixel = img.getpixel((x - 1, y + 1))
                    img.putpixel((x - 1, y + 1), min(max(pixel + quant_error * 3 // 16, 0), 255))

    return dithered_image


# Function to decompose a CMYK image into individual channels, apply dithering, and return the results
def decompose_and_dither(image):
    """
    Decomposes a CMYK image into its individual Cyan, Magenta, and Yellow channels,
    applies Floyd-Steinberg dithering to each channel, and returns the dithered results.

    Parameters:
    image (PIL.Image.Image): The input CMYK image.

    Returns:
    tuple: A tuple containing three dithered images corresponding to the Cyan, Magenta,
           and Yellow channels. Each returned image is in grayscale format (mode "L") but
           represents the dithered intensity values of the respective CMYK channel from the
           original image.
    """
    cyan_channel = 0
    magenta_channel = 1
    yellow_channel = 2

    # Decompose channels
    cyan_monochrome = extract_cmyk_channel(image, cyan_channel)
    magenta_monochrome = extract_cmyk_channel(image, magenta_channel)
    yellow_monochrome = extract_cmyk_channel(image, yellow_channel)

    # Apply dithering to each channel
    dthrd_cyan = floyd_steinberg_dithering(cyan_monochrome)
    dthrd_magenta = floyd_steinberg_dithering(magenta_monochrome)
    dthrd_yellow = floyd_steinberg_dithering(yellow_monochrome)

    # Return the individual dithered channels
    return dthrd_cyan, dthrd_magenta, dthrd_yellow


def combine_cmyk_channels(share_c, share_m, share_y):
    """
    Combines the Cyan, Magenta, and Yellow shares into a single CMYK image.

    Parameters:
    share_c (PIL.Image.Image): The Cyan channel share.
    share_m (PIL.Image.Image): The Magenta channel share.
    share_y (PIL.Image.Image): The Yellow channel share.

    Returns:
    PIL.Image.Image: The combined CMYK image.
    """
    combined_image = Image.new("CMYK", share_c.size)

    for y in range(share_c.size[1]):
        for x in range(share_c.size[0]):
            cyan_value = share_c.getpixel((x, y))
            magenta_value = share_m.getpixel((x, y))
            yellow_value = share_y.getpixel((x, y))

            # Combine values into a single CMYK pixel
            pixels = (cyan_value, magenta_value, yellow_value, 0)
            combined_image.putpixel((x, y), pixels)

    return combined_image


def encrypt(image):
    """
    Encrypts a CMYK image using visual cryptography principles, generating two shares that can
    be combined to reconstruct the original image.

    Parameters:
    image (PIL.Image.Image): The input CMYK image to be encrypted.

    Returns:
    tuple: A pair of images (combined_image1, combined_image2) representing the two encrypted shares.
           These shares are CMYK images where each channel contains a visually cryptographic share
           derived from the dithering and encryption process.

    Notes:
    Since the `encrypt_bin_img` function of vc_basic has been reused, the individual channel shares are
    treated as binary images. This means that, for each channel, a pixel can take a value of 0 or 1.
    In binary images, this corresponds to black or white, but in CMYK images, this trivially translates
    to 0 (white) or 1 (also white), making the difference visually indistinguishable.
    For this reason the exported combined_share will look like full white images.
    """
    # Decompose, dither, and get individual channels (images in CMYK mode)
    print("Starting extraction and dithering...", end="")
    dthrd_cyan, dthrd_magenta, dthrd_yellow = decompose_and_dither(image)
    print(" done.")

    # Generate shares for each channel (Cyan, Magenta, Yellow)
    print("Starting encryption...")
    share1_c, share2_c = encrypt_bin_img(dthrd_cyan)
    share1_m, share2_m = encrypt_bin_img(dthrd_magenta)
    share1_y, share2_y = encrypt_bin_img(dthrd_yellow)
    print("\t 6 shares generated.")

    # Combine shares to reduce them to just 2 combined shares
    combined_image1 = combine_cmyk_channels(share1_c, share1_m, share1_y)
    combined_image2 = combine_cmyk_channels(share2_c, share2_m, share2_y)
    print("\t 2 combined shares generated.")

    return combined_image1, combined_image2


def decrypt(share1, share2):
    """
    Decrypts two encrypted CMYK shares to reconstruct the original image using visual cryptography.

    Parameters:
    share1 (PIL.Image.Image): The first encrypted share (CMYK image).
    share2 (PIL.Image.Image): The second encrypted share (CMYK image).

    Returns:
    PIL.Image.Image: A reconstructed CMYK image that combines the information from both shares.
    """
    # Reconstruct the Cyan, Magenta, and Yellow channels by decrypting the combined shares
    print("Starting decryption...")
    cyan_overlap = decrypt_bin_img(share1.split()[0], share2.split()[0])
    magenta_overlap = decrypt_bin_img(share1.split()[1], share2.split()[1])
    yellow_overlap = decrypt_bin_img(share1.split()[2], share2.split()[2])

    # Combine the overlapped channels into a single CMYK image
    decrypted = combine_cmyk_channels(cyan_overlap, magenta_overlap, yellow_overlap)
    print("\t 2 overlapping completed.")

    return decrypted


if __name__ == "__main__":
    image_path = '../images/test.png'
    output_path = '../images/output/'

    # Load the image and convert to CMYK
    image = Image.open(image_path).convert("CMYK")

    # ENCRYPT: Generate shares
    combined_image1, combined_image2 = encrypt(image)
    combined_image1.save(output_path + "combined_share1.tiff")
    combined_image2.save(output_path + "combined_share2.tiff")

    # DECRYPT: Overlay shares to reconstruct the image
    img_share1 = Image.open(output_path + "combined_share1.tiff")
    img_share2 = Image.open(output_path + "combined_share2.tiff")

    out = decrypt(img_share1, img_share2)
    out.save(output_path + "overlap.tiff")
