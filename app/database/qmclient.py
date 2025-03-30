"""
QMClient Python Wrapper for OpenQM

This module provides a Python wrapper for interacting with OpenQM database servers.
It supports both direct socket connections and web service connections.
"""

import socket
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qmclient.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ASCII control characters used by QM
FIELD_MARK = chr(254)
VALUE_MARK = chr(253)
SUBVALUE_MARK = chr(252)
TEXT_MARK = chr(251)
SEGMENT_MARK = chr(250)

class QMConnection:
    """
    QM Connection class for handling connections to OpenQM database servers.
    """
    
    def __init__(self, host: str, port: int, username: str, password: str, account: str):
        """
        Initialize a connection to an OpenQM server.
        
        Args:
            host: The server hostname or IP address
            port: The server port
            username: The username for authentication
            password: The password for authentication
            account: The QM account to use
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.account = account
        self.socket = None
        self.connected = False
        
    def connect(self) -> bool:
        """
        Connect to the OpenQM server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create a socket connection
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # Send login credentials
            login_data = f"{self.username}{FIELD_MARK}{self.password}{FIELD_MARK}{self.account}"
            self.socket.sendall(login_data.encode('utf-8'))
            
            # Receive response
            response = self.socket.recv(1024).decode('utf-8')
            
            if response.startswith('OK'):
                self.connected = True
                logger.info(f"Connected to OpenQM server at {self.host}:{self.port}")
                return True
            else:
                logger.error(f"Failed to connect to OpenQM server: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to OpenQM server: {str(e)}")
            return False
            
    def disconnect(self) -> None:
        """
        Disconnect from the OpenQM server.
        """
        if self.socket:
            try:
                # Send logout command
                self.socket.sendall(b'LOGOUT')
                self.socket.close()
                logger.info("Disconnected from OpenQM server")
            except Exception as e:
                logger.error(f"Error disconnecting from OpenQM server: {str(e)}")
            finally:
                self.socket = None
                self.connected = False
                
    def execute(self, command: str) -> str:
        """
        Execute a command on the OpenQM server.
        
        Args:
            command: The command to execute
            
        Returns:
            The command output
        """
        if not self.connected:
            logger.error("Not connected to OpenQM server")
            return ""
            
        try:
            # Send command
            cmd_data = f"EXECUTE{FIELD_MARK}{command}"
            self.socket.sendall(cmd_data.encode('utf-8'))
            
            # Receive response
            response = self._receive_data()
            return response
            
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return ""
            
    def read(self, file_name: str, record_id: str) -> str:
        """
        Read a record from the OpenQM database.
        
        Args:
            file_name: The QM file name
            record_id: The record ID
            
        Returns:
            The record data
        """
        if not self.connected:
            logger.error("Not connected to OpenQM server")
            return ""
            
        try:
            # Send read command
            cmd_data = f"READ{FIELD_MARK}{file_name}{FIELD_MARK}{record_id}"
            self.socket.sendall(cmd_data.encode('utf-8'))
            
            # Receive response
            response = self._receive_data()
            
            if response.startswith('ERROR'):
                logger.error(f"Error reading record: {response}")
                return ""
            else:
                return response
                
        except Exception as e:
            logger.error(f"Error reading record: {str(e)}")
            return ""
            
    def write(self, file_name: str, record_id: str, data: str) -> bool:
        """
        Write a record to the OpenQM database.
        
        Args:
            file_name: The QM file name
            record_id: The record ID
            data: The record data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Not connected to OpenQM server")
            return False
            
        try:
            # Send write command
            cmd_data = f"WRITE{FIELD_MARK}{file_name}{FIELD_MARK}{record_id}{FIELD_MARK}{data}"
            self.socket.sendall(cmd_data.encode('utf-8'))
            
            # Receive response
            response = self._receive_data()
            
            if response.startswith('OK'):
                return True
            else:
                logger.error(f"Error writing record: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error writing record: {str(e)}")
            return False
            
    def delete(self, file_name: str, record_id: str) -> bool:
        """
        Delete a record from the OpenQM database.
        
        Args:
            file_name: The QM file name
            record_id: The record ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Not connected to OpenQM server")
            return False
            
        try:
            # Send delete command
            cmd_data = f"DELETE{FIELD_MARK}{file_name}{FIELD_MARK}{record_id}"
            self.socket.sendall(cmd_data.encode('utf-8'))
            
            # Receive response
            response = self._receive_data()
            
            if response.startswith('OK'):
                return True
            else:
                logger.error(f"Error deleting record: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting record: {str(e)}")
            return False
            
    def select(self, file_name: str, query: str = "") -> List[str]:
        """
        Select records from the OpenQM database.
        
        Args:
            file_name: The QM file name
            query: The query string (optional)
            
        Returns:
            A list of record IDs matching the query
        """
        if not self.connected:
            logger.error("Not connected to OpenQM server")
            return []
            
        try:
            # Send select command
            if query:
                cmd_data = f"SELECT{FIELD_MARK}{file_name}{FIELD_MARK}{query}"
            else:
                cmd_data = f"SELECT{FIELD_MARK}{file_name}"
                
            self.socket.sendall(cmd_data.encode('utf-8'))
            
            # Receive response
            response = self._receive_data()
            
            if response.startswith('ERROR'):
                logger.error(f"Error selecting records: {response}")
                return []
            else:
                # Parse the list of record IDs
                return response.strip().split(VALUE_MARK)
                
        except Exception as e:
            logger.error(f"Error selecting records: {str(e)}")
            return []
            
    def _receive_data(self) -> str:
        """
        Receive data from the socket.
        
        Returns:
            The received data as a string
        """
        buffer = b""
        while True:
            chunk = self.socket.recv(4096)
            if not chunk:
                break
                
            buffer += chunk
            
            # Check if we've received the end of the data
            if chunk.endswith(b'\0') or len(chunk) < 4096:
                break
                
        return buffer.decode('utf-8').rstrip('\0')


