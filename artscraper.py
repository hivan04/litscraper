import requests
from bs4 import BeautifulSoup
import time
import random
import re
from urllib.parse import quote_plus

def get_scholar_results(author_query, max_results=3):
    """Search Google Scholar for articles by a specific author"""
    base_url = "https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q="
    query = quote_plus(author_query)
    url = base_url + query
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for item in soup.select('.gs_ri')[:max_results]:
            title_elem = item.select_one('.gs_rt a')
            if not title_elem:
                continue
                
            title = title_elem.text
            link = title_elem['href']
            
            # Try to get citation info
            citation_elem = item.select_one('.gs_a')
            citation = citation_elem.text if citation_elem else ""
            
            results.append({
                'author_query': author_query,
                'title': title,
                'link': link,
                'citation': citation
            })
            
        return results
    
    except Exception as e:
        print(f"Error searching for {author_query}: {str(e)}")
        return []

def process_author_list(file_path):
    """Process a text file of author names"""
    with open(file_path, 'r', encoding='utf-8') as f:
        authors = [line.strip() for line in f if line.strip()]
    return authors

def save_results(results, output_file):
    """Save results to a text file in a copy-paste friendly format"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(f"Author Query: {result['author_query']}\n")
            f.write(f"Title: {result['title']}\n")
            f.write(f"Link: {result['link']}\n")
            f.write(f"Citation: {result['citation']}\n")
            f.write("-" * 80 + "\n\n")

def main():
    # Input and output files
    input_file = "authors.txt"  # Your text file with one author per line
    output_file = "scholar_results.txt"
    
    # Get author list
    authors = process_author_list(input_file)
    
    all_results = []
    
    print(f"Processing {len(authors)} authors...")
    
    for i, author in enumerate(authors, 1):
        print(f"\n[{i}/{len(authors)}] Searching for: {author}")
        
        results = get_scholar_results(author)
        all_results.extend(results)
        
        # Random delay to avoid being blocked (3-10 seconds)
        delay = random.uniform(3, 10)
        time.sleep(delay)
    
    # Save results
    save_results(all_results, output_file)
    print(f"\nDone! Results saved to {output_file}")

if __name__ == "__main__":
    main()