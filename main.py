from flask import Flask, render_template, request, redirect, url_for,jsonify
from flask_pymongo import PyMongo
import json
from collections import Counter
from urllib.parse import urlencode, quote_plus, parse_qsl

app = Flask(__name__, static_folder="public", static_url_path="/public")

app.config['MONGO_URI'] = 'mongodb://localhost:27017/Hospital'
mongo = PyMongo(app)


def extract(query):
    patients = mongo.db.Patient.find(query)
    return patients


@app.route('/')
def main():
    return render_template("index.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/home')
def home():
    # Sex Chart
    sex = {'male': len(list(extract({'sex': 'M'}))),
           'female': len(list(extract({'sex': 'F'})))}

    # Age Chart
    ages = [doc['age'] for doc in extract({'age': {'$exists': True}})]
    age_ranges = [(20, 30), (31, 40), (41, 50), (51, 60), (61, 70), (71, 80)]
    age_range_counter = Counter()
    for age in ages:
        for range_start, range_end in age_ranges:
            if range_start <= age <= range_end:
                age_range_counter[(range_start, range_end)] += 1
    age_range_data = [{'range': f'{start}-{end}', 'count': count} for (start, end), count in age_range_counter.items()]

    # Smoker Chart
    smoker = {'Smoker': len(list(extract({'smoker': 'yes'}))),
           'Non-Smoker': len(list(extract({'smoker': 'no'})))}

    # Diabetes Chart
    diabetes = {'Diabetec': len(list(extract({'diabetes': 'yes'}))),
           'Non-Diabetec': len(list(extract({'diabetes': 'no'})))}
    
    return render_template("home.html", sex_data=sex,age_range_data=age_range_data,smoker_data=smoker,diabetes_data=diabetes)


@app.route('/patient', methods=['POST'])
def post_patient():
    id = request.form.get('id')
    patient_data = mongo.db.Patient.find_one({'id': int(id)})
    del patient_data['_id']
    del patient_data['']
    # encoded_data = urlencode({'patient_data': patient_data}, quote_via=quote_plus)
    data = {'patient_data': patient_data}
    return redirect(url_for('get_patient', data=json.dumps(data)))
    # return redirect(url_for('get_patient', data=encoded_data))

@app.route('/patient', methods=['GET'])
def get_patient():
    data_received = request.args.get('data')
    data_received = json.loads(data_received)
    # decoded_data = dict(parse_qsl(data_received))
    print(data_received)
    print(type(data_received))
    return render_template('patient.html', data=data_received)
    


if __name__ == "__main__":
    app.run(debug=True)
