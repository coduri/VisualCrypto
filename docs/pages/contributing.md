# Contributing
Thank you for your interest in contributing to this project!

This guide will walk you through the process of adding a new **Visual Secret Sharing (VSS) algorithm** to the repository.  

## Steps to Add a New Algorithm  

### Fork & Clone the Repository  
1. Fork this repository to your GitHub account.  
2. Clone your forked repository:  
   ```sh
   git clone https://github.com/coduri/VisualCrypto.git
   cd vss-project
   ```  
3. Create a new branch for your changes:  
   ```sh
   git checkout -b feature/new-algorithm
   ```

### Implement Your Algorithm  
Locate the appropriate directory based on your algorithm type:

- Visual Cryptography algorithms: `scripts/visual_cryptography/`  
- Random Grid algorithms: `scripts/random_grid/`

Create a new Python script for your VSS scheme. Follow the structure of existing scripts and implement the following functions:
#### **Core Functions**  
- **`encrypt(image)`** → Takes an image as input and returns the generated shares.  
- **`decrypt(shares)`** → Reconstructs the image from the shares.  
- **`main()`** → Tests the scheme using `scripts/images/test.png`. It imports an image, performs encryption, saves the shares, re-imports them for decryption, and saves the result. 

!!! info "Handling Multiple Encryption/Decryption Variants"
    If your algorithm supports multiple encryption or decryption methods, encapsulate them into a single function with a selection parameter.

    Example from `rg_grayscale_halftone.py`:

    ```python
    def decrypt(image1, image2, operation):
        if operation.upper() == "XOR":
            return decrypt_with_XOR(image1, image2)
        elif operation.upper() == "OR":
            return decrypt_with_OR(image1, image2)
        else:
            raise ValueError(f"Invalid decryption operation: {operation}. Choose 'XOR' or 'OR'.")
    ```

#### **Support Functions**
- **`get_description()`** → Provides details and references for the scheme.  
- **`get_requirements()`** → Specifies input requirements for encryption and decryption.  
- **`get_config()`** → Defines algorithm configurations for integration.

Refer to [Web Interface Integration](web_interface_integration.md#required-support-functions)

---

### Update the Algorithm Interface
!!! warning
    This step is essential to ensure that your algorithm is accessible through the web interface!

Once your script is implemented, update `algo_interface.py` by:

1. Importing your scheme:  
   ```python
   from scripts.visual_cryptography import (...), vc_new_scheme
   from scripts.random_grid import (...), rg_new_scheme
   ```
2. Adding an entry in the `ALGORITHM_MODULES` dictionary:  
   ```python
   ALGORITHM_MODULES = {
       (...)
       "vc_new_scheme": vc_new_scheme.get_config(),
       "rg_new_scheme": rg_new_scheme.get_config()
   }
   ```

---

### Test Your Algorithm  
Before submitting a Pull Request:

- Run your `main()` function and verify the output.  
- Test your algorithm within the Flask app to ensure correct share generation & decryption.

---

### Submit a Pull Request  
1. **Commit your changes:**  
   ```sh
   git add .
   git commit -m "Added new VSS algorithm: Your Algorithm Name"
   ```  
2. **Push your branch:**  
   ```sh
   git push origin feature/new-algorithm
   ```  
3. **Open a Pull Request on GitHub:**  
      - Navigate to the <a href="https://github.com/coduri/VisualCrypto" target="_blank">Original Repository</a>.  
      - Click **New Pull Request**.  
      - Select your branch, add a descriptive title, and explain your changes.  
      - Attach references, screenshots, or example outputs if applicable.  

---

## Thank You for Contributing!  
Contributions to this project are greatly appreciated. For any questions, feel free to open an issue or reach out to the maintainers. Contact details can be found in the footer of this documentation.

---
