
from flask import Flask, render_template, request, jsonify
import requests
import logging

app = Flask(__name__)

# Set up your APIM endpoint
APIM_ENDPOINT = "https://s4-appointment-apim.azure-api.net/s4-apis/appointment/new"

logging.basicConfig(level=logging.DEBUG)


@app.route('/')
def home():
    return render_template('form.html')  # Render the HTML form

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        logging.info(f"Received data: {data}")

        # Validate input
        if not all([data.get('name'), data.get('email'), data.get('uname'), data.get('appointmentDate')]):
            return jsonify({'message': 'All fields are required'}), 400

        headers = {
            'Content-Type': 'application/json',
        }

        # Send request to the external API
        response = requests.post(APIM_ENDPOINT, json=data, headers=headers)

        # Log the response from the external API
        logging.info(f"Response from APIM: {response.status_code} - {response.text}")

        # Check the content type of the response
        if response.status_code == 200:
            if response.headers.get('Content-Type') == 'application/json':
                try:
                    response_data = response.json()  # Attempt to parse JSON
                    return jsonify({'message': 'Appointment submitted successfully!', 'details': response_data}), 200
                except ValueError:
                    logging.error(f"Unexpected response format (JSON parsing failed): {response.text}")
                    return jsonify({'message': 'Unexpected response format', 'details': response.text}), 500
            else:
                # Handle plain text response
                logging.info("Received plain text response from APIM.")
                return jsonify({'message': 'Appointment submitted successfully!', 'details': response.text}), 200
        else:
            # Handle error responses
            logging.error(f"Failed to submit appointment, status code: {response.status_code}, details: {response.text}")
            return jsonify({'message': 'Failed to submit appointment', 'status_code': response.status_code, 'details': response.text}), response.status_code

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)