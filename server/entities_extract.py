
import sys
import json
from util import (
    enhance_entities,
    plural_to_singular,
    predict_entities_and_attributes,
)
def get_entities(description): 


    entities_snake_case,attributes_snake_case=predict_entities_and_attributes(description)
    attributes_final=list(set(attributes_snake_case))
    
    ent_array,attributes_final = enhance_entities(description, entities_snake_case, attributes_final)

    ent_array_sing = [plural_to_singular(ent) for ent in ent_array]
    ent_array=list(set(ent_array_sing))

    return ent_array

if __name__ == "__main__":
    input_text = sys.argv[1]
    output = get_entities(input_text)
    print(json.dumps(output))