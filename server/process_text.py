import sys
import json

def process_text(text):
    # Split the text into words
    words = text.split()
    return words

if __name__ == "__main__":
    input_text = sys.argv[1]
    output = process_text(input_text)
    print(json.dumps(output))
