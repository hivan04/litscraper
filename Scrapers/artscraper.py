# import requests
# from bs4 import BeautifulSoup
# import time
# import random
# import re
# from urllib.parse import quote_plus

# def get_scholar_results(author_query, max_results=3):
#     """Search Google Scholar for articles by a specific author"""
#     base_url = "https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=financial+literacy&btnG="
#     query = quote_plus(author_query)
#     url = base_url + query
    
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     }
    
#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.text, 'html.parser')
#         results = []
        
#         for item in soup.select('.gs_ri')[:max_results]:
#             title_elem = item.select_one('.gs_rt a')
#             if not title_elem:
#                 continue
                
#             title = title_elem.text
#             link = title_elem['href']
            
#             # Try to get citation info
#             citation_elem = item.select_one('.gs_a')
#             citation = citation_elem.text if citation_elem else ""
            
#             results.append({
#                 'author_query': author_query,
#                 'title': title,
#                 'link': link,
#                 'citation': citation
#             })
            
#         return results
    
#     except Exception as e:
#         print(f"Error searching for {author_query}: {str(e)}")
#         return []

# """Process a text file of author names"""
# def process_author_list(file_path):
#     with open(file_path, 'r', encoding='utf-8') as f:
#         authors = [line.strip() for line in f if line.strip()]
#     return authors

# """Save results to a .txt file"""
# def save_results(results, output_file):
#     with open(output_file, 'w', encoding='utf-8') as f:
#         for result in results:
#             f.write(f"Author Query: {result['author_query']}\n")
#             f.write(f"Title: {result['title']}\n")
#             f.write(f"Link: {result['link']}\n")
#             f.write(f"Citation: {result['citation']}\n")
#             f.write("-" * 80 + "\n\n")

# def main():
#     # Input and output files
#     input_file = "authors.txt"  # Your text file with one author per line
#     output_file = "scholar_results.txt"
    
#     # Get author list
#     authors = process_author_list(input_file)
    
#     all_results = []
    
#     print(f"Processing {len(authors)} authors...")
    
#     for i, author in enumerate(authors, 1):
#         print(f"\n[{i}/{len(authors)}] Searching for: {author}")
        
#         results = get_scholar_results(author)
#         all_results.extend(results)
        
#         # Random delay to avoid being blocked (3-10 seconds)
#         delay = random.uniform(3, 30)
#         time.sleep(delay)
    
#     # Save results
#     save_results(all_results, output_file)
#     print(f"\nDone! Results saved to {output_file}")

# if __name__ == "__main__":
#     main()

import requests
from bs4 import BeautifulSoup
import time
import random
import re
from urllib.parse import quote_plus

def get_scholar_results(author_query, max_results=3):
    """Search Google Scholar for articles by a specific author"""
    query = quote_plus(author_query + " financial literacy")
    url = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for item in soup.select('.gs_ri')[:max_results]:
            title_elem = item.select_one('.gs_rt a')
            if not title_elem:
                continue
                
            title = title_elem.text
            link = title_elem['href']
            
            # Get citation info (authors, year, journal)
            citation_elem = item.select_one('.gs_a')
            citation = citation_elem.text if citation_elem else ""
            
            # Extract year from citation if possible
            year_match = re.search(r'(\d{4})', citation)
            year = year_match.group(1) if year_match else "N/A"
            
            results.append({
                'author_query': author_query,
                'title': title,
                'link': link,
                'citation': citation,
                'year': year
            })
            
        return results
    
    except Exception as e:
        print(f"⚠️ Error searching for {author_query}: {str(e)}")
        return []

def process_author_list(file_path):
    """Read author names from a text file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        authors = [line.strip() for line in f if line.strip()]
    return authors

def save_results(results, output_file):
    """Save results to a structured .txt file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(f"Author Query: {result['author_query']}\n")
            f.write(f"Title: {result['title']}\n")
            f.write(f"Link: {result['link']}\n")
            f.write(f"Citation: {result['citation']}\n")
            f.write(f"Year: {result['year']}\n")
            f.write("-" * 80 + "\n\n")

def main():
    input_file = "authors.txt"  # One author per line
    output_file = "scholar_results.txt"
    
    authors = process_author_list(input_file)
    all_results = []
    seen_links = set()  # Track duplicates
    
    print(f"🔍 Processing {len(authors)} authors...")
    
    for i, author in enumerate(authors, 1):
        print(f"\n[{i}/{len(authors)}] Searching for: {author}")
        
        results = get_scholar_results(author)
        
        # Filter out duplicates
        unique_results = []
        for paper in results:
            if paper['link'] not in seen_links:
                seen_links.add(paper['link'])
                unique_results.append(paper)
        
        all_results.extend(unique_results)
        
        # Randomized delay (5-15 sec) to avoid blocking
        delay = random.uniform(5, 15)
        print(f"Waiting {delay:.1f} sec...")
        time.sleep(delay)
    
    # Save results
    save_results(all_results, output_file)
    print(f"\n✅ Done! Saved {len(all_results)} unique papers to {output_file}")

if __name__ == "__main__":
    main()