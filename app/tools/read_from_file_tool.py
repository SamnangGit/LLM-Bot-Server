from langchain.tools import BaseTool
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pydantic import Field, BaseModel
import os
import re
import json

class WebContentQuerySchema(BaseModel):
    """Schema for the WebContentReaderTool input"""
    query_type: str = Field(
        ...,
        description="Type of query: 'latest', 'by_domain', 'by_date', 'search', or 'file'"
    )
    value: str = Field(
        ...,
        description="Query value - domain name, date (YYYY-MM-DD), search term, or filename"
    )
    max_results: int = Field(
        default=5,
        description="Maximum number of results to return"
    )

class WebContentReaderTool(BaseTool):
    """LangChain tool for retrieving saved web content"""
    
    name: str = "web_content_reader_tool"
    description: str = "Retrieves saved web content based on various query parameters like domain, date, or search terms"
    base_directory: str = Field(default="scraped_content", description="Directory to read the content files from")
    args_schema: type[BaseModel] = WebContentQuerySchema

    def __init__(self, base_directory: str = "scraped_content"):
        super().__init__(base_directory=base_directory)
        if not os.path.exists(base_directory):
            os.makedirs(base_directory)

    def _parse_filename(self, filename: str) -> Dict[str, str]:
        """Extract information from filename"""
        # Expected format: domain_title_YYYYMMDD_HHMMSS.txt
        parts = filename.rsplit('_', 2)
        if len(parts) >= 3:
            timestamp_str = parts[-1].replace('.txt', '')
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                return {
                    'domain': parts[0],
                    'title': parts[1],
                    'timestamp': timestamp,
                    'filename': filename
                }
            except ValueError:
                return None
        return None

    def _read_file_content(self, filepath: str) -> Dict[str, Any]:
        """Read and parse the content of a saved file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)

            # Parse the content sections
            sections = {}
            current_section = 'header'
            current_content = []
            
            for line in content.split('\n'):
                if line.startswith('==='): 
                    continue
                elif line.startswith('URL: '):
                    sections['url'] = line.replace('URL: ', '').strip()
                elif line.startswith('Title: '):
                    sections['title'] = line.replace('Title: ', '').strip()
                elif line.startswith('Scraped on: '):
                    sections['scraped_on'] = line.replace('Scraped on: ', '').strip()
                elif line.strip() in ['META DESCRIPTION:', 'HEADINGS:', 'MAIN CONTENT:', 'LISTS:', 'TABLES:', 'LINKS:', 'IMAGES:']:
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content)
                        current_content = []
                    current_section = line.strip().lower().replace(':', '')
                elif line.startswith('-' * 20):
                    continue
                else:
                    current_content.append(line)
            
            if current_content:
                sections[current_section] = '\n'.join(current_content)

            return sections
        except Exception as e:
            return {'error': f"Error reading file: {str(e)}"}

    def _search_content(self, search_term: str, content: Dict[str, Any]) -> bool:
        """Search for term in content"""
        search_term = search_term.lower()
        # Search in title and URL
        if search_term in content.get('title', '').lower() or search_term in content.get('url', '').lower():
            return True
        # Search in main content
        if search_term in content.get('main_content', '').lower():
            return True
        return False

    def _get_files_by_query(self, query_type: str, value: str, max_results: int) -> List[Dict[str, Any]]:
        """Get files based on query parameters"""
        results = []
        files = [f for f in os.listdir(self.base_directory) if f.endswith('.txt')]
        
        for file in files:
            file_info = self._parse_filename(file)
            if not file_info:
                continue
                
            filepath = os.path.join(self.base_directory, file)
            content = self._read_file_content(filepath)
            
            if query_type == 'latest':
                results.append((file_info['timestamp'], content))
            elif query_type == 'by_domain' and value.lower() in file_info['domain'].lower():
                results.append((file_info['timestamp'], content))
            elif query_type == 'by_date':
                file_date = file_info['timestamp'].strftime('%Y-%m-%d')
                if file_date == value:
                    results.append((file_info['timestamp'], content))
            elif query_type == 'search' and self._search_content(value, content):
                results.append((file_info['timestamp'], content))
            elif query_type == 'file' and value.lower() in file.lower():
                results.append((file_info['timestamp'], content))
                
        # Sort by timestamp (most recent first) and limit results
        results.sort(key=lambda x: x[0], reverse=True)
        return [content for _, content in results[:max_results]]

    def _format_response(self, results: List[Dict[str, Any]]) -> str:
        """Format the results into a readable response"""
        if not results:
            return "No matching content found."
            
        response = []
        for i, content in enumerate(results, 1):
            response.append(f"\nResult {i}:")
            response.append("-" * 40)
            response.append(f"Title: {content.get('title', 'N/A')}")
            response.append(f"URL: {content.get('url', 'N/A')}")
            response.append(f"Scraped on: {content.get('scraped_on', 'N/A')}")
            
            # Add excerpt from main content if available
            if 'main_content' in content:
                excerpt = content['main_content'].split('\n')[0][:200] + "..."
                response.append(f"\nExcerpt: {excerpt}")
            
            response.append("")
            
        return "\n".join(response)

    def _run(self, query_type: str, value: str = "", max_results: int = 5) -> str:
        """
        Run the tool to retrieve content based on query parameters.
        
        Args:
            query_type: Type of query ('latest', 'by_domain', 'by_date', 'search', or 'file')
            value: Query value (can be empty for 'latest' queries)
            max_results: Maximum number of results to return
            
        Returns:
            str: Formatted response with matching content
        """
        if query_type not in ['latest', 'by_domain', 'by_date', 'search', 'file']:
            return "Error: Invalid query type. Must be 'latest', 'by_domain', 'by_date', 'search', or 'file'"
        
        # For 'latest' query type, we don't need a value
        if query_type == 'latest':
            value = ""  # Empty value is fine for latest
                
        results = self._get_files_by_query(query_type, value, max_results)
        return self._format_response(results)
    
    async def _arun(self, query_type: str, value: str, max_results: int = 5) -> str:
        """Async implementation of run"""
        return self._run(query_type, value, max_results)