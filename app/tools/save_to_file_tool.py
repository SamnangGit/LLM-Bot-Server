from langchain.tools import BaseTool
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import Field, BaseModel
import os
import re

class WebContentSaverSchema(BaseModel):
    """Schema for the WebContentSaverTool input"""
    content: Dict[str, Any] = Field(
        ...,
        description="The content dictionary to save. Should contain fields like 'url', 'title', 'paragraphs', etc."
    )

class WebContentSaverTool(BaseTool):
    """LangChain tool for saving web content"""
    
    name: str = "web_content_saver_tool"
    description: str = "Saves web content to a formatted text file. The content should be a dictionary containing scraped web content."
    base_directory: str = Field(default="scraped_content", description="Directory to save the content files")
    args_schema: type[BaseModel] = WebContentSaverSchema

    def __init__(self, base_directory: str = "scraped_content"):
        super().__init__(base_directory=base_directory)
        os.makedirs(base_directory, exist_ok=True)

    def _sanitize_filename(self, text: str) -> str:
        """Convert text to a valid filename"""
        # Remove invalid filename characters
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        # Replace spaces and other characters with underscores
        text = re.sub(r'[\s\t\n]+', '_', text)
        # Limit length to 50 characters
        return text[:50].strip('_')

    def _generate_filename(self, content: dict) -> str:
        """Create a meaningful filename from the content"""
        # Extract domain from URL
        url = content.get('url', 'no_url')
        domain = url.split('/')[2] if '://' in url else url.split('/')[0]
        domain = self._sanitize_filename(domain)
        
        # Get first few words of title
        title = content.get('title', 'no_title')
        title_part = self._sanitize_filename(title)[:30]
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{domain}_{title_part}_{timestamp}.txt"

    def _format_content(self, content: dict) -> str:
        """Format the content dictionary into a readable text structure"""
        formatted_text = []
        
        # Add URL and title
        formatted_text.append("=" * 80)
        formatted_text.append(f"URL: {content.get('url', 'No URL provided')}")
        formatted_text.append(f"Title: {content.get('title', 'No title')}")
        formatted_text.append(f"Scraped on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        formatted_text.append("=" * 80)
        
        # Add meta description
        if content.get('meta_description'):
            formatted_text.extend(["\nMETA DESCRIPTION:", "-" * 20, content['meta_description']])
        
        # Add headings
        if content.get('headings'):
            formatted_text.extend(["\nHEADINGS:", "-" * 20])
            for heading in content['headings']:
                formatted_text.append(f"[H{heading['level']}] {heading['text']}")
        
        # Add paragraphs
        if content.get('paragraphs'):
            formatted_text.extend(["\nMAIN CONTENT:", "-" * 20])
            for i, para in enumerate(content['paragraphs'], 1):
                formatted_text.extend([f"\nParagraph {i}:", para, ""])
        
        # Add lists
        if content.get('lists'):
            formatted_text.extend(["\nLISTS:", "-" * 20])
            for i, lst in enumerate(content['lists'], 1):
                formatted_text.extend([f"\nList {i} ({lst['type']}):", ""])
                for j, item in enumerate(lst['items'], 1):
                    formatted_text.append(f"  {j}. {item}")
        
        # Add tables
        if content.get('tables'):
            formatted_text.extend(["\nTABLES:", "-" * 20])
            for i, table in enumerate(content['tables'], 1):
                formatted_text.extend([f"\nTable {i}:", ""])
                if table['headers']:
                    formatted_text.append(" | ".join(table['headers']))
                    formatted_text.append("-" * (len(" | ".join(table['headers']))))
                for row in table['data']:
                    formatted_text.append(" | ".join(row))
        
        # Add links
        if content.get('links'):
            formatted_text.extend(["\nLINKS:", "-" * 20])
            for link in content['links']:
                formatted_text.append(f"- [{link['text']}] {link['url']}")
        
        # Add images
        if content.get('images'):
            formatted_text.extend(["\nIMAGES:", "-" * 20])
            for img in content['images']:
                formatted_text.append(f"- [{img['alt']}] {img['src']}")
        
        return "\n".join(formatted_text)

    def _save_content(self, formatted_content: str, filename: str) -> str:
        """Save the formatted content to a file"""
        try:
            filepath = os.path.join(self.base_directory, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            return filepath
        except Exception as e:
            return f"Error saving file: {str(e)}"

    def _run(self, content: Dict[str, Any]) -> str:
        """
        Run the tool to save content to a file.
        
        Args:
            content (dict): The content dictionary to save
            
        Returns:
            str: Path to the saved file or error message
        """
        if not isinstance(content, dict):
            return "Error: Content must be a dictionary"
        
        if "error" in content:
            return f"Error in content: {content['error']}"
        
        # Generate filename
        filename = self._generate_filename(content)
        
        # Format content
        formatted_content = self._format_content(content)
        
        # Save to file
        return self._save_content(formatted_content, filename)
    
    async def _arun(self, content: Dict[str, Any]) -> str:
        """Async implementation of run"""
        return self._run(content)