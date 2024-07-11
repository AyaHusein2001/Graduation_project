import re
import stanza
from pattern.en import singularize
import numpy as np
import joblib
import os
# Suppress TensorFlow and Keras logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
from custom_loss import custom_loss_
import os
import subprocess
import shutil
import re
import pandas as pd
import sqlite3
from collections import defaultdict

nlp = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse')
# Load the CSV file into a DataFrame
df = pd.read_csv('again_database.csv')

# ////////////////////////// test this 3nd aya
def predict_entities_and_attributes(description):
    # Load tokenizer and max_length
    tokenizer = joblib.load('tokenizer.pkl')
    max_length = joblib.load('max_length.pkl')

    # Define label mapping
    label_map = {
        '0': 0,
        '1b': 1,
        '1i': 2,
        '2b': 3,
        '2i': 4
    }

    # Define the input string
    input_arr = []
    input_string = description.replace(',', ' and ')
    input_string = input_string.replace('\n', ' ')
    input_arr = input_string.split('.')

    # Initialize arrays for entities and attributes
    entities_snake_case = []
    attributes_snake_case = []

    model = load_model('lstm_model.h5', custom_objects={'custom_loss_': custom_loss_})

    for sentence in input_arr:
        input_string = re.sub(r'\s+', ' ', sentence.strip())

        # Convert input string to lower case and split into words
        original_words = input_string.lower().strip().split()

        # Tokenize and pad sequences for the input string
        input_sequence = tokenizer.texts_to_sequences([input_string])
        X_input = pad_sequences(input_sequence, maxlen=max_length, padding='post')

        # Predict labels for the input string
        y_pred = model.predict(X_input)
        y_pred_classes = np.argmax(y_pred, axis=-1).flatten()

        # Retrieve predicted labels
        predicted_labels = y_pred_classes.tolist()

        # Map token indices back to words
        index_word = {v: k for k, v in tokenizer.word_index.items()}

        # Flatten the input sequence
        input_sequence_flat = input_sequence[0]

        # Iterate through the predicted labels to construct entities_snake_case and attributes_snake_case arrays
        i = 0
        while i < len(input_sequence_flat):
            label = predicted_labels[i]
            word = original_words[i] if input_sequence_flat[i] == 0 else index_word.get(input_sequence_flat[i], original_words[i])  # Current word

            if label == 1:  # Entity label
                if i + 1 < len(input_sequence_flat) and predicted_labels[i + 1] == 2:
                    next_word = original_words[i + 1] if input_sequence_flat[i + 1] == 0 else index_word.get(input_sequence_flat[i + 1], original_words[i + 1])
                    entities_snake_case.append(f"{word}_{next_word}")
                    i += 2  # Skip the next word as it's already processed
                else:
                    entities_snake_case.append(word)
                    i += 1
            elif label == 3:  # Attribute label
                if i + 1 < len(input_sequence_flat) and predicted_labels[i + 1] == 4:
                    next_word = original_words[i + 1] if input_sequence_flat[i + 1] == 0 else index_word.get(input_sequence_flat[i + 1], original_words[i + 1])
                    attributes_snake_case.append(f"{word}_{next_word}")
                    i += 2  # Skip the next word as it's already processed
                else:
                    attributes_snake_case.append(word)
                    i += 1
            else:
                i += 1

    return entities_snake_case, attributes_snake_case

# ////////////////////////////////////////////////////////////////////////////

def extract_top_attributes(ent_array):
    # Filter the DataFrame to include only the entities in `ent_array`
    filtered_df = df[df['Entity'].isin(ent_array)]

    # Initialize a dictionary to map entities to their top 10 important attributes
    entity_attributes_map = {}

    for index, row in filtered_df.iterrows():
        entity = row['Entity'].strip()
        # Extract attributes and their importance values
        attributes_with_importance = row['Merged_Attributes'].strip().split(',')
        datatypes = row['Merged_Types'].strip().split(',')
        # Parse the attributes and their importance values
        attributes_importance_list = []
        for attribute in attributes_with_importance:
            # Split the attribute to separate the name and the importance value
            attribute_name, importance = attribute.split('|')
            # Convert importance to an integer
            importance = int(importance)
            # Append the tuple (attribute name, importance) to the list
            attributes_importance_list.append((attribute_name, importance))
        
        # Sort attributes by importance in descending order and take the top 10
        top_10_attributes = sorted(attributes_importance_list, key=lambda x: x[1], reverse=True)[:10]
        
        # Extract the attribute names from the sorted list
        top_10_attribute_names = [attribute[0] for attribute in top_10_attributes]
        
        # Map the entity to its top 10 important attributes
        entity_attributes_map[entity] = top_10_attribute_names
    
    return entity_attributes_map


def plural_to_singular(word):
    if isinstance(word, str):
        # print('ent: ',word)
        # print(singularize(word))
        return singularize(word)
    return word

def map_entities_to_tokens(sentence, entities):
        token_id_to_entity = {}
        for entity in entities:
            entity_tokens = entity.split()
            entity_length = len(entity_tokens)
            for i in range(len(sentence.tokens) - entity_length + 1):
                if all(plural_to_singular(sentence.tokens[i + j].text) == entity_tokens[j] for j in range(entity_length)):
                    for j in range(entity_length):
                        token_id_to_entity[sentence.tokens[i + j].id[0]] = entity
        return token_id_to_entity

