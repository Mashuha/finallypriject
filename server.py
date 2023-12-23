import base64
import datetime
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, url_for
from matplotlib import pyplot as plt
from decoder import Tibox

app = Flask(__name__)

t = Tibox()

@app.route("/", methods=['POST', 'GET'])
def main_page():
    lessons = [lesson.name for lesson in t.get_lessons()]
    det = BeautifulSoup(t.reqSes.get("http://mpgu.su/ob-mpgu/struktura/faculties/matematicheskiy-fakultet/").content, "html.parser")
    det = det.find("div", {"class":"news"})
    if len(lessons) == 0:
        lessons = ["А их неть! (^_^)"]
    
    return render_template('home.html', lessons_tip=lessons, news=[i.text for i in det.findAll("a", {"class":"big-link"})])


@app.route("/aboutus", methods=['POST', 'GET'])
def aboutus():
    return render_template('aboutus.html')


@app.route("/result", methods=['POST'])
def result():
    points = []
    print(request.form)
    dt_start = datetime.datetime.strptime(request.form.get('start_date'), "%Y-%m-%d")
    orderBy = request.form.get('OrderBy')
    
    stat = t.make_stat(dt_start, orderBy)
    stat = {i:round(stat[i]/3600, 3) for i in list(stat)}
    values = list(stat.values())
    keys = list(map(lambda x: x.split()[0], list(stat)))

    fig, ax = plt.subplots()
    if orderBy == Tibox.OrderBy.TEACHERS:
        ax.bar(keys, values)
    elif orderBy == Tibox.OrderBy.DAYS:
        ax.hist(keys, bins=len(keys), weights=values)
    
    get_result = lambda x: (next(name for name in list(stat) if stat[name] == x), x)

    ax.set_xticks(keys)
    ax.set_xticklabels(keys, rotation=-45, fontsize=6)
    ax.set_ylabel('Кол-во часов')
    ax.set_xlabel('Преподаватели' if orderBy == Tibox.OrderBy.TEACHERS else 'Даты')
    ax.grid()
    buf = BytesIO()
    fig.savefig(buf, format='png')
    data = base64.b64encode(buf.getbuffer()).decode('ascii')

    return render_template("result.html", list_stat=keys, max=get_result(max(values)), avg=sum(values)/(len(values)+1), min=get_result(min(values)), type_time="ч", stat=stat, picture=data)


if __name__ == '__main__':
    app.run(debug=True)