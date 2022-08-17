from retry import retry
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

# 家賃3万以下、ワンルーム以外、安い順
base_url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/{}&cb=0.0&ct=3.0&mb=0&mt=9999999&md=02&md=03&md=04&md=05&md=06&et=9999999&cn=9999999&co=1&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=12&page={}"
json_open = open('areas.json', 'r')
locate_and_areas = json.load(json_open)

@retry(tries=3, delay=10, backoff=2)
def get_html(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup
 
all_data = []
max_page = 3

for locate_and_area in locate_and_areas:
    for page in range(1, max_page+1):
        area = locate_and_area['areas']
        location = locate_and_area['location']
        url = base_url.format(area, page)

        soup = get_html(url)

        items = soup.findAll("div", {"class": "cassetteitem"})
        print(location, "page", page, "items", len(items))

        for item in items:
            base_data = {}

            # collect base information    
            base_data["名称"] = item.find("div", {"class": "cassetteitem_content-title"}).getText().strip()
            # base_data["カテゴリー"] = item.find("div", {"class": "cassetteitem_content-label"}).getText().strip()
            # base_data["アドレス"] = item.find("li", {"class": "cassetteitem_detail-col1"}).getText().strip()
            # base_data["アクセス"] = station.getText().strip()
            # base_data["築年数"] = item.find("li", {"class": "cassetteitem_detail-col3"}).findAll("div")[0].getText().strip()
            # base_data["構造"] = item.find("li", {"class": "cassetteitem_detail-col3"}).findAll("div")[1].getText().strip()

            # process for each room
            tbodys = item.find("table", {"class": "cassetteitem_other"}).findAll("tbody")

            for tbody in tbodys:
                data = base_data.copy()

                data["階数"] = tbody.findAll("td")[2].getText().strip()

                data["家賃"] = tbody.findAll("td")[3].findAll("li")[0].getText().strip()
                data["管理費"] = tbody.findAll("td")[3].findAll("li")[1].getText().strip()

                # data["敷金"] = tbody.findAll("td")[4].findAll("li")[0].getText().strip()
                # data["礼金"] = tbody.findAll("td")[4].findAll("li")[1].getText().strip()

                data["間取り"] = tbody.findAll("td")[5].findAll("li")[0].getText().strip()
                data["面積"] = tbody.findAll("td")[5].findAll("li")[1].getText().strip()

                data["URL"] = "https://suumo.jp" + tbody.findAll("td")[8].find("a").get("href")

                all_data.append(data)    
    
# convert to dataframe
df = pd.DataFrame(all_data)
df.to_csv("tokyo_23words_raw_data.csv")