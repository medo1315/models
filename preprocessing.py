# preprocessing.py

import re
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Ensure required NLTK data is downloaded (if not already)
nltk.download('punkt')
nltk.download('stopwords')

def preprocess_text(text):
    """
    Exactly matches the simple_preprocess function used during model training
    """
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    words = word_tokenize(text)
    stopwrds = set(stopwords.words('english'))
    words = [word for word in words if word not in stopwrds]
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]
    return " ".join(words)



