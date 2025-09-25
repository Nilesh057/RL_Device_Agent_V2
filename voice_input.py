"""
Voice Input Module for RL Device Agent v2 (Bonus Feature)

This module provides voice-to-text functionality for hands-free task input.
Uses SpeechRecognition library with multiple backend support.
"""

try:
    import speech_recognition as sr
    import pyaudio
    VOICE_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    sr = None
    pyaudio = None
    VOICE_DEPENDENCIES_AVAILABLE = False
    print(f"⚠️ Voice input dependencies not available: {e}")
    print("Install with: pip install SpeechRecognition pyaudio")

import wave
import threading
import time
from typing import Optional, Callable
import queue


class VoiceInputHandler:
    """Voice-to-text input handler for RL agent"""
    
    def __init__(self, language: str = "en-US", timeout: int = 5, phrase_timeout: float = 0.3):
        if not VOICE_DEPENDENCIES_AVAILABLE:
            print("⚠️ Voice input dependencies not available")
            self.recognizer = None
            self.microphone = None
            return
            
        self.language = language
        self.timeout = timeout
        self.phrase_timeout = phrase_timeout
        
        # Initialize recognizer and microphone
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.audio_queue = queue.Queue()
        
        # Callbacks
        self.on_speech_detected = None
        self.on_speech_recognized = None
        self.on_speech_error = None
        
        # Initialize microphone
        self._initialize_microphone()
        
    def _initialize_microphone(self):
        """Initialize microphone with error handling"""
        if not VOICE_DEPENDENCIES_AVAILABLE:
            self.microphone = None
            return
            
        try:
            self.microphone = sr.Microphone()
            
            # Calibrate for ambient noise
            print("🎤 Calibrating microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Microphone calibrated!")
            
        except Exception as e:
            print(f"❌ Failed to initialize microphone: {e}")
            self.microphone = None
    
    def is_available(self) -> bool:
        """Check if voice input is available"""
        return VOICE_DEPENDENCIES_AVAILABLE and self.microphone is not None
    
    def listen_once(self, prompt: str = "🎤 Speak now...") -> Optional[str]:
        """Listen for a single voice command"""
        if not self.is_available():
            print("❌ Voice input not available")
            return None
        
        print(prompt)
        
        try:
            # Listen for audio
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=self.timeout, phrase_time_limit=5)
            
            print("🔄 Processing speech...")
            
            # Recognize speech using Google's service
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                print(f"✅ Recognized: '{text}'")
                return text.lower().strip()
                
            except sr.UnknownValueError:
                print("❌ Could not understand audio")
                return None
                
            except sr.RequestError as e:
                print(f"❌ Speech recognition service error: {e}")
                # Fallback to offline recognition
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    print(f"✅ Recognized (offline): '{text}'")
                    return text.lower().strip()
                except:
                    print("❌ Offline recognition also failed")
                    return None
        
        except sr.WaitTimeoutError:
            print("⏰ Listening timeout - no speech detected")
            return None
        
        except Exception as e:
            print(f"❌ Voice input error: {e}")
            return None
    
    def listen_continuous(self, callback: Callable[[str], None], 
                         stop_phrases: Optional[list] = None) -> Optional[threading.Thread]:
        """
        Start continuous listening in background thread
        
        Args:
            callback: Function to call with recognized text
            stop_phrases: List of phrases that stop listening
            
        Returns:
            Thread object for the listening process
        """
        if not self.is_available():
            print("❌ Voice input not available for continuous listening")
            return None
        
        if stop_phrases is None:
            stop_phrases = ["stop listening", "quit voice", "exit voice"]
        
        self.is_listening = True
        
        def listen_thread():
            print("🎤 Started continuous listening...")
            print(f"Say '{stop_phrases[0]}' to stop")
            
            while self.is_listening:
                try:
                    with self.microphone as source:
                        # Shorter timeout for continuous listening
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    try:
                        text = self.recognizer.recognize_google(audio, language=self.language)
                        text = text.lower().strip()
                        
                        print(f"🎤 Heard: '{text}'")
                        
                        # Check for stop phrases
                        if any(phrase in text for phrase in stop_phrases):
                            print("🛑 Stop phrase detected, ending continuous listening")
                            self.is_listening = False
                            break
                        
                        # Call the callback with recognized text
                        if callback:
                            callback(text)
                    
                    except sr.UnknownValueError:
                        pass  # Ignore unclear audio in continuous mode
                    
                    except sr.RequestError as e:
                        print(f"❌ Speech service error: {e}")
                        time.sleep(1)  # Brief pause before retrying
                
                except sr.WaitTimeoutError:
                    pass  # Continue listening
                
                except Exception as e:
                    print(f"❌ Continuous listening error: {e}")
                    time.sleep(1)
            
            print("🔇 Continuous listening stopped")
        
        thread = threading.Thread(target=listen_thread, daemon=True)
        thread.start()
        return thread
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.is_listening = False
    
    def test_voice_input(self):
        """Test voice input functionality"""
        print("🔊 Testing Voice Input")
        print("=" * 30)
        
        if not self.is_available():
            print("❌ Voice input not available")
            return False
        
        print("Please say 'hello world' for testing...")
        result = self.listen_once("🎤 Say 'hello world':")
        
        if result:
            print(f"✅ Test successful! Heard: '{result}'")
            return True
        else:
            print("❌ Test failed - no speech recognized")
            return False


