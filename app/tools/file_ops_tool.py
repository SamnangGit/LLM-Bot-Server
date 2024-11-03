from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import re
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

class FileOpsTool:
    """Tool class for file operations"""
    
    base_directory = os.getenv('FILE_CABINET_PATH')

    @staticmethod
    def _sanitize_filename(text: str) -> str:
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        text = re.sub(r'[\s\t\n]+', '_', text)
        return text[:50].strip('_')

    @staticmethod
    def _generate_filename(content: dict) -> str:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if 'title' in content:
            title_part = FileOpsTool._sanitize_filename(content['title'])[:30]
            return f"{title_part}_{timestamp}.txt"
        return f"content_{timestamp}.txt"

    @staticmethod
    def _format_content(content: Any) -> str:
        formatted = []
        formatted.append("=" * 80)
        formatted.append(f"Created on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if 'title' in content:
            formatted.append(f"Title: {content['title']}")
        if 'url' in content:
            formatted.append(f"Source URL: {content['url']}")
        
        formatted.append("=" * 80 + "\n")

        if 'text' in content:
            formatted.append(content['text'])
        
        for key, value in content.items():
            if key not in ['title', 'url', 'text']:
                formatted.append(f"\n{key.upper()}:")
                formatted.append("-" * 40)
                if isinstance(value, list):
                    formatted.extend(str(v) for v in value)
                else:
                    formatted.append(str(value))

        return "\n".join(formatted)

    @staticmethod
    @tool()
    def write_file(content: Any, filename: Optional[str] = None) -> str:
        """Save content to a text file. Content should be a dictionary with fields like 'url', 'title', 'text', etc."""
        try:
            final_filename = filename if filename else FileOpsTool._generate_filename(content)
            filepath = os.path.join(FileOpsTool.base_directory, final_filename)
            
            formatted_content = FileOpsTool._format_content(content)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            return f"Content successfully saved to {filepath}"
            
        except Exception as e:
            return f"Error saving content: {str(e)}"

    @staticmethod
    @tool()
    def read_file(query_type: str = "latest", value: str = "", max_results: int = 5) -> str:
        """
        Read content from stored files.
        Args:
            query_type: Type of query ('latest', 'by_name', 'search', or 'all')
            value: Search term or filename (not needed for 'latest' or 'all')
            max_results: Maximum number of results to return (default: 5)
        """
        try:
            if query_type not in ['latest', 'by_name', 'search', 'all']:
                return "Error: Invalid query type. Must be 'latest', 'by_name', 'search', or 'all'"
            
            results = []
            files = [f for f in os.listdir(FileOpsTool.base_directory) if f.endswith('.txt')]
            files.sort(key=lambda x: os.path.getmtime(os.path.join(FileOpsTool.base_directory, x)), reverse=True)
            
            for file in files:
                if len(results) >= max_results:
                    break
                    
                filepath = os.path.join(FileOpsTool.base_directory, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if query_type == 'latest':
                        results.append((file, content))
                    elif query_type == 'by_name' and value.lower() in file.lower():
                        results.append((file, content))
                    elif query_type == 'search' and value.lower() in content.lower():
                        results.append((file, content))
                    elif query_type == 'all':
                        results.append((file, content))
                except Exception:
                    continue
            
            if not results:
                return "No matching content found."
            
            output = []
            for i, (filename, content) in enumerate(results, 1):
                output.append(f"\nResult {i} - File: {filename}")
                output.append("-" * 40)
                excerpt = content[:500] + "..." if len(content) > 500 else content
                output.append(excerpt)
            
            return "\n".join(output)
            
        except Exception as e:
            return f"Error reading files: {str(e)}"


    @staticmethod
    def get_tools(include: List[str] = None) -> List[tool]:
        """
        Get list of file operation tools to pass to LLM.
        Args:
            include (List[str]): List of tools to include. Options: ['write', 'read']
            If None, returns all available tools.
        Returns:
            List[tool]: List of tool functions to pass to LLM
        """
        file_tools = {
            'write': FileOpsTool().write_file,
            'read': FileOpsTool().read_file
        }
        
        if include:
            return [file_tools[name] for name in include if name in file_tools]
        return list(file_tools.values())