class QMWebService:
    """
    QM Web Service class for handling connections to OpenQM web services.
    """
    
    def __init__(self, host: str, port: int, username: str, password: str, account: str):
        """
        Initialize a connection to an OpenQM web service.
        
        Args:
            host: The server hostname or IP address
            port: The server port
            username: The username for authentication
            password: The password for authentication
            account: The QM account to use
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.account = account
        self.base_url = f"http://{host}:{port}/qm/websvc"
        
    def execute(self, command: str) -> str:
        """
        Execute a command on the OpenQM server.
        
        Args:
            command: The command to execute
            
        Returns:
            The command output
        """
        try:
            response = requests.post(
                self.base_url,
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
                
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return ""
            
    def read(self, file_name: str, record_id: str) -> str:
        """
        Read a record from the OpenQM database.
        
        Args:
            file_name: The QM file name
            record_id: The record ID
            
        Returns:
            The record data
        """
        try:
            response = requests.post(
                self.base_url,
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
                return response.json().get('record', '')
            else:
                logger.error(f"Error reading record via WebSVC: {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Error reading record: {str(e)}")
            return ""
            
    def write(self, file_name: str, record_id: str, data: str) -> bool:
        """
        Write a record to the OpenQM database.
        
        Args:
            file_name: The QM file name
            record_id: The record ID
            data: The record data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                self.base_url,
                json={
                    "action": "write",
                    "file": file_name,
                    "id": record_id,
                    "record": data,
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
                
        except Exception as e:
            logger.error(f"Error writing record: {str(e)}")
            return False
            
    def delete(self, file_name: str, record_id: str) -> bool:
        """
        Delete a record from the OpenQM database.
        
        Args:
            file_name: The QM file name
            record_id: The record ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                self.base_url,
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
                
        except Exception as e:
            logger.error(f"Error deleting record: {str(e)}")
            return False
            
    def select(self, file_name: str, query: str = "") -> List[str]:
        """
        Select records from the OpenQM database.
        
        Args:
            file_name: The QM file name
            query: The query string (optional)
            
        Returns:
            A list of record IDs matching the query
        """
        try:
            payload = {
                "action": "select",
                "file": file_name,
                "account": self.account,
                "username": self.username,
                "password": self.password
            }
            
            if query:
                payload["query"] = query
                
            response = requests.post(
                self.base_url,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json().get('ids', [])
            else:
                logger.error(f"Error selecting records via WebSVC: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error selecting records: {str(e)}")
            return []


def connect(host: str, port: int, username: str, password: str, account: str, 
           use_websvc: bool = False) -> Union[QMConnection, QMWebService, None]:
    """
    Connect to an OpenQM server.
    
    Args:
        host: The server hostname or IP address
        port: The server port
        username: The username for authentication
        password: The password for authentication
        account: The QM account to use
        use_websvc: Whether to use web services instead of direct socket connection
        
    Returns:
        A QMConnection or QMWebService object, or None if connection fails
    """
    try:
        if use_websvc:
            # Use web services
            return QMWebService(host, port, username, password, account)
        else:
            # Use direct socket connection
            conn = QMConnection(host, port, username, password, account)
            if conn.connect():
                return conn
            else:
                return None
                
    except Exception as e:
        logger.error(f"Error connecting to OpenQM server: {str(e)}")
        return None


# Helper functions for working with QM data

def parse_record(record_data: str) -> Dict[str, Any]:
    """
    Parse a QM record into a Python dictionary.
    
    Args:
        record_data: The QM record data
        
    Returns:
        The parsed record as a dictionary
    """
    try:
        # Split the record by field marks
        fields = record_data.split(FIELD_MARK)
        
        # Create a dictionary from the fields
        result = {}
        
        for i, field in enumerate(fields):
            field_name = f"field{i}"
            
            # Handle multi-values
            if VALUE_MARK in field:
                values = field.split(VALUE_MARK)
                
                # Check if values contain subvalues
                has_subvalues = any(SUBVALUE_MARK in value for value in values)
                
                if has_subvalues:
                    # Handle subvalues
                    processed_values = []
                    for value in values:
                        if SUBVALUE_MARK in value:
                            processed_values.append(value.split(SUBVALUE_MARK))
                        else:
                            processed_values.append(value)
                    result[field_name] = processed_values
                else:
                    result[field_name] = values
            else:
                result[field_name] = field
                
        return result
        
    except Exception as e:
        logger.error(f"Error parsing record: {str(e)}")
        return {}
        
def format_record(data: Dict[str, Any]) -> str:
    """
    Format a Python dictionary into a QM record.
    
    Args:
        data: The record data as a dictionary
        
    Returns:
        The formatted QM record
    """
    try:
        fields = []
        
        for key, value in sorted(data.items()):
            if isinstance(value, list):
                # Handle lists (multi-values)
                values = []
                for item in value:
                    if isinstance(item, list):
                        # Handle sublists (subvalues)
                        values.append(SUBVALUE_MARK.join(str(subitem) for subitem in item))
                    else:
                        values.append(str(item))
                fields.append(VALUE_MARK.join(values))
            else:
                fields.append(str(value))
                
        return FIELD_MARK.join(fields)
        
    except Exception as e:
        logger.error(f"Error formatting record: {str(e)}")
        return ""


# Example usage
if __name__ == "__main__":
    # Example connection to OpenQM server
    conn = connect("10.1.34.103", 4243, "QMADMIN", "", "EMAILORG")
    
    if conn:
        print("Connected to OpenQM server")
        
        # Example command execution
        result = conn.execute("LIST USERS")
        print(f"Users: {result}")
        
        # Example record operations
        conn.write("USERS", "TEST", "Test User")
        record = conn.read("USERS", "TEST")
        print(f"Record: {record}")
        
        # Disconnect
        if isinstance(conn, QMConnection):
            conn.disconnect()
            
        print("Disconnected from OpenQM server")
    else:
        print("Failed to connect to OpenQM server")
