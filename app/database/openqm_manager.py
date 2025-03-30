"""
OpenQM Database Manager for Email Management Application

This module provides database operations using OpenQM as the backend database.
It communicates with an OpenQM server running on Windows at a specified IP address.
"""

import os
import json
import logging
import socket
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Import QMClient for direct database operations
try:
    import qmclient
except ImportError:
    logging.error("QMClient module not found. Please install it or ensure it's in the Python path.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('openqm_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OpenQMManager:
    """
    OpenQM Database Manager for handling database operations with OpenQM.
    
    This class provides methods for:
    - Connecting to OpenQM server
    - Creating, reading, updating, and deleting records
    - Managing email data, attachments, and related entities
    """
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the OpenQM Database Manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.load_config(config_path)
        self.connection = None
        self.websvc_url = f"http://{self.server_ip}:{self.websvc_port}/qm/websvc"
        
    def load_config(self, config_path: str) -> None:
        """
        Load configuration from the specified file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            db_config = config.get('database', {}).get('openqm', {})
            self.server_ip = db_config.get('server_ip', '10.1.34.103')
            self.server_port = db_config.get('server_port', 4243)
            self.websvc_port = db_config.get('websvc_port', 8080)
            self.username = db_config.get('username', 'QMADMIN')
            self.password = db_config.get('password', '')
            self.account = db_config.get('account', 'EMAILORG')
            self.use_websvc = db_config.get('use_websvc', True)
            self.use_socket = db_config.get('use_socket', False)
            self.use_phantom = db_config.get('use_phantom', True)
            
            # Validate configuration
            if not self.server_ip:
                raise ValueError("OpenQM server IP address not specified")
                
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            # Set default values
            self.server_ip = '10.1.34.103'
            self.server_port = 4243
            self.websvc_port = 8080
            self.username = 'QMADMIN'
            self.password = ''
            self.account = 'EMAILORG'
            self.use_websvc = True
            self.use_socket = False
            self.use_phantom = True
            
    def connect(self) -> bool:
        """
        Connect to the OpenQM server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.use_websvc:
                # Using Web Services for connection
                logger.info(f"Connecting to OpenQM server via WebSVC at {self.websvc_url}")
                # Web services connection would be established per request
                return True
                
            else:
                # Using direct QMClient connection
                logger.info(f"Connecting to OpenQM server at {self.server_ip}:{self.server_port}")
                self.connection = qmclient.connect(
                    self.server_ip,
                    self.server_port,
                    self.username,
                    self.password,
                    self.account
                )
                return self.connection is not None
                
        except Exception as e:
            logger.error(f"Error connecting to OpenQM server: {str(e)}")
            return False
            
    def disconnect(self) -> None:
        """
        Disconnect from the OpenQM server.
        """
        if self.connection:
            try:
                self.connection.disconnect()
                logger.info("Disconnected from OpenQM server")
            except Exception as e:
                logger.error(f"Error disconnecting from OpenQM server: {str(e)}")
            finally:
                self.connection = None
                
    def execute_command(self, command: str) -> str:
        """
        Execute a command on the OpenQM server.
        
        Args:
            command: The command to execute
            
        Returns:
            The command output
        """
        try:
            if self.use_websvc:
                # Using Web Services for command execution
                import requests
                
                response = requests.post(
                    self.websvc_url,
                    json={
                        "action": "execute",
                        "command": command,
                        "account": self.account,
                        "username": self.username,
                        "password": self.password
                    }
                )
                
                if response.status_code == 200:
                    return response.json().get('result', '')
                else:
                    logger.error(f"Error executing command via WebSVC: {response.text}")
                    return ""
                    
            elif self.connection:
                # Using direct QMClient connection
                return self.connection.execute(command)
                
            else:
                # Try to connect first
                if self.connect():
                    return self.execute_command(command)
                else:
                    logger.error("Failed to connect to OpenQM server")
                    return ""
                    
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return ""
            
    def read_record(self, file_name: str, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a record from the OpenQM database.
        
        Args:
            file_name: The QM file name
            record_id: The record ID
            
        Returns:
            The record data as a dictionary, or None if not found
        """
        try:
            if self.use_websvc:
                # Using Web Services for record retrieval
                import requests
                
                response = requests.post(
                    self.websvc_url,
                    json={
                        "action": "read",
                        "file": file_name,
                        "id": record_id,
                        "account": self.account,
                        "username": self.username,
                        "password": self.password
                    }
                )
                
                if response.status_code == 200:
                    data = response.json().get('record', '')
                    if data:
                        return self._parse_record(data)
                    else:
                        return None
                else:
                    logger.error(f"Error reading record via WebSVC: {response.text}")
                    return None
                    
            elif self.connection:
                # Using direct QMClient connection
                record = self.connection.read(file_name, record_id)
                if record:
                    return self._parse_record(record)
                else:
                    return None
                    
            else:
                # Try to connect first
                if self.connect():
                    return self.read_record(file_name, record_id)
                else:
                    logger.error("Failed to connect to OpenQM server")
                    return None
                    
        except Exception as e:
            logger.error(f"Error reading record: {str(e)}")
            return None
            
    def write_record(self, file_name: str, record_id: str, data: Dict[str, Any]) -> bool:
        """
        Write a record to the OpenQM database.
        
        Args:
            file_name: The QM file name
            record_id: The record ID
            data: The record data as a dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert data dictionary to QM record format
            record_data = self._format_record(data)
            
            if self.use_websvc:
                # Using Web Services for record writing
                import requests
                
                response = requests.post(
                    self.websvc_url,
                    json={
                        "action": "write",
                        "file": file_name,
                        "id": record_id,
                        "record": record_data,
                        "account": self.account,
                        "username": self.username,
                        "password": self.password
                    }
                )
                
                if response.status_code == 200:
                    return response.json().get('success', False)
                else:
                    logger.error(f"Error writing record via WebSVC: {response.text}")
                    return False
                    
            elif self.connection:
                # Using direct QMClient connection
                return self.connection.write(file_name, record_id, record_data)
                
            else:
                # Try to connect first
                if self.connect():
                    return self.write_record(file_name, record_id, data)
                else:
                    logger.error("Failed to connect to OpenQM server")
                    return False
                    
        except Exception as e:
            logger.error(f"Error writing record: {str(e)}")
            return False
            
    def delete_record(self, file_name: str, record_id: str) -> bool:
        """
        Delete a record from the OpenQM database.
        
        Args:
            file_name: The QM file name
            record_id: The record ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.use_websvc:
                # Using Web Services for record deletion
                import requests
                
                response = requests.post(
                    self.websvc_url,
                    json={
                        "action": "delete",
                        "file": file_name,
                        "id": record_id,
                        "account": self.account,
                        "username": self.username,
                        "password": self.password
                    }
                )
                
                if response.status_code == 200:
                    return response.json().get('success', False)
                else:
                    logger.error(f"Error deleting record via WebSVC: {response.text}")
                    return False
                    
            elif self.connection:
                # Using direct QMClient connection
                return self.connection.delete(file_name, record_id)
                
            else:
                # Try to connect first
                if self.connect():
                    return self.delete_record(file_name, record_id)
                else:
                    logger.error("Failed to connect to OpenQM server")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting record: {str(e)}")
            return False
            
    def query(self, query_str: str) -> List[Dict[str, Any]]:
        """
        Execute a query on the OpenQM database.
        
        Args:
            query_str: The query string (QMBasic or QM command)
            
        Returns:
            A list of records matching the query
        """
        try:
            results = []
            
            if self.use_phantom:
                # Execute query using a phantom process on the server
                # This is more efficient for complex queries
                query_result = self.execute_command(f"PHANTOM EMAIL.QUERY '{query_str}'")
                
                # Parse the query result (implementation depends on how the phantom process returns data)
                # This is a simplified example
                if query_result:
                    result_ids = query_result.strip().split('\n')
                    for record_id in result_ids:
                        record = self.read_record("EMAILS", record_id.strip())
                        if record:
                            results.append(record)
                            
            else:
                # Execute query directly
                # This is a simplified example - actual implementation would depend on the query format
                query_result = self.execute_command(query_str)
                
                # Parse the query result
                if query_result:
                    result_ids = query_result.strip().split('\n')
                    for record_id in result_ids:
                        record = self.read_record("EMAILS", record_id.strip())
                        if record:
                            results.append(record)
                            
            return results
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return []
            
    def _parse_record(self, record_data: str) -> Dict[str, Any]:
        """
        Parse a QM record into a Python dictionary.
        
        Args:
            record_data: The QM record data
            
        Returns:
            The parsed record as a dictionary
        """
        try:
            # Split the record by field marks (ASCII 254)
            fields = record_data.split(chr(254))
            
            # Create a dictionary from the fields
            # This is a simplified example - actual implementation would depend on the record structure
            result = {}
            
            for i, field in enumerate(fields):
                if i == 0:
                    result['id'] = field
                elif i == 1:
                    result['type'] = field
                else:
                    # Handle multi-values (ASCII 253) and sub-values (ASCII 252)
                    if chr(253) in field:
                        values = field.split(chr(253))
                        result[f'field{i}'] = values
                    else:
                        result[f'field{i}'] = field
                        
            return result
            
        except Exception as e:
            logger.error(f"Error parsing record: {str(e)}")
            return {}
            
    def _format_record(self, data: Dict[str, Any]) -> str:
        """
        Format a Python dictionary into a QM record.
        
        Args:
            data: The record data as a dictionary
            
        Returns:
            The formatted QM record
        """
        try:
            # Convert dictionary to QM record format
            # This is a simplified example - actual implementation would depend on the record structure
            fields = []
            
            # Add ID and type fields
            fields.append(data.get('id', ''))
            fields.append(data.get('type', ''))
            
            # Add other fields
            for key, value in data.items():
                if key not in ['id', 'type']:
                    if isinstance(value, list):
                        # Handle multi-values
                        fields.append(chr(253).join(value))
                    else:
                        fields.append(str(value))
                        
            # Join fields with field marks (ASCII 254)
            return chr(254).join(fields)
            
        except Exception as e:
            logger.error(f"Error formatting record: {str(e)}")
            return ""
            
    # Email-specific methods
    
    def add_user(self, user_data: Dict[str, Any]) -> str:
        """
        Add a user to the database.
        
        Args:
            user_data: User data
            
        Returns:
            User ID
        """
        user_id = user_data.get('id', str(uuid.uuid4()))
        user_data['id'] = user_id
        
        if self.write_record("USERS", user_id, user_data):
            return user_id
        else:
            return ""
            
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User data or None if not found
        """
        return self.read_record("USERS", user_id)
        
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by username.
        
        Args:
            username: Username
            
        Returns:
            User data or None if not found
        """
        # Execute a query to find the user by username
        query_result = self.execute_command(f"SELECT USERS WITH USERNAME = '{username}'")
        
        if query_result:
            user_ids = query_result.strip().split('\n')
            if user_ids and user_ids[0]:
                return self.read_record("USERS", user_ids[0])
                
        return None
        
    def add_email(self, email_data: Dict[str, Any]) -> str:
        """
        Add an email to the database.
        
        Args:
            email_data: Email data
            
        Returns:
            Email ID
        """
        email_id = email_data.get('id', str(uuid.uuid4()))
        email_data['id'] = email_id
        
        if self.write_record("EMAILS", email_id, email_data):
            # If the email is part of a thread, update the thread
            thread_id = email_data.get('thread_id')
            if thread_id:
                thread = self.read_record("THREADS", thread_id)
                if thread:
                    # Add email to thread's email list
                    emails = thread.get('emails', [])
                    if email_id not in emails:
                        emails.append(email_id)
                        thread['emails'] = emails
                        
                        # Update thread dates if needed
                        email_date = email_data.get('date_sent')
                        if email_date:
                            if not thread.get('date_started') or email_date < thread.get('date_started'):
                                thread['date_started'] = email_date
                            if not thread.get('last_date') or email_date > thread.get('last_date'):
                                thread['last_date'] = email_date
                                
                        # Write updated thread back to database
                        self.write_record("THREADS", thread_id, thread)
                        
            return email_id
        else:
            return ""
            
    def get_email(self, email_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an email by ID.
        
        Args:
            email_id: Email ID
            
        Returns:
            Email data or None if not found
        """
        return self.read_record("EMAILS", email_id)
        
    def search_emails(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for emails based on filters.
        
        Args:
            filters: Search filters
            
        Returns:
            List of matching emails
        """
        # Build the query string based on filters
        query_parts = []
        
        if 'account_id' in filters:
            account_id = filters['account_id']
            if isinstance(account_id, list):
                account_ids = "'" + "','".join(account_id) + "'"
                query_parts.append(f"ACCOUNT_ID IN ({account_ids})")
            else:
                query_parts.append(f"ACCOUNT_ID = '{account_id}'")
                
        if 'thread_id' in filters:
            query_parts.append(f"THREAD_ID = '{filters['thread_id']}'")
            
        if 'from_address' in filters:
            query_parts.append(f"FROM_ADDRESS LIKE '%{filters['from_address']}%'")
            
        if 'to_address' in filters:
            query_parts.append(f"TO_ADDRESSES LIKE '%{filters['to_address']}%'")
            
        if 'subject' in filters:
            query_parts.append(f"SUBJECT LIKE '%{filters['subject']}%'")
            
        if 'start_date' in filters:
            start_date = filters['start_date']
            if isinstance(start_date, datetime):
                start_date = start_date.isoformat()
            query_parts.append(f"DATE_SENT >= '{start_date}'")
            
        if 'end_date' in filters:
            end_date = filters['end_date']
            if isinstance(end_date, datetime):
                end_date = end_date.isoformat()
            query_parts.append(f"DATE_SENT <= '{end_date}'")
            
        # Build the final query
        if query_parts:
            query = "SELECT EMAILS WITH " + " AND ".join(query_parts)
        else:
            query = "SELECT EMAILS"
            
        # Execute the query
        return self.query(query)
        
    def add_thread(self, thread_data: Dict[str, Any]) -> str:
        """
        Add a thread to the database.
        
        Args:
            thread_data: Thread data
            
        Returns:
            Thread ID
        """
        thread_id = thread_data.get('id', str(uuid.uuid4()))
        thread_data['id'] = thread_id
        
        if self.write_record("THREADS", thread_id, thread_data):
            return thread_id
        else:
            return ""
            
    def get_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a thread by ID.
        
        Args:
            thread_id: Thread ID
            
        Returns:
            Thread data or None if not found
        """
        return self.read_record("THREADS", thread_id)
        
    def search_threads(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for threads based on filters.
        
        Args:
            filters: Search filters
            
        Returns:
            List of matching threads
        """
        # Build the query string based on filters
        query_parts = []
        
        if 'subject' in filters:
            query_parts.append(f"SUBJECT LIKE '%{filters['subject']}%'")
            
        if 'start_date' in filters:
            start_date = filters['start_date']
            if isinstance(start_date, datetime):
                start_date = start_date.isoformat()
            query_parts.append(f"DATE_STARTED >= '{start_date}'")
            
        if 'end_date' in filters:
            end_date = filters['end_date']
            if isinstance(end_date, datetime):
                end_date = end_date.isoformat()
            query_parts.append(f"LAST_DATE <= '{end_date}'")
            
        # Build the final query
        if query_parts:
            query = "SELECT THREADS WITH " + " AND ".join(query_parts)
        else:
            query = "SELECT THREADS"
            
        # Execute the query
        return self.query(query)
        
    def add_attachment(self, attachment_data: Dict[str, Any]) -> str:
        """
        Add an attachment to the database.
        
        Args:
            attachment_data: Attachment data
            
        Returns:
            Attachment ID
        """
        attachment_id = attachment_data.get('id', str(uuid.uuid4()))
        attachment_data['id'] = attachment_id
        
        if self.write_record("ATTACHMENTS", attachment_id, attachment_data):
            return attachment_id
        else:
            return ""
            
    def get_attachment(self, attachment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an attachment by ID.
        
        Args:
            attachment_id: Attachment ID
            
        Returns:
            Attachment data or None if not found
        """
        return self.read_record("ATTACHMENTS", attachment_id)
        
    def get_email_attachments(self, email_id: str) -> List[Dict[str, Any]]:
        """
        Get all attachments for an email.
        
        Args:
            email_id: Email ID
            
        Returns:
            List of attachment data
        """
        email = self.get_email(email_id)
        if not email:
            return []
            
        attachment_ids = email.get('attachment_ids', [])
        attachments = []
        
        for attachment_id in attachment_ids:
            attachment = self.get_attachment(attachment_id)
            if attachment:
                attachments.append(attachment)
                
        return attachments


# Example usage
if __name__ == "__main__":
    db = OpenQMManager()
    
    # Test connection
    if db.connect():
        print("Connected to OpenQM server")
        
        # Test query
        emails = db.search_emails({"subject": "Test"})
        print(f"Found {len(emails)} emails with subject containing 'Test'")
        
        # Disconnect
        db.disconnect()
    else:
        print("Failed to connect to OpenQM server")
