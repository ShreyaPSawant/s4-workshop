from flask import Flask, render_template, request, jsonify
import requests
import logging

app = Flask(__name__)

# Set up your APIM endpoints
APIM_APPOINTMENT_ENDPOINT = "https://s4-appointment-apim.azure-api.net/s4-apis/appointment/new"
APIM_AVAILABLE_DATES_ENDPOINT = "https://s4-appointment-apim.azure-api.net/s4-apis;rev=2/appointment/available-dates"

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
        response = requests.post(APIM_APPOINTMENT_ENDPOINT, json=data, headers=headers)

        # Log the response from the external API
        logging.info(f"Response from APIM: {response.status_code} - {response.text}")

        if response.status_code == 200:
            return jsonify({'message': 'Appointment submitted successfully!'}), 200
        else:
            return jsonify({'message': 'Failed to submit appointment', 'details': response.text}), response.status_code

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@app.route('/api/available-dates', methods=['GET'])
def get_available_dates():
    try:
        # Fetch the available dates from the external API
        response = requests.get(APIM_AVAILABLE_DATES_ENDPOINT)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'message': 'Failed to fetch available dates', 'details': response.text}), response.status_code

    except Exception as e:
        logging.error(f"Error occurred while fetching available dates: {str(e)}")
        return jsonify({'message': 'An error occurred while fetching available dates', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
