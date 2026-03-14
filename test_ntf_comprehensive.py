#!/usr/bin/env python3
"""Comprehensive NTF Testing Suite - Unit, Integration, and Performance Tests."""

import json
import time
import sys
from ntf_standard import run_ntf, normalize_text, compress_tokens, compute_intfr, NTF_VOCAB

class TestResults:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
    
    def add(self, name, passed, message=""):
        self.tests.append({"name": name, "passed": passed, "message": message})
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def summary(self):
        total = self.passed + self.failed
        return {
            "total": total,
            "passed": self.passed,
            "failed": self.failed,
            "success_rate": round((self.passed / total * 100) if total > 0 else 0, 1)
        }

def test_normalization():
    """Test 1: Normalisierung funktioniert korrekt."""
    results = TestResults()
    
    test_cases = [
        ("Hello World", ["hello", "world"]),
        ("test-case", ["test", "case"]),
        ("123 abc", ["123", "abc"]),
        ("", []),
    ]
    
    for input_text, expected in test_cases:
        output = normalize_text(input_text)
        passed = output == expected
        results.add(f"normalize({repr(input_text)})", passed, f"Expected {expected}, got {output}")
    
    return results

def test_keyword_mapping():
    """Test 2: Keyword-Mapping ist vollständig."""
    results = TestResults()
    
    from ntf_standard import KEYWORD_MAP
    
    # Alle Synonyme sollten gemappt sein
    for synonym, concept in KEYWORD_MAP.items():
        passed = concept in NTF_VOCAB
        results.add(f"keyword_map({synonym})", passed, f"Mapped to {concept}")
    
    # Alle Konzepte sollten existieren
    for concept in NTF_VOCAB:
        has_mapping = any(v == concept for v in KEYWORD_MAP.values())
        results.add(f"concept_exists({concept})", has_mapping)
    
    return results

def test_intfr_calculation():
    """Test 3: INTFR-Berechnung ist korrekt."""
    results = TestResults()
    
    test_cases = [
        (0.5, 0.5, 0.5, 1.25),  # (0.5 * 0.5 * 0.5) * 10 = 1.25
        (1.0, 1.0, 1.0, 10.0),  # (1.0 * 1.0 * 1.0) * 10 = 10.0
        (0.0, 0.0, 0.0, 0.0),   # (0.0 * 0.0 * 0.0) * 10 = 0.0
    ]
    
    for coverage, ratio, diversity, expected in test_cases:
        result = compute_intfr(coverage, ratio, diversity)
        passed = result == expected
        results.add(f"intfr({coverage}, {ratio}, {diversity})", passed, f"Expected {expected}, got {result}")
    
    return results

def test_entropy_density_progression():
    """Test 4: Entropiedichte-Abhängigkeit (der "Knick")."""
    results = TestResults()
    
    import random
    random.seed(42)
    
    from ntf_standard import KEYWORD_MAP
    keywords = list(KEYWORD_MAP.keys())
    filler = ["the", "a", "is", "and", "or", "but", "process", "system", "data"]
    
    densities = [0.05, 0.1, 0.2, 0.5, 0.8]
    text_length = 1000
    
    intfr_values = []
    
    for density in densities:
        words = []
        for _ in range(text_length):
            if random.random() < density:
                words.append(random.choice(keywords))
            else:
                words.append(random.choice(filler))
        
        text = " ".join(words)
        res = run_ntf(text)
        intfr_values.append(res.intfr)
        
        # INTFR sollte mit Entropiedichte steigen
        passed = res.intfr >= 0
        results.add(f"entropy_density({density*100}%)", passed, f"INTFR={res.intfr}")
    
    # Überprüfe, dass INTFR monoton steigt
    for i in range(len(intfr_values) - 1):
        passed = intfr_values[i] <= intfr_values[i+1]
        results.add(f"intfr_monotonic({densities[i]*100}% -> {densities[i+1]*100}%)", passed, 
                   f"{intfr_values[i]} <= {intfr_values[i+1]}")
    
    return results

def test_compression_ratio():
    """Test 5: Kompressionsverhältnis ist sinnvoll."""
    results = TestResults()
    
    import random
    random.seed(42)
    
    from ntf_standard import KEYWORD_MAP
    keywords = list(KEYWORD_MAP.keys())
    
    # Test mit 80% Entropiedichte (sollte gut komprimieren)
    words = []
    for _ in range(500):
        if random.random() < 0.8:
            words.append(random.choice(keywords))
        else:
            words.append("filler")
    
    text = " ".join(words)
    res = run_ntf(text)
    
    # Bei 80% Entropiedichte sollte Ratio > 1.5x sein
    ratio = res.original_words / res.compressed_tokens if res.compressed_tokens > 0 else 0
    passed = ratio > 1.5
    results.add(f"compression_ratio(80% entropy)", passed, f"Ratio={ratio}x (expected > 1.5x)")
    
    # Bei 5% Entropiedichte sollte Ratio ≈ 1.0x sein
    words = []
    for _ in range(500):
        if random.random() < 0.05:
            words.append(random.choice(keywords))
        else:
            words.append("filler")
    
    text = " ".join(words)
    res = run_ntf(text)
    ratio = res.original_words / res.compressed_tokens if res.compressed_tokens > 0 else 0
    passed = ratio < 1.1
    results.add(f"compression_ratio(5% entropy)", passed, f"Ratio={ratio}x (expected < 1.1x)")
    
    return results

