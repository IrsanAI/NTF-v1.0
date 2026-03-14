#!/usr/bin/env python3
import time
import json
import math
import random
from ntf_standard import run_ntf, NTF_VOCAB, KEYWORD_MAP

def generate_text(length, entropy_density):
    """
    Generiert Text mit einer bestimmten Dichte an NTF-Keywords.
    entropy_density: 0.0 bis 1.0 (Wahrscheinlichkeit, dass ein Wort ein NTF-Keyword ist)
    """
    keywords = list(KEYWORD_MAP.keys())
    filler = ["the", "a", "is", "and", "or", "but", "process", "system", "data", "agent", "network", "node"]
    
    words = []
    for _ in range(length):
        if random.random() < entropy_density:
            words.append(random.choice(keywords))
        else:
            words.append(random.choice(filler))
    return " ".join(words)

def run_benchmark():
    lengths = [10, 50, 100, 500, 1000, 5000]
    densities = [0.05, 0.1, 0.2, 0.5, 0.8]
    
    results = []
    
    print(f"| Length | Density | Original Words | Compressed Tokens | Ratio | INTFR | Time (ms) |")
    print(f"|---:|---:|---:|---:|---:|---:|---:|")
    
    for length in lengths:
        for density in densities:
            text = generate_text(length, density)
            
            start_time = time.time()
            res = run_ntf(text)
            end_time = time.time()
            
            duration_ms = (end_time - start_time) * 1000
            
            # Tatsächliche Ratio berechnen (Original / Compressed)
            actual_ratio = res.original_words / res.compressed_tokens if res.compressed_tokens > 0 else 0
            
            results.append({
                "length": length,
                "density": density,
                "original_words": res.original_words,
                "compressed_tokens": res.compressed_tokens,
                "ratio": round(actual_ratio, 2),
                "intfr": res.intfr,
                "duration_ms": round(duration_ms, 4)
            })
            
            print(f"| {length} | {density*100}% | {res.original_words} | {res.compressed_tokens} | {round(actual_ratio, 2)}x | {res.intfr} | {round(duration_ms, 2)} |")

    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_benchmark()
