from typing import Dict, List, Optional
from langchain_core.tools import tool
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin
import json
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List


load_dotenv()

class WebScrapingTool:
    """Tool class for web scraping operations"""
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Validate if the given string is a proper URL."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
    
    @staticmethod
    def _get_page_content(url: str) -> Optional[str]:
        """Fetch the raw HTML content of a webpage."""
        try:
            response = requests.get(url, headers=WebScrapingTool.HEADERS, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            return None
            
    @staticmethod
    def _extract_content(html: str, url: str) -> Dict:
        """Extract content using BeautifulSoup."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'iframe', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
            
        result = {
            'url': url,
            'title': '',
            'text': '',
            'description': '',
            'images': [],
            'links': []
        }
        
        # Extract title
        if soup.title:
            result['title'] = soup.title.string.strip()
            
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            result['description'] = meta_desc.get('content', '').strip()
            
        # Extract meta author
        meta_author = soup.find('meta', attrs={'name': ['author', 'Author']})
        if meta_author:
            result['author'] = meta_author.get('content', '').strip()
            
        # Try to find main content
        main_content = None
        
        # Look for common content containers
        content_candidates = [
            soup.find(['article', 'main']),  # Semantic HTML5 tags
            soup.find(id=['content', 'main-content', 'article-content']),  # Common IDs
            soup.find(class_=['content', 'main-content', 'article-content']),  # Common classes
            soup.find('div', {'role': 'main'})  # ARIA role
        ]
        
        for candidate in content_candidates:
            if candidate:
                main_content = candidate
                break
                
        # If no main content found, use body
        if not main_content:
            main_content = soup.body
            
        if main_content:
            # Extract text content
            paragraphs = []
            for p in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                text = p.get_text().strip()
                if text and len(text) > 20:  # Filter out short fragments
                    paragraphs.append(text)
            result['text'] = '\n\n'.join(paragraphs)
            
            # Extract images with absolute URLs
            for img in main_content.find_all('img', src=True):
                img_url = urljoin(url, img['src'])
                img_data = {
                    'url': img_url,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                }
                if img_data['alt'] or img_data['title']:  # Only include images with metadata
                    result['images'].append(img_data)
                    
            # Extract links with absolute URLs
            for link in main_content.find_all('a', href=True):
                link_url = urljoin(url, link['href'])
                link_text = link.get_text().strip()
                if link_text and WebScrapingTool._is_valid_url(link_url):
                    result['links'].append({
                        'url': link_url,
                        'text': link_text
                    })
        
        return result

    @staticmethod
    def _clean_content(content: Dict) -> Dict:
        """Clean and normalize the extracted content."""
        cleaned = {}
        
        if not content:
            return cleaned
            
        # Clean text content
        if 'text' in content and content['text']:
            # Remove excessive whitespace
            lines = [line.strip() for line in content['text'].split('\n')]
            lines = [line for line in lines if line]
            cleaned['text'] = '\n\n'.join(lines)
            
        # Clean and copy other fields
        for field in ['title', 'url', 'description', 'author']:
            if field in content and content[field]:
                cleaned[field] = content[field].strip()
                
        # Clean images and links
        if 'images' in content and content['images']:
            cleaned['images'] = [img for img in content['images'] 
                               if img.get('url') and (img.get('alt') or img.get('title'))][:5]
            
        if 'links' in content and content['links']:
            cleaned['links'] = [link for link in content['links'] 
                              if link.get('url') and link.get('text')][:10]
                
        return cleaned

    @staticmethod
    @tool
    def scrape_webpage(url: Any) -> Dict:
        """
        Scrape content from a webpage URL.
        
        Args:
            url (str): The URL of the webpage to scrape
            
        Returns:
            Dict: Extracted content including title, text, and metadata. Example return format:
            {
                'title': 'Page Title',
                'text': 'Main content text...',
                'description': 'Meta description',
                'url': 'https://example.com',
                'author': 'Author name if available',
                'images': [
                    {'url': 'image1.jpg', 'alt': 'Image description', 'title': 'Image title'},
                    ...
                ],
                'links': [
                    {'url': 'https://example.com/link', 'text': 'Link text'},
                    ...
                ]
            }
        """
        if not WebScrapingTool._is_valid_url(url):
            return {"error": "Invalid URL provided"}
            
        html_content = WebScrapingTool._get_page_content(url)
        if not html_content:
            return {"error": "Failed to fetch webpage content"}
            
        content = WebScrapingTool._extract_content(html_content, url)
        if not content:
            return {"error": "Failed to extract content from webpage"}
            
        cleaned_content = WebScrapingTool._clean_content(content)
        if not cleaned_content:
            return {"error": "Failed to process extracted content"}
            
        return cleaned_content

    @staticmethod
    def get_tools(include: List[str] = None) -> List[tool]:
        """
        Get list of web scraping tools to pass to LLM.
        
        Args:
            include (List[str]): List of tools to include. Options: ['scrape']
                               If None, returns all available tools.
                               
        Returns:
            List[tool]: List of tool functions to pass to LLM
        """
        scraping_tools = {
            'scrape': WebScrapingTool.scrape_webpage
        }
        
        if include:
            return [scraping_tools[name] for name in include if name in scraping_tools]
        return list(scraping_tools.values())