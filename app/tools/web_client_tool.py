from typing import Dict, Any, Optional, List
from datetime import datetime
from langchain.tools import tool
import json

class WebClientTool:
    """Tool class for web client operations"""

    @staticmethod
    def _generate_basic_html_template(content: dict) -> str:
        """Generate a basic HTML template with provided content"""
        return f"""
        <!DOCTYPE html>
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
        </html>
        """

    @staticmethod
    @tool()
    def generate_html(content: Dict[str, Any]) -> str:
        """
        Generate HTML content based on provided specifications.
        
        Args:
            content: Dictionary containing HTML specifications with fields:
                - title: Page title
                - styles: CSS styles
                - body: HTML body content
                - scripts: JavaScript code
        
        Returns:
            str: Generated HTML content or error message
        """
        try:
            required_fields = ['title', 'body']
            missing_fields = [field for field in required_fields if field not in content]
            
            if missing_fields:
                return f"Error: Missing required fields: {', '.join(missing_fields)}"
            
            html_content = WebClientTool._generate_basic_html_template(content)
            return html_content.strip()
            
        except Exception as e:
            return f"Error generating HTML: {str(e)}"
