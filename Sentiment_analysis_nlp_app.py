# Import necessary libraries
import streamlit as st
import pickle
import pandas as pd
import numpy as np
import re
import nltk
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import base64
from PIL import Image


# Load NLTK resources
nltk.download('stopwords')  # Comment this line after the first run
from nltk.corpus import stopwords

# Load CountVectorizer
with open(r"C:\Users\new\VS\vscode.project\RESUME PROJCT\SENTIMENT ANALYSIS\count_vectorizer.pkl","rb") as file:
    cv=pickle.load(file)
    
 # Function to set a background image and sidebar color
def set_background(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
        encoded_image = base64.b64encode(data).decode()

    page_bg_img = page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    /* Change the sidebar background color to black */
    section[data-testid="stSidebar"] {{
        background-color: #000000; /* Black color */
        color: white; /* Sidebar text color in white for contrast */
    }}
    /* Sidebar text styles */
    section[data-testid="stSidebar"] .css-1y4p8pa, 
    section[data-testid="stSidebar"] .css-17eq0hr {{
        color: white !important; /* Ensure sidebar text remains white */
    }}
    /* General text styles */
    h1, h2, h3, h4, h5, h6, p, label {{
        color: white;
    }}
    /* Custom button styles */
    .stButton > button {{
        background-color: #4C4C6D;
        color: white;
        border-radius: 10px;
        font-size: 16px;
        padding: 10px 20px;
    }}
    .stButton > button:hover {{
        background-color: #6A5ACD;
        color: white;
    }}
    /* Slider label styles */
    .css-1q8dd3e, .css-1b9lf8j {{
        color: white !important;
        font-weight: bold;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)
    # Set background image and sidebar style
set_background(r"C:\Users\new\Pictures\Sentiment-Analysis-02.jpg")


# Load the test and train data
try:
    with open(r"C:\Users\new\VS\vscode.project\RESUME PROJCT\SENTIMENT ANALYSIS\X_test.pkl", "rb") as file:
        X_test = pickle.load(file)
    with open(r"C:\Users\new\VS\vscode.project\RESUME PROJCT\SENTIMENT ANALYSIS\y_test.pkl", "rb") as file:
        y_test = pickle.load(file)
    with open(r"C:\Users\new\VS\vscode.project\RESUME PROJCT\SENTIMENT ANALYSIS\X_train.pkl", "rb") as file :
        X_train = pickle.load(file)
    with open(r"C:\Users\new\VS\vscode.project\RESUME PROJCT\SENTIMENT ANALYSIS\y_train.pkl", "rb") as file:
        y_train = pickle.load(file)
except FileNotFoundError:
    st.error("Error loading train/test data files.")
    st.stop()

classifiers = {}
for name in ['Decision Tree', 'K-Nearest Neighbors', 'Logistic Regression', 
             'Random Forest', 'Support Vector Classifier', 'AdaBoost', 
             'Gradient Boosting']:
    file_path = (r"C:\Users\new\VS\vscode.project\RESUME PROJCT\SENTIMENT ANALYSIS\Decision Tree_model.pkl")  # Modify this line
    with open(file_path, "rb") as file:
        classifiers[name] = pickle.load(file)


# Load reviews data for word clouds
reviews_df = pd.read_csv(r"C:\Users\new\VS\vscode.project\RESUME PROJCT\SENTIMENT ANALYSIS\4.CUSTOMERS REVIEW DATASET\Restaurant_Reviews.tsv",sep='\t')


# Sidebar for model selection
st.sidebar.title("Choose Classifier")
classifier_name = st.sidebar.selectbox(
    "Select a model:",
    list(classifiers.keys())
)

# Title and input
st.title("Sentiment Analyzer 🧠")
st.write("Enter a review to predict whether it is positive or negative.")

# Text input
user_review = st.text_input("Your Review:")

# Preprocess user input
if user_review:
    # Preprocessing
    review = re.sub('[^a-zA-Z]', ' ', user_review)
    review = review.lower().split()
    ps = nltk.PorterStemmer()
    review = [ps.stem(word) for word in review if word not in set(stopwords.words('english'))]
    review = ' '.join(review)

    # Transform the input into Bag of Words format
    input_data = cv.transform([review]).toarray()

    # Predict sentiment
    classifier = classifiers[classifier_name]
    prediction = classifier.predict(input_data)
    sentiment = "Positive" if prediction[0] == 1 else "Negative"

    # Display sentiment prediction
    st.write(f"**Prediction ({classifier_name}):**", sentiment)

    # Check for accuracy, bias, and variance
    y_pred = classifier.predict(X_test)  # Predict on test data
    accuracy = accuracy_score(y_test, y_pred)  # Calculate accuracy
    bias = classifier.score(X_train, y_train)  # Model score on training data (bias)
    variance = classifier.score(X_test, y_test)  # Model score on test data (variance)

    # Display accuracy, bias, and variance
    st.write(f"**Test Accuracy (Model Accuracy)**: {accuracy:.2f}")  # Display model accuracy first
    st.write(f"**Training Accuracy (Bias)**: {bias:.2f}")
    st.write(f"**Test Accuracy (Variance)**: {variance:.2f}")

    # Confusion matrix and classification report
    cm = confusion_matrix(y_test, y_pred)
    class_report = classification_report(y_test, y_pred, output_dict=True)

    # Display confusion matrix as DataFrame for better readability
    cm_df = pd.DataFrame(cm, index=np.unique(y_test), columns=np.unique(y_test))
    st.write("**Confusion Matrix:**")
    st.dataframe(cm_df)
    
    
    # Display classification report as a DataFrame
    st.write("### Classification Report:")
    report_df = pd.DataFrame(class_report).transpose()  # Transpose to have labels as index
    st.dataframe(report_df)


    # Create Word Cloud for Positive and Negative Reviews
    st.write("### Word Cloud of Positive and Negative Reviews")
    positive_reviews = " ".join(reviews_df[reviews_df['Liked'] == 1]['Review'])  # Assuming '1' is positive
    negative_reviews = " ".join(reviews_df[reviews_df['Liked'] == 0]['Review'])  # Assuming '0' is negative

    # Generate word clouds
    positive_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(positive_reviews)
    negative_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(negative_reviews)

    # Display word clouds
    fig_wc, ax_wc = plt.subplots(1, 2, figsize=(16, 8))
    ax_wc[0].imshow(positive_wordcloud, interpolation='bilinear')
    ax_wc[0].axis('off')
    ax_wc[0].set_title("Positive Reviews Word Cloud")

    ax_wc[1].imshow(negative_wordcloud, interpolation='bilinear')
    ax_wc[1].axis('off')
    ax_wc[1].set_title("Negative Reviews Word Cloud")

    st.pyplot(fig_wc)

    # Create columns for distribution of positive and negative reviews and confusion matrix
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Distribution of Positive and Negative Reviews:")
        review_counts = reviews_df['Liked'].value_counts()
        fig_dist, ax_dist = plt.subplots(figsize=(6, 4))
        pastel_colors = ['#FF9999', '#66B2FF']  # Pastel colors
        review_counts.plot(kind='bar', color=pastel_colors, ax=ax_dist)
        ax_dist.set_title('Count of Positive and Negative Reviews')
        ax_dist.set_xticklabels(['Negative', 'Positive'], rotation=0)
        ax_dist.set_ylabel('Count')
        st.pyplot(fig_dist)

    with col2:
        st.write("### Confusion Matrix Heatmap:")
        
        fig_cm, ax_cm = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        st.pyplot(fig_cm)