def enhance_entities(text, entities, attributes):
    # Process the text
    doc = nlp(text)
    
    # Extract verbs and words ending with 'ing'
    verbs = []
    ing_words = []

    # Function to read words from a file and put them into an array
    def read_words_to_array(file_path):
        words = []
        with open(file_path, 'r') as file:
            for line in file:
                word = line.strip()
                if word:  # Only add non-empty words
                    words.append(word.lower())
        return words

    # Example usage
    file_path = 'words_list.txt'  # Replace with your file path
    words_array = read_words_to_array(file_path)
    # print(words_array)

    for sentence in doc.sentences:
        for word in sentence.words:
            if word.upos == 'VERB' or word.xpos == 'VBN':
                verbs.append(word.text)
            if word.text.endswith('ing'):
                ing_words.append(word.text)

    
    # Combine verbs and ing words
    combined_set = verbs+ing_words+words_array
    filtered_entities=[]
    for entity in entities :
        if entity not in combined_set and '_' not in entity:
           filtered_entities.append(entity) 
        elif '_' in entity:
            entity_arr=entity.split('_')
            mask = np.isin(entity_arr, combined_set,invert=True)
            if np.all(mask):
                filtered_entities.append(entity)
            else:
                ent_string=''
                for ent in entity_arr:
                    if ent not in combined_set :
                      if ent_string=='':
                         ent_string+=ent  
                      else:  
                        ent_string+='_'+ent
                if ent_string!='':
                    filtered_entities.append(ent_string)

    filtered_attributes=[]
    for attribute in attributes :
        if attribute not in combined_set and '_' not in attribute:
           filtered_attributes.append(attribute) 
        elif '_' in attribute:
            attribute_arr=attribute.split('_')
            

            mask = np.isin(attribute_arr, combined_set,invert=True)
            if np.all(mask):
                filtered_attributes.append(attribute)
            else:
                attr_string=''
                for attr in attribute_arr:
                    if attr not in combined_set :
                    #   print(attr)
                      
                      if attr_string=='':
                         attr_string+=attr  
                      else:  
                        attr_string+='_'+attr  
                if attr_string!='':
                    filtered_attributes.append(attr_string)
    # Modify each attribute before checking
    filtered_entities2 = [plural_to_singular(entity).replace('’s','').replace("'s","").replace("'","") for entity in filtered_entities ]
    modified_attributes = [attr.replace('’s','').replace("'s","").replace("'","")  for attr in filtered_attributes if plural_to_singular(attr) not in filtered_entities2]
    final_ent=list(set(filtered_entities2))
    final_attr=list(set(modified_attributes))
       
    return final_ent,final_attr

def process_string(doc, entities, attributes):
    # Prepare a list to store processed tokens
    processed_tokens = []
    # print(attributes)
    # print(entities)
    # print(doc)

    for sentence in doc.sentences:
        for word in sentence.words:

            if word.deprel == 'conj':
                coming_word=sentence.words[word.id]
                if coming_word.deprel=='conj':
                    merged_word=word.text+'_'+coming_word.text
                    if merged_word in entities or merged_word in attributes:
                        processed_tokens.append(merged_word)
                    else:
                        processed_tokens.append(word.text)
                else:
                    word_before=sentence.words[word.id-2]
                    merged_word=word_before.text+'_'+word.text
                    if merged_word not in entities and merged_word not in attributes:

                        processed_tokens.append(word.text)

            elif word.deprel == 'compound' or word.deprel == 'amod'  :

                head_index = word.head - 1
                if head_index < len(sentence.words):
                    head_word = sentence.words[head_index]
                    # Merge the compound words with an underscore
                    merged_compound = word.text + '_' + head_word.text
                    if (plural_to_singular(merged_compound) in entities and word.deprel == 'compound') or merged_compound in attributes:
                        # print("aya")
                        processed_tokens.append(merged_compound)
                    else:
                        processed_tokens.append(word.text)
                else:
                    processed_tokens.append(word.text)
            else:
                # Check if the previous word is not a compound
                word_before =  sentence.words[word.id - 2]
                merged_word= word_before.text +'_' + word.text
                if word.id > 1 and ((word_before.deprel != 'compound' and merged_word not in attributes ) or( word_before.deprel != 'amod' and  plural_to_singular(merged_word) not in entities and merged_word not in attributes) ):
                    processed_tokens.append(word.text)
                    if word.text == '.':
                      processed_tokens.append('\n')
                elif word.id == 1:
                  processed_tokens.append(word.text)
    

                
    
    # Join the processed tokens into a single string
    result_string = ' '.join(processed_tokens)

    

    # print(result_string)

    # Apply NLP processing using Stanza
    processed_doc = nlp(result_string)
    
    return processed_doc

def get_rid_of(doc,entities):
# Iterate over each sentence in the document
    for sentence in doc.sentences:
        # Map token ids to entities
        # token_id_to_entity = map_entities_to_tokens(sentence, entities)
        # print(token_id_to_entity)
        for word in sentence.words:
            # print(word)
            if word.text in ['which','that','who']:
                    verb = sentence.words[word.head-1]
                    # print(verb.text)
                    referenced_to = sentence.words[verb.head-1]
                    # print(referenced_to.text)
                    if plural_to_singular(referenced_to.text) in entities :  
                    #   print(word.text)        
                      word.text = referenced_to.text
                    #   print(word.text)

