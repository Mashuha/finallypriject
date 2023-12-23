import base64
import datetime
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, url_for
from matplotlib import pyplot as plt


app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def main_page():
 
    return render_template('home.html')


@app.route("/aboutus", methods=['POST', 'GET'])
def aboutus():
    return render_template('aboutus.html')


@app.route("/result", methods=['POST'])
def result():
    # ax.set_xticks(keys)
    # ax.set_xticklabels(keys, rotation=-45, fontsize=6)
    # ax.set_ylabel('Кол-во часов')
    # ax.set_xlabel('Преподаватели' if orderBy == Tibox.OrderBy.TEACHERS else 'Даты')
    # ax.grid()
    # buf = BytesIO()
    # fig.savefig(buf, format='png')
    # data = base64.b64encode(buf.getbuffer()).decode('ascii')

    return render_template("result.html")


if __name__ == '__main__':
    app.run(debug=True)