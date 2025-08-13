import nltk

print("Starting NLTK data download...")

# Download 'wordnet' for word definitions and relationships
nltk.download('wordnet')

# Download 'punkt' for sentence tokenization (very common)
nltk.download('punkt')
nltk.download('punkt_tab')

print("Download complete.")