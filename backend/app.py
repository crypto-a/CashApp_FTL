from flask import Flask, jsonify, request
from flask_cors import CORS
from data_formatter import DataFormatter
from data_reader import DataReader
from model_interactor import ModelInteractor

app = Flask('app')
CORS(app)
women_bias_data = DataReader('women_bias_data.csv').read_dataset()


# Example of an endpoint that returns test data
@app.route('/getinfo')
def getinfo():
    info = {"name":'breaking bias', "score":"stupendous"}
    return jsonify(info)


@app.route('/getPastData', methods=['POST'])
def get_past_data():
    filter_gender = request.get_json()['filtering_factor']

    past_data = (DataFormatter(women_bias_data)
                 .filter_by(filter_gender)
                 .filter_invalid_transactions()
                 .get_for_display())

    return jsonify(past_data)


@app.route('/predictData', methods=['POST'])
def predict_values():
    filter_gender = request.get_json()['filtering_factor']
    forecast_steps = request.get_json()['num_points']
    training_data = (DataFormatter(women_bias_data)
                     .filter_by(filter_gender)
                     .filter_invalid_transactions()
                     .get_for_predicting())

    return_data = ModelInteractor(training_data).execute(forecast_steps)
    return jsonify(return_data)


@app.route('/getPastDataUnbiased', methods=['POST'])
def get_past_data_unbiased():
    filter_gender = request.get_json()['filtering_factor']

    past_data = (DataFormatter(women_bias_data)
                 .filter_by(filter_gender)
                 .unbias()
                 .filter_invalid_transactions()
                 .get_for_display())

    return jsonify(past_data)


@app.route('/predictDataUnbiased', methods=['POST'])
def predict_values_unbiased():
    filter_gender = request.get_json()['filtering_factor']
    forecast_steps = request.get_json()['num_points']
    training_data = (DataFormatter(women_bias_data)
                     .filter_by(filter_gender)
                     .unbias()
                     .filter_invalid_transactions()
                     .get_for_predicting())

    return_data = ModelInteractor(training_data).execute(forecast_steps)
    return jsonify(return_data)


if __name__ == '__main__':
    app.run()
