import pandas as pd
import requests
from bs4 import BeautifulSoup
import random
import time
import urllib.parse
import os

# CSVファイルからデータを読み込む
df = pd.read_csv('/home/tsuneda/data_dl/情報検索特論課題1/list_person_all_utf8.csv')

success_count = 0  # 成功したダウンロードの数

# 成功したダウンロードのデータフレームを作成
success_df = pd.DataFrame(columns=df.columns)

# データフレーム全体をループ（ランダムに選ぶためにシャッフル）
for index, row in df.sample(frac=1).iterrows():
    if success_count >= 2000:  # 2000件ダウンロードしたら終了
        break

    person_id = str(row['人物ID']).zfill(6)  # 6桁になるように0を追加
    work_id = row['作品ID']

    # 作品のカードURLを生成
    card_url = f"https://www.aozora.gr.jp/cards/{person_id}/card{work_id}.html"
    response = requests.get(card_url)
    response.encoding = 'utf-8'

    if response.status_code != 200:
        print(f"Failed to access card for work {work_id}")
        continue

    # 404 Not Foundの場合を除外
    soup = BeautifulSoup(response.text, 'html.parser')
    title_tag = soup.find('title')
    if title_tag and '404 Not Found' in title_tag.string:
        print(f"404 Not Found for work {work_id}")
        continue

    # 「いますぐXHTML版で読む」のリンクを取得
    xhtml_tag = soup.find('a', string='いますぐXHTML版で読む')
    if xhtml_tag is not None:
        xhtml_link = xhtml_tag['href']

        # 相対リンクを絶対URLに変換
        xhtml_url = urllib.parse.urljoin(card_url, xhtml_link)

        # 作品をダウンロード
        response = requests.get(xhtml_url)
        if response.status_code == 200:
            save_path = os.path.join('./database', f"{work_id}.txt")
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded work {work_id} in HTML format to ./database/")
            success_count += 1  # 成功したダウンロードの数を増やす

            # 成功したダウンロードのデータを保存
            success_df = pd.concat([success_df, row.to_frame().T], ignore_index=True
            )
        else:
            print(f"Failed to download work {work_id}")
    else:
        print(f"Could not find 'いますぐXHTML版で読む' link for work {work_id}")

    time.sleep(1)  # サーバーに負荷をかけないように1秒待つ


# 成功したダウンロードのデータフレームをCSVとして出力
success_df.to_csv('successful_downloads.csv', index=False)