def extract_relationships(doc, entities):
    # Process the text with Stanza
    all_sentences_relationships = []
    all_jj=['a','an','one','1','each','every','many','any','all','more','multiple','some','single']
    one_jj=['a','an','one','1','each','every','any','single']
    many_jj=['many','some','all','more','multiple']
    for sentence in doc.sentences:
        relationships=set()
        token_id_to_entity = map_entities_to_tokens(sentence, entities)
        # print(token_id_to_entity)
        last_det_or_adj=''
        last_det_or_adj_head=-1
        for word in sentence.words:
            # print(word)
            E1_cardinality=''
            if word.text in all_jj:
                last_det_or_adj = word.text
                last_det_or_adj_head=word.head

            if word.id in token_id_to_entity:
                # print(word)
                E1 = token_id_to_entity[word.id]
                if word.id > 1 :
                    if last_det_or_adj in one_jj and last_det_or_adj_head == word.id:
                      E1_cardinality = '1'
                    elif  last_det_or_adj in many_jj and last_det_or_adj_head == word.id:
                      E1_cardinality = 'many'

                # Apply TDR14
                if word.deprel == 'nsubj' and word.head > 0:
                    head_word = sentence.words[word.head - 1]
                    if head_word.upos == 'VERB':
                        last_det_or_adj_E2=''
                        last_det_or_adj_head_E2=-1
                        for child in sentence.words:
                            if child.text in all_jj:
                                last_det_or_adj_E2 = child.text
                                last_det_or_adj_head_E2=child.head
                            if child.id in token_id_to_entity and child.head == word.head and child.deprel == 'obj':
                              E2 =child.text
                              # cardinality
                              if child.id > 1 :
                                if last_det_or_adj_E2 in one_jj and last_det_or_adj_head_E2 == child.id:
                                  E2_cardinality = '1'
                                elif  last_det_or_adj_E2 in many_jj and last_det_or_adj_head_E2 == child.id:
                                  E2_cardinality = 'many'
                                else : E2_cardinality=''
                              relationships.add((E1_cardinality,plural_to_singular(E1), child.id, E2_cardinality,plural_to_singular(E2),'14'))
                            

                # Apply TDR15
                if word.deprel == 'nsubj:pass' and word.head > 0:
                    head_word = sentence.words[word.head - 1]
                    sentence_cases ={}
                    if head_word.xpos == 'VBN':
                        last_det_or_adj_E2=''
                        E2_cardinality=''
                        last_det_or_adj_head_E2=-1
                        for child in sentence.words:
                            if child.text in all_jj:
                                last_det_or_adj_E2 = child.text
                                last_det_or_adj_head_E2=child.head
                            if child.deprel == 'case':
                                last_case=child.text
                                last_case_head=child.head
                                sentence_cases[last_case]=last_case_head
                            
                            if child.head == word.head and (child.deprel in  ["nmod:agent","obl:agent","acl:agent"] or child.deprel in ["nmod","obl","acl"]) and child.id in token_id_to_entity and 'by' in sentence_cases.keys():
                                if child.id == sentence_cases['by']:
                                    E2 = child.text
                                    if child.id > 1 :
                                        if last_det_or_adj_E2 in one_jj and last_det_or_adj_head_E2 == child.id:
                                            E2_cardinality = '1'
                                        elif  last_det_or_adj_E2 in many_jj and last_det_or_adj_head_E2 == child.id:
                                            E2_cardinality = 'many'

                                    relationships.add((E1_cardinality,plural_to_singular(E1), child.id , E2_cardinality, plural_to_singular(E2),'15'))

                # Apply TDR16
                if  word.head > 0:
                      sentence_cases ={}
                      last_det_or_adj_E2=''
                      last_det_or_adj_head_E2=-1
                      for child in sentence.words:
                            if child.text in all_jj:
                                last_det_or_adj_E2 = child.text
                                last_det_or_adj_head_E2=child.head
                            if child.deprel == 'case':
                                last_case=child.text
                                last_case_head=child.head
                                sentence_cases[last_case]=last_case_head
                            if child.head == word.id and (child.deprel in ["nmod","obl","acl"]) and child.id in token_id_to_entity and 'of' in sentence_cases.keys():
                             if child.id == sentence_cases['of']:
                                E2 = child.text
                                if child.id > 1 :
                                    if last_det_or_adj_E2 in one_jj and last_det_or_adj_head_E2 == child.id:
                                     E2_cardinality = '1'
                                    elif  last_det_or_adj_E2 in many_jj and last_det_or_adj_head_E2 == child.id:
                                        E2_cardinality = 'many'
                                    else : E2_cardinality=''
                                relationships.add(( E2_cardinality,plural_to_singular(E2), child.id,E1_cardinality, plural_to_singular(E1),'16'))
                # Apply TDR18
                if word.deprel == 'nsubj' and word.head > 0:
                    head_word = sentence.words[word.head - 1]
                    sentence_cases ={}
                    if head_word.upos == 'VERB':
                        last_det_or_adj_E2=''
                        last_det_or_adj_head_E2=-1
                        E2_cardinality=''
                        E3_cardinality='' 
                        E2=''
                        E2_id=-1
                        sentence_dets_adjs={}
                        for child in sentence.words:
                            if child.text in all_jj:
                                last_det_or_adj_E2 = child.text
                                last_det_or_adj_head_E2=child.head
                                sentence_dets_adjs[last_det_or_adj_E2]=last_det_or_adj_head_E2
                            if child.deprel == 'case':
                                last_case=child.text
                                last_case_head=child.head
                                sentence_cases[last_case]=last_case_head
                            if child.deprel =="obj" and child.head == head_word.id and child.id in token_id_to_entity:
                                E2=child.text
                                E2_id=child.id
                                if child.id > 1 :
                                    for adj in one_jj:
                                        if adj in sentence_dets_adjs.keys() and  child.id == sentence_dets_adjs[adj]:
                                                E2_cardinality = '1'
                                    
                                    for adj in many_jj:
                                        if adj in sentence_dets_adjs.keys() and  child.id == sentence_dets_adjs[adj]:
                                                E2_cardinality = 'many'
                         
                            if child.head == word.head and child.deprel in ["nmod","obl","acl"] and child.id in token_id_to_entity and 'to' in sentence_cases.keys() and E2 !='':
                                if child.id == sentence_cases['to']:
                                    E3 = child.text
                                    if child.id > 1 :
                                        for adj in one_jj:
                                            if adj in sentence_dets_adjs.keys() and  child.id == sentence_dets_adjs[adj]:
                                                    E3_cardinality = '1' 

                                        for adj in many_jj:
                                            if adj in sentence_dets_adjs.keys() and  child.id == sentence_dets_adjs[adj]:
                                                    E3_cardinality = 'many'

                                    relationships.add((E1_cardinality,plural_to_singular(E1),E2_id,E2_cardinality ,plural_to_singular(E2),'18_1'))
                                    relationships.add((E2_cardinality,plural_to_singular(E2), child.id, E3_cardinality,plural_to_singular(E3),'18_2'))
                                    relationships.add((E1_cardinality,plural_to_singular(E1), child.id, E3_cardinality,plural_to_singular(E3),'18_3'))

                # Apply TDR19
                if word.deprel == 'nsubj:pass' and word.head > 0:
                    head_word = sentence.words[word.head - 1]
                    sentence_cases ={}
                    last_det_or_adj_E2=''
                    last_det_or_adj_head_E2=-1
                    if head_word.xpos == 'VBN':
                        for child in sentence.words:
                            if child.text in all_jj:
                                last_det_or_adj_E2 = child.text
                                last_det_or_adj_head_E2=child.head
                            if child.deprel == 'case':
                                last_case=child.text
                                last_case_head=child.head
                                sentence_cases[last_case]=last_case_head
                            if child.head == word.head and child.deprel in ["nmod","obl","acl"] and child.id in token_id_to_entity and 'to' in sentence_cases.keys():
                                if child.id == sentence_cases['to']:
                                    E2 = child.text
                                    if child.id > 1 :
                                        if last_det_or_adj_E2 in one_jj and last_det_or_adj_head_E2 == child.id:
                                            E2_cardinality = '1'
                                        elif  last_det_or_adj_E2 in many_jj and last_det_or_adj_head_E2 == child.id:
                                            E2_cardinality = 'many'
                                        else : E2_cardinality=''
                                    relationships.add((E1_cardinality,plural_to_singular(E1),child.id,E2_cardinality,plural_to_singular(E2),'19'))

                # Apply TDR21 and TDR22
                if word.deprel == 'nsubj' and word.head > 0:
                    head_word = sentence.words[word.head - 1]
                    sentence_cases ={}
                    last_det_or_adj_E2=''
                    E2_cardinality=''
                    last_det_or_adj_head_E2=-1
                    if head_word.upos == 'VERB':
                        for child in sentence.words:
                            if child.text in all_jj:
                                last_det_or_adj_E2 = child.text
                                last_det_or_adj_head_E2=child.head
                            if child.deprel == 'case':
                                last_case=child.text
                                last_case_head=child.head
                                sentence_cases[last_case]=last_case_head
                                # print(sentence_cases.items())
                            if child.head == word.head and child.deprel in ["nmod","obl","acl"] and child.id in token_id_to_entity:
                                # to is aftkasaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                                for mod in {'in', 'for', 'on','to'}: 
                                  if mod in sentence_cases.keys() and child.id == sentence_cases[mod]:
                                    E2 = child.text
                                    if child.id > 1 :
                                        if last_det_or_adj_E2 in one_jj and last_det_or_adj_head_E2 == child.id:
                                            E2_cardinality = '1'
                                        elif  last_det_or_adj_E2 in many_jj and last_det_or_adj_head_E2 == child.id:
                                            E2_cardinality = 'many'
                                    relationships.add((E1_cardinality,plural_to_singular(E1), child.id, E2_cardinality,plural_to_singular(E2),'21,22'))
                                    break

                # Apply TDR23
                if word.deprel in ["nmod","obl","acl"]  and word.head > 0:
                    head_word = sentence.words[word.head - 1]
                    sentence_cases ={}
                    last_det_or_adj_E2=''
                    E2_cardinality=''
                    last_det_or_adj_head_E2=-1
                    if head_word.upos == 'VERB':
                        for child in sentence.words:
                            if child.text in all_jj:
                                last_det_or_adj_E2 = child.text
                                last_det_or_adj_head_E2=child.head
                            if child.deprel == 'case':
                                last_case=child.text
                                last_case_head=child.head
                                sentence_cases[last_case]=last_case_head
                            if child.head == head_word.id and child.deprel == 'obj' and 'as' in sentence_cases.keys() and child.id in token_id_to_entity:
                                if  word.id == sentence_cases['as']:
                                    E2 = child.text
                                    if child.id > 1 :
                                        if last_det_or_adj_E2 in one_jj and last_det_or_adj_head_E2 == child.id:
                                            E2_cardinality = '1'
                                        elif  last_det_or_adj_E2 in many_jj and last_det_or_adj_head_E2 == child.id:
                                            E2_cardinality = 'many'
                                    relationships.add((E1_cardinality,plural_to_singular(E1), child.id, E2_cardinality, plural_to_singular(E2),'23'))
            # our iftekasa
                if word.deprel == 'conj' and word.head > 0:
                    head_word = sentence.words[word.head - 1]
                    head_of_head = sentence.words[head_word.head-1]

                    last_det_or_adj_E2=''
                    E2_cardinality=''
                    last_det_or_adj_head_E2=-1

                    if head_of_head.upos in ['VERB','VBN']:

                        for child in sentence.words:

                            # edit: 34an nw2fo 3nd al f3l w mi3ml4 3laqa bin mcln student , section in the issue below
                            if child.id == head_of_head.id :
                                break

                            if child.text in all_jj:
                                last_det_or_adj_E2 = child.text
                                last_det_or_adj_head_E2=child.head
                            
                            if child.head == head_of_head.id and child.id in token_id_to_entity:
                                E2 =child.text
                                # cardinality
                                if child.id > 1 :
                                    if last_det_or_adj_E2 in one_jj and last_det_or_adj_head_E2 == child.id:
                                        E2_cardinality = '1'
                                    elif  last_det_or_adj_E2 in many_jj and last_det_or_adj_head_E2 == child.id:
                                        E2_cardinality = 'many'
                                    else : E2_cardinality=''
                                relationships.add((E2_cardinality,plural_to_singular(E2), word.id , E1_cardinality,plural_to_singular(E1),'2222'))
                                break
                            

            else:
                # Apply TDR24 --------------------------------------------->23*
                if word.text in ['relation','relationship']:
                    E1=''
                    last_case=''
                    E1_id=-1
                    E1_cardinality = ''
                    E2_cardinality = ''
                    if sentence.words[word.id-2].text in ['many','one','1'] and sentence.words[word.id-3].text == 'to' and sentence.words[word.id-4].text in ['many','one','1'] :
                        E1_cardinality = sentence.words[word.id-2].text
                        E2_cardinality = sentence.words[word.id-4].text
                    for child in sentence.words:
                                if child.head == word.id and child.id in token_id_to_entity :
                                  E1=child.text  
                                  E1_id=child.id
                                if child.text == 'between':
                                    last_case=child.text
                                if last_case != '' and child.id in token_id_to_entity and child.head == E1_id:
                                  E2=child.text
                                #   print(E2)
                                  relationships.add((E1_cardinality,plural_to_singular(E1), child.id,E2_cardinality, plural_to_singular(E2),'24'))
        all_sentences_relationships.append(relationships)
    return all_sentences_relationships

