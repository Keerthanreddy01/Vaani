"""
Vaani Backend Server
Provides advanced NLU, dialogue management, and action routing for the Android app
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from aiohttp import web
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from pipeline.nlu.intent_classifier import IntentClassifier
from pipeline.dst.state_manager import StateManager
from pipeline.dm.decision_manager import DecisionManager
from pipeline.nlg.response_generator import ResponseGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VaaniBackendServer:
    """
    Backend server for Vaani Voice Assistant
    Provides enhanced NLU and dialogue management beyond what's possible on Android
    """
    
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        
        # Initialize NLU components
        logger.info("Initializing NLU components...")
        self.intent_classifier = IntentClassifier()
        self.state_manager = StateManager()
        self.decision_manager = DecisionManager()
        self.response_generator = ResponseGenerator()
        
        # Session storage
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Setup routes
        self.setup_routes()
        
        logger.info(f"Vaani Backend Server initialized on {host}:{port}")
    
    def setup_routes(self):
        """Setup API routes"""
        self.app.router.add_post('/process', self.process_command)
        self.app.router.add_post('/wake_word', self.wake_word_detected)
        self.app.router.add_get('/status', self.get_status)
        self.app.router.add_post('/session/reset', self.reset_session)
        self.app.router.add_get('/health', self.health_check)
    
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    async def get_status(self, request):
        """Get server status"""
        return web.json_response({
            'status': 'running',
            'active_sessions': len(self.sessions),
            'timestamp': datetime.now().isoformat()
        })
    
    async def wake_word_detected(self, request):
        """
        Handle wake word detection from Android app
        Returns: Acknowledgement and readiness status
        """
        try:
            data = await request.json()
            device_id = data.get('device_id', 'unknown')
            wake_word = data.get('wake_word', 'Vaani')
            
            logger.info(f"Wake word '{wake_word}' detected on device {device_id}")
            
            # Initialize or get session
            if device_id not in self.sessions:
                self.sessions[device_id] = {
                    'state': {},
                    'history': [],
                    'last_active': datetime.now()
                }
            
            self.sessions[device_id]['last_active'] = datetime.now()
            
            return web.json_response({
                'status': 'ready',
                'message': 'Ready for command',
                'session_id': device_id
            })
            
        except Exception as e:
            logger.error(f"Error in wake_word_detected: {e}")
            return web.json_response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    async def process_command(self, request):
        """
        Process voice command from Android app
        Input: { "device_id": "...", "text": "...", "timestamp": ... }
        Output: { "intent": "...", "entities": {...}, "action": {...}, "response": "..." }
        """
        try:
            data = await request.json()
            device_id = data.get('device_id', 'unknown')
            text = data.get('text', '')
            timestamp = data.get('timestamp', datetime.now().isoformat())
            
            logger.info(f"Processing command from {device_id}: '{text}'")
            
            # Get or create session
            if device_id not in self.sessions:
                self.sessions[device_id] = {
                    'state': {},
                    'history': [],
                    'last_active': datetime.now()
                }
            
            session = self.sessions[device_id]
            session['last_active'] = datetime.now()
            
            # Step 1: Intent Classification
            classification = self.intent_classifier.classify(text)
            intent = classification['intent']
            entities = classification['entities']
            confidence = classification['confidence']
            
            logger.info(f"Classified: intent={intent}, confidence={confidence:.2f}")
            
            # Step 2: Update Dialogue State
            state = self.state_manager.update(
                current_state=session['state'],
                intent=intent,
                entities=entities,
                user_utterance=text
            )
            session['state'] = state
            
            # Step 3: Decide Action
            decision = self.decision_manager.decide(
                intent=intent,
                entities=entities,
                state=state
            )
            
            # Step 4: Generate Response
            response_text = self.response_generator.generate(
                intent=intent,
                entities=entities,
                action_result=decision
            )
            
            # Step 5: Add to history
            session['history'].append({
                'timestamp': timestamp,
                'text': text,
                'intent': intent,
                'entities': entities,
                'response': response_text
            })
            
            # Prepare result
            result = {
                'status': 'success',
                'intent': intent,
                'entities': entities,
                'confidence': confidence,
                'action': decision,
                'response': response_text,
                'state': state
            }
            
            logger.info(f"Processed successfully: {intent} -> {response_text}")
            
            return web.json_response(result)
            
        except Exception as e:
            logger.error(f"Error processing command: {e}", exc_info=True)
            return web.json_response({
                'status': 'error',
                'message': str(e),
                'response': "Sorry, I encountered an error processing that command."
            }, status=500)
    
    async def reset_session(self, request):
        """Reset a device session"""
        try:
            data = await request.json()
            device_id = data.get('device_id', 'unknown')
            
            if device_id in self.sessions:
                del self.sessions[device_id]
                logger.info(f"Reset session for device {device_id}")
            
            return web.json_response({
                'status': 'success',
                'message': 'Session reset'
            })
            
        except Exception as e:
            logger.error(f"Error resetting session: {e}")
            return web.json_response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    def run(self):
        """Start the server"""
        logger.info(f"Starting Vaani Backend Server on {self.host}:{self.port}")
        logger.info("API Endpoints:")
        logger.info(f"  POST http://{self.host}:{self.port}/wake_word - Wake word detected")
        logger.info(f"  POST http://{self.host}:{self.port}/process - Process command")
        logger.info(f"  GET  http://{self.host}:{self.port}/status - Server status")
        logger.info(f"  POST http://{self.host}:{self.port}/session/reset - Reset session")
        logger.info(f"  GET  http://{self.host}:{self.port}/health - Health check")
        logger.info("")
        logger.info("Server ready! Waiting for requests from Android app...")
        
        web.run_app(self.app, host=self.host, port=self.port)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Vaani Backend Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    
    args = parser.parse_args()
    
    server = VaaniBackendServer(host=args.host, port=args.port)
    server.run()


if __name__ == '__main__':
    main()
