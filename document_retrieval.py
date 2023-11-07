from bs4 import BeautifulSoup
from janome.tokenizer import Tokenizer
import pandas as pd
import numpy as np
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tkinter as tk
from tkinter import ttk
import webbrowser

# csvからメタデータを読み込む
df = pd.read_csv('successful_downloads.csv')
# 解析済み文書を読み込む
with open('analyzed_documents2.json', 'r', encoding='utf-8') as file:
    analyzed_documents = json.load(file)

# GUI for keyword input and showing results
class DocumentRetrievalApp:
    def __init__(self, master):
        self.master = master
        self.master.title("文書検索アプリ")

        # Keyword Entry
        self.label1 = tk.Label(self.master, text="キーワードを入力: ")
        self.label1.grid(row=0, column=0)
        self.entry1 = tk.Entry(self.master)
        self.entry1.grid(row=0, column=1)

        # Search Button
        self.button1 = tk.Button(self.master, text="検索", command=self.search_documents)
        self.button1.grid(row=0, column=2)

        # Results Display
        self.tree = ttk.Treeview(self.master, columns=("Rank", "著者名", "作品名", "URL", "類似度"))
        self.tree.grid(row=1, column=0, columnspan=4)
        self.tree.heading("#1", text="ランク")
        self.tree.heading("#2", text="著者名")
        self.tree.heading("#3", text="作品名")
        self.tree.heading("#4", text="URL")
        self.tree.heading("#5", text="類似度")

    def open_url(self, event):
        # Handle URL click event
        item = self.tree.selection()[0]
        url = self.tree.item(item, "values")[3] 
        webbrowser.open_new(url)

    def search_documents(self):
        keywords = self.entry1.get().split(',')
        keywords = [kw.strip() for kw in keywords if kw.strip()]
        if not keywords:
            return

        document_strings = [' '.join(doc) for doc in analyzed_documents.values()]
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(document_strings)
        print(tfidf_matrix.shape)
        keyword_vector = tfidf_vectorizer.transform(keywords)
        print(keyword_vector)
        similarities = cosine_similarity(tfidf_matrix, keyword_vector)
        sorted_indices = np.argsort(similarities.flatten())[::-1][:50]

        for item in self.tree.get_children():
            self.tree.delete(item)

        # Show top 50 most similar documents
        for rank, idx in enumerate(sorted_indices, start=1):
            author = df.iloc[idx]['著者名']
            title = df.iloc[idx]['作品名']
            person_id = df.iloc[idx]['人物ID']
            work_id = df.iloc[idx]['作品ID']
            url = f"https://www.aozora.gr.jp/cards/{str(person_id).zfill(6)}/card{work_id}.html"
            similarity = similarities[idx][0]
            self.tree.insert("", tk.END, values=(rank, author, title, url, f"{similarity:.4f}"))

        # Bind URL click event to open_url function
        self.tree.bind("<Button-1>", self.open_url)

# Initialize the GUI
root = tk.Tk()
app = DocumentRetrievalApp(root)
root.mainloop()
