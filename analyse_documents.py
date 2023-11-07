from bs4 import BeautifulSoup
from janome.tokenizer import Tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
import json
from tqdm import tqdm

# csvからメタデータを読み込む
df = pd.read_csv('successful_downloads.csv')

# janomeトークナイザーの準備
t = Tokenizer()

# 解析済みの文書を格納するリスト
analyzed_documents = []

# ストップワード辞書を読み込む関数
def load_stopwords(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        stopwords = [line.strip() for line in file]
    return set(stopwords)

stopwords = load_stopwords("./stopword.txt")

# 生データから指定したdivタグを抽出する関数
def extract_main_text(text):
    soup = BeautifulSoup(text, 'html.parser')

    # "main_text" クラスを持つdivタグを抽出
    main_text_div = soup.find("div", class_="main_text")

    # divタグが見つかった場合、その中のテキストを取得
    if main_text_div:
        main_text = main_text_div.get_text()
    else:
        main_text = text  # "main_text" クラスのdivタグが見つからない場合は元のテキストを使用

    return main_text

# 形態素解析、不要語削除、品詞フィルタリングを一度に行う関数
def analyze_text(text, stopwords, tokenizer):
    tokens = tokenizer.tokenize(text)
    cleaned_tokens = [token for token in tokens if token.surface not in stopwords]
    stemmed_tokens = [token.base_form for token in cleaned_tokens if token.part_of_speech.split(',')[0] in ['名詞', '形容詞', '動詞']]
    return stemmed_tokens

# tqdmでプログレスバーを表示
with tqdm(total=df.shape[0]) as pbar:
    # すべてのテキストファイルについて処理
    for index, row in tqdm(df.iterrows()):
        # テキストファイルを読み込む
        with open(f"./database/{row['作品ID']}.txt", 'r', encoding='shift_jis', errors='ignore') as f:
            text = f.read()

        # 本文以外の部分を削除
        cleaned_text = extract_main_text(text)

        # 形態素解析、不要語削除、品詞フィルタリング
        words = analyze_text(cleaned_text, stopwords, t)

        # 抽出した単語リストを解析済み文書リストに追加
        analyzed_documents.append(words)

        # プログレスバーを更新
        pbar.update(1)
# 解析結果をJSONファイルに保存
with open('analyzed_documents.json', 'w', encoding='utf-8') as file:
    json.dump(analyzed_documents, file, ensure_ascii=False, indent=4)