def associate_entities_attr(doc, entities, attributes, all_sentences_relations, entity_attributes_map):
    current_entity = None
    entities_with_attr = defaultdict(list)
    for index, sentence in zip(range(len(doc.sentences)), doc.sentences):
        sentence_words = []
        each_sentence_removed_words_ids=[]
        if len(all_sentences_relations[index]) == 0:
                for word in sentence.words:
                   sentence_words.append(word.text)
        else:
            for relation in all_sentences_relations[index]:
                # print(relation)
                _, _, entity_2_id, _, _, _ = relation
                each_sentence_removed_words_ids.append(entity_2_id)
            for word in sentence.words:
                            if word.id not in each_sentence_removed_words_ids:
                               sentence_words.append(word.text)
        # print(sentence_words)# products !

        for each_word in sentence_words:
            each_word=plural_to_singular(each_word)
            if each_word in entities:
                current_entity = each_word
            elif each_word in attributes:
                if current_entity is not None:
                    if each_word not in entities_with_attr[current_entity]:
                        entities_with_attr[current_entity].append(each_word)
                    
    return entities_with_attr

def get_primary_keys(doc,entities_with_attr,entity_attributes_map):
    # step1 : extact the primary key from text
    primary_keys = {entity: '' for entity in entities_with_attr.keys()}
    # first check it in the text 
    for sentence in doc.sentences:
        # Map token ids to entities
        # print(sentence)
        # print(entities_with_attr.keys())
        token_id_to_entity = map_entities_to_tokens(sentence, entities_with_attr.keys())
        # print(token_id_to_entity)
        for word in sentence.words:
            if word.text == 'primary_key':
                # print("nada")
                for child in sentence.words:
                                if child.id in token_id_to_entity :
                                #   print("aaa")
                                  primary_keys[child.text]=sentence.words[word.id].text
    # Step 2: For each empty primary key, assign attributes based on priority
    for entity in primary_keys:
        if primary_keys[entity] == '':

            # Priority list of attributes
            priority_attributes = ['id', 'num', 'number', 'name', entity]
            # also give higher priorities for the attributes that comes from text
            # Iterate over the priority list
            for priority_attr in priority_attributes:
                # Iterate over each attribute to check if it matches the current priority attribute
                for attribute in entities_with_attr[entity]:
                    if priority_attr in attribute and entity in entity_attributes_map :
                        # If an attribute matches the current priority, add it to the result dictionary
                        primary_keys[entity] = attribute
                        break  # Stop searching after finding the first matching attribute
                if primary_keys[entity] != '':
                    break  # Stop searching if the primary key is already set

            # print(primary_keys[entity])
            if primary_keys[entity] == '':
                # Priority list of attributes
                priority_attributes = ['id', 'num', 'number', 'name', entity]
                
                # Iterate over the priority list
                for priority_attr in priority_attributes:
                    # Iterate over each attribute to check if it matches the current priority attribute
                    if entity in entity_attributes_map:
                        for attribute in  entity_attributes_map[entity]:
                            if priority_attr in attribute:
                                # If an attribute matches the current priority, add it to the result dictionary
                                primary_keys[entity] = attribute
                                break  # Stop searching after finding the first matching attribute
                        if primary_keys[entity] != '':
                            break  # Stop searching if the primary key is already set

    # print(primary_keys)
    # step3 : search in database if it is not found any id in the attr 
    for entity in primary_keys:
        if primary_keys[entity]=='':
                primary_keys_list = df[df['Entity'] == entity]['Merged_Primary_Key'].values
                if len(primary_keys_list) > 0:
                    primary_keys_db = primary_keys_list[0].split(',')
                    for pk in  primary_keys_db:
                        if any(sub_pk in pk for sub_pk in ['id','num','number','name',entity]):
                            # If an attribute contains 'id', add it to the result dictionary
                            primary_keys[entity] = pk
                            break  # Stop searching after finding the first 'id' attribute
                    if primary_keys[entity]=='':
                          primary_keys[entity]=primary_keys_db[0]
    # print(primary_keys)
    # step4 : put the pk if it is still '' by entity_id
    for entity in primary_keys:
        if primary_keys[entity]=='':
                    # edit : removed entity from it :entity + '_id'
                    primary_keys[entity]='_id'
    # print(primary_keys) 
    for entity in entities_with_attr:
         if primary_keys[entity] not in entities_with_attr[entity]:
              entities_with_attr[entity].append(primary_keys[entity])
    return primary_keys,entities_with_attr

