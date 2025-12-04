#!/usr/bin/env python3
"""
VAANI Response Generator
Generate natural language responses from templates and action parameters.

Usage:
    from pipeline.nlg.generate_response import ResponseGenerator
    
    generator = ResponseGenerator()
    response = generator.generate(action)
"""

from pipeline.nlg.nlg_templates import (
    get_template, get_contextual_greeting, 
    get_error_message, get_follow_up_question
)


class ResponseGenerator:
    """Generate natural language responses."""
    
    def __init__(self):
        """Initialize response generator."""
        pass
    
    def generate(self, action):
        """
        Generate response from action.

        Args:
            action: Action dictionary from DecisionManager or ActionExecutor result

        Returns:
            str: Generated response text
        """
        if isinstance(action, dict) and 'status' in action:
            return self._generate_action_result_response(action)

        action_type = action.get('action')

        if action_type == 'respond':
            return self._generate_simple_response(action)

        elif action_type == 'api_call':
            return self._generate_api_response(action)

        elif action_type == 'system_command':
            return self._generate_command_response(action)

        elif action_type == 'request_info':
            return self._generate_info_request(action)

        elif action_type == 'error':
            return self._generate_error_response(action)

        elif action_type == 'unknown_intent':
            return action.get('response', get_template('unknown_intent'))

        else:
            return get_template('error')

    def _generate_action_result_response(self, result):
        """Generate response from action execution result."""
        status = result.get('status', 'error')
        message = result.get('message', '')

        if status == 'success':
            return message
        elif status == 'error':
            return f"Sorry, {message}"
        else:
            return message
    
    def _generate_simple_response(self, action):
        """Generate simple response from template."""
        template_name = action.get('response_template')
        params = action.get('params', {})
        
        # Special handling for greeting
        if template_name == 'greeting':
            return get_contextual_greeting()
        
        # Get template and fill parameters
        template = get_template(template_name)
        
        try:
            return template.format(**params)
        except KeyError as e:
            return f"Error generating response: missing parameter {e}"
    
    def _generate_api_response(self, action):
        """Generate response for API call results."""
        api_name = action.get('api')
        params = action.get('params', {})
        template_name = action.get('response_template')
        
        # In real implementation, this would call actual APIs
        # For now, generate mock responses
        
        if api_name == 'weather':
            location = params.get('location', 'your location')
            # Mock weather data
            mock_data = {
                'location': location,
                'condition': 'sunny',
                'temperature': '28'
            }
            template = get_template(template_name)
            return template.format(**mock_data)
        
        elif api_name == 'knowledge_base':
            # Mock knowledge response
            return "I don't have that information right now, but I'm learning every day!"
        
        else:
            return get_template('error')
    
    def _generate_command_response(self, action):
        """Generate response for system commands."""
        command = action.get('command')
        params = action.get('params', {})
        template_name = action.get('response_template')
        
        # Get template and fill parameters
        template = get_template(template_name)
        
        try:
            return template.format(**params)
        except KeyError as e:
            return f"Error generating response: missing parameter {e}"
    
    def _generate_info_request(self, action):
        """Generate request for missing information."""
        missing = action.get('missing')
        custom_response = action.get('response')
        
        if custom_response:
            return custom_response
        
        question = get_follow_up_question(missing)
        template = get_template('missing_info')
        return template.format(question=question)
    
    def _generate_error_response(self, action):
        """Generate error response."""
        error_type = action.get('error_type')
        custom_message = action.get('message')
        
        if custom_message:
            return custom_message
        
        if error_type:
            return get_error_message(error_type)
        
        return get_template('error')
    
    def generate_confirmation(self, action_description):
        """Generate confirmation message."""
        template = get_template('confirmation')
        return template.format(action=action_description)
    
    def generate_goodbye(self):
        """Generate goodbye message."""
        return get_template('goodbye')


# Example usage
if __name__ == "__main__":
    print("🗣️  VAANI Response Generator Demo\n")
    
    generator = ResponseGenerator()
    
    # Test different action types
    test_actions = [
        {
            'action': 'respond',
            'response_template': 'greeting'
        },
        {
            'action': 'respond',
            'response_template': 'time',
            'params': {'time': '10:30 AM'}
        },
        {
            'action': 'api_call',
            'api': 'weather',
            'params': {'location': 'Mumbai'},
            'response_template': 'weather'
        },
        {
            'action': 'system_command',
            'command': 'set_alarm',
            'params': {'time': '7 AM'},
            'response_template': 'alarm_set'
        },
        {
            'action': 'request_info',
            'missing': 'location',
            'response': 'Which city would you like to know the weather for?'
        },
        {
            'action': 'respond',
            'response_template': 'joke'
        }
    ]
    
    for i, action in enumerate(test_actions, 1):
        response = generator.generate(action)
        print(f"{i}. Action: {action.get('action')}")
        print(f"   Response: {response}\n")
    
    # Test confirmation and goodbye
    print(f"Confirmation: {generator.generate_confirmation('Alarm set for 7 AM')}")
    print(f"Goodbye: {generator.generate_goodbye()}")

