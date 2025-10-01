#!/usr/bin/env python3
"""
Q-table Reset and Correction Script for RL Device Agent V2
Fixes the corrupted Q-table that's making wrong action selections
"""

import os
import sys
import pickle
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def reset_corrupted_qtable():
    """Reset Q-table and apply correct intent-action mappings"""
    
    qtable_file = "models/qtable.pkl"
    
    print("🔧 Q-table Reset and Correction Tool")
    print("=" * 50)
    
    # Load existing Q-table if it exists
    old_qtable = None
    if os.path.exists(qtable_file):
        try:
            with open(qtable_file, 'rb') as f:
                old_data = pickle.load(f)
                old_qtable = old_data.get("q_table", {})
            print(f"📚 Loaded existing Q-table with {len(old_qtable)} states")
        except Exception as e:
            print(f"⚠️ Could not load existing Q-table: {e}")
    
    # Create corrected Q-table
    corrected_qtable = defaultdict(lambda: defaultdict(float))
    action_counts = defaultdict(lambda: defaultdict(int))
    state_visits = defaultdict(int)
    
    # Define correct intent-action mappings
    correct_mappings = {
        "intent_take_screenshot": {
            "take_screenshot": 2.0,      # High reward for correct action
            "open_photo_viewer": -1.0,    # Negative for wrong but related action
            "show_system_info": 0.1,      # Low for unrelated actions
            "open_browser": 0.1
        },
        "intent_open_notepad": {
            "open_notepad": 2.0,
            "open_text_editor": 1.8,     # Good alternative
            "create_new_file": 1.0,       # Related action
            "open_file_browser": 0.5
        },
        "intent_mute_audio": {
            "mute_audio": 2.0,
            "unmute_audio": -0.5,         # Opposite action gets penalty
            "volume_down": 1.0,           # Related action
            "toggle_audio": 1.5
        },
        "intent_open_browser": {
            "open_browser": 2.0,
            "search_online": 1.5,
            "open_notepad": 0.1
        },
        "intent_show_system_info": {
            "show_system_info": 2.0,
            "check_network_status": 1.2,
            "check_disk_usage": 1.2,
            "check_memory_usage": 1.2,
            "take_screenshot": 0.1
        }
    }
    
    # Apply corrections
    print("\n🎯 Applying intent-action corrections...")
    for state, actions in correct_mappings.items():
        for action, reward in actions.items():
            corrected_qtable[state][action] = reward
            action_counts[state][action] = 3  # Give some experience
            state_visits[state] = 10
        print(f"  ✅ Fixed {state}: {len(actions)} actions")
    
    # Preserve good Q-values from old table for other states
    if old_qtable:
        print("\n📋 Preserving other learned states...")
        for state, actions in old_qtable.items():
            if state not in corrected_qtable:
                # Only keep states that don't have obvious misalignments
                for action, q_val in actions.items():
                    if q_val > 0.5:  # Only preserve good experiences
                        corrected_qtable[state][action] = q_val
                        action_counts[state][action] = 2
                        state_visits[state] = 5
    
    # Create backup of old Q-table
    if os.path.exists(qtable_file):
        backup_file = qtable_file.replace('.pkl', '_backup.pkl')
        os.rename(qtable_file, backup_file)
        print(f"💾 Backed up old Q-table to {backup_file}")
    
    # Save corrected Q-table
    os.makedirs(os.path.dirname(qtable_file), exist_ok=True)
    
    qtable_data = {
        "q_table": dict(corrected_qtable),
        "action_counts": dict(action_counts),
        "state_visits": dict(state_visits),
        "epsilon": 0.2,  # Reset exploration rate
        "metadata": {
            "total_states": len(corrected_qtable),
            "correction_applied": True,
            "last_corrected": "2025-10-01T12:00:00"
        }
    }
    
    with open(qtable_file, 'wb') as f:
        pickle.dump(qtable_data, f)
    
    print(f"✅ Saved corrected Q-table to {qtable_file}")
    print(f"📊 States: {len(corrected_qtable)}")
    print(f"🔍 Exploration rate reset to: {qtable_data['epsilon']}")
    
    # Show corrections made
    print("\n🎯 Key Corrections Applied:")
    for state, actions in correct_mappings.items():
        intent = state.replace("intent_", "")
        best_action = max(actions.items(), key=lambda x: x[1])
        print(f"  • {intent} → {best_action[0]} (Q={best_action[1]:.1f})")
    
    return qtable_data

def test_corrected_qtable():
    """Test the corrected Q-table"""
    print("\n🧪 Testing Corrected Q-table...")
    
    from rl_agent import QLearningAgent
    
    # Create agent with corrected Q-table
    agent = QLearningAgent()
    agent.device_actions.debug_mode = True  # Safe testing
    
    test_cases = [
        ("take screenshot", "take_screenshot"),
        ("open notepad", "open_notepad"), 
        ("mute audio", "mute_audio"),
        ("open browser", "open_browser"),
        ("show system info", "show_system_info")
    ]
    
    print("\n📋 Testing intent-action alignment:")
    for task, expected_action in test_cases:
        result = agent.process_task(task)
        
        selected = result['selected_action']
        confidence = result['confidence_score']
        success = selected == expected_action
        
        status = "✅" if success else "❌"
        print(f"  {status} '{task}' → {selected} (confidence: {confidence:.2f})")
        
        if not success:
            print(f"    Expected: {expected_action}")
        
        # Simulate correct feedback
        if success:
            agent.receive_feedback("👍")
        else:
            agent.receive_feedback("👎", expected_action)
    
    print("\n🎯 Correction Test Complete!")

def main():
    """Main function"""
    print("🚀 Starting Q-table correction...")
    
    try:
        # Reset and correct Q-table
        corrected_data = reset_corrupted_qtable()
        
        # Test the corrections
        test_corrected_qtable()
        
        print("\n" + "=" * 50)
        print("✅ Q-table correction completed successfully!")
        print("\n💡 Next Steps:")
        print("  1. Run the Streamlit app to test the corrected behavior")
        print("  2. Try 'take screenshot' - should now select 'take_screenshot'")
        print("  3. Provide feedback to continue training with correct actions")
        print("  4. Monitor learning progress in the Action Testing tab")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Correction failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())