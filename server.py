import base64
import datetime
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, url_for
from matplotlib import pyplot as plt


app = Flask(__name__)

soup = BeautifulSoup(requests.get("https://www.pogoda.msk.ru/").content, 'html.parser')
table = soup.findAll('table')[6]
status = table.find("tr").find('th', {"id":"dt"})
data = {}
for row in table.findAll("tr"):
  if row.has_attr('class'):
   if status.text != row.find('th', {"id":"dt"}).text:
      status = row.find('th', {"id":"dt"})
  if row.has_attr('valign'):
    if status.text[:5] not in data:
      data[status.text[:5]] = []
    row_data = row.findAll('td')
    data[status.text[:5]].append(dict(
        temp=list(map(int, row_data[2].text.split('..'))),
        davl=int(row_data[3].text.strip('%'))
    ))

@app.route("/", methods=['POST', 'GET'])
def main_page():
    return render_template('home.html', dates = list(data))


@app.route("/aboutus", methods=['POST', 'GET'])
def aboutus():
    return render_template('about.html')


@app.route("/result", methods=['POST'])
def result():
    type_name = ["Утро", "День", "Вечер", "Ночь"]
    dt = request.form['start_date']
    
    max_list = {}
    full_list = {}
    for day in list(data):
      for block in data[day]:
        if day not in max_list:
          max_list[day] = []
        if day not in full_list:
          full_list[day] = []
        max_list[day].append(max(block['temp']))
        for i in block['temp']:
          full_list[day].append(i)

    temp_max_list = []
    keys = []
    for day in list(max_list):
      for i, temp in enumerate(max_list[day]):
        temp_max_list.append(temp)
        keys.append(day + f'({type_name[len(type_name)-len(max_list[day])+i]})')
    
    fig, ax = plt.subplots()
    ax.plot(keys, temp_max_list)
    ax.set_xticklabels(keys, rotation=-45, fontsize=6)
    ax.set_ylabel('max temp')
    ax.set_xlabel('Дни(<периоды>)')
    ax.grid()
    buf = BytesIO()
    fig.savefig(buf, format='png')
    image = base64.b64encode(buf.getbuffer()).decode('ascii')
    
    return render_template("result.html", day=dt, image = image, max=max(full_list[dt]), min=min(full_list[dt]), avg=sum(full_list[dt])/len(full_list[dt]))


if __name__ == '__main__':
    app.run(debug=True)