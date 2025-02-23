from PIL import Image
from flask import Flask, render_template, request, url_for, jsonify
import os

from algo_interface import ALGORITHM_MODULES

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)


# Route for the main page
@app.route('/')
def home():
    return render_template('index.html')


# Route that returns the list of algorithms available
@app.route('/api/algorithm_list', methods=['GET'])
def get_algorithms():
    algorithms = {key: value["name"] for key, value in ALGORITHM_MODULES.items()}  # Extract key and name
    return jsonify({"algorithms": algorithms})


# Route that returns the description of the indicated algorithm
@app.route('/api/algorithm_description/<algorithm>')
def get_algorithm_description(algorithm):
    module = ALGORITHM_MODULES.get(algorithm)
    if module and "description" in module:
        return jsonify(module["description"])

    return jsonify({"text": "Description not available.", "links": []})


# Route that returns the requirements of the indicated algorithm
@app.route('/api/algorithm_requirements/<algorithm>/<operation>', methods=['GET'])
def get_algorithm_requirements(algorithm, operation):
    try:
        # Check if the requested algorithm exists
        if algorithm not in ALGORITHM_MODULES:
            return jsonify({"error": "Algorithm not found"}), 404

        # Retrieve the algorithm's requirements
        requirements = ALGORITHM_MODULES[algorithm].get("requirements", {})

        # Check if the requested operation (encryption/decryption) exists
        if operation not in requirements:
            return jsonify({"error": "Invalid operation"}), 400

        # Extract the required number of input images and parameters
        operation_requirements = requirements[operation]
        num_images = operation_requirements.get("num_images", 1)
        parameters = operation_requirements.get("parameters", {})

        # Return the JSON response
        return jsonify({
            "num_images": num_images,
            "parameters": parameters
        })

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500


# Process the selected operation
@app.route('/process', methods=['POST'])
def process():
    try:
        operation = request.form['operation']
        algorithm = request.form['algorithm']

        # Retrieve the algorithm module
        algorithm_module = ALGORITHM_MODULES.get(algorithm)
        if not algorithm_module:
            error_message = f"Unknown algorithm: {algorithm}"
            return render_template('error.html', error_message=error_message), 500

        # Retrieve algorithm requirements for the operation
        requirements = algorithm_module.get("requirements", {}).get(operation, {})
        num_images = requirements.get("num_images", 1)
        parameters = requirements.get("parameters", {})

        # Dynamically retrieve uploaded images based on num_images
        input_paths = []
        for i in range(1, num_images + 1):
            file = request.files.get(f"image{i}")
            if file and file.filename:
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(save_path)
                input_paths.append(save_path)

        # Ensure correct number of images
        if len(input_paths) != num_images:
            error_message = f"{operation.capitalize()} requires {num_images} image(s), but {len(input_paths)} provided."
            return render_template('error.html', error_message=error_message), 500

        # Open images
        images = [Image.open(path).convert(algorithm_module.get("image_type")) for path in input_paths]

        # Extract additional parameters from the form
        param_values = {}
        for param_key, param_config in parameters.items():
            if param_config["type"] == "number":
                param_values[param_key] = int(request.form.get(param_key, param_config.get("default", 0)))
            elif param_config["type"] == "select":
                param_values[param_key] = request.form.get(param_key, param_config.get("default"))
            # Here it is possible to add other types of requirements for new schemes

        # Call the appropriate method dynamically
        if operation == "encryption":
            encrypt_method = algorithm_module.get("encrypt")
            result = encrypt_method(*images, *param_values.values())  # Pass images first, then only parameter values
            return save_and_render_shares(*result, extension=algorithm_module.get("extension"))

        elif operation == "decryption":
            decrypt_method = algorithm_module.get("decrypt")
            result = decrypt_method(*images, *param_values.values())  # Pass images first, then only parameter values
            return save_and_render_decryption_result(result, algorithm_module.get("extension"))

    except Exception as e:
        error_message = str(e)
        return render_template('error.html', error_message=error_message), 500


def save_and_render_shares(*shares, extension, output_folder='output'):
    share_urls = []
    download_urls = []

    for i, share in enumerate(shares, start=1):
        filename = f"share{i}.{extension}"
        share_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)

        # Save shares
        share.save(share_path)

        # Generate URLs for rendering and downloading
        share_urls.append(url_for('static', filename=f'{output_folder}/{filename}'))
        download_urls.append(url_for('static', filename=f'{output_folder}/{filename}'))

    # Render results dynamically. This rendering handles the case where more than 2 shares are generated.
    return render_template(
        'enc_result.html',
        share_urls=share_urls,
        download_urls=download_urls,
        zip=zip  # For using zip in the loop of enc_result.html
    )


# Helper function to handle decryption and rendering results
def save_and_render_decryption_result(result_image, extension, output_folder='output'):
    result_path = os.path.join(app.config['OUTPUT_FOLDER'], f'decrypted.{extension}')
    result_image.save(result_path)

    # Render results
    return render_template(
        'dec_result.html',
        result_url=url_for('static', filename=f'{output_folder}/decrypted.{extension}'),
        result_download=url_for('static', filename=f'{output_folder}/decrypted.{extension}')
    )


if __name__ == '__main__':
    app.run(debug=True)