def merge_db_attr_with_text_attr(entity_attributes_map,entities_with_attr):
   for current_entity in entity_attributes_map:
        if current_entity in entities_with_attr:
         for attr in entity_attributes_map[current_entity]:
            if attr not in entities_with_attr[current_entity]:
                entities_with_attr[current_entity].append(attr)
        else:
           entities_with_attr[current_entity]=entity_attributes_map[current_entity]


def process_relations(relations):
    updated_all_sentences_relations=[]
    for each_sentence_relations in relations:
        updated_relations = []
        for relation in each_sentence_relations:
            entity_1_card, entity_1, relation_text, entity_2_card, entity_2, _ = relation
            if entity_1_card != '' and entity_2_card != '':
                updated_relations.append(tuple(relation)) 
                continue
            if entity_1_card == '' or entity_2_card == '':
                if entity_1_card == '':
                    entity = entity_1
                    card_pos = 0
                    other_entity = entity_2
                else:
                    entity = entity_2
                    card_pos = 3
                    other_entity = entity_1

                references = df[df['Entity'] == entity]['Merged_References'].values
                foreign_keys_1 = df[df['Entity'] == entity]['Merged_Foreign_Key_1'].values
                foreign_keys_2 = df[df['Entity'] == entity]['Merged_Foreign_Key_2'].values
                
                if len(references) > 0 and isinstance(references[0], str):
                    references_list = references[0].split(',') 
                    if other_entity in references_list:
                        index = references_list.index(other_entity)
                        foreign_keys_1_list = foreign_keys_1[0].split(',')
                        foreign_keys_2_list = foreign_keys_2[0].split(',')
                        
                        if index < len(foreign_keys_1_list) and index < len(foreign_keys_2_list):
                            updated_relation = list(relation)
                            updated_relation[card_pos] = 'many'
                            if card_pos == 0:
                                updated_relation[3] = '1'
                            else:
                                updated_relation[0] = '1'

                            updated_relation[5] = foreign_keys_1_list[index]
                            updated_relation.append(foreign_keys_2_list[index])
                            updated_relations.append(tuple(updated_relation))
                            continue
                # Default to 'many' for both if no conditions are met
                updated_relation = list(relation)
                if updated_relation[0]=='':
                 updated_relation[0] = 'many' 
                if updated_relation[3]=='':
                 updated_relation[3] = 'many'
                updated_relations.append(tuple(updated_relation))
                

        updated_all_sentences_relations.append(updated_relations)    
    return updated_all_sentences_relations


