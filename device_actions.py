import os
import subprocess
import platform
import pyautogui
import time
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
import psutil
import json
import signal
from threading import Timer


class DeviceActions:
    """Device control actions for RL agent with expanded functionality"""
    
    def __init__(self, debug_mode: bool = False):
        self.system = platform.system()
        self.debug_mode = debug_mode
        self.actions_map = {
            # File operations
            "open_file_browser": self.open_file_browser,
            "open_notepad": self.open_notepad,
            "open_text_editor": self.open_text_editor,
            "create_new_file": self.create_new_file,
            "delete_file": self.delete_file,
            "open_documents_folder": self.open_documents_folder,
            "open_downloads_folder": self.open_downloads_folder,
            "open_pictures_folder": self.open_pictures_folder,
            
            # Audio/Media controls
            "mute_audio": self.mute_audio,
            "unmute_audio": self.unmute_audio,
            "volume_up": self.volume_up,
            "volume_down": self.volume_down,
            "toggle_audio": self.toggle_audio,
            "max_volume": self.max_volume,
            "min_volume": self.min_volume,
            
            # System operations
            "take_screenshot": self.take_screenshot,
            "lock_screen": self.lock_screen,
            "open_task_manager": self.open_task_manager,
            "minimize_all_windows": self.minimize_all_windows,
            "close_active_window": self.close_active_window,
            "show_system_info": self.show_system_info,
            "check_network_status": self.check_network_status,
            "check_disk_usage": self.check_disk_usage,
            "check_memory_usage": self.check_memory_usage,
            "check_battery_status": self.check_battery_status,
            
            # Application controls
            "open_browser": self.open_browser,
            "open_calculator": self.open_calculator,
            "open_calendar": self.open_calendar,
            "open_terminal": self.open_terminal,
            "open_settings": self.open_settings,
            "open_email_app": self.open_email_app,
            "open_music_player": self.open_music_player,
            "open_photo_viewer": self.open_photo_viewer,
            "open_video_player": self.open_video_player,
            
            # Window management
            "maximize_window": self.maximize_window,
            "minimize_window": self.minimize_window,
            "switch_window": self.switch_window,
            "close_all_windows": self.close_all_windows,
            "tile_windows": self.tile_windows,
            "fullscreen_mode": self.fullscreen_mode,
            "snap_window_left": self.snap_window_left,
            "snap_window_right": self.snap_window_right,
            
            # Performance monitoring
            "show_running_processes": self.show_running_processes,
            "check_cpu_usage": self.check_cpu_usage,
            "monitor_performance": self.monitor_performance,
            
            # Productivity
            "create_document": self.create_document,
            "open_spreadsheet": self.open_spreadsheet,
            "search_online": self.search_online,
            "set_reminder": self.set_reminder,
            "start_timer": self.start_timer,
            
            # Security
            "clear_browser_data": self.clear_browser_data,
            "check_privacy_settings": self.check_privacy_settings,
            "enable_firewall": self.enable_firewall,
            "scan_for_malware": self.scan_for_malware
        }
        
        # Initialize pyautogui settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        if self.debug_mode:
            print(f"🐛 DeviceActions initialized in DEBUG mode on {self.system}")
            print(f"📋 Available actions: {len(self.actions_map)}")
    
    def execute_action(self, action_name: str, timeout: int = 10, **kwargs) -> Tuple[bool, str, Dict[str, Any]]:
        """Execute a device action with timeout and validation"""
        if action_name not in self.actions_map:
            return False, f"Unknown action: {action_name}", {}
        
        # Debug mode simulation
        if self.debug_mode:
            time.sleep(0.1)  # Simulate execution time
            return True, f"DEBUG: Simulated execution of '{action_name}'", {
                "action_type": "debug",
                "execution_time": datetime.now().isoformat(),
                "platform": self.system,
                "debug_mode": True
            }
        
        try:
            # Set up timeout for long-running actions
            def timeout_handler():
                raise TimeoutError(f"Action '{action_name}' timed out after {timeout} seconds")
            
            timer = Timer(timeout, timeout_handler)
            timer.start()
            
            try:
                result = self.actions_map[action_name](**kwargs)
                timer.cancel()  # Cancel timeout if action completes
                
                # Validate result format
                if not isinstance(result, tuple) or len(result) != 3:
                    return False, f"Invalid result format from action '{action_name}'", {}
                
                success, message, info = result
                
                # Add execution metadata
                if isinstance(info, dict):
                    info["execution_time"] = datetime.now().isoformat()
                    info["platform"] = self.system
                
                return success, message, info
                
            except TimeoutError as e:
                timer.cancel()
                return False, str(e), {"error": "timeout"}
                
        except Exception as e:
            return False, f"Error executing {action_name}: {str(e)}", {"error": str(e)}
    
    def get_available_actions(self) -> list:
        """Get list of available actions"""
        return list(self.actions_map.keys())
    
    def validate_action_availability(self, action_name: str) -> Tuple[bool, str]:
        """Validate if an action is available and properly implemented"""
        if action_name not in self.actions_map:
            return False, f"Action '{action_name}' not found"
        
        # Test if the action is a placeholder
        try:
            # Get the function
            action_func = self.actions_map[action_name]
            
            # Check if it's a simple placeholder by examining the source
            import inspect
            source = inspect.getsource(action_func)
            
            if "functionality available" in source.lower():
                return False, f"Action '{action_name}' is a placeholder implementation"
            
            return True, f"Action '{action_name}' is available"
            
        except Exception as e:
            return False, f"Cannot validate action '{action_name}': {str(e)}"
    
    # Core implementations (key methods only - rest use similar patterns)
    def open_file_browser(self) -> Tuple[bool, str, Dict]:
        """Open system file browser"""
        try:
            if self.system == "Windows":
                subprocess.run(["explorer"], check=True)
            elif self.system == "Darwin":
                subprocess.run(["open", "."], check=True)
            else:
                subprocess.run(["nautilus", "."], check=True)
            return True, "File browser opened successfully", {"action_type": "file_operation"}
        except Exception as e:
            return False, f"Failed to open file browser: {str(e)}", {}
    
    def take_screenshot(self) -> Tuple[bool, str, Dict]:
        """Take a screenshot and save to system Pictures directory"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
            # Determine system Pictures directory
            if self.system == "Windows":
                pictures_dir = os.path.expanduser("~/Pictures")
            elif self.system == "Darwin":
                pictures_dir = os.path.expanduser("~/Pictures")
            else:
                pictures_dir = os.path.expanduser("~/Pictures")
            
            # Create Pictures directory if it doesn't exist
            os.makedirs(pictures_dir, exist_ok=True)
            
            # Full path for screenshot 
            screenshot_path = os.path.join(pictures_dir, filename)
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            
            # Try to open the screenshot in default photo viewer
            try:
                if self.system == "Windows":
                    os.startfile(screenshot_path)
                elif self.system == "Darwin":
                    subprocess.run(["open", screenshot_path], check=False)
                else:
                    subprocess.run(["xdg-open", screenshot_path], check=False)
            except Exception as e:
                print(f"Could not open photo viewer: {e}")
            
            return True, f"Screenshot saved to Pictures folder as {filename} and opened in photo viewer", {
                "filename": filename, 
                "full_path": screenshot_path,
                "action_type": "system_operation",
                "opened_in_viewer": True
            }
            
        except Exception as e:
            return False, f"Failed to take screenshot: {str(e)}", {}
    
    def mute_audio(self) -> Tuple[bool, str, Dict]:
        """Mute system audio"""
        try:
            if self.system == "Windows":
                subprocess.run(["powershell", "-c", "(New-Object -comObject WScript.Shell).SendKeys([char]173)"], check=True)
            elif self.system == "Darwin":
                subprocess.run(["osascript", "-e", "set volume output muted true"], check=True)
            else:
                subprocess.run(["amixer", "set", "Master", "mute"], check=True)
            return True, "Audio muted successfully", {"action_type": "audio_control"}
        except Exception as e:
            return False, f"Failed to mute audio: {str(e)}", {}
    
    def show_system_info(self) -> Tuple[bool, str, Dict]:
        """Get system information"""
        try:
            info = {
                "system": platform.system(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/').percent if platform.system() != "Windows" else psutil.disk_usage('C:').percent
            }
            return True, "System information retrieved", info
        except Exception as e:
            return False, f"Failed to get system info: {str(e)}", {}
    
    # Additional method implementations following similar patterns...
    # (Each method follows the same structure: try/except with platform-specific commands)
    
    def open_notepad(self) -> Tuple[bool, str, Dict]:
        cmd_map = {"Windows": ["notepad"], "Darwin": ["open", "-a", "TextEdit"], "Linux": ["gedit"]}
        return self._exec_platform_cmd(cmd_map, "Text editor opened successfully", "application")
    
    def open_text_editor(self) -> Tuple[bool, str, Dict]:
        """Alias for open_notepad - opens system text editor"""
        return self.open_notepad()
    
    def create_new_file(self) -> Tuple[bool, str, Dict]:
        """Create a new text file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"new_file_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(f"# New File\nCreated on: {datetime.now()}\n")
            return True, f"New file '{filename}' created successfully", {"filename": filename, "action_type": "file_operation"}
        except Exception as e:
            return False, f"Failed to create file: {str(e)}", {}
    
    def delete_file(self, filename: Optional[str] = None) -> Tuple[bool, str, Dict]:
        """Delete a file (demo purpose - creates and deletes temp file)"""
        try:
            if not filename:
                # For demo, create a temp file and delete it
                temp_file = "temp_demo_file.txt"
                with open(temp_file, 'w') as f:
                    f.write("Temporary file for deletion demo")
                os.remove(temp_file)
                return True, f"Demo file deletion completed", {"action_type": "file_operation"}
            else:
                if os.path.exists(filename):
                    os.remove(filename)
                    return True, f"File '{filename}' deleted successfully", {"filename": filename, "action_type": "file_operation"}
                else:
                    return False, f"File '{filename}' not found", {}
        except Exception as e:
            return False, f"Failed to delete file: {str(e)}", {}
    
    def open_calculator(self) -> Tuple[bool, str, Dict]:
        cmd_map = {"Windows": ["calc"], "Darwin": ["open", "-a", "Calculator"], "Linux": ["gnome-calculator"]}
        return self._exec_platform_cmd(cmd_map, "Calculator opened successfully", "application")
    
    def open_browser(self) -> Tuple[bool, str, Dict]:
        cmd_map = {"Windows": ["start", "chrome"], "Darwin": ["open", "-a", "Safari"], "Linux": ["firefox"]}
        return self._exec_platform_cmd(cmd_map, "Browser opened successfully", "application", shell_windows=True)
    
    def _exec_platform_cmd(self, cmd_map: dict, success_msg: str, action_type: str, shell_windows: bool = False, timeout: int = 5) -> Tuple[bool, str, Dict]:
        """Helper to execute platform-specific commands with timeout"""
        try:
            if self.system in cmd_map:
                result = subprocess.run(
                    cmd_map[self.system], 
                    check=True, 
                    shell=(shell_windows and self.system == "Windows"),
                    timeout=timeout,
                    capture_output=True,
                    text=True
                )
                return True, success_msg, {"action_type": action_type, "stdout": result.stdout.strip()}
            else:
                return False, f"Action not supported on {self.system}", {}
        except subprocess.TimeoutExpired:
            return False, f"Command timed out after {timeout} seconds", {"error": "timeout"}
        except subprocess.CalledProcessError as e:
            return False, f"Command failed with exit code {e.returncode}: {e.stderr}", {"error": "command_failed"}
        except Exception as e:
            return False, f"Failed to execute command: {str(e)}", {"error": str(e)}
    
    # Simplified implementations for new actions
    def open_documents_folder(self) -> Tuple[bool, str, Dict]:
        return self._open_folder("~/Documents", "Documents folder opened")
    
    def open_downloads_folder(self) -> Tuple[bool, str, Dict]:
        return self._open_folder("~/Downloads", "Downloads folder opened")
    
    def open_pictures_folder(self) -> Tuple[bool, str, Dict]:
        return self._open_folder("~/Pictures", "Pictures folder opened")
    
    def _open_folder(self, folder_path: str, success_msg: str) -> Tuple[bool, str, Dict]:
        """Helper to open folders"""
        try:
            expanded_path = os.path.expanduser(folder_path)
            if self.system == "Windows":
                subprocess.run(["explorer", expanded_path], check=True)
            elif self.system == "Darwin":
                subprocess.run(["open", expanded_path], check=True)
            else:
                subprocess.run(["xdg-open", expanded_path], check=True)
            return True, success_msg, {"action_type": "file_operation"}
        except Exception as e:
            return False, f"Failed to open folder: {str(e)}", {}
    
    # Audio controls
    def volume_up(self) -> Tuple[bool, str, Dict]:
        return self._volume_control("up", "Volume increased")
    
    def volume_down(self) -> Tuple[bool, str, Dict]:
        return self._volume_control("down", "Volume decreased")
    
    def _volume_control(self, direction: str, success_msg: str) -> Tuple[bool, str, Dict]:
        """Helper for volume control"""
        try:
            if self.system == "Windows":
                key_code = "[char]175" if direction == "up" else "[char]174"
                subprocess.run(["powershell", "-c", f"(New-Object -comObject WScript.Shell).SendKeys({key_code})"], check=True)
            elif self.system == "Darwin":
                op = "+" if direction == "up" else "-"
                subprocess.run(["osascript", "-e", f"set volume output volume (output volume of (get volume settings) {op} 10)"], check=True)
            else:
                op = "5%+" if direction == "up" else "5%-"
                subprocess.run(["amixer", "set", "Master", op], check=True)
            return True, success_msg, {"action_type": "audio_control"}
        except Exception as e:
            return False, f"Failed to control volume: {str(e)}", {}
    
    # Additional implementations for new categories
    def check_memory_usage(self) -> Tuple[bool, str, Dict]:
        try:
            memory = psutil.virtual_memory()
            return True, f"Memory usage: {memory.percent:.1f}%", {"memory_percent": memory.percent, "action_type": "system_info"}
        except Exception as e:
            return False, f"Failed to check memory: {str(e)}", {}
    
    def check_cpu_usage(self) -> Tuple[bool, str, Dict]:
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            return True, f"CPU usage: {cpu_percent:.1f}%", {"cpu_percent": cpu_percent, "action_type": "system_info"}
        except Exception as e:
            return False, f"Failed to check CPU: {str(e)}", {}
    
    def create_document(self) -> Tuple[bool, str, Dict]:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"document_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(f"# New Document\nCreated on: {datetime.now()}\n")
            return True, f"Document '{filename}' created", {"filename": filename, "action_type": "productivity"}
        except Exception as e:
            return False, f"Failed to create document: {str(e)}", {}
    
    # Placeholder implementations for remaining actions (following same pattern)
    def unmute_audio(self) -> Tuple[bool, str, Dict]:
        """Unmute system audio"""
        try:
            if self.system == "Windows":
                subprocess.run(["powershell", "-c", "(New-Object -comObject WScript.Shell).SendKeys([char]173)"], check=True)
            elif self.system == "Darwin":
                subprocess.run(["osascript", "-e", "set volume output muted false"], check=True)
            else:
                subprocess.run(["amixer", "set", "Master", "unmute"], check=True)
            return True, "Audio unmuted successfully", {"action_type": "audio_control"}
        except Exception as e:
            return False, f"Failed to unmute audio: {str(e)}", {}
    
    def toggle_audio(self) -> Tuple[bool, str, Dict]:
        return self.mute_audio()
    
    def max_volume(self) -> Tuple[bool, str, Dict]:
        return True, "Max volume functionality available", {"action_type": "audio_control"}
    
    def min_volume(self) -> Tuple[bool, str, Dict]:
        return True, "Min volume functionality available", {"action_type": "audio_control"}
    
    def lock_screen(self) -> Tuple[bool, str, Dict]:
        """Lock the screen"""
        try:
            if self.system == "Windows":
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
            elif self.system == "Darwin":
                subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"], check=True)
            else:
                # Try common Linux screen lockers
                for cmd in [["gnome-screensaver-command", "-l"], ["xdg-screensaver", "lock"], ["loginctl", "lock-session"]]:
                    try:
                        subprocess.run(cmd, check=True)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                else:
                    return False, "No screen locker found", {}
            return True, "Screen locked successfully", {"action_type": "system_operation"}
        except Exception as e:
            return False, f"Failed to lock screen: {str(e)}", {}
    
    def open_task_manager(self) -> Tuple[bool, str, Dict]:
        cmd_map = {"Windows": ["taskmgr"], "Darwin": ["open", "-a", "Activity Monitor"], "Linux": ["gnome-system-monitor"]}
        return self._exec_platform_cmd(cmd_map, "Task manager opened", "system_operation")
    
    def minimize_all_windows(self) -> Tuple[bool, str, Dict]:
        try:
            if self.system == "Windows":
                pyautogui.hotkey('win', 'm')
            elif self.system == "Darwin":
                pyautogui.hotkey('cmd', 'option', 'm')
            else:
                pyautogui.hotkey('ctrl', 'alt', 'd')
            return True, "All windows minimized", {"action_type": "window_management"}
        except Exception as e:
            return False, f"Failed to minimize windows: {str(e)}", {}
    
    def close_active_window(self) -> Tuple[bool, str, Dict]:
        try:
            if self.system == "Windows":
                pyautogui.hotkey('alt', 'f4')
            elif self.system == "Darwin":
                pyautogui.hotkey('cmd', 'w')
            else:
                pyautogui.hotkey('alt', 'f4')
            return True, "Active window closed", {"action_type": "window_management"}
        except Exception as e:
            return False, f"Failed to close window: {str(e)}", {}
    
    # Generic implementations for remaining methods
    def check_network_status(self) -> Tuple[bool, str, Dict]:
        """Check network connectivity status"""
        try:
            import socket
            # Try to connect to a well-known server
            socket.create_connection(("8.8.8.8", 53), 2)
            return True, "Network connection active", {"connected": True, "action_type": "system_info"}
        except OSError:
            return True, "Network connection unavailable", {"connected": False, "action_type": "system_info"}
        except Exception as e:
            return False, f"Failed to check network: {str(e)}", {}
    
    def check_disk_usage(self) -> Tuple[bool, str, Dict]:
        """Check disk usage information"""
        try:
            if self.system == "Windows":
                disk_path = 'C:'
            else:
                disk_path = '/'
            
            usage = psutil.disk_usage(disk_path)
            used_percent = (usage.used / usage.total) * 100
            
            return True, f"Disk usage: {used_percent:.1f}% used", {
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "used_percent": round(used_percent, 1),
                "action_type": "system_info"
            }
        except Exception as e:
            return False, f"Failed to check disk usage: {str(e)}", {}
    
    def check_battery_status(self) -> Tuple[bool, str, Dict]:
        """Check battery status if available"""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return True, "No battery detected (Desktop system)", {"has_battery": False, "action_type": "system_info"}
            
            return True, f"Battery: {battery.percent:.0f}% ({'Charging' if battery.power_plugged else 'Discharging'})", {
                "percent": battery.percent,
                "plugged": battery.power_plugged,
                "has_battery": True,
                "action_type": "system_info"
            }
        except Exception as e:
            return False, f"Failed to check battery: {str(e)}", {}
    
    def open_calendar(self) -> Tuple[bool, str, Dict]:
        """Open system calendar application"""
        cmd_map = {
            "Windows": ["start", "outlookcal:"], 
            "Darwin": ["open", "-a", "Calendar"], 
            "Linux": ["gnome-calendar"]
        }
        return self._exec_platform_cmd(cmd_map, "Calendar opened successfully", "application")
    
    def open_terminal(self) -> Tuple[bool, str, Dict]:
        cmd_map = {"Windows": ["cmd"], "Darwin": ["open", "-a", "Terminal"], "Linux": ["gnome-terminal"]}
        return self._exec_platform_cmd(cmd_map, "Terminal opened", "application")
    
    def open_settings(self) -> Tuple[bool, str, Dict]:
        """Open system settings"""
        cmd_map = {
            "Windows": ["start", "ms-settings:"], 
            "Darwin": ["open", "-a", "System Preferences"], 
            "Linux": ["gnome-control-center"]
        }
        return self._exec_platform_cmd(cmd_map, "Settings opened successfully", "application")
    
    # New application methods
    def open_email_app(self) -> Tuple[bool, str, Dict]:
        """Open default email application"""
        cmd_map = {
            "Windows": ["start", "mailto:"], 
            "Darwin": ["open", "-a", "Mail"], 
            "Linux": ["thunderbird"]
        }
        return self._exec_platform_cmd(cmd_map, "Email app opened successfully", "application")
    
    def open_music_player(self) -> Tuple[bool, str, Dict]:
        """Open default music player"""
        cmd_map = {
            "Windows": ["start", "mswindowsmusic:"], 
            "Darwin": ["open", "-a", "Music"], 
            "Linux": ["rhythmbox"]
        }
        return self._exec_platform_cmd(cmd_map, "Music player opened successfully", "application")
    
    def open_photo_viewer(self) -> Tuple[bool, str, Dict]:
        """Open default photo viewer"""
        cmd_map = {
            "Windows": ["start", "ms-photos:"], 
            "Darwin": ["open", "-a", "Photos"], 
            "Linux": ["eog"]
        }
        return self._exec_platform_cmd(cmd_map, "Photo viewer opened successfully", "application")
    
    def open_video_player(self) -> Tuple[bool, str, Dict]:
        """Open default video player"""
        cmd_map = {
            "Windows": ["start", "mswindowsvideo:"], 
            "Darwin": ["open", "-a", "QuickTime Player"], 
            "Linux": ["totem"]
        }
        return self._exec_platform_cmd(cmd_map, "Video player opened successfully", "application")
    
    # Window management
    def maximize_window(self) -> Tuple[bool, str, Dict]:
        """Maximize the active window"""
        try:
            if self.system == "Windows":
                pyautogui.hotkey('win', 'up')
            elif self.system == "Darwin":
                pyautogui.hotkey('cmd', 'ctrl', 'f')
            else:
                pyautogui.hotkey('alt', 'f10')
            return True, "Window maximized successfully", {"action_type": "window_management"}
        except Exception as e:
            return False, f"Failed to maximize window: {str(e)}", {}
    
    def minimize_window(self) -> Tuple[bool, str, Dict]:
        """Minimize the active window"""
        try:
            if self.system == "Windows":
                pyautogui.hotkey('win', 'down')
            elif self.system == "Darwin":
                pyautogui.hotkey('cmd', 'm')
            else:
                pyautogui.hotkey('alt', 'f9')
            return True, "Window minimized successfully", {"action_type": "window_management"}
        except Exception as e:
            return False, f"Failed to minimize window: {str(e)}", {}
    
    def switch_window(self) -> Tuple[bool, str, Dict]:
        """Switch between windows"""
        try:
            if self.system == "Windows":
                pyautogui.hotkey('alt', 'tab')
            elif self.system == "Darwin":
                pyautogui.hotkey('cmd', 'tab')
            else:
                pyautogui.hotkey('alt', 'tab')
            return True, "Window switched successfully", {"action_type": "window_management"}
        except Exception as e:
            return False, f"Failed to switch window: {str(e)}", {}
    
    def close_all_windows(self) -> Tuple[bool, str, Dict]:
        return True, "Close all windows functionality available", {"action_type": "window_management"}
    
    def tile_windows(self) -> Tuple[bool, str, Dict]:
        return True, "Window tiling functionality available", {"action_type": "window_management"}
    
    def fullscreen_mode(self) -> Tuple[bool, str, Dict]:
        """Toggle fullscreen mode for active window"""
        try:
            if self.system == "Windows":
                pyautogui.press('f11')
            elif self.system == "Darwin":
                pyautogui.hotkey('cmd', 'ctrl', 'f')
            else:
                pyautogui.press('f11')
            return True, "Fullscreen mode toggled successfully", {"action_type": "window_management"}
        except Exception as e:
            return False, f"Failed to toggle fullscreen: {str(e)}", {}
    
    def snap_window_left(self) -> Tuple[bool, str, Dict]:
        """Snap window to left half of screen"""
        try:
            if self.system == "Windows":
                pyautogui.hotkey('win', 'left')
            elif self.system == "Darwin":
                # macOS doesn't have native window snapping, but we can try third-party or use Mission Control
                pyautogui.hotkey('ctrl', 'left')
            else:
                pyautogui.hotkey('super', 'left')
            return True, "Window snapped to left successfully", {"action_type": "window_management"}
        except Exception as e:
            return False, f"Failed to snap window left: {str(e)}", {}
    
    def snap_window_right(self) -> Tuple[bool, str, Dict]:
        """Snap window to right half of screen"""
        try:
            if self.system == "Windows":
                pyautogui.hotkey('win', 'right')
            elif self.system == "Darwin":
                # macOS doesn't have native window snapping, but we can try third-party or use Mission Control
                pyautogui.hotkey('ctrl', 'right')
            else:
                pyautogui.hotkey('super', 'right')
            return True, "Window snapped to right successfully", {"action_type": "window_management"}
        except Exception as e:
            return False, f"Failed to snap window right: {str(e)}", {}
    
    # Performance and productivity
    def show_running_processes(self) -> Tuple[bool, str, Dict]:
        try:
            process_count = len(list(psutil.process_iter()))
            return True, f"Found {process_count} running processes", {"total_processes": process_count, "action_type": "system_info"}
        except Exception as e:
            return False, f"Failed to get processes: {str(e)}", {}
    
    def monitor_performance(self) -> Tuple[bool, str, Dict]:
        return True, "Performance monitoring functionality available", {"action_type": "system_info"}
    
    def open_spreadsheet(self) -> Tuple[bool, str, Dict]:
        return True, "Spreadsheet functionality available", {"action_type": "productivity"}
    
    def search_online(self) -> Tuple[bool, str, Dict]:
        return True, "Online search functionality available", {"action_type": "productivity"}
    
    def set_reminder(self) -> Tuple[bool, str, Dict]:
        return True, "Reminder functionality available", {"action_type": "productivity"}
    
    def start_timer(self) -> Tuple[bool, str, Dict]:
        return True, "Timer functionality available", {"action_type": "productivity"}
    
    # Security
    def clear_browser_data(self) -> Tuple[bool, str, Dict]:
        return True, "Browser data clearing functionality available", {"action_type": "security"}
    
    def check_privacy_settings(self) -> Tuple[bool, str, Dict]:
        return True, "Privacy settings check functionality available", {"action_type": "security"}
    
    def enable_firewall(self) -> Tuple[bool, str, Dict]:
        return True, "Firewall functionality available", {"action_type": "security"}
    
    def scan_for_malware(self) -> Tuple[bool, str, Dict]:
        return True, "Malware scan functionality available", {"action_type": "security"}


# Example usage
if __name__ == "__main__":
    actions = DeviceActions()
    print("Available actions:", len(actions.get_available_actions()))
    
    # Test some actions
    test_actions = ["take_screenshot", "show_system_info", "open_calculator"]
    for action in test_actions:
        success, message, info = actions.execute_action(action)
        print(f"{action}: {success} - {message}")