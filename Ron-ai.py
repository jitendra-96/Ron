# Enhanced AI Voice Assistant Implementation
# Improved version with better error handling, security, and features

import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import sys
import subprocess
import requests
import json
from threading import Thread, Lock
import queue
import time
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import pickle
from pathlib import Path

# Configure logging with rotation
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Setup comprehensive logging with file rotation"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "ron_ai.log"
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Setup logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

class CommandType(Enum):
    """Enum for command types"""
    TIME = "time"
    DATE = "date"
    WEATHER = "weather"
    SEARCH = "search"
    OPEN_APP = "open_app"
    SYSTEM = "system"
    VOLUME = "volume"
    MUSIC = "music"
    INFO = "info"
    SMART_HOME = "smart_home"
    REMINDER = "reminder"
    NOTE = "note"
    UNKNOWN = "unknown"

@dataclass
class UserPreference:
    """User preference data structure"""
    name: str = "User"
    city: str = "New York"
    preferred_voice: int = 0
    speech_rate: int = 180
    volume: float = 0.8
    language: str = "en-US"
    wake_words: List[str] = None
    
    def __post_init__(self):
        if self.wake_words is None:
            self.wake_words = ['hey ron', 'ron', 'hey assistant']

class ConfigManager:
    """Manage configuration and preferences"""
    
    def __init__(self, config_path: str = "config"):
        self.config_path = Path(config_path)
        self.config_path.mkdir(exist_ok=True)
        self.preferences_file = self.config_path / "preferences.json"
        self.secrets_file = self.config_path / ".secrets"
        
    def load_preferences(self) -> UserPreference:
        """Load user preferences from file"""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r') as f:
                    data = json.load(f)
                    return UserPreference(**data)
            return UserPreference()
        except Exception as e:
            logger.error(f"Failed to load preferences: {e}")
            return UserPreference()
    
    def save_preferences(self, preferences: UserPreference):
        """Save user preferences to file"""
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(asdict(preferences), f, indent=2)
            logger.info("Preferences saved successfully")
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Securely retrieve API key for a service"""
        try:
            # First check environment variables
            env_key = os.getenv(f'{service.upper()}_API_KEY')
            if env_key:
                return env_key
            
            # Then check secrets file
            if self.secrets_file.exists():
                with open(self.secrets_file, 'r') as f:
                    secrets = json.load(f)
                    return secrets.get(service)
            
            return None
        except Exception as e:
            logger.error(f"Failed to get API key for {service}: {e}")
            return None

class SpeechManager:
    """Manage speech recognition and synthesis"""
    
    def __init__(self, preferences: UserPreference):
        self.preferences = preferences
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.tts_engine = None
        self.tts_lock = Lock()
        self._initialize()
    
    def _initialize(self):
        """Initialize speech components"""
        try:
            # Initialize TTS
            self.tts_engine = pyttsx3.init()
            self._setup_voice()
            
            # Initialize microphone
            self.microphone = sr.Microphone()
            self._calibrate_microphone()
            
            logger.info("Speech manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize speech manager: {e}")
            raise
    
    def _setup_voice(self):
        """Configure TTS voice settings"""
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices and 0 <= self.preferences.preferred_voice < len(voices):
                self.tts_engine.setProperty('voice', voices[self.preferences.preferred_voice].id)
            
            self.tts_engine.setProperty('rate', self.preferences.speech_rate)
            self.tts_engine.setProperty('volume', self.preferences.volume)
            
            logger.info("Voice settings configured")
        except Exception as e:
            logger.error(f"Failed to setup voice: {e}")
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            logger.info("Calibrating microphone...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                # Set recognition parameters
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.8
            logger.info("Microphone calibrated")
        except Exception as e:
            logger.error(f"Failed to calibrate microphone: {e}")
    
    def speak(self, text: str, wait: bool = True):
        """Convert text to speech thread-safely"""
        def _speak():
            with self.tts_lock:
                try:
                    print(f"Ron: {text}")
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    logger.error(f"TTS error: {e}")
        
        if wait:
            _speak()
        else:
            Thread(target=_speak, daemon=True).start()
    
    def listen(self, timeout: float = 5, phrase_limit: float = 10) -> Optional[str]:
        """Listen for speech input"""
        try:
            with self.microphone as source:
                logger.debug("Listening...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )
            
            # Try multiple recognition services for redundancy
            text = None
            
            # Try Google first
            try:
                text = self.recognizer.recognize_google(
                    audio,
                    language=self.preferences.language
                ).lower()
            except sr.RequestError:
                logger.warning("Google recognition failed, trying alternatives...")
                # Try Sphinx offline recognition as backup
                try:
                    text = self.recognizer.recognize_sphinx(audio).lower()
                except:
                    pass
            
            if text:
                logger.info(f"Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return None

class CommandProcessor:
    """Process and execute commands"""
    
    def __init__(self, speech_manager: SpeechManager, config_manager: ConfigManager):
        self.speech = speech_manager
        self.config = config_manager
        self.command_history = []
        self.context = {}
        
        # Command patterns
        self.command_patterns = {
            CommandType.TIME: ['time', 'clock', 'what time'],
            CommandType.DATE: ['date', 'day', 'what day'],
            CommandType.WEATHER: ['weather', 'temperature', 'forecast'],
            CommandType.SEARCH: ['search', 'google', 'look up', 'find'],
            CommandType.OPEN_APP: ['open', 'launch', 'start'],
            CommandType.VOLUME: ['volume', 'sound', 'mute', 'unmute'],
            CommandType.MUSIC: ['play music', 'pause music', 'stop music', 'next song'],
            CommandType.INFO: ['tell me about', 'what is', 'who is', 'define'],
            CommandType.SMART_HOME: ['lights', 'temperature', 'thermostat', 'lock', 'unlock'],
            CommandType.REMINDER: ['remind', 'reminder', 'alert me'],
            CommandType.NOTE: ['note', 'write down', 'remember this'],
        }
    
    def classify_command(self, command: str) -> CommandType:
        """Classify command type based on keywords"""
        command_lower = command.lower()
        
        for cmd_type, patterns in self.command_patterns.items():
            if any(pattern in command_lower for pattern in patterns):
                return cmd_type
        
        return CommandType.UNKNOWN
    
    def process(self, command: str) -> bool:
        """Process command and return whether to continue"""
        try:
            # Add to history
            self.command_history.append({
                'timestamp': datetime.datetime.now(),
                'command': command
            })
            
            # Classify command
            cmd_type = self.classify_command(command)
            logger.info(f"Command type: {cmd_type.value}")
            
            # Handle special exit commands
            if any(word in command.lower() for word in ['goodbye', 'exit', 'quit', 'bye']):
                self.speech.speak("Goodbye! It was nice talking to you.")
                return False
            
            # Route to appropriate handler
            handlers = {
                CommandType.TIME: self._handle_time,
                CommandType.DATE: self._handle_date,
                CommandType.WEATHER: self._handle_weather,
                CommandType.SEARCH: self._handle_search,
                CommandType.OPEN_APP: self._handle_open_app,
                CommandType.VOLUME: self._handle_volume,
                CommandType.MUSIC: self._handle_music,
                CommandType.INFO: self._handle_info,
                CommandType.SMART_HOME: self._handle_smart_home,
                CommandType.REMINDER: self._handle_reminder,
                CommandType.NOTE: self._handle_note,
                CommandType.UNKNOWN: self._handle_unknown
            }
            
            handler = handlers.get(cmd_type, self._handle_unknown)
            handler(command)
            
            return True
            
        except Exception as e:
            logger.error(f"Command processing error: {e}")
            self.speech.speak("Sorry, I encountered an error processing that command.")
            return True
    
    def _handle_time(self, command: str):
        """Handle time-related commands"""
        try:
            current_time = datetime.datetime.now()
            time_str = current_time.strftime("%I:%M %p")
            self.speech.speak(f"It's {time_str}")
        except Exception as e:
            logger.error(f"Time handler error: {e}")
            self.speech.speak("Sorry, I couldn't get the time.")
    
    def _handle_date(self, command: str):
        """Handle date-related commands"""
        try:
            current_date = datetime.datetime.now()
            date_str = current_date.strftime("%A, %B %d, %Y")
            self.speech.speak(f"Today is {date_str}")
        except Exception as e:
            logger.error(f"Date handler error: {e}")
            self.speech.speak("Sorry, I couldn't get the date.")
    
    def _handle_weather(self, command: str):
        """Handle weather requests"""
        try:
            api_key = self.config.get_api_key('openweather')
            if not api_key:
                self.speech.speak("Weather service is not configured. Please set up your API key.")
                return
            
            city = self.speech.preferences.city
            
            # Extract city from command if mentioned
            if "in" in command:
                parts = command.split("in")
                if len(parts) > 1:
                    city = parts[-1].strip()
            
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                temp = round(data['main']['temp'])
                feels_like = round(data['main']['feels_like'])
                description = data['weather'][0]['description']
                humidity = data['main']['humidity']
                
                weather_msg = (f"The weather in {city} is {description} "
                             f"with a temperature of {temp}°C, "
                             f"feels like {feels_like}°C, "
                             f"and humidity at {humidity}%")
                
                self.speech.speak(weather_msg)
            else:
                self.speech.speak(f"Sorry, I couldn't get weather information for {city}.")
                
        except requests.RequestException as e:
            logger.error(f"Weather API error: {e}")
            self.speech.speak("Weather service is currently unavailable.")
        except Exception as e:
            logger.error(f"Weather handler error: {e}")
            self.speech.speak("Sorry, I couldn't get the weather.")
    
    def _handle_search(self, command: str):
        """Handle web search requests"""
        try:
            # Extract search query
            search_terms = ['search for', 'google', 'search', 'look up', 'find']
            query = command.lower()
            
            for term in search_terms:
                if term in query:
                    query = query.split(term)[-1].strip()
                    break
            
            if query and query != command.lower():
                url = f"https://www.google.com/search?q={query}"
                webbrowser.open(url)
                self.speech.speak(f"I've opened search results for {query}")
            else:
                self.speech.speak("What would you like me to search for?")
                
        except Exception as e:
            logger.error(f"Search handler error: {e}")
            self.speech.speak("Sorry, I couldn't perform the search.")
    
    def _handle_open_app(self, command: str):
        """Handle application opening requests"""
        try:
            apps = {
                'calculator': ['calc', 'Calculator'],
                'notepad': ['notepad', 'TextEdit'],
                'browser': ['start https://www.google.com', 'open -a Safari'],
                'terminal': ['cmd', 'Terminal'],
                'settings': ['start ms-settings:', 'open -b com.apple.preference'],
            }
            
            opened = False
            for app_name, commands in apps.items():
                if app_name in command.lower():
                    try:
                        if sys.platform == 'win32':
                            os.system(commands[0])
                        elif sys.platform == 'darwin':
                            os.system(f"open -a {commands[1]}")
                        else:  # Linux
                            subprocess.Popen([app_name])
                        
                        self.speech.speak(f"Opening {app_name}")
                        opened = True
                        break
                    except Exception as e:
                        logger.error(f"Failed to open {app_name}: {e}")
            
            if not opened:
                self.speech.speak("I'm not sure which application to open.")
                
        except Exception as e:
            logger.error(f"Open app handler error: {e}")
            self.speech.speak("Sorry, I couldn't open that application.")
    
    def _handle_volume(self, command: str):
        """Handle volume control"""
        try:
            if sys.platform == 'win32':
                # Windows volume control using nircmd if available
                if "up" in command or "increase" in command:
                    os.system("nircmd.exe changesysvolume 5000")
                    self.speech.speak("Volume increased")
                elif "down" in command or "decrease" in command:
                    os.system("nircmd.exe changesysvolume -5000")
                    self.speech.speak("Volume decreased")
                elif "mute" in command:
                    os.system("nircmd.exe mutesysvolume 1")
                    self.speech.speak("Muted")
                elif "unmute" in command:
                    os.system("nircmd.exe mutesysvolume 0")
                    self.speech.speak("Unmuted")
            elif sys.platform == 'darwin':
                # macOS volume control
                if "up" in command or "increase" in command:
                    os.system("osascript -e 'set volume output volume ((output volume of (get volume settings)) + 10)'")
                    self.speech.speak("Volume increased")
                elif "down" in command or "decrease" in command:
                    os.system("osascript -e 'set volume output volume ((output volume of (get volume settings)) - 10)'")
                    self.speech.speak("Volume decreased")
                elif "mute" in command:
                    os.system("osascript -e 'set volume output muted true'")
                    self.speech.speak("Muted")
                elif "unmute" in command:
                    os.system("osascript -e 'set volume output muted false'")
                    self.speech.speak("Unmuted")
            else:
                self.speech.speak("Volume control is not configured for this system.")
                
        except Exception as e:
            logger.error(f"Volume handler error: {e}")
            self.speech.speak("Sorry, I couldn't control the volume.")
    
    def _handle_music(self, command: str):
        """Handle music playback commands"""
        try:
            if "play" in command:
                # Open a music streaming service
                webbrowser.open("https://music.youtube.com")
                self.speech.speak("Opening YouTube Music")
            elif "pause" in command or "stop" in command:
                self.speech.speak("Music control requires integration with your music player.")
            else:
                self.speech.speak("Please specify what you'd like to do with music.")
                
        except Exception as e:
            logger.error(f"Music handler error: {e}")
            self.speech.speak("Sorry, I couldn't control music playback.")
    
    def _handle_info(self, command: str):
        """Handle information requests"""
        try:
            # Extract topic
            info_terms = ['tell me about', 'what is', 'who is', 'define']
            topic = command.lower()
            
            for term in info_terms:
                if term in topic:
                    topic = topic.split(term)[-1].strip()
                    break
            
            if topic and topic != command.lower():
                url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
                webbrowser.open(url)
                self.speech.speak(f"I've opened information about {topic}")
            else:
                self.speech.speak("What would you like to know about?")
                
        except Exception as e:
            logger.error(f"Info handler error: {e}")
            self.speech.speak("Sorry, I couldn't find that information.")
    
    def _handle_smart_home(self, command: str):
        """Handle smart home commands"""
        try:
            # This would integrate with actual smart home APIs
            if "lights on" in command:
                self.speech.speak("I would turn on the lights if connected to your smart home system.")
            elif "lights off" in command:
                self.speech.speak("I would turn off the lights if connected to your smart home system.")
            elif "temperature" in command:
                self.speech.speak("Temperature control requires smart home integration.")
            else:
                self.speech.speak("Smart home features require additional setup.")
                
        except Exception as e:
            logger.error(f"Smart home handler error: {e}")
            self.speech.speak("Sorry, I couldn't control the smart home device.")
    
    def _handle_reminder(self, command: str):
        """Handle reminder requests"""
        try:
            # Extract reminder details
            if "remind me to" in command:
                task = command.split("remind me to")[-1].strip()
                # Here you would implement actual reminder logic
                self.speech.speak(f"I'll remind you to {task}. Note: Reminder system needs to be configured.")
            else:
                self.speech.speak("What would you like me to remind you about?")
                
        except Exception as e:
            logger.error(f"Reminder handler error: {e}")
            self.speech.speak("Sorry, I couldn't set that reminder.")
    
    def _handle_note(self, command: str):
        """Handle note-taking requests"""
        try:
            # Extract note content
            note_terms = ['note that', 'write down', 'remember']
            note = command.lower()
            
            for term in note_terms:
                if term in note:
                    note = note.split(term)[-1].strip()
                    break
            
            if note and note != command.lower():
                # Save note to file
                notes_dir = Path("notes")
                notes_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                note_file = notes_dir / f"note_{timestamp}.txt"
                
                with open(note_file, 'w') as f:
                    f.write(f"Note created at {datetime.datetime.now()}\n")
                    f.write(f"{note}\n")
                
                self.speech.speak(f"I've saved your note: {note}")
            else:
                self.speech.speak("What would you like me to note down?")
                
        except Exception as e:
            logger.error(f"Note handler error: {e}")
            self.speech.speak("Sorry, I couldn't save that note.")
    
    def _handle_unknown(self, command: str):
        """Handle unknown commands"""
        self.speech.speak("I'm not sure how to help with that. Could you please rephrase?")

class RonAI:
    """Main AI Assistant class"""
    
    def __init__(self):
        """Initialize Ron AI Assistant"""
        try:
            logger.info("Initializing Ron AI...")
            
            # Load configuration
            self.config_manager = ConfigManager()
            self.preferences = self.config_manager.load_preferences()
            
            # Initialize speech components
            self.speech_manager = SpeechManager(self.preferences)
            
            # Initialize command processor
            self.command_processor = CommandProcessor(
                self.speech_manager,
                self.config_manager
            )
            
            # State management
            self.is_running = False
            self.is_listening = False
            
            logger.info("Ron AI initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize Ron AI: {e}")
            raise
    
    def run(self):
        """Main execution loop"""
        try:
            self.is_running = True
            self.speech_manager.speak(
                f"Hello! I'm Ron, your AI assistant. "
                f"Say 'Hey Ron' to activate me."
            )
            
            while self.is_running:
                try:
                    # Listen for wake word
                    text = self.speech_manager.listen(timeout=1, phrase_limit=3)
                    
                    if text:
                        # Check for wake word
                        if any(wake_word in text for wake_word in self.preferences.wake_words):
                            self.handle_activation()
                    
                    # Small delay to prevent CPU overuse
                    time.sleep(0.1)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    time.sleep(1)
            
            self.shutdown()
            
        except Exception as e:
            logger.error(f"Fatal error in run: {e}")
            self.shutdown()
    
    def handle_activation(self):
        """Handle wake word activation"""
        try:
            self.speech_manager.speak("Yes, how can I help you?")
            
            # Listen for command
            command = self.speech_manager.listen(timeout=5, phrase_limit=10)
            
            if command:
                # Process the command
                should_continue = self.command_processor.process(command)
                
                if not should_continue:
                    self.is_running = False
            else:
                self.speech_manager.speak("I didn't hear anything. Please try again.")
                
        except Exception as e:
            logger.error(f"Error handling activation: {e}")
            self.speech_manager.speak("Sorry, I encountered an error.")
    
    def shutdown(self):
        """Cleanup and shutdown"""
        try:
            logger.info("Shutting down Ron AI...")
            
            # Save preferences
            self.config_manager.save_preferences(self.preferences)
            
            # Cleanup speech resources
            if self.speech_manager.tts_engine:
                self.speech_manager.tts_engine.stop()
            
            self.speech_manager.speak("Ron shutting down. Goodbye!")
            
            logger.info("Ron AI shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


def main():
    """Main entry point"""
    try:
        # Check dependencies
        required_packages = ['speech_recognition', 'pyttsx3', 'requests']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"Missing required packages: {', '.join(missing_packages)}")
            print("Please install them using: pip install " + ' '.join(missing_packages))
            return
        
        # Start Ron AI
        ron = RonAI()
        ron.run()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()