def add_missing_fk(updated_relations,entities_with_pks):
    all_modified_sentences_relations=[]
    for sentence_relation in updated_relations:
        modified_relations = []
        for relation in sentence_relation:
            
                if len(relation) == 6:
                    # print(relation)
                    first_elem, first_entity, _, fourth_elem, second_entity, _ = relation
                    if first_entity in entities_with_pks and second_entity in entities_with_pks :
                        # print(relation)
                        if first_elem == 'many' and fourth_elem == 'many':
                       
                            modified_tuple = (
                                relation[0], relation[1], relation[2], relation[3], relation[4],
                                entities_with_pks[first_entity], entities_with_pks[second_entity]
                            )
                        
                        elif first_elem == '1' and fourth_elem == 'many':
                            modified_tuple = (
                                relation[0], relation[1], relation[2], relation[3], relation[4],
                                entities_with_pks[first_entity], entities_with_pks[first_entity]
                            )
                        
                        elif (first_elem == 'many' and fourth_elem == '1') or (first_elem == '1' and fourth_elem == '1'):
                            modified_tuple = (
                                'many', relation[1], relation[2],'1', relation[4],
                                entities_with_pks[second_entity], entities_with_pks[second_entity]
                            )
                        modified_relations.append(modified_tuple)
                else:
                    if relation[1] in entities_with_pks and relation[4] in entities_with_pks :
                        modified_relations.append(relation)
            
        all_modified_sentences_relations.append(modified_relations)

    return all_modified_sentences_relations

