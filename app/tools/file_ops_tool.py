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
    def write_file(content: str, filename: Optional[str] = None) -> str:
        """
        Saves the given content to a text file within the tool's base directory. If a filename
        is not provided, one is automatically generated from the content.

        The content should be a dictionary containing information relevant to the file. 
        For example, the dictionary may include keys such as 'url', 'title', and 'text', 
        though the function can handle any valid dictionary data.

        The function uses an internal formatting method to transform the dictionary data 
        into a string, and then writes this string to the specified or generated file.

        Args:
            content (Any): The content to be written. Typically a dictionary with fields 
                like 'url', 'title', 'text', etc.
            filename (Optional[str], optional): The name of the file to write. If None, a 
                filename will be generated based on the content. Defaults to None.

        Returns:
            str: A message indicating either the success of saving the file (including the 
            file path) or the error that occurred if the save failed.
        """
        try:
            final_filename = filename if filename else FileOpsTool._generate_filename(content)
            filepath = os.path.join(FileOpsTool.base_directory, final_filename)

            # formatted_content = FileOpsTool._format_content(content)
            formatted_content = content
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
    

    @staticmethod
    @tool()
    def write_html(*, content: Dict[str, str], filename: Optional[str] = None) -> str:
        """
        Saves HTML content to a file within the tool's base directory.
        
        Args:
            content (Dict[str, str]): Dictionary containing HTML specifications with fields:
                - title: Page title (required)
                - body: HTML body content (required)
                - styles: CSS styles (optional)
                - scripts: JavaScript code (optional)
            filename (Optional[str]): The name of the file to write. If None, generates 
                                filename based on content title and timestamp.
        
        Returns:
            str: Success message with filepath or error message
        """
        try:
            # Validate required fields
            required_fields = ['title', 'body']
            missing_fields = [field for field in required_fields if field not in content]
            if missing_fields:
                return f"Error: Missing required fields: {', '.join(missing_fields)}"

            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                title_part = FileOpsTool._sanitize_filename(content['title'])[:30]
                filename = f"{title_part}_{timestamp}.html"
            elif not filename.endswith('.html'):
                filename += '.html'
            
            filepath = os.path.join(FileOpsTool.base_directory, filename)

            # Generate HTML content
            html_content = f"""<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{content.get('title', 'Generated Page')}</title>
                    <style>
                        {content.get('styles', '')}
                    </style>
                </head>
                <body>
                    {content.get('body', '')}
                    <script>
                        {content.get('scripts', '')}
                    </script>
                </body>
                </html>"""

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return f"HTML file successfully saved to {filepath}"

        except Exception as e:
            return f"Error saving HTML file: {str(e)}"