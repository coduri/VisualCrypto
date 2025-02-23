# Getting Started
This guide provides instructions for setting up and using the **VisualCrypto** repository.

---

## **Installation**
Follow these steps to set up the repository:  

### 1. Clone the Repository  
```bash
git clone https://github.com/coduri/VisualCrypto.git
cd VisualCrypto
```

### 2. Install Dependencies  
Ensure you have Python installed, then run:  
```bash
pip install -r requirements.txt
```

---

## **Usage**
You can interact with the repository in two ways:  

- By running **scripts** directly 
- Through the **web app** interface 

### 1. Running Scripts (CLI Approach) 
To encrypt or decrypt an image using Python scripts:  

1. Navigate to the `scripts/` directory:  
   ```bash
   cd scripts
   ```  

2. Choose an encryption scheme:  
    - **Visual Cryptography**  
     ```bash
     cd visual_cryptography
     ```  
    - **Random Grid**  
     ```bash
     cd random_grid
     ```

3. Ensure the input image and output directories are correctly set in the script:  
   ```python
   image_path = '../images/test.png'
   output_path = '../images/output/'
   ```

4. Run the script:  
   ```bash
   python3 vc_grayscale_halftone.py
   ```
   The generated shares and reconstructed images will be stored in `scripts/images/output/`.  

---

### 2. Using the Web App (GUI Approach) 
The repository includes a **Flask-based web application** for a more user-friendly interaction.  

1. Set the Python Path:

      Before running the application, you need to set the `PYTHONPATH` environment variable. This ensures that Python can correctly locate the project directory and its dependencies. Without this step, launching the web application may result in **ModuleNotFoundError** or import issues.
      
      To set the `PYTHONPATH`, use the following command, replacing `<path-to-repo>` with the absolute path to your project directory:
```bash
export PYTHONPATH=<path-to-repo>
```

    !!! example
        ```bash
        export PYTHONPATH=/Users/yourusername/Desktop/VisualCrypto
        ```

2. Start the Flask Application
```bash
python3 web_app/app.py
```

3. Access the Web Interface: open your browser and go to: `http://127.0.0.1:5000/`  

You can now encrypt and decrypt images using the web interface.  

---