def find_and_merge_tuples(relations):
    merged_relations = []
    merged_set = set()
    
    for i in range(len(relations)):
        if i in merged_set:
            continue
        for j in range(i + 1, len(relations)):
            if j in merged_set:
                continue
            
            t1, t2 = relations[i], relations[j]
            
            # Check merge conditions
            if (t1[0] == '1' and t1[3] == 'many' and t2[0] == '1' and t2[3] == 'many' and 
                t1[1] == t2[4] and t1[4] == t2[1]) or (t1[0] == '1' and t1[3] == 'many' and t2[0] == 'many' and t2[3] == '1' and 
                t1[1] == t2[1] and t1[4] == t2[4]):
                merged_tuple = ('many', t2[1], t2[2], 'many', t2[4], t2[5], t1[5])
                merged_relations.append(merged_tuple)
                merged_set.add(i)
                merged_set.add(j)
    
    # Add non-merged tuples to the result
    for i in range(len(relations)):
        if i not in merged_set:
            merged_relations.append(relations[i])
    
    return merged_relations


def filtering(relations):
    merged_relations = []
    merged_set = set()
    
    for i in range(len(relations)):
        if i in merged_set:
            continue
        for j in range(len(relations)):
            if j in merged_set:
                continue
            t1, t2 = relations[i], relations[j]
            if t1 == t2 :
                continue
            # Check merge conditions
            if (((t1[0] == '1' and t1[3] == 'many') or (t1[0] == 'many' and t1[3] == '1') ) and t2[0] == 'many' and t2[3] == 'many' and 
                t1[1] == t2[4] and t1[4] == t2[1]) or (((t1[0] == '1' and t1[3] == 'many') or(t1[0] == 'many' and t1[3] == '1')) and t2[0] == 'many' and t2[3] == 'many' and 
                t1[1] == t2[1] and t1[4] == t2[4]):
                merged_relations.append(t1)
                merged_set.add(i)
                merged_set.add(j)
    
    # Add non-merged tuples to the result
    for i in range(len(relations)):
        if i not in merged_set:
            merged_relations.append(relations[i])
    
    return merged_relations


def last_filtering(relations):
    merged_relations = []
    merged_set = set()

    for i in range(len(relations)):
        if i in merged_set:
            continue
        for j in range(len(relations)):
            if j in merged_set:
                continue
            t1, t2 = relations[i], relations[j]
            if t1 == t2 :
                continue
            # Check merge conditions
            if (t1[0] == t2[3] and t1[3] == t2[0] and t1[1] == t2[4] and t1[4] == t2[1]) or (t1[0] == t2[0] and t1[3] == t2[3] and t1[1] == t2[1] and t1[4] == t2[4]):
                merged_relations.append(t1)
                merged_set.add(i)
                merged_set.add(j)
    
    # Add non-merged tuples to the result
    for i in range(len(relations)):
        if i not in merged_set:
            merged_relations.append(relations[i])
    
    return merged_relations


def remove_third_element_and_convert_to_set(relationships):
    # Create a list to hold the modified tuples
    modified_tuples = []
    
    for relationship in relationships:
        # Remove the third element from the tuple
        modified_tuple = relationship[:2] + relationship[3:]
        # Append the modified tuple to the list
        modified_tuples.append(modified_tuple)
    
    # Convert the list of modified tuples to a set
    result_set = set(modified_tuples)
    
    return result_set


def run_command(command):
    """Run a system command and check for errors."""
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Command failed: {command}")
        exit(result.returncode)

