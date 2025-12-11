"""
API Test Results Analyzer

Analyzes the CSV results from automated_api_tests.py and generates
summary statistics and insights for the Tuesday meeting.
"""

import csv
import statistics
from pathlib import Path
from datetime import datetime
from collections import defaultdict


RESULTS_DIR = Path(__file__).parent / "test_results"
RESULTS_FILE = RESULTS_DIR / "api_test_results.csv"


def load_results():
    """Load test results from CSV file."""
    if not RESULTS_FILE.exists():
        print(f"❌ No results file found at {RESULTS_FILE}")
        print("   Run automated_api_tests.py first to generate data.")
        return []
    
    results = []
    with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            for field in ['age', 'intake_response_time', 'message_response_time', 
                         'total_response_time', 'trials_found', 'intake_status', 'message_status']:
                if row.get(field) and row[field] != 'None':
                    try:
                        if field in ['age', 'trials_found', 'intake_status', 'message_status']:
                            row[field] = int(float(row[field]))
                        else:
                            row[field] = float(row[field])
                    except ValueError:
                        row[field] = None
            
            # Convert boolean
            row['success'] = row.get('success', '').lower() == 'true'
            
            results.append(row)
    
    return results


def analyze_results(results):
    """Generate comprehensive analysis of test results."""
    if not results:
        print("No results to analyze.")
        return
    
    print("\n" + "="*80)
    print(" 📊 MaleCare ChatBot - API Performance Test Results Analysis")
    print("="*80)
    
    # Basic stats
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - successful_tests
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📈 OVERALL STATISTICS")
    print("-"*80)
    print(f"Total Tests Run: {total_tests}")
    print(f"Successful Tests: {successful_tests} ({success_rate:.1f}%)")
    print(f"Failed Tests: {failed_tests} ({100-success_rate:.1f}%)")
    
    if results[0].get('timestamp') and results[-1].get('timestamp'):
        first_test = datetime.fromisoformat(results[0]['timestamp'])
        last_test = datetime.fromisoformat(results[-1]['timestamp'])
        duration = last_test - first_test
        print(f"Test Period: {first_test.strftime('%Y-%m-%d %H:%M')} to {last_test.strftime('%Y-%m-%d %H:%M')}")
        print(f"Duration: {duration.days} days, {duration.seconds // 3600} hours")
    
    # Response time analysis
    response_times = [r['total_response_time'] for r in results if r.get('total_response_time') is not None]
    intake_times = [r['intake_response_time'] for r in results if r.get('intake_response_time') is not None]
    message_times = [r['message_response_time'] for r in results if r.get('message_response_time') is not None]
    
    if response_times:
        print(f"\n⏱️  RESPONSE TIME ANALYSIS")
        print("-"*80)
        print(f"Total Response Times:")
        print(f"  Average: {statistics.mean(response_times):.6f} seconds")
        print(f"  Median:  {statistics.median(response_times):.6f} seconds")
        print(f"  Min:     {min(response_times):.6f} seconds")
        print(f"  Max:     {max(response_times):.6f} seconds")
        if len(response_times) > 1:
            print(f"  Std Dev: {statistics.stdev(response_times):.6f} seconds")
        
        under_3s = sum(1 for t in response_times if t < 3.0)
        print(f"\n  Tests under 3 seconds: {under_3s}/{len(response_times)} ({under_3s/len(response_times)*100:.1f}%)")
        
        if intake_times:
            print(f"\nIntake Endpoint:")
            print(f"  Average: {statistics.mean(intake_times):.6f} seconds")
            print(f"  Min:     {min(intake_times):.6f} seconds")
            print(f"  Max:     {max(intake_times):.6f} seconds")
        
        if message_times:
            print(f"\nMessage Endpoint (Trial Search):")
            print(f"  Average: {statistics.mean(message_times):.6f} seconds")
            print(f"  Min:     {min(message_times):.6f} seconds")
            print(f"  Max:     {max(message_times):.6f} seconds")
    
    # Cancer type breakdown
    cancer_stats = defaultdict(lambda: {'total': 0, 'successful': 0, 'trials': []})
    for r in results:
        cancer_type = r.get('cancer_type', 'Unknown')
        cancer_stats[cancer_type]['total'] += 1
        if r['success']:
            cancer_stats[cancer_type]['successful'] += 1
        if r.get('trials_found') is not None:
            cancer_stats[cancer_type]['trials'].append(r['trials_found'])
    
    print(f"\n🎗️  CANCER TYPE BREAKDOWN")
    print("-"*80)
    for cancer_type in sorted(cancer_stats.keys()):
        stats = cancer_stats[cancer_type]
        success_rate = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
        avg_trials = statistics.mean(stats['trials']) if stats['trials'] else 0
        
        print(f"\n{cancer_type.title()}:")
        print(f"  Tests: {stats['total']}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Avg Trials Found: {avg_trials:.1f}")
        if stats['trials']:
            print(f"  Min Trials: {min(stats['trials'])}")
            print(f"  Max Trials: {max(stats['trials'])}")
    
    # Location analysis
    location_stats = defaultdict(int)
    for r in results:
        if r.get('location'):
            location_stats[r['location']] += 1
    
    print(f"\n📍 LOCATION COVERAGE")
    print("-"*80)
    for location in sorted(location_stats.keys(), key=lambda x: location_stats[x], reverse=True):
        print(f"  {location}: {location_stats[location]} tests")
    
    # Error analysis
    intake_errors = [r for r in results if r.get('intake_error')]
    message_errors = [r for r in results if r.get('message_error')]
    
    if intake_errors or message_errors:
        print(f"\n⚠️  ERROR ANALYSIS")
        print("-"*80)
        
        if intake_errors:
            print(f"Intake Endpoint Errors: {len(intake_errors)}")
            error_types = defaultdict(int)
            for r in intake_errors:
                error_types[r['intake_error']] += 1
            for error, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  - {error}: {count} occurrences")
        
        if message_errors:
            print(f"\nMessage Endpoint Errors: {len(message_errors)}")
            error_types = defaultdict(int)
            for r in message_errors:
                error_types[r['message_error']] += 1
            for error, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  - {error}: {count} occurrences")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS FOR TUESDAY MEETING")
    print("-"*80)
    
    if response_times:
        avg_time = statistics.mean(response_times)
        if avg_time >= 3.0:
            print("❗ Average response time exceeds 3 second target")
            print("   → Consider optimizing API queries or caching")
        else:
            print(f"✅ Average response time ({avg_time:.3f}s) meets <3s target")
    
    if success_rate < 95:
        print(f"❗ Success rate ({success_rate:.1f}%) below optimal")
        print("   → Review error logs and implement better error handling")
    else:
        print(f"✅ Success rate ({success_rate:.1f}%) is excellent")
    
    # Check if all cancer types tested
    cancer_types_tested = set(cancer_stats.keys())
    expected_types = {"breast cancer", "prostate cancer", "lung cancer"}
    missing_types = expected_types - cancer_types_tested
    
    if missing_types:
        print(f"❗ Missing cancer types: {', '.join(missing_types)}")
    else:
        print("✅ All three cancer types tested successfully")
    
    # Trials found analysis
    all_trials = [r['trials_found'] for r in results if r.get('trials_found') is not None]
    if all_trials:
        avg_trials = statistics.mean(all_trials)
        zero_results = sum(1 for t in all_trials if t == 0)
        print(f"\n📊 Trial Results:")
        print(f"   Average trials per search: {avg_trials:.1f}")
        if zero_results > 0:
            print(f"   Searches with no results: {zero_results}/{len(all_trials)} ({zero_results/len(all_trials)*100:.1f}%)")
    
    print("\n" + "="*80 + "\n")


def generate_summary_report():
    """Generate a concise summary report for the meeting."""
    results = load_results()
    
    if not results:
        return
    
    analyze_results(results)
    
    # Generate CSV summary
    summary_file = RESULTS_DIR / "summary_report.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("MaleCare ChatBot - API Performance Test Summary\n")
        f.write("="*80 + "\n\n")
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r['success'])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        f.write(f"Total Tests: {total_tests}\n")
        f.write(f"Success Rate: {success_rate:.1f}%\n\n")
        
        response_times = [r['total_response_time'] for r in results if r.get('total_response_time') is not None]
        if response_times:
            f.write(f"Average Response Time: {statistics.mean(response_times):.6f} seconds\n")
            f.write(f"Target (<3s): {'PASS' if statistics.mean(response_times) < 3.0 else 'FAIL'}\n\n")
        
        f.write("Cancer Types Tested:\n")
        cancer_stats = defaultdict(int)
        for r in results:
            cancer_stats[r.get('cancer_type', 'Unknown')] += 1
        for cancer_type, count in sorted(cancer_stats.items()):
            f.write(f"  - {cancer_type}: {count} tests\n")
    
    print(f"✅ Summary report saved to: {summary_file}")


if __name__ == "__main__":
    generate_summary_report()
