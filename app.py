from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Enable CORS (after app initialization)
CORS(app)

# Load and preprocess the dataset
file_path = "cleaned_Ndataset.csv"  # Replace with your dataset path
try:
    data = pd.read_csv(file_path)
except FileNotFoundError:
    raise FileNotFoundError(f"Dataset not found at {file_path}. Please check the file path.")

# Ensure 'Area Locality' column exists and preprocess it
if 'Area Locality' not in data.columns:
    raise ValueError("The dataset must contain an 'Area Locality' column.")

# Standardize 'Area Locality' to lowercase and strip spaces
data['Area Locality'] = data['Area Locality'].fillna('Unknown').str.lower().str.strip()

# Recommendation function with exact matching
def recommend_houses(user_location):
    user_location = user_location.lower().strip()
    matched_data = data[data['Area Locality'] == user_location]

    # Check if there are matches
    if matched_data.empty:
        return None
    return matched_data

# Home route to display input form
@app.route('/')
def home():
    return render_template('index.html')
 # Create this page if needed


# Route to handle recommendations based on user input
@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Check for JSON payload or form data
        if request.is_json:
            user_location = request.json.get('location', '').strip()
        else:
            user_location = request.form.get('location', '').strip()

        # Ensure location is provided
        if not user_location:
            return jsonify({"message": "Location is required."}), 400

        # Get recommendations
        recommendations = recommend_houses(user_location)

        if recommendations is not None and not recommendations.empty:
            # Select relevant columns for the response
            houses = recommendations[['Area Locality', 'Tenant Preferred', 'Rent', 'Point of Contact', 'phone number']].to_dict(orient='records')
            return jsonify(houses)
        else:
            return jsonify({"message": "No houses found for the given location."}), 404

    except Exception as e:
        # Catch and return any unexpected errors
        return jsonify({"message": "An error occurred.", "error": str(e)}), 500

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
