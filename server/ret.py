import os
import re
import gensim.downloader as api
from bs4 import BeautifulSoup
from colour import Color
import spacy
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import nltk
from nltk.corpus import stopwords
import string
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from nltk.stem import WordNetLemmatizer
import shutil
from tkinter import colorchooser
nltk.download('wordnet')
nltk.download('omw-1.4')
def collect_descriptions_from_folder(folder_path,label):
    descriptions = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                descriptions.append((content,label))
    
    return descriptions

def collect_all_data():
    fol_name=['topic0_food','topic1_hotel','topic2_courses']
    labels=["Food and Drink","Hotel","Courses"]
    label_to_folder = dict(zip(labels, fol_name))  # Map labels to folder nam
    data=[]
    for i,fol in enumerate(fol_name):
        #3dly al path
        folder_path = f"F:/GP/{fol}/desc"
        data+=collect_descriptions_from_folder(folder_path,labels[i])
    return data,label_to_folder

def preprocess_text(text):
        text = text.lower()
        text = re.sub(r'\b\w{1,2}\b', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()

def classify(data,user_input,label_to_folder):

    # Split data into descriptions and labels
    descriptions, labels = zip(*data)

    # Preprocess the text data

    descriptions = [preprocess_text(desc) for desc in descriptions]

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(descriptions, labels, test_size=0.2, random_state=42)

    # Convert text data into numerical features using TF-IDF
    vectorizer = TfidfVectorizer()
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    # Train a Logistic Regression classifier
    classifier = LogisticRegression()
    classifier.fit(X_train_tfidf, y_train)

    # Calculate accuracy and print classification report
    y_pred = classifier.predict(X_test_tfidf)
    # Function to classify new descriptions and return folder paths
    def classify_and_get_folders(new_descriptions, classifier, vectorizer, label_to_folder):
        new_descriptions_preprocessed = [preprocess_text(desc) for desc in new_descriptions]
        new_descriptions_tfidf = vectorizer.transform(new_descriptions_preprocessed)
        predictions = classifier.predict(new_descriptions_tfidf)
        
        folders = []
        for desc, category in zip(new_descriptions, predictions):
            #3dly al path
            folder = os.path.join("F:/GP", label_to_folder[category])
            folders.append(folder)
        
        return folders

    # Example new descriptions
    

    # Get the folders for the new descriptions
    folders = classify_and_get_folders(user_input, classifier, vectorizer, label_to_folder)
    return folders

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    tokens = nltk.word_tokenize(text.lower())
    tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(tokens)


def preprocess_texts(texts):
    return [preprocess_text(text) for text in texts]

def text_to_embedding(texts, model, tfidf_vectorizer):
    tfidf_matrix = tfidf_vectorizer.fit_transform(texts)
    feature_names = tfidf_vectorizer.get_feature_names_out()

    def get_word_vector(word):
        try:
            return model[word]
        except KeyError:
            return np.zeros(model.vector_size)

    embeddings = []
    for text in texts:
        text_embedding = np.zeros(model.vector_size)
        word_count = 0
        for word in text.split():
            if word in feature_names:
                tfidf_value = tfidf_vectorizer.transform([word]).data[0]
                word_embedding = get_word_vector(word) * tfidf_value
                text_embedding += word_embedding
                word_count += 1
        if word_count > 0:
            text_embedding /= word_count
        embeddings.append(text_embedding)
    return np.array(embeddings)

def compute_similarity(embeddings, query_embedding):
    similarities = cosine_similarity([query_embedding], embeddings).flatten()
    return similarities

def collect_descriptions_from_folder(folder_path):
    descriptions = []
    file_to_folder = {}

    # Loop through each file in the desc folder
    desc_folder = os.path.join(folder_path, 'desc')
    pages_folder = os.path.join(folder_path, 'pages')

    for filename in os.listdir(desc_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(desc_folder, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                descriptions.append(content)
                file_to_folder[content] = os.path.join(pages_folder, filename[:-4])  # Mapping description to folder
    
    return descriptions, file_to_folder

def retrieve_top_k_websites(folder_path, user_input, word2vec_model, tfidf_vectorizer, k=5):
    descriptions, file_to_folder = collect_descriptions_from_folder(folder_path)
    preprocessed_descriptions = preprocess_texts(descriptions)
    embeddings = text_to_embedding(preprocessed_descriptions, word2vec_model, tfidf_vectorizer)
    preprocessed_input = preprocess_text(user_input)  # Ensure user_input is a string here
    input_embedding = text_to_embedding([preprocessed_input], word2vec_model, tfidf_vectorizer)[0]
    similarities = compute_similarity(embeddings, input_embedding)
    top_k_indices = similarities.argsort()[-k:][::-1]
    top_k_folders = [file_to_folder[descriptions[i]] for i in top_k_indices]

    return top_k_folders[:k]

def top(folders):
    folder_path = folders[0]
    word2vec_model = api.load("word2vec-google-news-300")

    vectorizer = TfidfVectorizer()

    top_k_folders = retrieve_top_k_websites(folder_path, user_input[0], word2vec_model, vectorizer, k=1)
    return top_k_folders


def trans(top_k_folders):
   if os.path.exists(top_k_folders[0]):
     shutil.rmtree(top_k_folders[0])
   shutil.copytree(top_k_folders[0], '9')

def pick_color():
    # Open the color picker dialog
    color_code = colorchooser.askcolor(title="Choose a color")[1]
    base_color = Color(color_code)
    return base_color.hex

def paths(main_folder):
    html_file_path = os.path.join(main_folder, 'index.html')
    css_folder_path = os.path.join(main_folder, 'css')
    js_folder_path = os.path.join(main_folder, 'js')
    return html_file_path

def read_css(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_css(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def find_colors(css_content):
    # Regex to find hex, rgb, rgba colors
    hex_color_regex = r'#[0-9a-fA-F]{3,6}'
    rgb_color_regex = r'rgb\s?\(\s?\d{1,3}\s?,\s?\d{1,3}\s?,\s?\d{1,3}\s?\)'
    rgba_color_regex = r'rgba\s?\(\s?\d{1,3}\s?,\s?\d{1,3}\s?,\s?\d{1,3}\s?,\s?\d?\.?\d+\s?\)'
    
    colors = re.findall(f'{hex_color_regex}|{rgb_color_regex}|{rgba_color_regex}', css_content)
    return colors

def rgba_to_hex(rgba):
    match = re.match(r'rgba\s?\(\s?(\d{1,3})\s?,\s?(\d{1,3})\s?,\s?(\d{1,3})\s?,\s?\d?\.?\d+\s?\)', rgba)
    if match:
        r, g, b = map(int, match.groups())
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)
    return rgba

def generate_new_palette(base_color, old_colors):
    base = Color(base_color)
    new_palette = [base]

    for old_color in old_colors[1:]:
        if 'rgba' in old_color:
            old_color = rgba_to_hex(old_color)
        old_c = Color(old_color)
        new_c = Color(base_color)
        new_c.luminance = old_c.luminance
        new_palette.append(new_c)

    return new_palette

def replace_colors(css_content, old_colors, new_colors):
    for old_color, new_color in zip(old_colors, new_colors):
        css_content = re.sub(re.escape(old_color), new_color, css_content)
    return css_content

def get_linked_css_files(html_file_path):
    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'lxml')
    
    # Find all <link> tags with rel="stylesheet"
    css_files = []
    for link_tag in soup.find_all('link', rel='stylesheet'):
        href = link_tag.get('href')
        if href:
            # Check if it's a local path or an external URL
            if href.startswith('http://') or href.startswith('https://'):
                # Handle external URLs if needed
                do=None
            else:
                css_files.append(href)
    
    return css_files

def modifyallcss(main_folder,css_files,base_color):
    for css_file in css_files:
        input_css_path = os.path.join(main_folder, css_file)
        output_css_path = os.path.join(main_folder, css_file)  # Adjust if needed
        
        # Read CSS content
        css_content = read_css(input_css_path)
        
        # Find colors in CSS
        old_colors = find_colors(css_content)
        
        # Generate new color palette
            # Example base color
        if len(old_colors) != 0:
            new_palette = generate_new_palette(base_color, old_colors)
            new_colors = [color.hex for color in new_palette]
            
            
            # Step 4: Replace old colors with new colors
            updated_css_content = replace_colors(css_content, old_colors, new_colors)
            
            # Step 5: Write the updated CSS content to a new file
            write_css(output_css_path, updated_css_content)
            

def modify_html(html_content, details):
    try:
        # Modify title
        html_content = re.sub(r'<title>.*?</title>', f"<title>{details.get('topic', 'My Website')}</title>", html_content)

        # Modify header
        if re.search(r'<h1>.*?</h1>', html_content):
            html_content = re.sub(r'<h1>.*?</h1>', f"<h1>Welcome to our {details.get('topic', 'website')}</h1>", html_content)
        else:
            html_content = re.sub(r'<h2>.*?</h2>', f"<h2>Welcome to our {details.get('topic', 'website')}</h2>", html_content)
        
        # Modify location if available
        if 'location' in details:
            location_html = f"<p>Location: {details['location']}</p>"
            html_content = re.sub(r'<!-- location -->', location_html, html_content)
        # Modify hotline if available
        if 'hotline' in details:
            hotline_html = f"<p>Hotline: {details['hotline']}</p>"
            html_content = re.sub(r'<!-- hotline -->', hotline_html, html_content)

    except Exception as e:
        str(e)

    return html_content


def collect_feedback(description, extracted_details, user_feedback):
    try:
        # Example: Assume user provides corrected details
        corrected_details = {
            'topic': 'coffee website',
            'location': 'Cairo',
            'colors': ['brown', 'cafe'],
            'hotline': '19888'
        }

        # Integrate user feedback to improve accuracy (example)
        updated_details = {**extracted_details, **corrected_details}

        return updated_details

    except Exception as e:
        return extracted_details  # Return original extracted details in case of error


def extract_details_advanced(description):
    details = {}
    nlp = spacy.load('en_core_web_sm')
    keywords = {
    'topic': ['website', 'web page', 'site', 'online platform', 'internet presence', 'blog', 'ecommerce site', 'portfolio'],
    'location': ['in', 'located in', 'at', 'based in', 'headquartered in', 'global', 'regional', 'national', 'local'],
    'colors': ['colors', 'color scheme', 'color palette', 'shades', 'hue', 'primary color', 'secondary color', 'accent color', 'gradient'],
    'hotline': ['hotline', 'contact', 'phone number', 'customer service', 'support line', 'helpline', 'contact number', 'service hotline']
     }
    try:
        # Use SpaCy for NER
        doc = nlp(description)

        # Extract entities
        for ent in doc.ents:
            if ent.label_ == 'ORG' and 'topic' not in details:
                details['topic'] = ent.text
            elif ent.label_ == 'GPE' and 'location' not in details:
                details['location'] = ent.text
            elif ent.label_ == 'PRODUCT' and 'topic' not in details:
                details['topic'] = ent.text

        # Extract colors and hotline based on keywords
        for token in doc:
            if token.text.lower() in keywords['colors'] and token.i + 1 < len(doc):
                details['primary_color'] = doc[token.i + 1].text
            elif token.text.lower() in keywords['hotline'] and token.i + 1 < len(doc):
                next_token = doc[token.i + 1]
                if next_token.like_num:
                    details['hotline'] = next_token.text

    except Exception as e:
       str(e)

    return details

def readandwrite(html_file_path,updated_details):
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    modified_html = modify_html(html_content, updated_details)
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(modified_html)