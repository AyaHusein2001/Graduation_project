import sys
import json

def process_elements(elements):
    lengths = [len(element) for element in elements]
    return lengths

if __name__ == '__main__':
    elements = json.loads(sys.argv[1])
    result = process_elements(elements)
    print(json.dumps(result))
