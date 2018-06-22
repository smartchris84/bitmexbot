from flask import Flask, jsonify, make_response
from db import trade

app = Flask(__name__)


@app.route('/api/trade', methods=['GET'])
def get_trade():
    trade_info = trade.read()
    return jsonify({'result': trade_info})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'result': False}), 404)


if __name__ == '__main__':
    app.run(debug=True)
