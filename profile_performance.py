#!/usr/bin/env python3
"""
Performance profiling script for the LangQuality Toolkit.
Tests that 10,000 sentences can be processed in under 5 minutes.
"""

import sys
import os
import time
import cProfile
import pstats
from pathlib import Path
from io import StringIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from langquality.data.loader import DataLoader
from langquality.data.models import Sentence
from langquality.config.loader import ConfigLoader
from langquality.pipeline.controller import PipelineController


def generate_test_sentences(count=10000):
    """Generate test sentences for performance testing."""
    print(f"Generating {count} test sentences...")
    
    # Sample French sentences of varying complexity
    templates = [
        "Le chat mange du poisson.",
        "Les étudiants apprennent le français à l'école.",
        "La médecine moderne permet de soigner de nombreuses maladies.",
        "L'agriculture est essentielle pour nourrir la population.",
        "Le commerce international favorise les échanges culturels.",
        "La famille se réunit pour célébrer les fêtes traditionnelles.",
        "Les enfants jouent dans le parc tous les jours.",
        "Le médecin examine le patient avec attention.",
        "L'enseignant explique la leçon aux élèves attentivement.",
        "Les agriculteurs cultivent le maïs et le riz dans les champs.",
    ]
    
    domains = ["education", "sante", "agriculture", "commerce", "famille"]
    
    sentences = []
    for i in range(count):
        template = templates[i % len(templates)]
        domain = domains[i % len(domains)]
        
        # Add variation
        text = f"{template} Phrase numéro {i+1}."
        
        sentence = Sentence(
            text=text,
            domain=domain,
            source_file=f"test_{domain}.csv",
            line_number=i+1,
            char_count=len(text),
            word_count=len(text.split()),
            metadata={}
        )
        sentences.append(sentence)
    
    print(f"✓ Generated {len(sentences)} sentences")
    return sentences


def profile_pipeline(sentences, config):
    """Profile the pipeline execution."""
    print(f"\nProfiling pipeline with {len(sentences)} sentences...")
    
    # Create profiler
    profiler = cProfile.Profile()
    
    # Run pipeline with profiling
    controller = PipelineController(config)
    
    start_time = time.time()
    profiler.enable()
    
    results = controller.run(sentences)
    
    profiler.disable()
    end_time = time.time()
    
    elapsed = end_time - start_time
    
    return results, elapsed, profiler


