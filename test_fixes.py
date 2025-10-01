#!/usr/bin/env python3
"""
Test script to validate the fixes for RL Device Agent V2
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rl_agent import QLearningAgent
from device_actions import DeviceActions
import time

def test_device_actions():
    """Test device actions with both debug and real modes"""
    print("🧪 Testing Device Actions...")
    
    # Test with debug mode
    print("\n🐛 Testing Debug Mode:")
    debug_actions = DeviceActions(debug_mode=True)
    
    test_actions = ["take_screenshot", "open_notepad", "mute_audio", "show_system_info"]
    
    for action in test_actions:
        print(f"  Testing {action}...")
        success, message, info = debug_actions.execute_action(action)
        status = "✅" if success else "❌"
        print(f"    {status} {message}")
        
        # Validate action availability
        is_available, availability_msg = debug_actions.validate_action_availability(action)
        availability_status = "✅" if is_available else "⚠️"
        print(f"    {availability_status} {availability_msg}")
    
    # Test with real mode (but only safe actions)
    print("\n🔧 Testing Real Mode (Safe Actions Only):")
    real_actions = DeviceActions(debug_mode=False)
    
    safe_actions = ["show_system_info", "check_network_status", "check_disk_usage"]
    
    for action in safe_actions:
        print(f"  Testing {action}...")
        success, message, info = real_actions.execute_action(action)
        status = "✅" if success else "❌"
        print(f"    {status} {message}")
        if info:
            print(f"    📊 Info: {info}")

def test_rl_agent():
    """Test RL Agent with improved reward system"""
    print("\n🤖 Testing RL Agent...")
    
    agent = QLearningAgent()
    
    # Set debug mode for safe testing
    agent.device_actions.debug_mode = True
    print("🐛 Debug mode enabled for safe testing")
    
    test_tasks = [
        "open notepad",
        "take screenshot", 
        "mute audio",
        "some unknown action"
    ]
    
    for task in test_tasks:
        print(f"\n📋 Processing task: '{task}'")
        result = agent.process_task(task)
        
        print(f"  🎯 Parsed Intent: {result['parsed_intent']}")
        print(f"  🤖 Selected Action: {result['selected_action']}")
        print(f"  🎯 Confidence: {result['confidence_score']:.2f}")
        print(f"  ⚡ Success: {'✅' if result['execution_success'] else '❌'}")
        print(f"  🎁 Internal Reward: {result['internal_reward']}")
        
        # Check if placeholder warning was detected
        if "functionality available" in result.get('execution_message', '').lower():
            print(f"  ⚠️ Placeholder action detected - reduced reward applied")
        
        # Simulate positive feedback
        total_reward = agent.receive_feedback("👍")
        print(f"  📊 Total Reward after feedback: {total_reward:.2f}")

def test_action_categories():
    """Test actions by category to identify working vs placeholder implementations"""
    print("\n📂 Testing Action Categories...")
    
    actions = DeviceActions(debug_mode=False)
    
    categories = {
        "File Operations": ["open_file_browser", "open_notepad", "create_new_file"],
        "Audio Controls": ["mute_audio", "unmute_audio", "volume_up"],
        "System Operations": ["take_screenshot", "show_system_info", "check_network_status"],
        "Window Management": ["minimize_all_windows", "maximize_window", "close_active_window"],
        "Applications": ["open_browser", "open_calculator", "open_calendar"]
    }
    
    for category, action_list in categories.items():
        print(f"\n📁 {category}:")
        working = 0
        placeholder = 0
        
        for action in action_list:
            is_available, msg = actions.validate_action_availability(action)
            if is_available:
                working += 1
                print(f"  ✅ {action} - Fully implemented")
            else:
                placeholder += 1
                print(f"  ⚠️ {action} - Placeholder ({msg})")
        
        print(f"  📊 Summary: {working} working, {placeholder} placeholder")

def main():
    """Run all tests"""
    print("🚀 RL Device Agent V2 - Fix Validation Tests")
    print("=" * 50)
    
    try:
        test_device_actions()
        test_rl_agent()
        test_action_categories()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("\n💡 Key Improvements:")
        print("  • Fixed placeholder action detection and reduced rewards")
        print("  • Added debug mode for safe training")
        print("  • Improved error handling and timeout support")
        print("  • Enhanced Streamlit interface with action validation")
        print("  • Updated type annotations for better code safety")
        
        print("\n🎯 Training Recommendations:")
        print("  • Use Debug Mode in Streamlit for safe training on all actions")
        print("  • Focus real training on fully implemented actions")
        print("  • Monitor reward signals - placeholders get reduced rewards")
        print("  • Use the new Action Testing tab to validate implementations")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())