"""
Database configuration for KRAI Engine
"""

import os
from typing import Dict, Any

class DatabaseConfig:
    """Database configuration manager"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load database configuration from environment variables"""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'krai_engine'),
            'user': os.getenv('DB_USER', 'krai_user'),
            'password': os.getenv('DB_PASSWORD', 'krai_password'),
            'min_connections': int(os.getenv('DB_MIN_CONNECTIONS', 5)),
            'max_connections': int(os.getenv('DB_MAX_CONNECTIONS', 20)),
            'command_timeout': int(os.getenv('DB_COMMAND_TIMEOUT', 60))
        }
    
    def get_connection_string(self) -> str:
        """Get PostgreSQL connection string"""
        return (
            f"postgresql://{self.config['user']}:{self.config['password']}"
            f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
        )
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters for asyncpg"""
        return {
            'host': self.config['host'],
            'port': self.config['port'],
            'database': self.config['database'],
            'user': self.config['user'],
            'password': self.config['password'],
            'min_size': self.config['min_connections'],
            'max_size': self.config['max_connections'],
            'command_timeout': self.config['command_timeout']
        }
    
    def get_supabase_connection_string(self) -> str:
        """Get Supabase connection string"""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_password = os.getenv('SUPABASE_PASSWORD')
        
        if not supabase_url or not supabase_password:
            raise ValueError("SUPABASE_URL and SUPABASE_PASSWORD environment variables must be set")
        
        # Extract database info from Supabase URL
        # Supabase URL format: https://project-id.supabase.co
        db_host = supabase_url.replace('https://', '').replace('.supabase.co', '')
        db_host = f"{db_host}.supabase.co"
        
        return (
            f"postgresql://postgres:{supabase_password}"
            f"@{db_host}:5432/postgres"
        )

# Global database config instance
db_config = DatabaseConfig()
