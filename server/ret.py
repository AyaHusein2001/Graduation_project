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
from gensim.models import KeyedVectors
# nltk.download('wordnet')
# nltk.download('omw-1.4')
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
    fol_name=['coffee','fittness','resturant']
    labels=['coffee','fittness','resturant']
    label_to_folder = dict(zip(labels, fol_name))  
    data=[]
    for i,fol in enumerate(fol_name):
        #3dly al path
        folder_path = f"{fol}/desc"
        data+=collect_descriptions_from_folder(folder_path,labels[i])
    return data,label_to_folder

def preprocess_text(text):
        text = text.lower()
        text = re.sub(r'\b\w{1,2}\b', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()

def classify(data,user_input,label_to_folder):

    descriptions, labels = zip(*data)

    descriptions = [preprocess_text(desc) for desc in descriptions]
    X_train, X_test, y_train, y_test = train_test_split(descriptions, labels, test_size=0.2, random_state=42)
    vectorizer = TfidfVectorizer()
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    classifier = LogisticRegression()
    classifier.fit(X_train_tfidf, y_train)
    y_pred = classifier.predict(X_test_tfidf)
    def classify_and_get_folders(new_descriptions, classifier, vectorizer, label_to_folder):
        new_descriptions_preprocessed = [preprocess_text(desc) for desc in new_descriptions]
        new_descriptions_tfidf = vectorizer.transform(new_descriptions_preprocessed)
        predictions = classifier.predict(new_descriptions_tfidf)
        
        folders = []
        for desc, category in zip(new_descriptions, predictions):
            folder =  label_to_folder[category]
            folders.append(folder)
        
        return folders
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

def collect_descriptions_folder(folder_path):
    descriptions = []
    file_to_folder = {}
    desc_folder = os.path.join(folder_path, 'desc')
    pages_folder = os.path.join(folder_path, 'pages')

    for filename in os.listdir(desc_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(desc_folder, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                descriptions.append(content)
                file_to_folder[content] = os.path.join(pages_folder, filename[:-4])
    
    return descriptions, file_to_folder

def retrieve_top_k_websites(folder_path, user_input, word2vec_model, tfidf_vectorizer, k=5):
    descriptions, file_to_folder = collect_descriptions_folder(folder_path)
    preprocessed_descriptions = preprocess_texts(descriptions)
    embeddings = text_to_embedding(preprocessed_descriptions, word2vec_model, tfidf_vectorizer)
    preprocessed_input = preprocess_text(user_input) 
    input_embedding = text_to_embedding([preprocessed_input], word2vec_model, tfidf_vectorizer)[0]
    similarities = compute_similarity(embeddings, input_embedding)
    top_k_indices = similarities.argsort()[-k:][::-1]
    top_k_folders = [file_to_folder[descriptions[i]] for i in top_k_indices]

    return top_k_folders[:k]

def top(folders,description):
    folder_path = folders[0]
    word2vec_model_path = 'D:\GP\Website\Graduation_project\GoogleNews-vectors-negative300.bin.gz'
    word2vec_model = KeyedVectors.load_word2vec_format(word2vec_model_path, binary=True, limit=3000000)  

    vectorizer = TfidfVectorizer()

    top_k_folders = retrieve_top_k_websites(folder_path, description, word2vec_model, vectorizer, k=1)
    return top_k_folders


def trans(top_k_folders):
   if os.path.exists('D:\GP\Website\Graduation_project\9'):
     shutil.rmtree('D:\GP\Website\Graduation_project\9')
   shutil.copytree(top_k_folders, 'D:\GP\Website\Graduation_project\9')

def pick_color():
    color_code = colorchooser.askcolor(title="Choose a color")[1]
    base_color = Color(color_code)
    return base_color.hex

def paths(main_folder):
    html_file_path = os.path.join(main_folder, 'home.html')
    return html_file_path

def read_css(file_path):
    file_path = file_path.rstrip('\\')
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_css(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def find_colors(css_content):
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
def is_valid_hex_color(color):
    match = re.fullmatch(r'#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})', color)
    return match is not None
def generate_new_palette(base_color, old_colors):
    base = Color(base_color)
    new_palette = [base]

    for old_color in old_colors[1:]:
        if 'rgba' in old_color:
            old_color = rgba_to_hex(old_color)
        if not is_valid_hex_color(old_color):
            continue
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
    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'lxml')
    css_files = []
    for link_tag in soup.find_all('link', rel='stylesheet'):
        href = link_tag.get('href')
        if href:
            if href.startswith('http://') or href.startswith('https://'):
                do=None
            else:
                css_files.append(href)
    
    return css_files

def modifyallcss(main_folder,css_files,base_color):
    for css_file in css_files:
        pattern = r"{% static '([^']+)' %}"
        css_file = re.sub(pattern, r"\1", css_file)
        css_file.replace('/', '\\')
        print("css_file",css_file)
        input_css_path = os.path.join(main_folder, css_file)
        output_css_path = os.path.join(main_folder, css_file)  
        css_content = read_css(input_css_path)
        old_colors = find_colors(css_content)
        if len(old_colors) != 0:
            new_palette = generate_new_palette(base_color, old_colors)
            new_colors = [color.hex for color in new_palette]
            updated_css_content = replace_colors(css_content, old_colors, new_colors)
            write_css(output_css_path, updated_css_content)
            

def move_files_and_folders(source_dir, templates_dir, static_dir):
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)

    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        if os.path.isfile(source_item) and item.endswith('.html'):
            shutil.copy(source_item, os.path.join(templates_dir, item))
        elif os.path.isdir(source_item):
            shutil.copytree(source_item, os.path.join(static_dir, item))
def move_admin(source_dir, templates_dir, static_dir):
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        if os.path.isfile(source_item) and item.endswith('.css'):
            shutil.copy(source_item, os.path.join(templates_dir, item))
        elif os.path.isdir(source_item):
            shutil.copytree(source_item, os.path.join(static_dir, item))

def replace_file(old_file_path, new_file_path):
    if os.path.exists(old_file_path):
        os.remove(old_file_path)
        print(f"Deleted the old file: {old_file_path}")
    else:
        print(f"The old file does not exist: {old_file_path}")
    
    shutil.copy(new_file_path, old_file_path)
    print(f"Replaced with the new file: {new_file_path}")

def add_home_view(views_file_path):
    home_view_code = """
from django.shortcuts import render
from django.apps import apps
from django.core.exceptions import AppRegistryNotReady

# Define apps to exclude from being treated as sellable models
EXCLUDED_APPS = ['auth']

def is_sellable_model(model):
    sellable_criteria = [
        'name', 'title', 'product_name', 'item_name', 'label',
        'price', 'cost', 'amount', 'value', 'pricing', 'rate', 'charge',
        'description', 'details', 'info', 'summary', 'overview', 'spec', 'specification',
        'quantity', 'amount', 'count', 'number', 'volume', 'total', 'stock',
        'size', 'dimension', 'length', 'width', 'height', 'measurements',
        'weight', 'mass', 'heaviness', 'load', 'burden'
    ]
    
    # Check if the model has any of the sellable criteria fields
    if model._meta.app_label in EXCLUDED_APPS:
        return False

    fields = model._meta.get_fields()
    for field in fields:
        if field.name in sellable_criteria:
            return True
    
    return False

def get_tables_with_sellable_objects():
    try:
        models = apps.get_models()
        sellable_models = []
        for model in models:
            if is_sellable_model(model):
                sellable_models.append(model)
        return sellable_models
    except AppRegistryNotReady:
        return []

def get_sellable_objects():
    sellable_models = get_tables_with_sellable_objects()
    sellable_objects = []

    sellable_criteria = [
        'name', 'title', 'product_name', 'item_name', 'label',
        'price', 'cost', 'amount', 'value', 'pricing', 'rate', 'charge',
        'description', 'details', 'info', 'summary', 'overview', 'spec', 'specification',
        'quantity', 'amount', 'count', 'number', 'volume', 'total', 'stock',
        'size', 'dimension', 'length', 'width', 'height', 'measurements',
        'weight', 'mass', 'heaviness', 'load', 'burden'
    ]

    for model in sellable_models:
        # Skip the Permission model explicitly
        if model._meta.model_name == 'Permission':
            continue
        
        objects = model.objects.all()
        for obj in objects:
            obj_data = {'model_name': model.__name__}
            for field in model._meta.get_fields():
                if field.name in sellable_criteria:
                    obj_data[field.name] = getattr(obj, field.name, '')
            sellable_objects.append(obj_data)

    return sellable_objects

def home(request):
    sellable_objects = get_sellable_objects()
    
    # Debug statements to print sellable_objects
    print("Sellable Objects:")
    for obj in sellable_objects:
        print(obj)

    context = {
        'sellable_objects': sellable_objects,
    }
    return render(request, 'home.html', context)

"""

    with open(views_file_path, 'r+') as file:
        content = file.read()
        
        if 'def home(request):' not in content:
            file.write(home_view_code)
      



def move_files_and_folders(source_dir, templates_dir, static_dir, file_extension):

    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)

    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        if os.path.isfile(source_item) and item.endswith(file_extension):
            shutil.copy(source_item, os.path.join(templates_dir, item))
            print(f"Copied {item} to {templates_dir}")
        
        elif os.path.isdir(source_item):
            destination_dir = os.path.join(static_dir, item)
            shutil.copytree(source_item, destination_dir)
            print(f"Copied directory {item} to {static_dir}")