def test_edge_cases():
    """Test 6: Edge Cases."""
    results = TestResults()
    
    edge_cases = [
        ("", "empty_text"),
        ("flux", "single_keyword"),
        ("flux flux flux", "repeated_keyword"),
        ("the the the", "repeated_filler"),
        ("flux anchor drift pulse mirror weave relay horizon resonance folding consensus overclock deployment checkpoint synthesis state", "all_keywords"),
    ]
    
    for text, description in edge_cases:
        try:
            res = run_ntf(text)
            passed = res.original_words >= 0
            results.add(f"edge_case({description})", passed, f"Processed successfully")
        except Exception as e:
            results.add(f"edge_case({description})", False, str(e))
    
    return results

def test_performance():
    """Test 7: Performance-Tests."""
    results = TestResults()
    
    import random
    random.seed(42)
    
    from ntf_standard import KEYWORD_MAP
    keywords = list(KEYWORD_MAP.keys())
    filler = ["the", "a", "is", "and", "or", "but"]
    
    text_lengths = [100, 500, 1000, 5000]
    
    for length in text_lengths:
        words = []
        for _ in range(length):
            if random.random() < 0.5:
                words.append(random.choice(keywords))
            else:
                words.append(random.choice(filler))
        
        text = " ".join(words)
        
        start = time.time()
        res = run_ntf(text)
        duration_ms = (time.time() - start) * 1000
        
        # Sollte unter 50ms sein
        passed = duration_ms < 50
        results.add(f"performance({length} words)", passed, f"Duration: {duration_ms:.2f}ms")
    
    return results

def test_consistency():
    """Test 8: Konsistenz - mehrfaches Ausführen sollte gleiche Ergebnisse liefern."""
    results = TestResults()
    
    test_text = "flux anchor drift pulse mirror weave relay horizon resonance folding consensus overclock deployment checkpoint synthesis state the process system data agent network"
    
    results_list = []
    for i in range(3):
        res = run_ntf(test_text)
        results_list.append({
            "original_words": res.original_words,
            "compressed_tokens": res.compressed_tokens,
            "intfr": res.intfr
        })
    
    # Alle Ergebnisse sollten identisch sein
    for i in range(1, len(results_list)):
        passed = results_list[i] == results_list[0]
        results.add(f"consistency_run_{i}", passed, f"Result matches first run")
    
    return results

def run_all_tests():
    """Führe alle Tests aus."""
    print("=" * 80)
    print("NTF COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()
    
    all_results = {}
    
    test_suites = [
        ("Unit Tests: Normalisierung", test_normalization),
        ("Unit Tests: Keyword-Mapping", test_keyword_mapping),
        ("Unit Tests: INTFR-Berechnung", test_intfr_calculation),
        ("Integration Tests: Entropiedichte-Abhängigkeit", test_entropy_density_progression),
        ("Integration Tests: Kompressionsverhältnis", test_compression_ratio),
        ("Integration Tests: Edge Cases", test_edge_cases),
        ("Performance Tests", test_performance),
        ("Consistency Tests", test_consistency),
    ]
    
    for suite_name, test_func in test_suites:
        print(f"\n{suite_name}")
        print("-" * 80)
        
        results = test_func()
        all_results[suite_name] = results
        
        summary = results.summary()
        print(f"✓ Passed: {results.passed} | ✗ Failed: {results.failed} | Success Rate: {summary['success_rate']}%")
        
        for test in results.tests:
            status = "✓" if test["passed"] else "✗"
            message = f" ({test['message']})" if test["message"] else ""
            print(f"  {status} {test['name']}{message}")
    
    # Gesamtzusammenfassung
    print("\n" + "=" * 80)
    print("GESAMTZUSAMMENFASSUNG")
    print("=" * 80)
    
    total_passed = sum(r.passed for r in all_results.values())
    total_failed = sum(r.failed for r in all_results.values())
    total_tests = total_passed + total_failed
    
    print(f"Gesamt: {total_passed}/{total_tests} Tests bestanden ({round(total_passed/total_tests*100, 1)}%)")
    print()
    
    # Speichere Ergebnisse als JSON
    test_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": total_tests,
        "passed": total_passed,
        "failed": total_failed,
        "success_rate": round(total_passed / total_tests * 100, 1),
        "suites": {
            name: {
                "passed": results.passed,
                "failed": results.failed,
                "success_rate": results.summary()["success_rate"],
                "tests": results.tests
            }
            for name, results in all_results.items()
        }
    }
    
    with open("test_results.json", "w") as f:
        json.dump(test_report, f, indent=2)
    
    print(f"✓ Test-Ergebnisse gespeichert in: test_results.json")
    
    return total_failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
