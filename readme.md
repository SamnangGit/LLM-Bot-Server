# LLM Chatbot Server

## Installation

To get started with this project, follow these steps:

1. **Navigate to the Root Directory** 
   ```bash
   cd /path/to/your/project
   ```
2. **Create and Activate Python Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Create .env File and Put in Your API Key**
   ```bash
   cp .envexample .env
   ```   
5. **Navigate to the App Directory**
   ```bash
   cd path/to/your/project/app
   ```
6. **Serve the Application**
   ```bash
   uvicorn main:app --reload
   ```

Your application should now be running on the specified development server.

## Additional information
Ensure you have Python installed. It is recommended to use a virtual environment for managing project dependencies.


## Project Tech Stack

This project utilizes the following technologies:

- **LangChain**: For managing and interacting with language models.
- **Python**: The programming language used for the server-side application.
- **Uvicorn**: ASGI server for running FastAPI applications.
- **FastAPI**: Framework for building APIs with Python 3.7+.
- **Pydantic**: Data validation and settings management using Python type annotations.