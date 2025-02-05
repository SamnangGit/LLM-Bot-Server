from typing import Dict, Any, Optional
from langchain_community.utilities import SQLDatabase
from langchain.tools import tool


class SQLDatabaseTool:
    """Tool class for core SQL database operations"""


    @staticmethod
    @tool    
    def get_schema() -> str:
        """
        Get database schema information
        
        Returns:
            str: Database schema information
        """
        db = SQLDatabaseTool._init_database(user='root', password='root', host='localhost', port='8889', database='dev_srfashion')

        query = db.get_table_info()
        return query
    
    @staticmethod
    @tool
    def execute_sql(query: str) -> str:
        """
        Execute SQL query and return results
        
        Args:
            query: SQL query to execute
        Returns:
            str: Query results
        """
        db = SQLDatabaseTool._init_database(user='root', password='root', host='localhost', port='8889', database='dev_srfashion')
        result = db.run(query)
        return result

    @staticmethod
    def _init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
        db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
        db = SQLDatabase.from_uri(db_uri)
        return db