def create_superuser(username, email, password):
    """Create a Django superuser."""
    python_code = f"""
from django.contrib.auth import get_user_model

User = get_user_model()
print(User.objects.filter(username='{username}').exists())
if not User.objects.filter(username='{username}').exists():
    User.objects.create_superuser(username='{username}', email='{email}', password='{password}')
print(User.objects.filter(username='{username}').exists())
print('Superuser creation script executed.')
"""
    shell_command = "python manage.py shell"
    
    # Open a subprocess to the Django shell and write the python_code to it line by line
    process = subprocess.Popen(shell_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output, error = process.communicate(input=python_code)

    # Print the output and error streams
    print("Output:\n", output)
    if error:
        print("Error:\n", error)

def register_models_in_admin():
    """Register all models in models.py with the Django admin site."""
    admin_file_path = os.path.join("library", "admin.py")
    models_file_path = os.path.join("library", "models.py")

    with open(models_file_path, "r") as models_file:
        models_content = models_file.read()

    # Extract all model class names from models.py
    model_classes = re.findall(r'class (\w+)\(', models_content)

    # Generate the admin registration lines
    admin_lines = "\n".join([f"admin.site.register({model_class})" for model_class in model_classes])

    # Write the import and registration lines to admin.py
    with open(admin_file_path, "a") as admin_file:
        admin_file.write("\nfrom .models import *\n")
        admin_file.write(admin_lines)

def remove_meta_classes(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Regex pattern to match class Meta blocks
    meta_class_pattern = re.compile(
        r'class Meta:\s*(\n\s+.*?)*?\n\s*(?=class|$)', 
        re.MULTILINE
    )

    # Remove all matches of the pattern from the content
    new_content = re.sub(meta_class_pattern, '\n', content)

    with open(file_path, 'w') as file:
        file.write(new_content)

def create_database_tables(entities_with_attr, entities_with_pks, relationships):
    sql_commands = []
    unique_tables = []

    # Iterate through entities and their attributes to generate SQL commands
    for entity, attrs in entities_with_attr.items():
        primary_key = entities_with_pks[entity]
        new_attrs = []

        # Check for relationships to add foreign keys
        for relationship in relationships:
            card1, entity1, card2, entity2, pk1, pk2 = relationship
            if card1 == 'many' and entity == entity1 and card2 == '1':
                if f'{entity2}__{pk2}' not in attrs:
                    new_attrs.append(f'{entity2}__{pk2}')
            elif card2 == 'many' and entity == entity2 and card1 == '1':
                if f'{entity1}__{pk1}' not in attrs:
                    new_attrs.append(f'{entity1}__{pk1}')

        # Construct SQL for attributes
        attrs_sql_1 = ", ".join([f"{attr} TEXT NOT NULL" if attr == primary_key else f"{attr} TEXT" for attr in attrs])
        attrs_sql_2 = ", ".join([f"{attr} TEXT NOT NULL" for attr in new_attrs])
        if attrs_sql_2 != '':
            attrs_sql = attrs_sql_1 + ',' + attrs_sql_2
        else:
            attrs_sql = attrs_sql_1

        # Create table SQL statement
        if entity not in unique_tables:
            sql = f"CREATE TABLE IF NOT EXISTS {entity} ({attrs_sql}, PRIMARY KEY ({primary_key}));"
            unique_tables.append(entity)

            # Handle relationships for many-to-many
            for relationship in relationships:
                card1, entity1, card2, entity2, pk1, pk2 = relationship
                if card1 == 'many' and card2 == 'many':
                    pk_1 = f"{entity1}__{pk1}"
                    pk_2 = f"{entity2}__{pk2}"
                    table_name = f"{entity1}_{entity2}"
                    if table_name not in unique_tables:
                        sql_many_many = f"CREATE TABLE IF NOT EXISTS {table_name} ({pk_1} TEXT NOT NULL, {pk_2} TEXT NOT NULL, PRIMARY KEY ({pk_1}, {pk_2}), FOREIGN KEY ({pk_1}) REFERENCES {entity1}({pk1}), FOREIGN KEY ({pk_2}) REFERENCES {entity2}({pk2}));"
                        unique_tables.append(table_name)
                        sql_commands.append(sql_many_many)
                elif card1 == 'many' and entity == entity1 and card2 == '1':
                    pk_2 = f"{entity2}__{pk2}"
                    sql = sql.replace(');', f", FOREIGN KEY ({pk_2}) REFERENCES {entity2}({pk2}));")
                elif card2 == 'many' and entity == entity2 and card1 == '1':
                    pk_1 = f"{entity1}__{pk1}"
                    sql = sql.replace(');', f", FOREIGN KEY ({pk_1}) REFERENCES {entity1}({pk1}));")

            sql_commands.append(sql)

    # Connect to SQLite database
    conn = sqlite3.connect('_db.sqlite3')
    cursor = conn.cursor()

    # Execute SQL commands to create tables
    for command in sql_commands:
        cursor.execute(command)

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("Database and tables created successfully.")


def create_django_project():
    """Create a Django project and an app named 'library'."""
    # Install Django
    run_command("pip install django")
    
    # Start a new Django project named 'myproject'
    run_command("django-admin startproject myproject")
    
    # Change directory to 'myproject'
    os.chdir("myproject")
    
    # Start a new app named 'library'
    run_command("python manage.py startapp library")
    
    # Add 'library' to INSTALLED_APPS in settings.py
    settings_path = os.path.join("myproject", "settings.py")
    with open(settings_path, "r") as file:
        settings_content = file.read()
    
    settings_content = settings_content.replace(
        "INSTALLED_APPS = [",
        "INSTALLED_APPS = [\n    'library',"
    )
    
    with open(settings_path, "w") as file:
        file.write(settings_content)
    
    # Make migrations and migrate the database
    run_command("python manage.py makemigrations")
    run_command("python manage.py migrate")
    
    # Create the superuser with specified credentials
    create_superuser("aya", "aya@h.com", "malika")

    # Save the credentials in a text file
    with open("superuser_credentials.txt", "w") as file:
        file.write("Username: admin\n")
        file.write("Email:a@h.com\n")
        file.write("Password:a\n")
    
    # Rename original db.sqlite3 to wdb.sqlite3 if it exists
    if os.path.exists("db.sqlite3"):
        os.rename("db.sqlite3", "wdb.sqlite3")
    
    # Rename ../../_db.sqlite3 to db.sqlite3 and move it inside myproject
    outer_db_path = os.path.abspath(os.path.join("../", "_db.sqlite3"))
    if os.path.exists(outer_db_path):
        new_db_path = os.path.join(os.getcwd(), "db.sqlite3")
        os.rename(outer_db_path, new_db_path)
    
    # Run inspectdb command and save output to models.py
    run_command("python manage.py inspectdb > models.py")
    
    # Overwrite library/models.py with the content of models.py
    shutil.copyfile("models.py", os.path.join("library", "models.py"))
 
    input_file = os.path.join("library", "models.py")

    remove_meta_classes(input_file)

    # Rename original db.sqlite3 to _db.sqlite3 if it exists
    if os.path.exists("db.sqlite3"):
        os.rename("db.sqlite3", "_db.sqlite3")

    # Rename original wdb.sqlite3 to db.sqlite3 if it exists
    if os.path.exists("wdb.sqlite3"):
        os.rename("wdb.sqlite3", "db.sqlite3")

    # Make migrations and migrate the database
    run_command("python manage.py makemigrations")
    run_command("python manage.py migrate")
    
    # Register all models in admin.py
    register_models_in_admin()
    
    run_command("python manage.py runserver")