class VoiceEnabledAgent:
    """RL Agent with voice input capabilities"""
    
    def __init__(self, agent=None):
        from rl_agent import QLearningAgent
        self.agent = agent or QLearningAgent()
        self.voice_handler = VoiceInputHandler()
        self.voice_enabled = self.voice_handler.is_available()
        
        if self.voice_enabled:
            print("🎤 Voice input enabled!")
        else:
            print("⚠️ Voice input not available, using text input only")
    
    def get_task_input(self, prompt: str = "Enter task") -> Optional[str]:
        """Get task input via voice or text"""
        print(f"\n{prompt}:")
        print("Options:")
        print("  - Type your task")
        if self.voice_enabled:
            print("  - Say 'voice' to use voice input")
        print("  - Say 'quit' to exit")
        
        user_input = input("\n> ").strip().lower()
        
        if user_input == "quit":
            return None
        elif user_input == "voice" and self.voice_enabled:
            return self._get_voice_task()
        else:
            return user_input if user_input else None
    
    def _get_voice_task(self) -> Optional[str]:
        """Get task via voice input"""
        print("\n🎤 Voice Input Mode")
        print("Speak your task clearly...")
        
        for attempt in range(3):  # Allow 3 attempts
            result = self.voice_handler.listen_once(f"🎤 Attempt {attempt + 1}/3 - Speak now:")
            
            if result:
                # Confirm the recognized text
                print(f"I heard: '{result}'")
                confirm = input("Is this correct? (y/n/retry): ").strip().lower()
                
                if confirm in ['y', 'yes', '']:
                    return result
                elif confirm in ['n', 'no']:
                    manual_input = input("Enter the task manually: ").strip()
                    return manual_input if manual_input else None
                else:
                    continue  # Retry
            else:
                print(f"❌ Attempt {attempt + 1} failed")
        
        print("❌ Voice input failed after 3 attempts")
        fallback = input("Enter task manually: ").strip()
        return fallback if fallback else None
    
    def run_voice_demo(self):
        """Run a demo with voice input capabilities"""
        print("🎤 RL Device Agent v2 - Voice Input Demo")
        print("=" * 50)
        
        if not self.voice_enabled:
            print("❌ Voice input not available for demo")
            return
        
        # Test voice input first
        if not self.voice_handler.test_voice_input():
            print("❌ Voice test failed, falling back to text input")
            self.voice_enabled = False
            return
        
        print("\n🎬 Starting voice-enabled task execution...")
        
        task_count = 0
        while task_count < 5:  # Demo with 5 tasks
            task_input = self.get_task_input(f"Task {task_count + 1}/5")
            
            if task_input is None:
                break
            
            # Process the task
            result = self.agent.process_task(task_input)
            
            # Get feedback
            print("\n💬 How was this action?")
            feedback_input = input("Feedback (👍/👎 or 'voice'): ").strip().lower()
            
            if feedback_input == "voice" and self.voice_enabled:
                feedback_text = self.voice_handler.listen_once("🎤 Say 'good' or 'bad':")
                if feedback_text:
                    if any(word in feedback_text for word in ['good', 'great', 'correct', 'right', 'yes']):
                        feedback = "👍"
                    elif any(word in feedback_text for word in ['bad', 'wrong', 'incorrect', 'no']):
                        feedback = "👎"
                    else:
                        feedback = None
                else:
                    feedback = None
            elif feedback_input in ['👍', 'good', 'positive']:
                feedback = "👍"
            elif feedback_input in ['👎', 'bad', 'negative']:
                feedback = "👎"
            else:
                feedback = None
            
            if feedback:
                self.agent.receive_feedback(feedback)
            
            task_count += 1
            
            if task_count < 5:
                input("\nPress Enter for next task...")
        
        # End episode
        self.agent.end_episode()
        print("\n🎉 Voice demo completed!")
    
    def run_continuous_voice_mode(self):
        """Run continuous voice listening mode"""
        if not self.voice_enabled:
            print("❌ Voice input not available")
            return
        
        print("🎤 Continuous Voice Mode")
        print("=" * 30)
        print("Speak tasks naturally, I'll execute them!")
        print("Say 'stop listening' to exit")
        
        def handle_voice_task(text: str):
            """Handle voice task in continuous mode"""
            print(f"\n🎯 Processing: '{text}'")
            
            # Process the task
            result = self.agent.process_task(text)
            
            # Brief status update
            status = "✅ Success" if result['execution_success'] else "❌ Failed"
            print(f"{status} - {result['execution_message']}")
        
        # Start continuous listening
        listen_thread = self.voice_handler.listen_continuous(
            callback=handle_voice_task,
            stop_phrases=["stop listening", "quit voice", "exit voice", "stop agent"]
        )
        
        if listen_thread:
            try:
                listen_thread.join()  # Wait for listening to stop
            except KeyboardInterrupt:
                print("\n🛑 Interrupted by user")
                self.voice_handler.stop_listening()
        
        print("🔇 Voice mode ended")


def main():
    """Main function for voice input testing and demo"""
    print("🎤 RL Device Agent v2 - Voice Input Module")
    print("=" * 50)
    
    # Test basic voice input
    voice_handler = VoiceInputHandler()
    
    if not voice_handler.is_available():
        print("❌ Voice input not available on this system")
        print("Make sure you have:")
        print("  - A working microphone")
        print("  - pyaudio installed (pip install pyaudio)")
        print("  - SpeechRecognition installed (pip install SpeechRecognition)")
        return
    
    while True:
        print("\nVoice Input Options:")
        print("1. Test Voice Recognition")
        print("2. Single Voice Command Demo")
        print("3. Voice-Enabled Agent Demo") 
        print("4. Continuous Voice Mode")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            voice_handler.test_voice_input()
            
        elif choice == "2":
            result = voice_handler.listen_once("🎤 Say any command:")
            if result:
                print(f"You said: '{result}'")
            
        elif choice == "3":
            voice_agent = VoiceEnabledAgent()
            voice_agent.run_voice_demo()
            
        elif choice == "4":
            voice_agent = VoiceEnabledAgent()
            voice_agent.run_continuous_voice_mode()
            
        elif choice == "5":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()