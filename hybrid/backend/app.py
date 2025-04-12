from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import requests

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Load dataset
df = pd.read_csv("final_drama_dataset.csv")

df["genres"] = df["genres"].str.replace(",", " ")
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["rating"] = df["rating"].fillna("N/A")  # Replace NaN ratings with 'N/A'

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(df["genres"] + " " + df["synopsis"])

# Convert to Sparse Matrix
tfidf_sparse = csr_matrix(tfidf_matrix)

# Nearest Neighbors Model
knn = NearestNeighbors(metric="cosine", algorithm="brute", n_neighbors=6)
knn.fit(tfidf_sparse)

# OMDb API Key
OMDB_API_KEY = "81eab8cd"
PLACEHOLDER_IMAGE = "https://via.placeholder.com/200"

def fetch_drama_image(title):
    """Fetch the drama image from OMDb API"""
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(url).json()
    return response.get("Poster", PLACEHOLDER_IMAGE)

def get_hybrid_recommendations(title, top_n=5):
    title = title.lower()
    if title not in df["title"].str.lower().values:
        return []
    
    idx = df[df["title"].str.lower() == title].index[0]
    distances, indices = knn.kneighbors(tfidf_sparse[idx], n_neighbors=top_n+1)
    
    recommendations = []
    
    # Include the searched drama
    searched_drama = {
        "title": df.iloc[idx]["title"].title(),
        "genres": df.iloc[idx]["genres"],
        "image_url": fetch_drama_image(df.iloc[idx]["title"]),
        "rating": df.iloc[idx]["rating"] if df.iloc[idx]["rating"] != "N/A" else "Not Available",
        "note": "You searched for this drama"
    }
    recommendations.append(searched_drama)
    
    # Recommended dramas
    for i in indices[0][1:]:  # Skip input drama
        recommendations.append({
            "title": df.iloc[i]["title"].title(),
            "genres": df.iloc[i]["genres"],
            "image_url": fetch_drama_image(df.iloc[i]["title"]),
            "rating": df.iloc[i]["rating"] if df.iloc[i]["rating"] != "N/A" else "Not Available"
        })
    
    return recommendations

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommend", methods=["GET"])
def recommend():
    title = request.args.get("title")
    if not title:
        return jsonify({"error": "Please provide a drama title."})
    
    recommendations = get_hybrid_recommendations(title.lower())
    if not recommendations:
        return jsonify({"error": "No similar dramas found. Try another title."})
    
    return jsonify({"recommendations": recommendations})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)

'''if __name__ == "__main__":
    app.run(debug=True)'''

'''import gradio as gr
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import requests

# Load dataset
df = pd.read_csv("final_drama_dataset.csv")
df["genres"] = df["genres"].str.replace(",", " ")
df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna("N/A")

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(df["genres"] + " " + df["synopsis"])
tfidf_sparse = csr_matrix(tfidf_matrix)

# Nearest Neighbors Model
knn = NearestNeighbors(metric="cosine", algorithm="brute", n_neighbors=6)
knn.fit(tfidf_sparse)

# OMDb API
OMDB_API_KEY = "81eab8cd"
PLACEHOLDER_IMAGE = "https://via.placeholder.com/200"

def fetch_drama_image(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(url).json()
    return response.get("Poster", PLACEHOLDER_IMAGE)

# Define Recommendation Function
def recommend_drama(title):
    title = title.lower()
    if title not in df["title"].str.lower().values:
        return "Drama not found. Try another title."

    idx = df[df["title"].str.lower() == title].index[0]
    distances, indices = knn.kneighbors(tfidf_sparse[idx], n_neighbors=6)

    recommendations = []
    for i in indices[0][1:]:
        recommendations.append(df.iloc[i]["title"])
    
    return recommendations

# Gradio UI
iface = gr.Interface(
    fn=recommend_drama,
    inputs=gr.Textbox(label="Enter Drama Title"),
    outputs=gr.JSON(label="Recommended Dramas"),
    title="Hybrid Drama Recommender",
    description="Enter a drama title and get recommendations!"
)

if __name__ == "__main__":
    iface.launch()'''

