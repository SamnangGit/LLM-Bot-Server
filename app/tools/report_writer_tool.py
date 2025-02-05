from typing import Dict, Any, Optional
import os
from datetime import datetime
from langchain.tools import tool
import re
import json

class ResearchReportWriter:
    """Tool class for research report writing operations"""
    
    @staticmethod
    @tool
    def write_file(
        content: str, 
        title: Optional[str] = None,
        author: Optional[str] = None,
        keywords: Optional[list] = None,
        references: Optional[list] = None
    ) -> str:
        """
        Write research content to a file with automatic sanitization and formatting
        
        Args:
            content: Research content to write to file
            filename: Name of the file to write to
            title: Optional title for the research report
            author: Optional author name
            keywords: Optional list of keywords
            references: Optional list of references
            
        Returns:
            str: Success message or error description
        """
        try:
            content = json.loads(content)
            filename = content.get('filename')
            final_content = content.get('content')
            # Ensure the research_reports directory exists
            os.makedirs('research_reports', exist_ok=True)
            
            # Sanitize filename and ensure proper extension
            safe_filename = os.path.basename(filename)
            if not safe_filename.endswith(('.txt', '.md', '.json')):
                safe_filename += '.md'  # Default to markdown
            
            file_path = os.path.join('research_reports', safe_filename)
            
            # First sanitize the content
            clean_content = ResearchReportWriter.content_sanitizer(final_content)
            
            # Format the content based on file type
            if safe_filename.endswith('.json'):
                # For JSON files, use JSON formatting
                formatted_content = ResearchReportWriter.export_as_json(
                    title=title or "Research Report",
                    content=clean_content,
                    metadata={
                        "author": author,
                        "keywords": keywords,
                        "references": references
                    }
                )
            else:
                # For text/markdown files, use research report formatting
                formatted_content = ResearchReportWriter.format_research_report(
                    title=title or "Research Report",
                    content=clean_content,
                    author=author,
                    keywords=keywords,
                    references=references
                )
            
            # Write formatted content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
                
            return f"Successfully wrote formatted research report to {safe_filename}"
            
        except Exception as e:
            return f"Error writing research report: {str(e)}"
    
    @staticmethod
    @tool
    def content_sanitizer(content: str) -> str:
        """
        Sanitize and format research content for consistency and readability
        
        Args:
            content: Raw research content to sanitize and format
            
        Returns:
            str: Sanitized and formatted content
        """
        # Convert content to string if it isn't already
        content = str(content)
        
        # Remove control characters while preserving legitimate whitespace
        content = ''.join(char for char in content if char.isprintable() or char in '\n\t')
        
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Fix common formatting issues
        # Ensure consistent spacing after punctuation
        content = re.sub(r'([.!?])\s*', r'\1 ', content)
        # Remove multiple spaces
        content = re.sub(r' +', ' ', content)
        # Ensure consistent paragraph spacing
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Remove any trailing/leading whitespace
        content = content.strip()
        
        return content
    
    @staticmethod
    def format_research_report(
        title: str,
        content: str,
        author: Optional[str] = None,
        keywords: Optional[list] = None,
        references: Optional[list] = None
    ) -> str:
        """
        Format a complete research report with metadata
        
        Args:
            title: Research report title
            content: Main research content
            author: Optional author name
            keywords: Optional list of keywords
            references: Optional list of references
            
        Returns:
            str: Formatted research report
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build the report header
        header = f"""# {title}

Date: {timestamp}"""
        
        if author:
            header += f"\nAuthor: {author}"
            
        if keywords:
            header += f"\nKeywords: {', '.join(keywords)}"
            
        # Build the main report body
        body = f"""

## Abstract

{content[:500] + '...' if len(content) > 500 else content}

## Full Content

{content}"""
        
        # Add references if provided
        if references:
            refs = "\n## References\n\n"
            for i, ref in enumerate(references, 1):
                refs += f"{i}. {ref}\n"
            body += f"\n{refs}"
        
        return header + body
    
    @staticmethod
    def export_as_json(
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Export research report in JSON format
        """
        report_data = {
            "title": title,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)