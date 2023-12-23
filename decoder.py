import datetime
import json
from typing import Optional

import requests
from bs4 import BeautifulSoup
class Lesson:
    def __init__(self, name="", teachers=[], text="", t_start=datetime.datetime(1,1,1), t_end=datetime.datetime(1,1,1)):
        self.name = name
        self.teacher = teachers
        self.text = text
        self.t_start = t_start
        self.delay = (t_end - t_start).total_seconds()
class Tibox:
    class OrderBy:
        TEACHERS = "TEACHERS"
        DAYS = "DAYS"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.google.com/',  # Replace with the actual referer
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers',
    }
    def __init__(self):
        self.siteMap = {
            "login": lambda x=1702475616: "https://tibox.tk/notauth",
            "now": lambda x=1702475616: "http://tibox.tk/now",
            "timetable": lambda x=1702475616: f"https://tibox.tk/box?time={x}"
        }
        self.reqSes = requests.Session()
        self.get_ticket()

    @property
    def cookies(self):
        return self.reqSes.cookies.get_dict()

    def get_ticket(self):
        data = self.reqSes.post(
            self.siteMap['login'](),
            data=dict(institute=3, group=11, submit=""),
            headers=self.headers
        )

    def get_lessons(self, dt= None):
        result = []
        
        if dt: dt = int(dt.timestamp())

        page = BeautifulSoup(self.reqSes.get(
            self.siteMap['timetable' if dt else 'now'](dt),
            headers=self.headers
        ).content, "html.parser").find("div", {"class": "timetableBox"})

        parsed_data = page.findAll("div", {"class": "lesson"})
        if dt:
          if datetime.datetime.fromtimestamp(dt).month != 1:
            for item in parsed_data:
                item_full = page.find(
                    "div",
                    {
                        "id": item.find('a').get('data-src').strip('#')
                    }
                )
                result.append(Lesson(
                    name=item.find("p", {"id":"TextOne"}).text.split("(")[0],
                    t_start=datetime.datetime.strptime(item.find("div", {"id":"time"}).text.split("-")[0], "%H:%M"),
                    t_end=datetime.datetime.strptime(item.find("div", {"id":"time"}).text.split("-")[1], "%H:%M"),
                    teachers=item_full.find("span").text.strip("Профессора ").strip("Профессор ").split(", "),
                    text=item_full.find("p", {"id":"info"}).text
                ))
        return result

    def make_stat(self, dt_start: datetime.datetime, order_by: str = OrderBy.TEACHERS, days: int = 14):
        data = {}
        for i in range(days):
            dtPoint = dt_start + datetime.timedelta(days=i)
            data[dtPoint] = self.get_lessons(dtPoint)

        stat_data = {}
        if order_by == self.OrderBy.TEACHERS:
            for day in data:
                for lesson in data[day]:
                    for teacher in lesson.teacher:
                        if teacher not in stat_data: stat_data[teacher] = 0
                        stat_data[teacher] += lesson.delay
        elif order_by == self.OrderBy.DAYS:
            for day in data:
                for lesson in data[day]:
                    if day.strftime("%Y-%m-%d") not in stat_data: stat_data[day.strftime("%Y-%m-%d")] = 0
                    stat_data[day.strftime("%Y-%m-%d")] += lesson.delay
        return stat_data


