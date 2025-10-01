#!/usr/bin/env python3
"""
Screenshot Enhancement Script for RL Device Agent V2
Ensures take_screenshot works correctly and saves to Pictures folder
"""

import os
import sys
import pickle
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def enhance_screenshot_qtable():
    """Enhance Q-table to ensure take_screenshot is strongly preferred"""
    
    qtable_file = "models/qtable.pkl"
    
    print("🔧 Screenshot Enhancement Tool")
    print("=" * 40)
    
    # Load existing Q-table
    if os.path.exists(qtable_file):
        try:
            with open(qtable_file, 'rb') as f:
                qtable_data = pickle.load(f)
            
            q_table = defaultdict(lambda: defaultdict(float), qtable_data.get("q_table", {}))
            action_counts = defaultdict(lambda: defaultdict(int), qtable_data.get("action_counts", {}))
            state_visits = defaultdict(int, qtable_data.get("state_visits", {}))
            epsilon = qtable_data.get("epsilon", 0.2)
            
            print(f"📚 Loaded existing Q-table with {len(q_table)} states")
        except Exception as e:
            print(f"⚠️ Could not load Q-table: {e}")
            return False
    else:
        print("❌ No Q-table found")
        return False
    
    # Enhance take_screenshot preference
    screenshot_state = "intent_take_screenshot"
    
    # Strongly boost take_screenshot action
    q_table[screenshot_state]["take_screenshot"] = 5.0  # Very high reward
    action_counts[screenshot_state]["take_screenshot"] = 10  # High experience
    state_visits[screenshot_state] = 15
    
    # Reduce other actions for this state
    for action in ["open_photo_viewer", "show_system_info", "create_document"]:
        if action in q_table[screenshot_state]:
            q_table[screenshot_state][action] = max(-0.5, q_table[screenshot_state][action] - 1.0)
    
    # Reduce exploration rate for more consistent behavior
    epsilon = min(0.1, epsilon)
    
    # Create backup
    backup_file = qtable_file.replace('.pkl', '_pre_screenshot_enhancement.pkl')
    if os.path.exists(qtable_file):
        os.rename(qtable_file, backup_file)
        print(f"💾 Backed up Q-table to {backup_file}")
    
    # Save enhanced Q-table
    enhanced_data = {
        "q_table": dict(q_table),
        "action_counts": dict(action_counts),
        "state_visits": dict(state_visits),
        "epsilon": epsilon,
        "metadata": {
            "total_states": len(q_table),
            "screenshot_enhanced": True,
            "enhancement_date": "2025-10-01T13:00:00"
        }
    }
    
    with open(qtable_file, 'wb') as f:
        pickle.dump(enhanced_data, f)
    
    print(f"✅ Enhanced Q-table saved")
    print(f"📊 take_screenshot Q-value: {q_table[screenshot_state]['take_screenshot']}")
    print(f"🔍 Exploration rate: {epsilon}")
    
    return True

def test_screenshot_functionality():
    """Test the enhanced screenshot functionality"""
    
    print("\n🧪 Testing Screenshot Functionality")
    print("-" * 35)
    
    from rl_agent import QLearningAgent
    from device_actions import DeviceActions
    
    # Test direct device action
    print("1. Testing direct screenshot action...")
    actions = DeviceActions(debug_mode=False)
    success, message, info = actions.execute_action('take_screenshot')
    
    if success:
        print(f"   ✅ Direct action: {message}")
        print(f"   📁 Saved to: {info.get('full_path', 'Unknown')}")
        print(f"   🖼️ Opened in viewer: {info.get('opened_in_viewer', False)}")
    else:
        print(f"   ❌ Direct action failed: {message}")
    
    # Test via RL agent
    print("\n2. Testing via RL agent...")
    agent = QLearningAgent()
    agent.device_actions.debug_mode = False
    
    result = agent.process_task('take screenshot')
    
    if result['selected_action'] == 'take_screenshot':
        print(f"   ✅ Correct action selected: {result['selected_action']}")
        print(f"   🎯 Confidence: {result['confidence_score']:.2f}")
        
        if result['execution_success']:
            print(f"   ✅ Execution successful: {result['execution_message']}")
        else:
            print(f"   ❌ Execution failed: {result['execution_message']}")
    else:
        print(f"   ❌ Wrong action selected: {result['selected_action']} (expected: take_screenshot)")
        print(f"   🎯 Confidence: {result['confidence_score']:.2f}")
    
    return result['selected_action'] == 'take_screenshot' and result['execution_success']

def main():
    """Main enhancement function"""
    
    print("🚀 Starting Screenshot Enhancement...")
    
    try:
        # Enhance Q-table
        if not enhance_screenshot_qtable():
            print("❌ Failed to enhance Q-table")
            return 1
        
        # Test functionality
        if test_screenshot_functionality():
            print("\n" + "=" * 50)
            print("✅ SUCCESS: Screenshot functionality enhanced!")
            print("\n💡 What's been improved:")
            print("  • Screenshots now save to ~/Pictures folder")
            print("  • Screenshots automatically open in photo viewer")
            print("  • Q-table strongly prefers 'take_screenshot' for screenshot intents")
            print("  • Reduced exploration rate for more consistent behavior")
            print("\n🎯 Next steps:")
            print("  1. Try 'take screenshot' in Streamlit - should work correctly")
            print("  2. Screenshots will be saved to your Pictures folder")
            print("  3. Photo viewer should open automatically")
            print("  4. Provide 👍 feedback to reinforce correct behavior")
            
            return 0
        else:
            print("\n⚠️ Enhancement completed but testing revealed issues")
            return 1
            
    except Exception as e:
        print(f"\n❌ Enhancement failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())