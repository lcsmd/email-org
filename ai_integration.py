"""
AI Integration Module for Email Management Application

This module provides AI-driven natural language processing capabilities for the email management application.
It allows users to interact with their emails using natural language commands and queries.
"""

import os
import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
import openai
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIIntegration:
    """
    AI Integration class for processing natural language commands and queries.
    
    This class provides methods for:
    - Processing natural language commands for email management
    - Generating email categorization rules
    - Summarizing email content
    - Suggesting responses to emails
    - Extracting key information from emails
    """
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the AI Integration module.
        
        Args:
            config_path: Path to the configuration file
        """
        self.load_config(config_path)
        self.setup_openai()
        
    def load_config(self, config_path: str) -> None:
        """
        Load configuration from the specified file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            self.config = config.get('ai', {})
            self.api_key = self.config.get('openai_api_key', '')
            self.model = self.config.get('model', 'gpt-4')
            self.temperature = self.config.get('temperature', 0.7)
            self.max_tokens = self.config.get('max_tokens', 500)
            
            if not self.api_key:
                logger.warning("OpenAI API key not found in configuration")
                
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            self.config = {}
            self.api_key = ''
            self.model = 'gpt-4'
            self.temperature = 0.7
            self.max_tokens = 500
            
    def setup_openai(self) -> None:
        """
        Set up the OpenAI client with the API key.
        """
        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.warning("OpenAI API key not set, AI features will not work")
            
    def process_command(self, command: str, user_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a natural language command from the user.
        
        Args:
            command: The natural language command
            user_id: The ID of the user making the command
            context: Additional context for the command (e.g., current view, selected emails)
            
        Returns:
            A dictionary containing the processed command and any relevant actions or data
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'OpenAI API key not configured',
                'command_type': 'unknown',
                'actions': []
            }
            
        try:
            # Prepare context for the AI
            context_str = self._format_context(context)
            
            # Prepare the prompt for the AI
            prompt = f"""
            You are an AI assistant for an email management application. The user has given you the following command:
            
            "{command}"
            
            {context_str}
            
            Analyze this command and return a structured response with the following information:
            1. The type of command (search, filter, categorize, summarize, respond, etc.)
            2. The specific actions to take
            3. Any parameters or filters to apply
            
            Return your response as a JSON object with the following structure:
            {{
                "command_type": "the type of command",
                "actions": [
                    {{
                        "action": "the specific action to take",
                        "parameters": {{
                            "param1": "value1",
                            "param2": "value2"
                        }}
                    }}
                ],
                "explanation": "A brief explanation of what you understood and what actions you're taking"
            }}
            """
            
            # Call the OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant for email management."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract and parse the response
            ai_response = response.choices[0].message.content.strip()
            parsed_response = self._extract_json(ai_response)
            
            if not parsed_response:
                return {
                    'success': False,
                    'error': 'Failed to parse AI response',
                    'command_type': 'unknown',
                    'actions': []
                }
                
            # Add success flag to the response
            parsed_response['success'] = True
            
            return parsed_response
            
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'command_type': 'unknown',
                'actions': []
            }
            
    def generate_categorization_rules(self, emails: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
        """
        Generate categorization rules based on a set of emails.
        
        Args:
            emails: A list of email data to analyze
            user_id: The ID of the user
            
        Returns:
            A list of suggested categorization rules
        """
        if not self.api_key or not emails:
            return []
            
        try:
            # Prepare email data for the AI
            email_data = self._format_emails_for_analysis(emails)
            
            # Prepare the prompt for the AI
            prompt = f"""
            You are an AI assistant for an email management application. Analyze the following set of emails:
            
            {email_data}
            
            Based on these emails, suggest categorization rules that would help organize the user's inbox.
            Consider sender domains, subject patterns, content keywords, and other relevant factors.
            
            Return your suggestions as a JSON array with the following structure for each rule:
            [
                {{
                    "rule_name": "A descriptive name for the rule",
                    "rule_type": "The type of rule (domain, subject, content, etc.)",
                    "pattern": "The pattern to match",
                    "category": "The suggested category name",
                    "priority": "A suggested priority level (high, medium, low)",
                    "explanation": "Why you're suggesting this rule"
                }}
            ]
            """
            
            # Call the OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant for email management."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract and parse the response
            ai_response = response.choices[0].message.content.strip()
            parsed_response = self._extract_json(ai_response)
            
            if not parsed_response or not isinstance(parsed_response, list):
                return []
                
            return parsed_response
            
        except Exception as e:
            logger.error(f"Error generating categorization rules: {str(e)}")
            return []
            
    def summarize_email(self, email_data: Dict[str, Any]) -> str:
        """
        Generate a summary of an email.
        
        Args:
            email_data: The email data to summarize
            
        Returns:
            A summary of the email
        """
        if not self.api_key:
            return "Email summarization not available (API key not configured)"
            
        try:
            # Extract relevant email content
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            sender = email_data.get('from_address', '')
            
            # Prepare the prompt for the AI
            prompt = f"""
            Summarize the following email:
            
            From: {sender}
            Subject: {subject}
            
            {body}
            
            Provide a concise summary (2-3 sentences) that captures the main points and any action items.
            """
            
            # Call the OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant for email management."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,  # Lower temperature for more focused summary
                max_tokens=100    # Limit tokens for concise summary
            )
            
            # Extract the summary
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing email: {str(e)}")
            return "Error generating summary"
            
    def suggest_response(self, email_data: Dict[str, Any], user_profile: Dict[str, Any] = None) -> str:
        """
        Suggest a response to an email.
        
        Args:
            email_data: The email data to respond to
            user_profile: Optional user profile information to personalize the response
            
        Returns:
            A suggested response to the email
        """
        if not self.api_key:
            return "Response suggestions not available (API key not configured)"
            
        try:
            # Extract relevant email content
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            sender = email_data.get('from_address', '')
            
            # Prepare user context
            user_context = ""
            if user_profile:
                name = user_profile.get('first_name', '') + ' ' + user_profile.get('last_name', '')
                role = user_profile.get('role', '')
                user_context = f"Your name is {name.strip()}."
                if role:
                    user_context += f" You work as a {role}."
            
            # Prepare the prompt for the AI
            prompt = f"""
            You need to draft a professional email response to the following email:
            
            From: {sender}
            Subject: {subject}
            
            {body}
            
            {user_context}
            
            Draft a concise, professional response that addresses the main points of the email.
            Be polite and maintain a professional tone. If there are action items or questions,
            address them appropriately.
            """
            
            # Call the OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant for email management."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=250
            )
            
            # Extract the suggested response
            suggested_response = response.choices[0].message.content.strip()
            return suggested_response
            
        except Exception as e:
            logger.error(f"Error suggesting response: {str(e)}")
            return "Error generating response suggestion"
            
    def extract_key_information(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key information from an email.
        
        Args:
            email_data: The email data to analyze
            
        Returns:
            A dictionary containing extracted key information
        """
        if not self.api_key:
            return {"error": "Information extraction not available (API key not configured)"}
            
        try:
            # Extract relevant email content
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            
            # Prepare the prompt for the AI
            prompt = f"""
            Extract key information from the following email:
            
            Subject: {subject}
            
            {body}
            
            Extract and return the following information in JSON format:
            1. Any dates or deadlines mentioned
            2. Action items or requests
            3. Key contacts or people mentioned
            4. Important facts or figures
            5. Any decisions made or conclusions
            
            Return your response as a JSON object with these categories as keys.
            """
            
            # Call the OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant for email management."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more accurate extraction
                max_tokens=300
            )
            
            # Extract and parse the response
            ai_response = response.choices[0].message.content.strip()
            parsed_response = self._extract_json(ai_response)
            
            if not parsed_response:
                return {"error": "Failed to extract information"}
                
            return parsed_response
            
        except Exception as e:
            logger.error(f"Error extracting key information: {str(e)}")
            return {"error": str(e)}
    
    def _format_context(self, context: Dict[str, Any] = None) -> str:
        """
        Format context information for the AI prompt.
        
        Args:
            context: Context information
            
        Returns:
            Formatted context string
        """
        if not context:
            return "No additional context provided."
            
        context_parts = []
        
        if 'current_view' in context:
            context_parts.append(f"Current view: {context['current_view']}")
            
        if 'selected_emails' in context and context['selected_emails']:
            email_count = len(context['selected_emails'])
            context_parts.append(f"Selected emails: {email_count}")
            
        if 'current_folder' in context:
            context_parts.append(f"Current folder: {context['current_folder']}")
            
        if 'filters' in context and context['filters']:
            filter_str = ", ".join([f"{k}: {v}" for k, v in context['filters'].items()])
            context_parts.append(f"Active filters: {filter_str}")
            
        if context_parts:
            return "Context:\n" + "\n".join(context_parts)
        else:
            return "No additional context provided."
    
    def _format_emails_for_analysis(self, emails: List[Dict[str, Any]]) -> str:
        """
        Format email data for AI analysis.
        
        Args:
            emails: List of email data
            
        Returns:
            Formatted email data string
        """
        if not emails:
            return "No emails provided."
            
        # Limit to a reasonable number of emails for analysis
        max_emails = min(10, len(emails))
        emails = emails[:max_emails]
        
        email_parts = []
        
        for i, email in enumerate(emails, 1):
            subject = email.get('subject', 'No subject')
            sender = email.get('from_address', 'Unknown sender')
            date = email.get('date_sent', '')
            if date:
                date = date if isinstance(date, str) else date.isoformat()
                
            # Truncate body for analysis
            body = email.get('body', '')
            if body and len(body) > 500:
                body = body[:500] + "..."
                
            email_parts.append(f"Email {i}:\nFrom: {sender}\nDate: {date}\nSubject: {subject}\nBody: {body}\n")
            
        return "\n".join(email_parts)
    
    def _extract_json(self, text: str) -> Any:
        """
        Extract and parse JSON from text.
        
        Args:
            text: Text containing JSON
            
        Returns:
            Parsed JSON object or None if parsing fails
        """
        try:
            # Try to parse the entire text as JSON
            return json.loads(text)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON using regex
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```|{[\s\S]*}|\[[\s\S]*\]', text)
            if json_match:
                json_str = json_match.group(1) if json_match.group(1) else json_match.group(0)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse extracted JSON: {json_str}")
                    return None
            else:
                logger.error("No JSON found in response")
                return None


# Example usage
if __name__ == "__main__":
    ai = AIIntegration()
    
    # Example command processing
    result = ai.process_command(
        "Find all emails from John about the budget meeting last week",
        "user123",
        {"current_view": "inbox", "filters": {"folder": "inbox"}}
    )
    
    print(json.dumps(result, indent=2))
