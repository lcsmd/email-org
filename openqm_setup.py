"""
OpenQM Database Setup Script for Email Management Application

This script sets up the necessary database structure in OpenQM for the Email Management Application.
It creates the required files, dictionaries, and phantom processes for efficient email processing.

Usage:
    python openqm_setup.py
"""

import os
import sys
import json
import logging
from app.database.qmclient import connect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('openqm_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_path='config.json'):
    """
    Load configuration from the specified file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return {}

def setup_openqm_database():
    """
    Set up the OpenQM database structure for the Email Management Application.
    
    Creates the necessary files, dictionaries, and phantom processes.
    """
    # Load configuration
    config = load_config()
    db_config = config.get('database', {}).get('openqm', {})
    
    # Extract connection parameters
    server_ip = db_config.get('server_ip', '10.1.34.103')
    server_port = db_config.get('server_port', 4243)
    username = db_config.get('username', 'QMADMIN')
    password = db_config.get('password', '')
    account = db_config.get('account', 'EMAILORG')
    use_websvc = db_config.get('use_websvc', True)
    
    # Connect to OpenQM
    logger.info(f"Connecting to OpenQM server at {server_ip}:{server_port}")
    conn = connect(server_ip, server_port, username, password, account, use_websvc)
    
    if not conn:
        logger.error("Failed to connect to OpenQM server")
        return False
    
    try:
        # Create the necessary files if they don't exist
        logger.info("Creating database files")
        
        # Define the files to create
        files = [
            "USERS",        # User accounts
            "EMAILS",       # Email messages
            "THREADS",      # Email threads
            "ATTACHMENTS",  # Email attachments
            "HTML_OBJECTS", # HTML embedded objects
            "BODIES",       # Email body content
            "CATEGORIES",   # Email categories
            "RULES",        # Email rules
            "DOMAINS",      # Email domains
            "CONTACTS",     # Contact information
            "DISCLAIMERS",  # Email disclaimers
            "KEYWORDS"      # Email keywords
        ]
        
        # Create each file
        for file_name in files:
            result = conn.execute(f"CREATE.FILE {file_name} DIRECTORY")
            logger.info(f"Created file {file_name}: {result}")
            
            # Create dictionary items for each file
            create_dictionary_items(conn, file_name)
        
        # Create phantom processes for email processing
        logger.info("Creating phantom processes")
        create_phantom_processes(conn)
        
        # Create web service endpoints
        logger.info("Creating web service endpoints")
        create_web_services(conn)
        
        logger.info("OpenQM database setup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error setting up OpenQM database: {str(e)}")
        return False
    finally:
        # Disconnect from OpenQM
        if hasattr(conn, 'disconnect'):
            conn.disconnect()

def create_dictionary_items(conn, file_name):
    """
    Create dictionary items for the specified file.
    
    Args:
        conn: OpenQM connection
        file_name: Name of the file to create dictionary items for
    """
    try:
        # Define dictionary items based on file type
        if file_name == "USERS":
            items = [
                {"name": "ID", "type": "C", "description": "User ID (UUID)"},
                {"name": "USERNAME", "type": "C", "description": "Username"},
                {"name": "PASSWORD", "type": "C", "description": "Encrypted password"},
                {"name": "EMAIL", "type": "C", "description": "User email address"},
                {"name": "FIRST_NAME", "type": "C", "description": "First name"},
                {"name": "LAST_NAME", "type": "C", "description": "Last name"},
                {"name": "CREATED_AT", "type": "D", "description": "Creation date"},
                {"name": "LAST_LOGIN", "type": "D", "description": "Last login date"},
                {"name": "ROLE", "type": "C", "description": "User role"},
                {"name": "STATUS", "type": "C", "description": "Account status"}
            ]
        elif file_name == "EMAILS":
            items = [
                {"name": "ID", "type": "C", "description": "Email ID (UUID)"},
                {"name": "ACCOUNT_ID", "type": "C", "description": "Email account ID"},
                {"name": "FROM_ADDRESS", "type": "C", "description": "Sender email address"},
                {"name": "TO_ADDRESSES", "type": "C", "description": "Recipient email addresses (multi-value)"},
                {"name": "CC_ADDRESSES", "type": "C", "description": "CC email addresses (multi-value)"},
                {"name": "BCC_ADDRESSES", "type": "C", "description": "BCC email addresses (multi-value)"},
                {"name": "SUBJECT", "type": "C", "description": "Email subject"},
                {"name": "DATE_SENT", "type": "D", "description": "Date sent"},
                {"name": "DATE_RECEIVED", "type": "D", "description": "Date received"},
                {"name": "BODY_ID", "type": "C", "description": "Body ID reference"},
                {"name": "HTML_ID", "type": "C", "description": "HTML ID reference"},
                {"name": "THREAD_ID", "type": "C", "description": "Thread ID reference"},
                {"name": "ATTACHMENT_IDS", "type": "C", "description": "Attachment IDs (multi-value)"},
                {"name": "CATEGORY_IDS", "type": "C", "description": "Category IDs (multi-value)"},
                {"name": "DISCLAIMER_IDS", "type": "C", "description": "Disclaimer IDs (multi-value)"},
                {"name": "PRIORITY", "type": "I", "description": "Email priority"},
                {"name": "IS_READ", "type": "B", "description": "Read status"},
                {"name": "IS_FLAGGED", "type": "B", "description": "Flagged status"},
                {"name": "IS_DELETED", "type": "B", "description": "Deleted status"},
                {"name": "IS_SPAM", "type": "B", "description": "Spam status"},
                {"name": "SPAM_SCORE", "type": "F", "description": "Spam score"},
                {"name": "IS_CONFIDENTIAL", "type": "B", "description": "Confidential status"},
                {"name": "RETENTION_POLICY", "type": "C", "description": "Retention policy"},
                {"name": "MESSAGE_ID", "type": "C", "description": "Original message ID"},
                {"name": "IN_REPLY_TO", "type": "C", "description": "In-reply-to header"},
                {"name": "REFERENCES", "type": "C", "description": "References header"}
            ]
        elif file_name == "THREADS":
            items = [
                {"name": "ID", "type": "C", "description": "Thread ID (UUID)"},
                {"name": "SUBJECT", "type": "C", "description": "Thread subject"},
                {"name": "EMAIL_IDS", "type": "C", "description": "Email IDs in thread (multi-value)"},
                {"name": "DATE_STARTED", "type": "D", "description": "Thread start date"},
                {"name": "LAST_DATE", "type": "D", "description": "Last email date"},
                {"name": "PARTICIPANT_IDS", "type": "C", "description": "Participant IDs (multi-value)"},
                {"name": "CATEGORY_IDS", "type": "C", "description": "Category IDs (multi-value)"},
                {"name": "PRIORITY", "type": "I", "description": "Thread priority"},
                {"name": "IS_COMPLETE", "type": "B", "description": "Thread completion status"}
            ]
        elif file_name == "ATTACHMENTS":
            items = [
                {"name": "ID", "type": "C", "description": "Attachment ID (UUID)"},
                {"name": "FILENAME", "type": "C", "description": "Original filename"},
                {"name": "CONTENT_TYPE", "type": "C", "description": "MIME content type"},
                {"name": "SIZE", "type": "I", "description": "File size in bytes"},
                {"name": "HASH", "type": "C", "description": "File hash for deduplication"},
                {"name": "STORAGE_PATH", "type": "C", "description": "Path to stored file"},
                {"name": "EMAIL_IDS", "type": "C", "description": "Email IDs using this attachment (multi-value)"},
                {"name": "DATE_ADDED", "type": "D", "description": "Date attachment was added"}
            ]
        elif file_name == "HTML_OBJECTS":
            items = [
                {"name": "ID", "type": "C", "description": "HTML object ID (UUID)"},
                {"name": "FILENAME", "type": "C", "description": "Original filename"},
                {"name": "CONTENT_TYPE", "type": "C", "description": "MIME content type"},
                {"name": "SIZE", "type": "I", "description": "File size in bytes"},
                {"name": "HASH", "type": "C", "description": "File hash for deduplication"},
                {"name": "STORAGE_PATH", "type": "C", "description": "Path to stored file"},
                {"name": "EMAIL_IDS", "type": "C", "description": "Email IDs using this object (multi-value)"},
                {"name": "DATE_ADDED", "type": "D", "description": "Date object was added"}
            ]
        elif file_name == "BODIES":
            items = [
                {"name": "ID", "type": "C", "description": "Body ID (UUID)"},
                {"name": "CONTENT", "type": "C", "description": "Text content"},
                {"name": "DISCLAIMER_IDS", "type": "C", "description": "Disclaimer IDs (multi-value)"},
                {"name": "LANGUAGE", "type": "C", "description": "Detected language"},
                {"name": "WORD_COUNT", "type": "I", "description": "Word count"},
                {"name": "HASH", "type": "C", "description": "Content hash for deduplication"}
            ]
        elif file_name == "CATEGORIES":
            items = [
                {"name": "ID", "type": "C", "description": "Category ID (UUID)"},
                {"name": "NAME", "type": "C", "description": "Category name"},
                {"name": "DESCRIPTION", "type": "C", "description": "Category description"},
                {"name": "PARENT_ID", "type": "C", "description": "Parent category ID"},
                {"name": "CHILD_IDS", "type": "C", "description": "Child category IDs (multi-value)"},
                {"name": "COLOR", "type": "C", "description": "Display color"},
                {"name": "USER_ID", "type": "C", "description": "Owner user ID"},
                {"name": "IS_SYSTEM", "type": "B", "description": "System category flag"}
            ]
        elif file_name == "RULES":
            items = [
                {"name": "ID", "type": "C", "description": "Rule ID (UUID)"},
                {"name": "NAME", "type": "C", "description": "Rule name"},
                {"name": "DESCRIPTION", "type": "C", "description": "Rule description"},
                {"name": "TYPE", "type": "C", "description": "Rule type"},
                {"name": "TARGETS", "type": "C", "description": "Target fields (multi-value)"},
                {"name": "PARAMETERS", "type": "C", "description": "Rule parameters (multi-value)"},
                {"name": "RESULTS", "type": "C", "description": "Rule results (multi-value)"},
                {"name": "USER_ID", "type": "C", "description": "Owner user ID"},
                {"name": "IS_ACTIVE", "type": "B", "description": "Active status"},
                {"name": "PRIORITY", "type": "I", "description": "Rule priority"}
            ]
        elif file_name == "DOMAINS":
            items = [
                {"name": "ID", "type": "C", "description": "Domain ID (UUID)"},
                {"name": "NAME", "type": "C", "description": "Domain name"},
                {"name": "CATEGORY_IDS", "type": "C", "description": "Category IDs (multi-value)"},
                {"name": "PRIORITY", "type": "I", "description": "Domain priority"},
                {"name": "RETENTION_POLICY", "type": "C", "description": "Retention policy"},
                {"name": "RULE_IDS", "type": "C", "description": "Rule IDs (multi-value)"}
            ]
        elif file_name == "CONTACTS":
            items = [
                {"name": "ID", "type": "C", "description": "Contact ID (UUID)"},
                {"name": "EMAIL", "type": "C", "description": "Email address"},
                {"name": "FIRST_NAME", "type": "C", "description": "First name"},
                {"name": "LAST_NAME", "type": "C", "description": "Last name"},
                {"name": "CATEGORY_IDS", "type": "C", "description": "Category IDs (multi-value)"},
                {"name": "PRIORITY", "type": "I", "description": "Contact priority"},
                {"name": "RETENTION_POLICY", "type": "C", "description": "Retention policy"},
                {"name": "USER_ID", "type": "C", "description": "Owner user ID"},
                {"name": "ORGANIZATION", "type": "C", "description": "Organization"},
                {"name": "PHONE", "type": "C", "description": "Phone number"},
                {"name": "NOTES", "type": "C", "description": "Notes"}
            ]
        elif file_name == "DISCLAIMERS":
            items = [
                {"name": "ID", "type": "C", "description": "Disclaimer ID (UUID)"},
                {"name": "TEXT", "type": "C", "description": "Disclaimer text"},
                {"name": "HASH", "type": "C", "description": "Text hash for deduplication"},
                {"name": "DOMAIN", "type": "C", "description": "Associated domain"},
                {"name": "DATE_ADDED", "type": "D", "description": "Date disclaimer was added"}
            ]
        elif file_name == "KEYWORDS":
            items = [
                {"name": "ID", "type": "C", "description": "Keyword ID (UUID)"},
                {"name": "KEYWORD", "type": "C", "description": "Keyword text"},
                {"name": "EMAIL_IDS", "type": "C", "description": "Email IDs containing this keyword (multi-value)"},
                {"name": "FREQUENCY", "type": "I", "description": "Keyword frequency"}
            ]
        else:
            items = []
        
        # Create dictionary items
        for item in items:
            cmd = f"CREATE.DICT {file_name} {item['name']} TYPE={item['type']}"
            result = conn.execute(cmd)
            logger.info(f"Created dictionary item {file_name}.{item['name']}: {result}")
            
            # Add description
            cmd = f"MODIFY.DICT {file_name} {item['name']} DESCRIPTION='{item['description']}'"
            result = conn.execute(cmd)
            
    except Exception as e:
        logger.error(f"Error creating dictionary items for {file_name}: {str(e)}")

def create_phantom_processes(conn):
    """
    Create phantom processes for email processing.
    
    Args:
        conn: OpenQM connection
    """
    try:
        # Create the EMAIL.QUERY program
        email_query_program = """
PROGRAM EMAIL.QUERY
* Program to query emails based on criteria
* Input: Query string
* Output: List of matching email IDs

$INCLUDE KEYS.H
$INCLUDE SYSCOM KEYS.H

QUERY.STR = SENTENCE(1)
IF QUERY.STR = '' THEN
  PRINT 'ERROR: No query string provided'
  STOP
END

EXECUTE 'SELECT EMAILS WITH ' : QUERY.STR : ' TO 11'
LIST.FILE = '11'

OPEN LIST.FILE TO F.LIST ELSE
  PRINT 'ERROR: Unable to open select list'
  STOP
END

LOOP
  READNEXT ID FROM F.LIST ELSE EXIT
  PRINT ID
REPEAT

CLOSE F.LIST
END
"""
        
        # Write the program to a file
        result = conn.execute("ED EMAIL.QUERY")
        if not result.startswith("ERROR"):
            for line in email_query_program.strip().split('\n'):
                result = conn.execute("I " + line)
            result = conn.execute("FS")
            logger.info("Created EMAIL.QUERY program")
            
            # Compile the program
            result = conn.execute("BASIC EMAIL.QUERY")
            logger.info(f"Compiled EMAIL.QUERY program: {result}")
        else:
            logger.error(f"Error creating EMAIL.QUERY program: {result}")
        
        # Create the EMAIL.PROCESS program
        email_process_program = """
PROGRAM EMAIL.PROCESS
* Program to process emails
* Input: Email ID
* Output: Processing result

$INCLUDE KEYS.H
$INCLUDE SYSCOM KEYS.H

EMAIL.ID = SENTENCE(1)
IF EMAIL.ID = '' THEN
  PRINT 'ERROR: No email ID provided'
  STOP
END

OPEN 'EMAILS' TO F.EMAILS ELSE
  PRINT 'ERROR: Unable to open EMAILS file'
  STOP
END

READ EMAIL.REC FROM F.EMAILS, EMAIL.ID ELSE
  PRINT 'ERROR: Email not found'
  STOP
END

* Process the email
* This is a placeholder for actual processing logic
PRINT 'Processing email ' : EMAIL.ID

* Update the email record
WRITE EMAIL.REC TO F.EMAILS, EMAIL.ID

CLOSE F.EMAILS
PRINT 'OK'
END
"""
        
        # Write the program to a file
        result = conn.execute("ED EMAIL.PROCESS")
        if not result.startswith("ERROR"):
            for line in email_process_program.strip().split('\n'):
                result = conn.execute("I " + line)
            result = conn.execute("FS")
            logger.info("Created EMAIL.PROCESS program")
            
            # Compile the program
            result = conn.execute("BASIC EMAIL.PROCESS")
            logger.info(f"Compiled EMAIL.PROCESS program: {result}")
        else:
            logger.error(f"Error creating EMAIL.PROCESS program: {result}")
            
    except Exception as e:
        logger.error(f"Error creating phantom processes: {str(e)}")

def create_web_services(conn):
    """
    Create web service endpoints for the Email Management Application.
    
    Args:
        conn: OpenQM connection
    """
    try:
        # Create the EMAIL.WS program for web services
        email_ws_program = """
PROGRAM EMAIL.WS
* Web service program for email management
* This program handles various email operations via web services

$INCLUDE KEYS.H
$INCLUDE SYSCOM KEYS.H
$INCLUDE SYSCOM WS.H

* Get the request data
REQUEST = WS$REQUEST
ACTION = REQUEST<'action'>

BEGIN CASE
  CASE ACTION = 'get_email'
    * Get an email by ID
    EMAIL.ID = REQUEST<'id'>
    IF EMAIL.ID = '' THEN
      WS$RESPONSE<'status'> = 'error'
      WS$RESPONSE<'message'> = 'Email ID is required'
      RETURN
    END
    
    OPEN 'EMAILS' TO F.EMAILS ELSE
      WS$RESPONSE<'status'> = 'error'
      WS$RESPONSE<'message'> = 'Unable to open EMAILS file'
      RETURN
    END
    
    READ EMAIL.REC FROM F.EMAILS, EMAIL.ID ELSE
      WS$RESPONSE<'status'> = 'error'
      WS$RESPONSE<'message'> = 'Email not found'
      CLOSE F.EMAILS
      RETURN
    END
    
    WS$RESPONSE<'status'> = 'success'
    WS$RESPONSE<'email'> = EMAIL.REC
    CLOSE F.EMAILS
    
  CASE ACTION = 'search_emails'
    * Search for emails based on criteria
    QUERY.STR = REQUEST<'query'>
    IF QUERY.STR = '' THEN
      QUERY.STR = '1'
    END
    
    EXECUTE 'SELECT EMAILS WITH ' : QUERY.STR : ' TO 11'
    LIST.FILE = '11'
    
    OPEN LIST.FILE TO F.LIST ELSE
      WS$RESPONSE<'status'> = 'error'
      WS$RESPONSE<'message'> = 'Unable to open select list'
      RETURN
    END
    
    EMAIL.IDS = ''
    LOOP
      READNEXT ID FROM F.LIST ELSE EXIT
      EMAIL.IDS<-1> = ID
    REPEAT
    
    CLOSE F.LIST
    
    WS$RESPONSE<'status'> = 'success'
    WS$RESPONSE<'email_ids'> = EMAIL.IDS
    
  CASE ACTION = 'add_email'
    * Add a new email
    EMAIL.REC = REQUEST<'email'>
    EMAIL.ID = REQUEST<'id'>
    
    IF EMAIL.ID = '' THEN
      WS$RESPONSE<'status'> = 'error'
      WS$RESPONSE<'message'> = 'Email ID is required'
      RETURN
    END
    
    OPEN 'EMAILS' TO F.EMAILS ELSE
      WS$RESPONSE<'status'> = 'error'
      WS$RESPONSE<'message'> = 'Unable to open EMAILS file'
      RETURN
    END
    
    WRITE EMAIL.REC TO F.EMAILS, EMAIL.ID
    
    WS$RESPONSE<'status'> = 'success'
    WS$RESPONSE<'id'> = EMAIL.ID
    CLOSE F.EMAILS
    
  CASE ACTION = 'update_email'
    * Update an existing email
    EMAIL.REC = REQUEST<'email'>
    EMAIL.ID = REQUEST<'id'>
    
    IF EMAIL.ID = '' THEN
      WS$RESPONSE<'status'> = 'error'
      WS$RESPONSE<'message'> = 'Email ID is required'
      RETURN
    END
    
    OPEN 'EMAILS' TO F.EMAILS ELSE
      WS$RESPONSE<'status'> = 'error'
      WS$RESPONSE<'message'> = 'Unable to open EMAILS file'
      RETURN
    END
    
    READ OLD.EMAIL.REC FROM F.EMAILS, EMAIL.ID ELSE
      WS$RESPONSE<'status'> = 'error'
      WS$RESPONSE<'message'> = 'Email not found'
      CLOSE F.EMAILS
      RETURN
    END
    
    WRITE EMAIL.REC TO F.EMAILS, EMAIL.ID
    
    WS$RESPONSE<'status'> = 'success'
    WS$RESPONSE<'id'> = EMAIL.ID
    CLOSE F.EMAILS
    
  CASE ACTION = 'delete_email'
    * Delete an email
    EMAIL.ID = REQUEST<'id'>
    
    IF EMAIL.ID = '' THEN
      WS$RESPONSE<'status'> = 'error'
      WS$RESPONSE<'message'> = 'Email ID is required'
      RETURN
    END
    
    OPEN 'EMAILS' TO F.EMAILS ELSE
      WS$RESPONSE<'status'> = 'error'
      WS$RESPONSE<'message'> = 'Unable to open EMAILS file'
      RETURN
    END
    
    DELETE F.EMAILS, EMAIL.ID
    
    WS$RESPONSE<'status'> = 'success'
    WS$RESPONSE<'id'> = EMAIL.ID
    CLOSE F.EMAILS
    
  CASE 1
    * Unknown action
    WS$RESPONSE<'status'> = 'error'
    WS$RESPONSE<'message'> = 'Unknown action: ' : ACTION
END CASE

END
"""
        
        # Write the program to a file
        result = conn.execute("ED EMAIL.WS")
        if not result.startswith("ERROR"):
            for line in email_ws_program.strip().split('\n'):
                result = conn.execute("I " + line)
            result = conn.execute("FS")
            logger.info("Created EMAIL.WS program")
            
            # Compile the program
            result = conn.execute("BASIC EMAIL.WS")
            logger.info(f"Compiled EMAIL.WS program: {result}")
            
            # Register the web service
            result = conn.execute("WS.REGISTER EMAIL.WS")
            logger.info(f"Registered EMAIL.WS web service: {result}")
        else:
            logger.error(f"Error creating EMAIL.WS program: {result}")
            
    except Exception as e:
        logger.error(f"Error creating web services: {str(e)}")

if __name__ == "__main__":
    setup_openqm_database()
