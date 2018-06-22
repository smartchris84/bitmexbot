import os
import flask
from time import sleep
from flask import Flask, render_template
from db import configs

app = Flask(__name__)


# region Methods


def get_logs():
    res = ""
    path__logs = '../bot/logs.log'
    if os.path.isfile(path__logs):  # returns whether the file exists or not
        f = open(path__logs)
        for line in f:
            res += line + ' '
    else:
        return 'There is no logs yet'
    return res


@app.route('/')
def show_index():
    current_timeframe = configs.read()['TIMEFRAME']
    return render_template('index.html', configs=configs.read(), current_timeframe=current_timeframe)


@app.route('/logs')
def show_logs():
    return render_template('logs.html', logs=get_logs())


@app.route('/start', methods=['POST'])
def start():
    tp = flask.request.form['tp_config']
    if tp == 'None':
        tp = 0
    sl = flask.request.form['sl_config']
    if sl == 'None':
        sl = 0

    configs.update(True, percent_to_trade=flask.request.form['volume_config'],
                   timeframe=flask.request.form['timeframe_config'],
                   leverage=flask.request.form['leverage_config'],
                   sl_percent=sl, tp_percent=tp,
                   rsi_top=flask.request.form['rsi_top_config'], rsi_bot=flask.request.form['rsi_bot_config']
                   )
    return flask.redirect(flask.url_for('show_index'))


@app.route('/change-keys', methods=['POST'])
def change_keys():
    configs.update(api_key=flask.request.form['BitmexAPIKey'], api_secret=flask.request.form['BitmexAPISecert'])
    return flask.redirect(flask.url_for('show_index'))


@app.route('/stop', methods=['GET'])
def stop():
    configs.update(is_running=False, updated=False)
    sleep(5)
    return flask.redirect(flask.url_for('show_index'))


@app.route('/clear-logs', methods=['GET'])
def clear_logs():
    path__logs = '../bot/logs.log'
    if os.path.isfile(path__logs):  # returns whether the file exists or not
        open(path__logs, 'w').close()
    return flask.redirect(flask.url_for('show_index'))


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
