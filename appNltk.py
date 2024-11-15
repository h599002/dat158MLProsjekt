"""
Filename: app.py
Description: Emotion Classification App
Authors: Vegard Aa Albretsen, Erlend Vitsø
Date: November 15, 2024

Generative AI has been used.
"""
import streamlit as st
import pickle
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import numpy as np
import pandas as pd
import os
from PIL import Image
import re
import nltk

nltk.download('punkt')
# Load the pre-trained model and vectorizer
with open('./saved_models/logistic_regression_model_corrected_tokens.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

with open('./saved_models/vectorizer_corrected_tokens.pkl', 'rb') as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

# Define emotion labels
output_labels = ["Sadness", "Joy", "Love", "Anger", "Fear", "Surprise"]

# Initialize the stemmer
stemmer = PorterStemmer()

# Preprocessing function
def preprocess_text(user_input):
    # Remove noise (keep apostrophes and spaces)
    clean_text = re.sub(r"[^a-zA-Z0-9'\s]", '', user_input).lower()
    # Tokenize
    tokens = word_tokenize(clean_text)
    # Stem each token
    stemmed_tokens = [stemmer.stem(word) for word in tokens]
    # Combine tokens back into a single string for vectorizer
    return ' '.join(stemmed_tokens)

# Set up the Streamlit app layout
st.title("Text Analysis App")
st.write("Enter some text below to analyze sentiment or classify it into either Sadness, Joy, Love, Anger, Fear, or Surprise.")

# Text input for the user
user_input = st.text_area("Enter your text here:")

if st.button("Analyze Text"):
    if user_input:
        try:
            # Preprocess the input text
            processed_input = preprocess_text(user_input)

            # Transform the processed text using the TF-IDF vectorizer
            input_vector = vectorizer.transform([processed_input])

            # Get prediction for the emotion
            prediction = model.predict(input_vector)[0]

            # Display the prediction
            st.write(f"Predicted Emotion: {output_labels[prediction]}")

            # Get probabilities for each emotion
            probabilities = model.predict_proba(input_vector)[0]

            # Sort emotions by probability in descending order
            sorted_indices = np.argsort(probabilities)[::-1]

            # Display top predictions
            st.write("Top Predictions:")
            for idx in sorted_indices:
                st.write(f"{output_labels[idx]}: {probabilities[idx]:.2%}")
        except Exception as e:
            st.write("Error processing text:", str(e))
    else:
        st.write("Please enter some text.")

# Feedback section
st.header("Give Us Feedback!")
st.write("This app is made by Vegard Aa Albretsen & Erlend Vitsø")
st.write("Was this service mega cool?")

# Feedback buttons
if st.button("👍 Yes"):
    feedback_type = "Thumbs Up"
    st.success("Thank you for your positive feedback!")
elif st.button("👎 No"):
    feedback_type = "Thumbs Down"
    st.warning("We appreciate your feedback and are working to improve.")

# Save feedback to a CSV file if a button was clicked
if 'feedback_type' in locals():
    feedback_file = 'feedback_summary.csv'

    # Check if the feedback file exists
    if os.path.exists(feedback_file):
        feedback_data = pd.read_csv(feedback_file)
    else:
        feedback_data = pd.DataFrame(columns=["FeedbackType"])

    # Append new feedback
    new_feedback = pd.DataFrame([[feedback_type]], columns=["FeedbackType"])
    feedback_data = pd.concat([feedback_data, new_feedback], ignore_index=True)

    # Save updated feedback data to CSV
    feedback_data.to_csv(feedback_file, index=False)
