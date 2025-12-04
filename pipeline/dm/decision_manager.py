#!/usr/bin/env python3
"""
VAANI Decision Manager (DM)
Rule-based decision engine that determines next actions based on intent and state.

Usage:
    from pipeline.dm.decision_manager import DecisionManager
    
    dm = DecisionManager()
    action = dm.decide("QUERY_WEATHER", state, entities)
"""

from datetime import datetime
import random


class DecisionManager:
    """Rule-based decision manager for VAANI."""

    def __init__(self):
        """Initialize decision manager."""
        self.intent_handlers = {
            'GREETING': self.handle_greeting,
            'QUERY_TIME': self.handle_query_time,
            'QUERY_WEATHER': self.handle_query_weather,
            'OPEN_APP': self.handle_open_app,
            'CALL_PERSON': self.handle_call_person,
            'GENERAL_KNOWLEDGE': self.handle_general_knowledge,
            'ALARM_SET': self.handle_alarm_set,
            'REMINDER_SET': self.handle_reminder_set,
            'JOKE': self.handle_joke,
            'CASUAL_CHAT': self.handle_casual_chat
        }

        self.action_intents = {
            'OPEN_APP', 'CALL_PERSON', 'ALARM_SET', 'REMINDER_SET',
            'OPEN_WEBSITE', 'PLAY_MUSIC', 'PLAY_MEDIA',
            'VOLUME_UP', 'VOLUME_DOWN', 'VOLUME_SET',
            'BRIGHTNESS_UP', 'BRIGHTNESS_DOWN', 'BRIGHTNESS_SET',
            'OPEN_FILE', 'OPEN_FOLDER',
            'SYSTEM_SHUTDOWN', 'SYSTEM_RESTART', 'SYSTEM_LOCK', 'SYSTEM_SLEEP'
        }
    
    def decide(self, intent, state, entities=None):
        """
        Decide next action based on intent and state.

        Args:
            intent: Detected intent
            state: DialogueStateManager instance
            entities: Extracted entities

        Returns:
            dict: Action to take with parameters
        """
        if intent in self.action_intents:
            return {
                'should_act': True,
                'action': intent,
                'entities': entities or {},
                'context': {
                    'safe_mode': True,
                    'state': state
                }
            }

        handler = self.intent_handlers.get(intent)

        if handler:
            return handler(state, entities or [])
        else:
            return {
                'action': 'unknown_intent',
                'response': "I'm not sure how to help with that.",
                'complete': True
            }
    
    def handle_greeting(self, state, entities):
        """Handle greeting intent."""
        return {
            'action': 'respond',
            'response_template': 'greeting',
            'complete': True
        }
    
    def handle_query_time(self, state, entities):
        """Handle time query intent."""
        current_time = datetime.now().strftime("%I:%M %p")
        return {
            'action': 'respond',
            'response_template': 'time',
            'params': {'time': current_time},
            'complete': True
        }
    
    def handle_query_weather(self, state, entities):
        """Handle weather query intent."""
        # Check if location is provided
        location = None
        for ent in entities:
            if ent.get('type') == 'LOCATION' or ent.get('label') == 'LOCATION':
                location = ent.get('value') or ent.get('text')
                break
        
        if not location:
            # Check state for previous location
            location = state.get_entity('LOCATION')
        
        if not location:
            # Missing information
            return {
                'action': 'request_info',
                'missing': 'location',
                'response': "Which city would you like to know the weather for?",
                'complete': False
            }
        
        # Call weather API (placeholder)
        return {
            'action': 'api_call',
            'api': 'weather',
            'params': {'location': location},
            'response_template': 'weather',
            'complete': True
        }
    
    def handle_open_app(self, state, entities):
        """Handle app opening intent."""
        # Check if app name is provided
        app_name = None
        for ent in entities:
            if ent.get('type') == 'APP' or ent.get('label') == 'APP':
                app_name = ent.get('value') or ent.get('text')
                break
        
        if not app_name:
            return {
                'action': 'request_info',
                'missing': 'app_name',
                'response': "Which app would you like to open?",
                'complete': False
            }
        
        return {
            'action': 'system_command',
            'command': 'open_app',
            'params': {'app_name': app_name},
            'response_template': 'open_app',
            'complete': True
        }
    
    def handle_call_person(self, state, entities):
        """Handle call person intent."""
        # Check if person is provided
        person = None
        for ent in entities:
            if ent.get('type') == 'PERSON' or ent.get('label') == 'PERSON':
                person = ent.get('value') or ent.get('text')
                break
        
        if not person:
            return {
                'action': 'request_info',
                'missing': 'person',
                'response': "Who would you like to call?",
                'complete': False
            }
        
        return {
            'action': 'system_command',
            'command': 'make_call',
            'params': {'person': person},
            'response_template': 'call_person',
            'complete': True
        }
    
    def handle_general_knowledge(self, state, entities):
        """Handle general knowledge query."""
        return {
            'action': 'api_call',
            'api': 'knowledge_base',
            'params': {'query': state.get_last_turn()['user_input']},
            'response_template': 'general_knowledge',
            'complete': True
        }
    
    def handle_alarm_set(self, state, entities):
        """Handle alarm setting intent."""
        # Check if time is provided
        time = None
        for ent in entities:
            if ent.get('type') == 'TIME' or ent.get('label') == 'TIME':
                time = ent.get('value') or ent.get('text')
                break
        
        if not time:
            return {
                'action': 'request_info',
                'missing': 'time',
                'response': "What time should I set the alarm for?",
                'complete': False
            }
        
        return {
            'action': 'system_command',
            'command': 'set_alarm',
            'params': {'time': time},
            'response_template': 'alarm_set',
            'complete': True
        }
    
    def handle_reminder_set(self, state, entities):
        """Handle reminder setting intent."""
        # Check for task and time
        task = None
        time = None
        
        for ent in entities:
            ent_type = ent.get('type') or ent.get('label')
            ent_value = ent.get('value') or ent.get('text')
            
            if ent_type == 'TASK':
                task = ent_value
            elif ent_type in ['TIME', 'DATE']:
                time = ent_value
        
        if not task:
            return {
                'action': 'request_info',
                'missing': 'task',
                'response': "What should I remind you about?",
                'complete': False
            }
        
        if not time:
            return {
                'action': 'request_info',
                'missing': 'time',
                'response': "When should I remind you?",
                'complete': False
            }
        
        return {
            'action': 'system_command',
            'command': 'set_reminder',
            'params': {'task': task, 'time': time},
            'response_template': 'reminder_set',
            'complete': True
        }
    
    def handle_joke(self, state, entities):
        """Handle joke request."""
        return {
            'action': 'respond',
            'response_template': 'joke',
            'complete': True
        }
    
    def handle_casual_chat(self, state, entities):
        """Handle casual chat."""
        return {
            'action': 'respond',
            'response_template': 'casual_chat',
            'complete': True
        }


# Example usage
if __name__ == "__main__":
    from pipeline.dst.state_manager import DialogueStateManager
    
    print("🎯 VAANI Decision Manager Demo\n")
    
    dm = DecisionManager()
    state = DialogueStateManager()
    
    # Test different intents
    test_cases = [
        ("GREETING", []),
        ("QUERY_TIME", []),
        ("QUERY_WEATHER", [{"type": "LOCATION", "value": "Mumbai"}]),
        ("QUERY_WEATHER", []),  # Missing location
        ("ALARM_SET", [{"type": "TIME", "value": "7 AM"}]),
        ("REMINDER_SET", [{"type": "TASK", "value": "buy groceries"}]),  # Missing time
    ]
    
    for intent, entities in test_cases:
        print(f"Intent: {intent}")
        print(f"Entities: {entities}")
        
        action = dm.decide(intent, state, entities)
        print(f"Action: {action}")
        print()

