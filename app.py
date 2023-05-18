from flask import Flask, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from underthesea import word_tokenize
import csv
import json
import subprocess
import query
import os

app = Flask(__name__)

# def get_data():
#     filename = 'query.py'
#     subprocess.run(['python', filename])

def tokenizer(text):
    return word_tokenize(text, format="text")


def add_data_user(json_data,id_trip):
    data = json.loads(json_data.decode('utf-8'))
    id_trip = data['idTrip']
    title = data['title']
    description = data['description']
    activities = data['activities']
    with open(id_trip+'.csv', 'a',encoding='utf-8', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([id_trip, activities, description, title])

def get_trip_index(trips_df,idTrip):
    return trips_df[trips_df['idTrip'] == idTrip].index[0]


def get_trip_id(trips_df,index):
    return trips_df[trips_df.index == index]['idTrip'].values[0]


@app.route("/")
def hello_world():
    return "<p>Xin chào, Đồ án 2</p>"

class UndertheseaTokenizer:
    def __call__(self, text):
        return word_tokenize(text)

@app.route("/recommend_trips",methods=['POST'])
def get_recommendations():
    id_trip=json.loads(request.data.decode('utf-8'))['idTrip']
    query.getData(id_trip)
    add_data_user(request.data,id_trip)
    trips_df = pd.read_csv(id_trip+'.csv')
    trips_df['text'] = trips_df['title'] + ' ' + trips_df['description']+ ' ' + trips_df['activities']
    vectorizer = TfidfVectorizer(tokenizer=UndertheseaTokenizer())
    tfidf_matrix = vectorizer.fit_transform(trips_df['text'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix) 
    print(tfidf_matrix)
    data=request.data
    data=json.loads(data.decode('utf-8'))
    trip_id = data['idTrip']
    # df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), index=trips_df['title'], columns=vectorizer.vocabulary_.keys())
    # df_tfidf.head()
    try:
        trip_index = get_trip_index(trips_df,trip_id)
    except IndexError:
        return jsonify({"error": f"Trip '{trip_id}' not found"}), 404


    sim_scores = list(enumerate(cosine_sim[trip_index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]

    recommended_trips_indices = [i[0] for i in sim_scores]
    recommended_trips = [get_trip_id(trips_df,i) for i in recommended_trips_indices]
    os.remove(id_trip+'.csv')
    return jsonify({"recommended_trips": recommended_trips}), 200


if __name__=="__main__":
    app.run()