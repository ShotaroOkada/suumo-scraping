from retry import retry
import requests
from bs4 import BeautifulSoup
import json
import time

max_page = 30
count_per_page = 30

all_room_data_list = []
json_open = open('areas.json', 'r')
area_label_and_params_list = json.load(json_open)

# 安い順
def search_url(
        area_params, # 市区町村のパラメータ
        include_one_room = False, # ワンルームを含めるか
        include_1K = False, # 1Kを含めるか
        include_1DK = False, # 1DKを含めるか
        include_1LDK = False, # 1LDKを含めるか
        include_2K = False, # 2Kを含めるか
        include_2DK = False, # 2DKを含めるか
        include_2LDK = True, # 2LDKを含めるか
        include_3K = False, # 3Kを含めるか
        include_3DK = False, # 3DKを含めるか
        include_3LDK = False, # 3LDKを含めるか
        is_only_1st_floor = True, # 1階の物件に限定するか
        max_rent = 3.5, # 家賃の上限（万円）
        min_room_size = 35, # 部屋の広さの下限（m^2）
        page = 1,
    ):
    only_1st_floor = "&tc=0400105" if is_only_1st_floor else ""
    one_room = "&md=01" if include_one_room else ""
    one_K = "&md=02" if include_1K else ""
    one_DK = "&md=03" if include_1DK else ""
    one_LDK = "&md=04" if include_1LDK else ""
    two_K = "&md=05" if include_2K else ""
    two_DK = "&md=06" if include_2DK else ""
    two_LDK = "&md=07" if include_2LDK else ""
    three_K = "&md=08" if include_3K else ""
    three_DK = "&md=09" if include_3DK else ""
    three_LDK = "&md=10" if include_3LDK else ""
    return f"https://suumo.jp/jj/chintai/ichiran/FR301FC001/?{area_params}{only_1st_floor}&cb=0.0&ct={max_rent}&mb={min_room_size}&mt=9999999{one_room}{one_K}{one_DK}{one_LDK}{two_K}{two_DK}{two_LDK}{three_K}{three_DK}{three_LDK}&et=9999999&cn=9999999&co=1&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=12&page={page}"

@retry(tries=3, delay=10, backoff=2)
def get_html(url):
    time.sleep(1) # アクセス過多対策
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup

for label_and_params in area_label_and_params_list:
    for page in range(1, max_page+1):
        area_params = label_and_params['area_params']
        area_label = label_and_params['area_label']
        url = search_url(area_params, page)

        soup = get_html(url)

        building_cards = soup.findAll("div", {"class": "cassetteitem"})
        print(area_label, "page", page, "該当件数", len(building_cards))
        if len(building_cards) == 0:
            break

        for item in building_cards:
            building_data = {}
 
            # building_data["名称"] = item.find("div", {"class": "cassetteitem_content-title"}).getText().strip()
            # building_data["カテゴリー"] = item.find("div", {"class": "cassetteitem_content-label"}).getText().strip()
            building_data["アドレス"] = item.find("li", {"class": "cassetteitem_detail-col1"}).getText().strip()
            # building_data["アクセス"] = station.getText().strip()
            # building_data["築年数"] = item.find("li", {"class": "cassetteitem_detail-col3"}).findAll("div")[0].getText().strip()
            # building_data["構造"] = item.find("li", {"class": "cassetteitem_detail-col3"}).findAll("div")[1].getText().strip()

            rooms_table = item.find("table", {"class": "cassetteitem_other"}).findAll("tbody")

            for room_table_row in rooms_table:
                room_data = building_data.copy()
                td_list = room_table_row.findAll("td")

                room_data["間取り画像URL"] = td_list[1].findAll("img")[0].get("rel")

                # スプシで画像を表示する用の列
                room_data["=ARRAYFORMULA(IMAGE(B1:B))"] = ""

                room_data["suumoリンク"] = "https://suumo.jp" + td_list[8].find("a").get("href")

                room_data["家賃（万円）"] = td_list[3].findAll("li")[0].getText().strip().replace("万円", "")
                room_data["管理費"] = td_list[3].findAll("li")[1].getText().strip()

                # room_data["階数"] = td_list[2].getText().strip()
                # room_data["敷金"] = td_list[4].findAll("li")[0].getText().strip()
                # room_data["礼金"] = td_list[4].findAll("li")[1].getText().strip()
                room_data["間取り"] = td_list[5].findAll("li")[0].getText().strip()
                room_data["面積"] = td_list[5].findAll("li")[1].getText().strip()

                # 間取り画像URLに被りがなければ追加
                if not any(d["間取り画像URL"] == room_data["間取り画像URL"] for d in all_room_data_list):
                    all_room_data_list.append(room_data)

        if len(building_cards) < count_per_page:
            break

timestamp = time.strftime("%Y%m%d%H%M%S")
with open(f"suumo_data_{timestamp}.csv", 'w', encoding='utf-8') as f:
    keys = list(all_room_data_list[0].keys())
    f.write(",".join(keys) + "\n")
    for data in all_room_data_list:
        f.write(",".join([data[key] for key in keys]) + "\n")
