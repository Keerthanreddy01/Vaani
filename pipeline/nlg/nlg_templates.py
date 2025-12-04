"""
VAANI Natural Language Generation Templates
Response templates for different intents and scenarios.
"""

import random

# Response templates organized by intent
TEMPLATES = {
    'greeting': [
        "Hello! How can I help you today?",
        "Hi there! What can I do for you?",
        "Hey! I'm VAANI, your voice assistant. How may I assist you?",
        "Good to hear from you! What would you like to do?",
        "Namaste! How can I help you today?"
    ],
    
    'time': [
        "The current time is {time}.",
        "It's {time} right now.",
        "Right now, it's {time}.",
        "The time is {time}."
    ],
    
    'weather': [
        "The weather in {location} is {condition}, with a temperature of {temperature}°C.",
        "It's {condition} in {location}, currently {temperature}°C.",
        "In {location}, it's {condition} and {temperature} degrees.",
        "{location} is experiencing {condition} weather at {temperature}°C."
    ],
    
    'weather_error': [
        "I couldn't fetch the weather information for {location}. Please try again.",
        "Sorry, I'm having trouble getting weather data for {location}.",
        "Weather information for {location} is currently unavailable."
    ],
    
    'open_app': [
        "Opening {app_name}.",
        "Launching {app_name} for you.",
        "Sure, opening {app_name}.",
        "Starting {app_name} now."
    ],
    
    'call_person': [
        "Calling {person}.",
        "Dialing {person} now.",
        "Sure, calling {person}.",
        "Placing a call to {person}."
    ],
    
    'alarm_set': [
        "Alarm set for {time}.",
        "Your alarm is set for {time}.",
        "Done! I've set an alarm for {time}.",
        "Alarm created for {time}."
    ],
    
    'reminder_set': [
        "Reminder set: {task} at {time}.",
        "I'll remind you to {task} at {time}.",
        "Got it! Reminder for {task} at {time}.",
        "Reminder created: {task} at {time}."
    ],
    
    'joke': [
        "Why don't scientists trust atoms? Because they make up everything!",
        "What do you call a bear with no teeth? A gummy bear!",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "What do you call a fake noodle? An impasta!",
        "Why don't eggs tell jokes? They'd crack each other up!",
        "What did the ocean say to the beach? Nothing, it just waved!",
        "Why did the bicycle fall over? It was two-tired!",
        "What do you call a can opener that doesn't work? A can't opener!"
    ],
    
    'casual_chat': [
        "I'm here to help! What would you like to do?",
        "That's interesting! Is there anything I can help you with?",
        "I'm doing great, thanks for asking! How can I assist you?",
        "I'm always ready to help! What do you need?",
        "Thanks for chatting! What can I do for you today?"
    ],
    
    'general_knowledge': [
        "Based on what I know, {answer}",
        "Here's what I found: {answer}",
        "According to my knowledge, {answer}",
        "Let me tell you: {answer}"
    ],
    
    'error': [
        "I'm sorry, I encountered an error. Please try again.",
        "Oops! Something went wrong. Can you repeat that?",
        "I didn't quite get that. Could you try again?",
        "Sorry, I'm having trouble processing that request."
    ],
    
    'unknown_intent': [
        "I'm not sure how to help with that. Can you rephrase?",
        "I didn't understand that. Could you say it differently?",
        "Sorry, I don't know how to handle that request yet.",
        "I'm still learning! Can you try asking in a different way?"
    ],
    
    'missing_info': [
        "I need more information. {question}",
        "Could you provide more details? {question}",
        "To help you, I need to know: {question}",
        "Please tell me: {question}"
    ],
    
    'confirmation': [
        "Got it! {action}",
        "Done! {action}",
        "All set! {action}",
        "Completed: {action}"
    ],
    
    'goodbye': [
        "Goodbye! Have a great day!",
        "See you later!",
        "Take care!",
        "Bye! Let me know if you need anything else.",
        "Goodbye! It was nice helping you."
    ]
}

# Context-aware templates
CONTEXTUAL_TEMPLATES = {
    'morning_greeting': [
        "Good morning! How can I help you today?",
        "Good morning! What would you like to do?",
        "Morning! Ready to start your day?"
    ],
    
    'afternoon_greeting': [
        "Good afternoon! How can I assist you?",
        "Good afternoon! What can I do for you?",
        "Afternoon! How may I help?"
    ],
    
    'evening_greeting': [
        "Good evening! How can I help you?",
        "Good evening! What would you like to do?",
        "Evening! How may I assist you?"
    ],
    
    'night_greeting': [
        "Good night! How can I help you?",
        "Hello! What can I do for you this evening?",
        "Hi! How may I assist you tonight?"
    ]
}

# Error messages
ERROR_MESSAGES = {
    'no_internet': "I need an internet connection for that. Please check your connection.",
    'permission_denied': "I don't have permission to do that. Please check your settings.",
    'service_unavailable': "That service is currently unavailable. Please try again later.",
    'invalid_input': "I didn't understand that input. Could you try again?",
    'timeout': "The request timed out. Please try again."
}

# Follow-up questions
FOLLOW_UP_QUESTIONS = {
    'location': "Which city or location?",
    'time': "What time?",
    'date': "Which date?",
    'person': "Who would you like to contact?",
    'app_name': "Which app?",
    'task': "What should I remind you about?",
    'query': "What would you like to know?"
}


def get_template(template_name):
    """Get a random template for the given name."""
    templates = TEMPLATES.get(template_name, TEMPLATES['error'])
    return random.choice(templates)


def get_contextual_greeting():
    """Get a context-aware greeting based on time of day."""
    from datetime import datetime
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        templates = CONTEXTUAL_TEMPLATES['morning_greeting']
    elif 12 <= hour < 17:
        templates = CONTEXTUAL_TEMPLATES['afternoon_greeting']
    elif 17 <= hour < 21:
        templates = CONTEXTUAL_TEMPLATES['evening_greeting']
    else:
        templates = CONTEXTUAL_TEMPLATES['night_greeting']
    
    return random.choice(templates)


def get_error_message(error_type):
    """Get error message for specific error type."""
    return ERROR_MESSAGES.get(error_type, ERROR_MESSAGES['invalid_input'])


def get_follow_up_question(missing_info):
    """Get follow-up question for missing information."""
    return FOLLOW_UP_QUESTIONS.get(missing_info, "Could you provide more information?")

