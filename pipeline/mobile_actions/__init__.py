"""
Mobile Actions Module for VAANI Accessibility Assistant

Provides Android/iOS action execution for hands-free phone control.
"""

from .android_bridge import AndroidBridge
from .mobile_action_executor import MobileActionExecutor

__all__ = ['AndroidBridge', 'MobileActionExecutor']

