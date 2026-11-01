import streamlit as st
import pickle
import pandas as pd
import requests

st.title("🎬 Movie Recommendation System 🍿")

# Load movie data and similarity matrix
with open("movie_data.pkl", "rb") as f:
    movie_data = pickle.load(f)

with open("similarity.pkl", "rb") as f:
    similarity = pickle.load(f)

movie_data = pd.DataFrame(movie_data)
similarity_data = pd.DataFrame(similarity)

# Function to fetch movie details from TMDB API
def fetch_movie_details(movie_id):
    try:
        api_key = "f11ca805ea8ddd941eef56ebb70dd032"
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&append_to_response=credits"
        response = requests.get(url)
        data = response.json()

        poster_url = f"https://image.tmdb.org/t/p/w185/{data.get('poster_path', '')}"
        description = data.get("overview", "Description not available.")
        imdb_rating = data.get("vote_average", "N/A")
        cast = [member["name"] for member in data["credits"]["cast"][:5]] if "credits" in data else []
        
        # Fetch genres
        genres = [genre["name"] for genre in data.get("genres", [])]  # Extract genre names

        return poster_url, description, imdb_rating, cast, genres

    except Exception:
        return (
            "https://tse4.mm.bing.net/th?id=OIP.59acm7M8zfvbkDUNHr6KdQAAAA&pid=Api&P=0&h=220",
            "Description not available.",
            "N/A",
            [],
            []  # Return empty list for genres in case of error
        )

# Function to recommend similar movies
def recommender(movie):
    if movie in movie_data["title"].values:
        movie_index = movie_data[movie_data["title"] == movie].index[0]
        distance = similarity_data[movie_index]
        movie_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]

        recommendations = []

        for i in movie_list:
            movie_id = movie_data.iloc[i[0]]["movie_id"]
            title = movie_data.iloc[i[0]]["title"].title()
            poster, description, imdb_rating, cast, genres = fetch_movie_details(movie_id)
            
            recommendations.append((title, poster, description, imdb_rating, cast, genres))

        return recommendations
    else:
        st.error("Movie Not Found!")
        st.error("Check the spelling or try another movie.")
        return []

# Dropdown menu to select a movie
option = st.selectbox("🎥 **Select a Movie**", movie_data["title"].values)

# Button to fetch recommendations
if st.button("🔍 Recommend"):
    try:
        # Fetch details of the selected movie
        selected_movie_id = movie_data[movie_data["title"] == option]["movie_id"].values[0]
        selected_poster, selected_description, selected_imdb_rating, selected_cast, selected_genres = fetch_movie_details(selected_movie_id)

        # Display details of the selected movie
        st.subheader("🎥 **Selected Movie Details**")
        st.markdown("---")

        col1, col2 = st.columns([1, 2])  # Creates two columns, 1/3 for image, 2/3 for details

        with col1:
            st.image(selected_poster, use_container_width=True)  # Updated parameter

        with col2:
            st.markdown(f"### 🎬 **{option}**")
            st.markdown(f"⭐ **IMDb Rating:** `{selected_imdb_rating}`")
            st.markdown(f"📝 **Description:** {selected_description[:300]}...")  # Show first 200 chars
            st.markdown(f"🎭 **Cast:** {', '.join(selected_cast)}")
            st.markdown(f"🎞️ **Genres:** {', '.join(selected_genres)}")  # Display genres

        st.markdown("---")  # Adds a separator between movies

        # Fetch and display recommendations
        similar_movies = recommender(option)

        if similar_movies:
            st.subheader("📌 **Recommended Movies**")
            st.markdown("---")

            for title, poster, description, imdb_rating, cast, genres in similar_movies:
                col1, col2 = st.columns([1, 2])  # Creates two columns, 1/3 for image, 2/3 for details

                with col1:
                    st.image(poster, use_container_width=True)  # Updated parameter

                with col2:
                    st.markdown(f"### 🎬 **{title}**")
                    st.markdown(f"⭐ **IMDb Rating:** `{imdb_rating}`")
                    st.markdown(f"📝 **Description:** {description[:300]}...")  # Show first 200 chars
                    st.markdown(f"🎭 **Cast:** {', '.join(cast)}")
                    st.markdown(f"🎞️ **Genres:** {', '.join(genres)}")  # Display genres

                st.markdown("---")  # Adds a separator between movies

    except Exception as e:
        st.error("The movie details cannot be retrieved due to some issues!")