# Email Management Application

A comprehensive email management application with a web-based frontend that integrates with Exchange Online and Gmail, featuring an AI-driven natural language interface and robust email processing capabilities.

## Features

- **User Authentication and Email Account Management**
  - Secure user registration and login
  - Support for multiple email accounts (Exchange Online and Gmail)
  - Secure credential storage with encryption

- **Email Processing**
  - Retrieval from Exchange Online and Gmail
  - Extraction of metadata (sender, recipients, subject, body, attachments)
  - Deduplication of redundant emails
  - Disclaimer detection and removal

- **Attachment Management**
  - Secure storage of attachments
  - Unique file identification using hashing
  - Efficient retrieval and viewing

- **HTML Object Management**
  - Processing of HTML emails
  - Extraction and storage of embedded objects (images, etc.)
  - Proper rendering in the web interface

- **Thread Management**
  - Reconstruction of email threads
  - Chronological viewing of conversations
  - Thread-based organization

- **Search and Filtering**
  - Comprehensive search capabilities
  - Filtering by date, sender, subject, keywords, etc.
  - Quick access to relevant emails

- **Modern Web Interface**
  - Responsive design using Material UI
  - Intuitive navigation
  - Thread and email viewing

## Project Structure

```
email-org/
├── app/
│   ├── models/
│   │   └── database_models.py  # SQLAlchemy models
│   ├── database/
│   │   └── database_manager.py  # Database operations
│   ├── email_processing/
│   │   ├── email_processor.py  # Email processing logic
│   │   ├── html_processor.py  # HTML content processing
│   │   └── attachment_handler.py  # Attachment processing
│   ├── email_retriever.py  # Email retrieval from providers
│   └── thread_manager.py  # Thread management
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       │   ├── Authentication/
│       │   ├── Dashboard/
│       │   ├── EmailAccounts/
│       │   ├── Common/
│       │   └── User/
│       ├── services/
│       ├── utils/
│       ├── App.js
│       └── index.js
├── config.json  # Application configuration
├── api.py  # Flask API endpoints
├── setup.py  # Setup script
├── openqm_setup.py  # OpenQM database setup script
└── README.md
```

## Technology Stack

### Backend
- **Python**: Core programming language
- **Flask**: Web application framework
- **SQLAlchemy**: ORM for database operations
- **exchangelib**: Library for Exchange Online integration
- **google-api-python-client**: Library for Gmail integration
- **BeautifulSoup**: For HTML parsing
- **PyJWT**: For JWT authentication
- **OpenQM**: Primary database backend

### Frontend
- **React**: JavaScript library for building user interfaces
- **Material UI**: React component library
- **Axios**: HTTP client for API requests
- **React Router**: For navigation
- **JWT Decode**: For JWT token handling

### Database
- **OpenQM**: Primary database backend running on Windows Server
- **SQLite/PostgreSQL**: Alternative database options

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn
- OpenQM database server (running on Windows Server)

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/email-org.git
   cd email-org
   ```

2. Run the setup script to create the necessary directories and files:
   ```bash
   python setup.py
   ```

3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure the application by editing `config.json`:
   ```json
   {
     "database": {
       "type": "openqm",
       "openqm": {
         "server_ip": "10.1.34.103",
         "server_port": 4243,
         "websvc_port": 8080,
         "username": "QMADMIN",
         "password": "",
         "account": "EMAILORG",
         "use_websvc": true,
         "use_socket": false,
         "use_phantom": true
       }
     },
     "paths": {
       "attachment_folder": "./attachments",
       "html_object_folder": "./html_objects",
       "upload_folder": "./uploads"
     },
     "email": {
       "max_attachment_size": 10485760
     },
     "api": {
       "secret_key": "your-secret-key",
       "token_expiry": 86400,
       "debug": true,
       "host": "localhost",
       "port": 5000,
       "max_content_length": 16777216
     }
   }
   ```

6. Set up the OpenQM database structure:
   ```bash
   python openqm_setup.py
   ```

7. Start the Flask API server:
   ```bash
   python api.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the required npm packages:
   ```bash
   npm install
   ```

3. Create a `.env` file with the API URL:
   ```
   REACT_APP_API_URL=http://localhost:5000/api
   ```

4. Start the development server:
   ```bash
   npm start
   ```

5. Access the application at `http://localhost:3000`

## Usage

### User Registration and Login
1. Navigate to the application URL
2. Click "Sign Up" to create a new account
3. Login with your credentials

### Adding Email Accounts
1. Go to "Email Accounts" in the sidebar
2. Click "Add Account"
3. Enter your email account details
   - For Gmail, you'll need to generate an app password
   - For Exchange, you'll need your server details

### Managing Emails
1. View all emails in the "All Emails" section
2. Click on an email to view its contents
3. Use the search and filter options to find specific emails
4. View email threads in the "Threads" section

### Managing Attachments
1. Attachments are displayed in the email view
2. Click on an attachment to download it

## Future Enhancements

- **AI-Driven Natural Language Interface**: Implementation of an AI layer to assist users in managing categories, rules, and email reconstruction
- **Advanced Categorization**: Dynamic categorization of emails based on content and user preferences
- **Mobile Application**: Native mobile applications for iOS and Android
- **Calendar Integration**: Integration with calendar services for appointment management
- **Contact Management**: Advanced contact management features

## Security Considerations

- User credentials are encrypted before storage
- JWT authentication with token expiration
- Secure handling of email account credentials
- Input validation and sanitization
- CORS configuration for API security

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
