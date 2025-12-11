"""
Weekend Monitoring Results Analyzer
Run this Monday morning to analyze the weekend API test results

Generates summary statistics and identifies any issues
"""

import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict

CSV_FILE = Path(__file__).parent / "weekend_api_monitoring.csv"


def analyze_weekend_results():
    """Analyze the weekend monitoring CSV and generate report"""
    
    if not CSV_FILE.exists():
        print(f"❌ CSV file not found: {CSV_FILE}")
        return
    
    print(f"""
{'='*70}
Weekend API Monitoring Results - Analysis Report
{'='*70}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Data File: {CSV_FILE.name}
{'='*70}
""")
    
    # Read CSV data
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if not rows:
        print("❌ No data found in CSV file")
        return
    
    total_tests = len(rows)
    
    # Metrics
    successful_tests = [r for r in rows if r['HTTP_Status_Code'] == '200']
    failed_tests = [r for r in rows if r['HTTP_Status_Code'] != '200']
    
    query_times = [float(r['API_Query_Time_Seconds']) for r in rows if r['API_Query_Time_Seconds']]
    trials_counts = [int(r['Trials_Found']) for r in rows if r['Trials_Found']]
    nationwide_results = [r for r in rows if r['Has_Nationwide_Results'] == 'True']
    
    errors_found = [r for r in rows if r['Error_Message']]
    
    # Cancer type breakdown
    cancer_types = defaultdict(int)
    for row in rows:
        cancer_types[row['Cancer_Type']] += 1
    
    # Location breakdown
    locations = defaultdict(int)
    for row in rows:
        locations[row['Location']] += 1
    
    # Print Summary
    print("📊 OVERALL STATISTICS")
    print(f"{'─'*70}")
    print(f"Total API Calls:        {total_tests}")
    print(f"Successful (200):       {len(successful_tests)} ({len(successful_tests)/total_tests*100:.1f}%)")
    print(f"Failed:                 {len(failed_tests)} ({len(failed_tests)/total_tests*100:.1f}%)")
    print(f"Errors Encountered:     {len(errors_found)}")
    print()
    
    print("⏱️  API PERFORMANCE")
    print(f"{'─'*70}")
    if query_times:
        print(f"Average Query Time:     {sum(query_times)/len(query_times):.3f} seconds")
        print(f"Fastest Query:          {min(query_times):.3f} seconds")
        print(f"Slowest Query:          {max(query_times):.3f} seconds")
    print()
    
    print("🔬 CLINICAL TRIALS RESULTS")
    print(f"{'─'*70}")
    if trials_counts:
        print(f"Total Trials Returned:  {sum(trials_counts)}")
        print(f"Average per Query:      {sum(trials_counts)/len(trials_counts):.1f}")
        print(f"Queries with 0 Results: {trials_counts.count(0)}")
        print(f"Nationwide Fallbacks:   {len(nationwide_results)} ({len(nationwide_results)/total_tests*100:.1f}%)")
    print()
    
    print("🏥 CANCER TYPES TESTED")
    print(f"{'─'*70}")
    for cancer_type, count in sorted(cancer_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cancer_type:<25} {count:>3} tests")
    print()
    
    print("📍 LOCATIONS TESTED")
    print(f"{'─'*70}")
    for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {location:<30} {count:>3} tests")
    print()
    
    # Error Report
    if errors_found:
        print("❌ ERRORS ENCOUNTERED")
        print(f"{'─'*70}")
        error_types = defaultdict(int)
        for row in errors_found:
            error_msg = row['Error_Message'][:50]
            error_types[error_msg] += 1
        
        for error, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  [{count}x] {error}")
        print()
    else:
        print("✅ NO ERRORS - All tests successful!")
        print()
    
    # Time Analysis
    print("📅 TESTING TIMELINE")
    print(f"{'─'*70}")
    if rows:
        first_test = rows[0]['Timestamp']
        last_test = rows[-1]['Timestamp']
        print(f"First Test:  {first_test}")
        print(f"Last Test:   {last_test}")
        
        # Calculate duration
        try:
            start = datetime.fromisoformat(first_test)
            end = datetime.fromisoformat(last_test)
            duration = end - start
            hours = duration.total_seconds() / 3600
            print(f"Duration:    {hours:.1f} hours ({duration.days} days)")
        except:
            pass
    print()
    
    # Sample Results
    print("📋 SAMPLE SUCCESSFUL RESULTS")
    print(f"{'─'*70}")
    successful_with_trials = [r for r in successful_tests if int(r['Trials_Found']) > 0][:3]
    
    for i, row in enumerate(successful_with_trials, 1):
        print(f"\nSample {i}:")
        print(f"  Patient:    {row['Patient_Name']}")
        print(f"  Cancer:     {row['Cancer_Type']}")
        print(f"  Location:   {row['Location']}")
        print(f"  Trials:     {row['Trials_Found']} found")
        print(f"  Query Time: {row['API_Query_Time_Seconds']}s")
        print(f"  Sample NCT: {row['Sample_Trial_NCT_ID']}")
        print(f"  Facility:   {row['Sample_Trial_Facility']}")
    
    print(f"\n{'='*70}")
    print("✅ Analysis Complete!")
    print(f"{'='*70}\n")
    
    # Recommendations
    print("💡 RECOMMENDATIONS")
    print(f"{'─'*70}")
    
    if query_times and max(query_times) > 5.0:
        print("⚠️  Some queries exceeded 5 seconds - consider timeout optimization")
    
    if len(failed_tests) > 0:
        print(f"⚠️  {len(failed_tests)} failed tests - review error messages above")
    
    if trials_counts and trials_counts.count(0) > total_tests * 0.1:
        print(f"⚠️  {trials_counts.count(0)} queries returned 0 results - may need broader search")
    
    if not errors_found and len(successful_tests) == total_tests:
        print("✅ Perfect weekend! All tests passed with no errors")
        print("✅ API is stable and performing well")
    
    print()


if __name__ == "__main__":
    analyze_weekend_results()
