#!/usr/bin/env python3
"""
Testing and validation script for PDF heading extraction
"""

import json
import os
import time
from pdf_extractor import PDFHeadingExtractor

def validate_output_format(result: dict) -> bool:
    """Validate that output matches expected JSON format"""
    required_fields = ['title', 'outline']
    
    # Check required fields
    for field in required_fields:
        if field not in result:
            print(f"Missing required field: {field}")
            return False
    
    # Validate title
    if not isinstance(result['title'], str):
        print("Title must be a string")
        return False
    
    # Validate outline
    if not isinstance(result['outline'], list):
        print("Outline must be a list")
        return False
    
    # Validate each heading in outline
    for i, heading in enumerate(result['outline']):
        if not isinstance(heading, dict):
            print(f"Heading {i} must be a dictionary")
            return False
        
        required_heading_fields = ['level', 'text', 'page']
        for field in required_heading_fields:
            if field not in heading:
                print(f"Heading {i} missing required field: {field}")
                return False
        
        # Validate level values
        if heading['level'] not in ['H1', 'H2', 'H3']:
            print(f"Heading {i} has invalid level: {heading['level']}")
            return False
        
        # Validate text
        if not isinstance(heading['text'], str) or not heading['text'].strip():
            print(f"Heading {i} has invalid text")
            return False
        
        # Validate page number
        if not isinstance(heading['page'], int) or heading['page'] < 1:
            print(f"Heading {i} has invalid page number: {heading['page']}")
            return False
    
    return True

def test_performance(pdf_path: str) -> dict:
    """Test performance metrics"""
    extractor = PDFHeadingExtractor()
    
    start_time = time.time()
    result = extractor.process_pdf(pdf_path)
    end_time = time.time()
    
    processing_time = end_time - start_time
    
    # Get PDF stats
    import fitz
    doc = fitz.open(pdf_path)
    page_count = len(doc)
    file_size = os.path.getsize(pdf_path)
    doc.close()
    
    return {
        'processing_time': processing_time,
        'page_count': page_count,
        'file_size_mb': file_size / (1024 * 1024),
        'pages_per_second': page_count / processing_time if processing_time > 0 else 0,
        'result': result
    }

def analyze_heading_distribution(result: dict) -> dict:
    """Analyze the distribution of heading levels"""
    if not result or 'outline' not in result:
        return {}
    
    level_counts = {'H1': 0, 'H2': 0, 'H3': 0}
    page_distribution = {}
    
    for heading in result['outline']:
        level = heading['level']
        page = heading['page']
        
        level_counts[level] += 1
        
        if page not in page_distribution:
            page_distribution[page] = {'H1': 0, 'H2': 0, 'H3': 0}
        page_distribution[page][level] += 1
    
    return {
        'level_counts': level_counts,
        'total_headings': sum(level_counts.values()),
        'page_distribution': page_distribution
    }

def create_test_report(pdf_path: str, output_path: str = None):
    """Create a comprehensive test report"""
    print(f"Testing PDF: {pdf_path}")
    print("=" * 60)
    
    # Performance test
    perf_results = test_performance(pdf_path)
    result = perf_results['result']
    
    print(f"📊 Performance Metrics:")
    print(f"  Processing time: {perf_results['processing_time']:.2f} seconds")
    print(f"  Page count: {perf_results['page_count']}")
    print(f"  File size: {perf_results['file_size_mb']:.2f} MB")
    print(f"  Pages per second: {perf_results['pages_per_second']:.2f}")
    print()
    
    # Validation test
    is_valid = validate_output_format(result)
    print(f"✅ Output format validation: {'PASSED' if is_valid else 'FAILED'}")
    print()
    
    # Heading analysis
    analysis = analyze_heading_distribution(result)
    if analysis:
        print(f"📋 Heading Analysis:")
        print(f"  Total headings found: {analysis['total_headings']}")
        print(f"  H1 headings: {analysis['level_counts']['H1']}")
        print(f"  H2 headings: {analysis['level_counts']['H2']}")
        print(f"  H3 headings: {analysis['level_counts']['H3']}")
        print()
    
    # Title extraction
    print(f"📖 Extracted Title: '{result.get('title', 'N/A')}'")
    print()
    
    # Sample headings
    if result.get('outline'):
        print("📝 Sample Headings:")
        for i, heading in enumerate(result['outline'][:10]):  # Show first 10
            print(f"  {heading['level']} (p.{heading['page']}): {heading['text']}")
        
        if len(result['outline']) > 10:
            print(f"  ... and {len(result['outline']) - 10} more")
    
    print()
    
    # Save detailed results if output path provided
    if output_path:
        detailed_report = {
            'pdf_path': pdf_path,
            'performance': perf_results,
            'validation': {'passed': is_valid},
            'analysis': analysis,
            'extraction_result': result
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Detailed report saved to: {output_path}")

def batch_test(input_dir: str, output_dir: str):
    """Test multiple PDFs and generate batch report"""
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in input directory")
        return
    
    batch_results = []
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        report_path = os.path.join(output_dir, f"{os.path.splitext(pdf_file)[0]}_report.json")
        
        print(f"\nProcessing: {pdf_file}")
        perf_results = test_performance(pdf_path)
        
        batch_results.append({
            'file': pdf_file,
            'processing_time': perf_results['processing_time'],
            'page_count': perf_results['page_count'],
            'file_size_mb': perf_results['file_size_mb'],
            'headings_found': len(perf_results['result'].get('outline', [])),
            'validation_passed': validate_output_format(perf_results['result'])
        })
        
        # Create individual report
        create_test_report(pdf_path, report_path)
    
    # Create batch summary
    summary_path = os.path.join(output_dir, 'batch_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_files': len(pdf_files),
            'results': batch_results,
            'summary_stats': {
                'avg_processing_time': sum(r['processing_time'] for r in batch_results) / len(batch_results),
                'total_pages': sum(r['page_count'] for r in batch_results),
                'total_headings': sum(r['headings_found'] for r in batch_results),
                'validation_success_rate': sum(r['validation_passed'] for r in batch_results) / len(batch_results)
            }
        }, f, indent=2)
    
    print(f"\n📊 Batch Summary saved to: {summary_path}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_validation.py <pdf_path> [output_report_path]")
        print("   or: python test_validation.py --batch <input_dir> <output_dir>")
        sys.exit(1)
    
    if sys.argv[1] == '--batch':
        if len(sys.argv) < 4:
            print("Batch mode requires input and output directories")
            sys.exit(1)
        batch_test(sys.argv[2], sys.argv[3])
    else:
        pdf_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        create_test_report(pdf_path, output_path)