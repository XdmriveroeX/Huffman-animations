from manim import *
from shannon_fano_visualization import ShannonFanoTree

def shannon_fano(symbols, probabilities):
    if len(symbols) <= 1:
        return {symbols[0]: ''}
    
    sorted_data = sorted(zip(symbols, probabilities), key=lambda x: x[1], reverse=True)
    symbols, probabilities = zip(*sorted_data)
    
    total = sum(probabilities)
    split_point = 0
    split_sum = 0
    while split_sum < total / 2:
        split_sum += probabilities[split_point]
        split_point += 1
    
    left_codes = shannon_fano(symbols[:split_point], probabilities[:split_point])
    right_codes = shannon_fano(symbols[split_point:], probabilities[split_point:])
    
    return {**{s: '0' + c for s, c in left_codes.items()},
            **{s: '1' + c for s, c in right_codes.items()}}

def encode_text(text, code_dict):
    return ''.join(code_dict[char] for char in text if char in code_dict)

def calculate_probabilities(text):
    char_count = {}
    total = len(text)
    for char in text:
        char_count[char] = char_count.get(char, 0) + 1
    return {char: count / total for char, count in char_count.items()}

def visualize_shannon_fano(symbols, probabilities):
    scene = ShannonFanoTree()
    scene.render()

if __name__ == "__main__":
    text = input("Enter text to encode: ")
    probabilities = calculate_probabilities(text)
    symbols = list(probabilities.keys())
    
    code_dict = shannon_fano(symbols, list(probabilities.values()))
    encoded_text = encode_text(text, code_dict)
    
    print("Shannon-Fano Codes:", code_dict)
    print("Encoded text:", encoded_text)
    
    visualize_shannon_fano(symbols, list(probabilities.values()))
