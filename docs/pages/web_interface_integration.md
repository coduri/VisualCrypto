# Web Interface Integration
The web interface is designed to **dynamically adapt** to newly added VSS schemes without requiring manual UI updates. When a new algorithm script is added and registered, the system automatically:

- Lists it in the **algorithm selection dropdown**.
- Retrieves and displays its **description and reference details**.
- Adjusts the **input form fields** according to the algorithm’s requirements.

This automation eliminates the need for hardcoded UI modifications, making it scalable and easy to maintain.

## Required Support Functions
To enable integration and compatibility with the web interface, your VC or RG script must implement three essential support functions:

| **Function**     | **Purpose**                                                                                         |
|------------------|-----------------------------------------------------------------------------------------------------|
| `get_description` | Provides a brief overview of the algorithm and links to related research papers.                    |
| `get_requirements` | Defines the expected inputs for encryption/decryption (number of images and additional parameters). |
| `get_config`     | Specifies the algorithm’s core settings, linking encryption/decryption functions with the web app.  |

The Flask backend utilizes these functions to dynamically generate the required UI elements. 
For a detailed explanation of how the backend interacts with these functions, refer to [API Reference](api_reference.md).

---

### `get_description()`
Provides a brief explanation of the scheme and references to related research papers.

!!! example
    ```python
    def get_description():
        return {
            "text": "Brief description of the implemented scheme...",
            "links": [
                {"text": "Research Paper 1", "url": "https://example.com/paper1"}, 
                {"text": "Research Paper 2", "url": "https://example.com/paper2"}
            ]
        }
    ```

---

### `get_requirements()`  
Specifies input parameters required for encryption and decryption:  

- `num_images`: The number of images required for encryption or decryption.  
- `parameters`: A dictionary containing additional input fields, such as dropdowns or numeric selectors, needed by the scheme.

The front-end JavaScript dynamically generates the HTML form based on these parameters.

!!! example "Basic Example (1 image for encryption, 2 for decryption)"
    ```python
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
    ```
    In this example, since `"num_images": 2` for decryption, if that operation is selected, the following HTML input fields will be generated:  
    
    ```html
    <input type="file" name="image1" id="image1" accept="image/*" required="">
    <input type="file" name="image2" id="image2" accept="image/*" required="">
    ```

!!! example "Advanced Example (Additional Input Field in the Form)"
    Example from `rg_grayscale_bitplane.py`:
    ```python
    "parameters": {
        "bitplanes": {
            "type": "number",
            "default": 3,
            "label": "Number of Most Significant Bit Planes to use:"
        }
    }
    ```
    In addition to the required number of input files, this will generate the following HTML input field:
    ```html
    <label for="bitplanes">Number of Most Significant Bit Planes to use:</label>
    <input type="number" id="bitplanes" name="bitplanes" value="3">
    ```

!!! example "Advanced Example (Additional Selector in the form)"
    Example from `rg_grayscale_halftone.py`:
    ```python
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
    ```
    In addition to the required number of input files, this will generate the following HTML select field:
    ```html
    <label for="xor_or">Choose whether to decrypt using OR or XOR:</label>
    <select id="xor_or" name="xor_or">
        <option value="OR" selected>OR</option>
        <option value="XOR">XOR</option>
    </select>
    ```

---

### `get_config()`
Defines how the Flask app interacts with your algorithm.

!!! example
    ```python
    def get_config():
        return {
            "name": "Algorithm Name",  
            "description": get_description(),   # Used for documentation & references
            "requirements": get_requirements(), # Dynamically generates form inputs
            "encrypt": encrypt,   # Encryption function
            "decrypt": decrypt,   # Decryption function
            "extension": "png",   # Image file format
            "image_type": "L"     # Image mode (e.g., 'L' for grayscale, '1' for binary)
        }
    ```
The `get_config()` function acts as a bridge between individual algorithms and the framework. It encapsulates all required metadata, descriptions, functions, and parameters within a single dictionary, allowing the Flask app to interact with the scheme simply by accessing `get_config()`.

---

## Another Key Component: `ALGORITHM_MODULES`
To simplify integration and eliminate the need to manually import each scheme’s `get_config()` in `app.py`, a centralized dictionary called `ALGORITHM_MODULES` is defined in `algo_interface.py`. This serves as a registry for all available algorithms and is structured as follows:

```python
ALGORITHM_MODULES = {
    "vc_scheme": vc_scheme.get_config(),
    "rg_scheme": rg_scheme.get_config(),
}
```  

By simply importing `ALGORITHM_MODULES` in `app.py`, the backend automatically gains access to all necessary details for executing each scheme and defining the required endpoints, which will be covered in the next section.

The following sequence diagram illustrates the interaction between `app.py`, `algo_interface.py`, and the individual scheme scripts:

``` mermaid
sequenceDiagram
    participant app.py
    participant algo_interface.py
    participant scripts

    algo_interface.py->>scripts: Call get_config() for all schemes
    scripts-->>algo_interface.py: Return configurations

    app.py->>algo_interface.py: Import ALGORITHM_MODULES
    algo_interface.py-->>app.py: Return ALGORITHM_MODULES
```

This structured approach ensures efficient access to all available algorithms without requiring manual updates in `app.py`.


---
