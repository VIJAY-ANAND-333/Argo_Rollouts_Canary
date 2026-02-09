from flask import Flask, render_template, jsonify, request
from connection import add_datas
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Common metrics (optional)
metrics.info('app_info', 'Application info', version='1.0.0')

mods = [
    {"id": 1, "name": "Spoiler", "price": 100000},
    {"id": 2, "name": "interier light uh", "price": 700000},
    {"id": 3, "name": "CF Hood", "price": 950000},
    {"id": 4, "name": "Exhaust", "price": 5105110}
]


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/services')
def services():
    data = list(add_datas.find())
    return render_template('services.html', mods=mods + data)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/modifications', methods=['POST', 'GET'])
def modifications():
    if request.method == 'POST':
        new_mods = request.json
        data = list(add_datas.find())
        new_mods['id'] = len(data) + len(mods) + 1
        add_datas.insert_one(new_mods)
        return f"Successfully added the item {request.json.get('name')}"
    return jsonify(mods + list(add_datas.find({}, {'_id': 0})))


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=9000)