def analyze_performance(elapsed, sentence_count, profiler):
    """Analyze performance metrics."""
    print("\n" + "="*60)
    print("PERFORMANCE ANALYSIS")
    print("="*60)
    
    print(f"\nTotal sentences: {sentence_count}")
    print(f"Total time: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
    print(f"Sentences per second: {sentence_count/elapsed:.2f}")
    print(f"Time per sentence: {elapsed/sentence_count*1000:.2f} ms")
    
    # Check if meets requirement (10,000 sentences in < 5 minutes)
    target_time = 300  # 5 minutes in seconds
    projected_time_10k = (elapsed / sentence_count) * 10000
    
    print(f"\nProjected time for 10,000 sentences: {projected_time_10k:.2f}s ({projected_time_10k/60:.2f} min)")
    
    if projected_time_10k < target_time:
        print(f"✓ PASS: Meets performance requirement (< 5 minutes)")
        margin = target_time - projected_time_10k
        print(f"  Margin: {margin:.2f}s ({margin/60:.2f} min)")
    else:
        print(f"✗ FAIL: Does not meet performance requirement")
        excess = projected_time_10k - target_time
        print(f"  Excess time: {excess:.2f}s ({excess/60:.2f} min)")
    
    # Show profiling stats
    print("\n" + "="*60)
    print("TOP 20 TIME-CONSUMING FUNCTIONS")
    print("="*60)
    
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.strip_dirs()
    ps.sort_stats('cumulative')
    ps.print_stats(20)
    
    print(s.getvalue())
    
    # Identify bottlenecks
    print("\n" + "="*60)
    print("BOTTLENECK ANALYSIS")
    print("="*60)
    
    ps = pstats.Stats(profiler)
    ps.strip_dirs()
    ps.sort_stats('cumulative')
    
    stats = ps.stats
    bottlenecks = []
    
    for func, (cc, nc, tt, ct, callers) in stats.items():
        if ct > elapsed * 0.1:  # Functions taking > 10% of total time
            func_name = f"{func[0]}:{func[1]}:{func[2]}"
            bottlenecks.append((func_name, ct, ct/elapsed*100))
    
    if bottlenecks:
        print("\nFunctions consuming > 10% of total time:")
        for func_name, time_spent, percentage in sorted(bottlenecks, key=lambda x: x[1], reverse=True):
            print(f"  - {func_name}")
            print(f"    Time: {time_spent:.2f}s ({percentage:.1f}%)")
    else:
        print("\n✓ No major bottlenecks detected (no single function > 10% of time)")
    
    return projected_time_10k < target_time


def test_scalability():
    """Test performance at different scales."""
    print("\n" + "="*60)
    print("SCALABILITY TEST")
    print("="*60)
    
    config_loader = ConfigLoader()
    config = config_loader.load_config("config/default_config.yaml")
    
    test_sizes = [100, 500, 1000, 2000, 5000]
    results_data = []
    
    for size in test_sizes:
        print(f"\nTesting with {size} sentences...")
        sentences = generate_test_sentences(size)
        
        controller = PipelineController(config)
        start = time.time()
        controller.run(sentences)
        elapsed = time.time() - start
        
        rate = size / elapsed
        results_data.append((size, elapsed, rate))
        print(f"  Time: {elapsed:.2f}s, Rate: {rate:.2f} sentences/s")
    
    # Analyze scalability
    print("\n" + "="*60)
    print("SCALABILITY ANALYSIS")
    print("="*60)
    
    print("\nSize | Time (s) | Rate (sent/s) | Time/sent (ms)")
    print("-" * 55)
    for size, elapsed, rate in results_data:
        time_per_sent = elapsed / size * 1000
        print(f"{size:5d} | {elapsed:8.2f} | {rate:13.2f} | {time_per_sent:14.2f}")
    
    # Check if performance degrades significantly
    if len(results_data) >= 2:
        first_rate = results_data[0][2]
        last_rate = results_data[-1][2]
        degradation = (first_rate - last_rate) / first_rate * 100
        
        print(f"\nPerformance degradation: {degradation:.1f}%")
        if degradation < 20:
            print("✓ Good scalability (< 20% degradation)")
        elif degradation < 50:
            print("⚠ Moderate scalability (20-50% degradation)")
        else:
            print("✗ Poor scalability (> 50% degradation)")


def main():
    """Run performance profiling."""
    print("="*60)
    print("LANGQUALITY TOOLKIT - PERFORMANCE PROFILING")
    print("="*60)
    
    # Load configuration
    config_loader = ConfigLoader()
    config = config_loader.load_config("config/default_config.yaml")
    
    # Test with different sizes
    test_sizes = [1000, 5000, 10000]
    
    for size in test_sizes:
        print(f"\n{'='*60}")
        print(f"TESTING WITH {size} SENTENCES")
        print(f"{'='*60}")
        
        sentences = generate_test_sentences(size)
        results, elapsed, profiler = profile_pipeline(sentences, config)
        
        meets_requirement = analyze_performance(elapsed, size, profiler)
        
        if size == 10000:
            if meets_requirement:
                print("\n" + "="*60)
                print("✓ PERFORMANCE REQUIREMENT MET")
                print("="*60)
                print("\n10,000 sentences processed in under 5 minutes!")
            else:
                print("\n" + "="*60)
                print("✗ PERFORMANCE REQUIREMENT NOT MET")
                print("="*60)
                print("\nOptimization needed to meet the 5-minute target.")
                return 1
    
    # Run scalability test
    test_scalability()
    
    print("\n" + "="*60)
    print("PROFILING COMPLETE")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
