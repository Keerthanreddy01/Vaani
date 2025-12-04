#!/usr/bin/env python3
"""
VAANI Dialogue State Tracker (DST)
Manages conversation context, tracks active intents, and stores entities.

Usage:
    from pipeline.dst.state_manager import DialogueStateManager
    
    state = DialogueStateManager()
    state.update_turn("What's the weather", "QUERY_WEATHER", [{"type": "LOCATION", "value": "Mumbai"}])
"""

import json
from datetime import datetime
from collections import deque


class DialogueStateManager:
    """Manages dialogue state and conversation context."""
    
    def __init__(self, max_history=10):
        """
        Initialize dialogue state manager.
        
        Args:
            max_history: Maximum number of turns to keep in history
        """
        self.max_history = max_history
        self.reset()
    
    def reset(self):
        """Reset dialogue state."""
        self.conversation_history = deque(maxlen=self.max_history)
        self.active_intent = None
        self.entities = {}
        self.context = {}
        self.session_start = datetime.now()
        self.turn_count = 0
    
    def update_turn(self, user_input, intent, entities=None, response=None):
        """
        Update state with new turn.
        
        Args:
            user_input: User's input text
            intent: Detected intent
            entities: List of extracted entities
            response: System response (optional)
        """
        self.turn_count += 1
        
        # Update active intent
        self.active_intent = intent
        
        # Update entities
        if entities:
            for entity in entities:
                entity_type = entity.get('type') or entity.get('label')
                entity_value = entity.get('value') or entity.get('text')
                
                # Store entity with turn information
                if entity_type not in self.entities:
                    self.entities[entity_type] = []
                
                self.entities[entity_type].append({
                    'value': entity_value,
                    'turn': self.turn_count,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Add to conversation history
        turn = {
            'turn': self.turn_count,
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'intent': intent,
            'entities': entities or [],
            'response': response
        }
        self.conversation_history.append(turn)
    
    def get_entity(self, entity_type, most_recent=True):
        """
        Get entity value by type.
        
        Args:
            entity_type: Type of entity to retrieve
            most_recent: If True, return most recent value; else return all
        
        Returns:
            Entity value(s) or None
        """
        if entity_type not in self.entities:
            return None
        
        if most_recent:
            return self.entities[entity_type][-1]['value']
        else:
            return [e['value'] for e in self.entities[entity_type]]
    
    def has_entity(self, entity_type):
        """Check if entity type exists in state."""
        return entity_type in self.entities and len(self.entities[entity_type]) > 0
    
    def get_last_turn(self):
        """Get the last conversation turn."""
        if self.conversation_history:
            return self.conversation_history[-1]
        return None
    
    def get_history(self, n=None):
        """
        Get conversation history.
        
        Args:
            n: Number of recent turns to return (None for all)
        
        Returns:
            List of conversation turns
        """
        if n is None:
            return list(self.conversation_history)
        else:
            return list(self.conversation_history)[-n:]
    
    def set_context(self, key, value):
        """Set context variable."""
        self.context[key] = value
    
    def get_context(self, key, default=None):
        """Get context variable."""
        return self.context.get(key, default)
    
    def clear_context(self, key=None):
        """Clear context variable(s)."""
        if key is None:
            self.context = {}
        elif key in self.context:
            del self.context[key]
    
    def is_task_complete(self):
        """Check if current task is complete."""
        return self.get_context('task_complete', False)
    
    def mark_task_complete(self):
        """Mark current task as complete."""
        self.set_context('task_complete', True)
        self.set_context('completed_intent', self.active_intent)
    
    def clear_task(self):
        """Clear current task state."""
        self.active_intent = None
        self.entities = {}
        self.clear_context('task_complete')
        self.clear_context('completed_intent')
    
    def to_dict(self):
        """Export state as dictionary."""
        return {
            'turn_count': self.turn_count,
            'active_intent': self.active_intent,
            'entities': self.entities,
            'context': self.context,
            'conversation_history': list(self.conversation_history),
            'session_start': self.session_start.isoformat()
        }
    
    def from_dict(self, state_dict):
        """Load state from dictionary."""
        self.turn_count = state_dict.get('turn_count', 0)
        self.active_intent = state_dict.get('active_intent')
        self.entities = state_dict.get('entities', {})
        self.context = state_dict.get('context', {})
        self.conversation_history = deque(
            state_dict.get('conversation_history', []),
            maxlen=self.max_history
        )
        session_start_str = state_dict.get('session_start')
        if session_start_str:
            self.session_start = datetime.fromisoformat(session_start_str)
    
    def save(self, filepath):
        """Save state to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load(self, filepath):
        """Load state from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            state_dict = json.load(f)
        self.from_dict(state_dict)
    
    def __str__(self):
        """String representation of state."""
        return (
            f"DialogueState(turn={self.turn_count}, "
            f"intent={self.active_intent}, "
            f"entities={len(self.entities)}, "
            f"history={len(self.conversation_history)})"
        )


# Example usage
if __name__ == "__main__":
    # Create state manager
    state = DialogueStateManager()
    
    # Simulate conversation
    print("🎙️  VAANI Dialogue State Manager Demo\n")
    
    # Turn 1
    state.update_turn(
        "What's the weather in Mumbai",
        "QUERY_WEATHER",
        [{"type": "LOCATION", "value": "Mumbai"}],
        "The weather in Mumbai is sunny, 28°C"
    )
    print(f"Turn 1: {state}")
    print(f"Location: {state.get_entity('LOCATION')}\n")
    
    # Turn 2
    state.update_turn(
        "Set an alarm for 7 AM",
        "ALARM_SET",
        [{"type": "TIME", "value": "7 AM"}],
        "Alarm set for 7 AM"
    )
    print(f"Turn 2: {state}")
    print(f"Time: {state.get_entity('TIME')}\n")
    
    # Show history
    print("Conversation History:")
    for turn in state.get_history():
        print(f"  Turn {turn['turn']}: {turn['user_input']} -> {turn['intent']}")
    
    # Save state
    state.save("dialogue_state.json")
    print("\n💾 State saved to dialogue_state.json")

