# API Reference

In this section the API endpoints available in `app.py` are described, including their purpose, parameters and response format.

---

| **Endpoint** | **Method** | **Description**                                                                                 |
|-------------|-----------|-------------------------------------------------------------------------------------------------|
| `/` | GET | Returns the main index.html page.                                                               |
| `/api/algorithm_list` | GET | Returns a list of available algorithms with their display names.                                |
| `/api/algorithm_description/<algorithm>` | GET | Returns a description and references for the specified algorithm.                                |
| `/api/algorithm_requirements/<algorithm>/<operation>` | GET | Returns the input and parameter requirements for the given algorithm and operation.             |
| `/process` | POST | Processes the selected encryption or decryption operation based on input images and parameters. |


## API endpoints

### **`/`**
- **Method:** `GET`
- **Description:**
      - Serves the main HTML page (`index.html`) of the application.
      - This is the entry point for users to interact with the visual cryptography tool via a web interface.

---

### **`/api/algorithm_list`**
- **Method:** `GET`
- **Purpose:** Returns a list of all available algorithms with their corresponding user-friendly names.
  - **Response Format:** A JSON object with key-value pairs, where the key is the algorithm identifier, and the value is its display name.

    !!! example "Example Response"
        ```json
        {
            "algorithms": {
                "vc_cmyk": "VC - Color CMYK",
                "rg_grayscale_bitplane": "RG - Grayscale Bitplane"
            }
        }
        ```

- **How it's used in JavaScript**: The key acts as the `<option>` element’s value in HTML, while the corresponding value is displayed as the visible text in the dropdown menu.

---

### **`/api/algorithm_description/<algorithm>`**
- **Method:** `GET`
- **Purpose:** Provides a textual description and relevant links for a given algorithm.
- **Path Parameter:**
    - `<algorithm>`: The identifier of the requested algorithm.
- **Response Format:** A JSON object that matches the exact output of `get_description()` for the specified `<algorithm>`:

    !!! example "Example Response"
        ```json
        {  
            "text": "Brief description of the implemented scheme...",
            "links": [
                {"text": "Research Paper 1", "url": "https://example.com/paper1"}, 
                {"text": "Research Paper 2", "url": "https://example.com/paper2"}
            ]
        }
        ```

    !!! example "Example Response where the description is unavailable"
        ```json
        {
            "text": "Description not available.",
            "links": []
        }
        ```

- **How it's used in JavaScript**: The returned JSON object will be used to display a description and some reference links in the information box.

---

### **`/api/algorithm_requirements/<algorithm>/<operation>`**
- **Method:** `GET`
- **Purpose:** Returns the required number of images and parameters for a specified algorithm and operation (encryption or decryption).
- **Path Parameters:**
      - `<algorithm>`: The algorithm identifier.
      - `<operation>`: Either `encryption` or `decryption`.
- **Response Format:** A JSON object containing the output of `get_requirements()` for the specified `<algorithm>`, filtered by `<operation>`:

    !!! example "Example Response (Encryption requiring additional parameters)"
        ```json
        {
            "num_images": 1,
            "parameters": {
                "bitplanes": {
                    "type": "number",
                    "default": 3,
                    "label": "Number of Most Significant Bit Planes to use"
                }
            }
        }
        ```

    !!! example "Example Response (Decryption with selection option)"
        ```json
        {
            "num_images": 2,
            "parameters": {
                "xor_or": {
                    "type": "select",
                    "options": ["OR", "XOR"],
                    "default": "OR",
                    "label": "Choose whether to decrypt using OR or XOR"
                }
            }
        }
        ```

- **How it's used in JavaScript**: The returned JSON object will be used to dynamically generate HTML form elements for image uploads and any required additional parameters.

---

### **`/process`**
- **Method:** `POST`
- **Purpose:** Processes encryption or decryption based on the selected algorithm, input images, and additional parameters.
- **Request Parameters:**
    - `operation` (encryption or decryption)
    - `algorithm` (algorithm identifier)
    - `image1, image2, ...` (uploaded images)
    - Additional parameters required by the selected algorithm.
- **Response:**
    - If encryption produces multiple images (e.g., shares), they are saved and displayed by rendering `enc_result.html`
    - If decryption is successful, the result is saved and displayed by rendering `dec_result.html`.
    - If an error occurs during encryption or decryption, `error.html` will be displayed with a description of the issue.

---

## How is the initialization of `index.html` done automatically?
When a new script is added following the [Contribution Guidelines](contributing.md), as long as it adheres to the required structure and is registered in `algo_interface`, the web interface **automatically**:

- Adds the new algorithm to the **selection dropdown** via JavaScript fetch to the route `/api/algorithm_list`.  
- Loads the **algorithm description** into the information box using by fetching `/api/algorithm_description/<algorithm>`.  
- Fetches the **algorithm’s requirements** and updates the UI dynamically through `/api/algorithm_requirements/<algorithm>/<operation>`.  

This automation ensures that new algorithms become available in the web interface instantly, without requiring manual updates

``` mermaid
sequenceDiagram
    participant index.html
    participant app.py
    participant algo_interface.py
    participant scripts

    algo_interface.py->>scripts: Call get_config() for all schemes
    scripts-->>algo_interface.py: Return configurations

    app.py->>algo_interface.py: Import ALGORITHM_MODULES
    algo_interface.py-->>app.py: Return ALGORITHM_MODULES

    index.html->>app.py: Request /api/algorithm_list
    app.py->>app.py: Execute backend logic
    app.py-->>index.html: Return list of available algorithms
    index.html->>index.html: Populate the `<select>` element with algorithm options

    index.html->>app.py: Request /api/algorithm_description/<algorithm>
    app.py->>app.py: Execute backend logic
    app.py-->>index.html: Return description of the selected algorithm
    index.html->>index.html: Display description in the info box

    index.html->>app.py: Request /api/algorithm_requirements/<algorithm>/<operation>
    app.py->>app.py: Execute backend logic
    app.py-->>index.html: Return requirements for the selected algorithm and operation
    index.html->>index.html: Update the HTML form based on the requirements

```

Once the initialization is complete, as illustrated in the sequence diagram above, the following queries are sufficient:  

- **`GET /api/algorithm_description/<algorithm>`** → Triggered when the selected algorithm changes.  
- **`GET /api/algorithm_requirements/<algorithm>/<operation>`** → Triggered when either the selected algorithm or the selected operation changes.  

---