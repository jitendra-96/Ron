# Ron AI Voice Assistant 🤖🎙️

An advanced, modular AI voice assistant built with Python that can help you with daily tasks through natural voice commands. Ron features speech recognition, text-to-speech, and various utility functions with a focus on reliability, security, and extensibility.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## ✨ Features

### Core Capabilities
- 🎤 **Voice Activation**: Wake word detection ("Hey Ron", "Ron")
- 🗣️ **Natural Language Processing**: Understands conversational commands
- 📢 **Text-to-Speech**: Natural voice responses
- 🔄 **Multi-platform Support**: Works on Windows, macOS, and Linux

### Available Commands

#### 📅 Time & Date
- "What time is it?"
- "What's the date today?"
- "What day is it?"

#### 🌤️ Weather
- "What's the weather?"
- "Weather in [city name]"
- "What's the temperature?"

#### 🔍 Web Search
- "Search for [query]"
- "Google [topic]"
- "Look up [information]"

#### 💻 Application Control
- "Open calculator"
- "Open notepad"
- "Launch browser"
- "Open settings"

#### 🔊 System Control
- "Volume up/down"
- "Mute/Unmute"
- "Play music"

#### 📝 Productivity
- "Take a note: [content]"
- "Remind me to [task]"
- "Tell me about [topic]"

#### 🏠 Smart Home (Ready for Integration)
- "Turn lights on/off"
- "Adjust temperature"
- "Lock/Unlock doors"

## 📋 Prerequisites

### System Requirements
- Python 3.8 or higher
- Microphone (built-in or external)
- Speakers or headphones
- Internet connection (for online speech recognition and web services)

### Operating System Support
- ✅ Windows 10/11
- ✅ macOS 10.14+
- ✅ Linux (Ubuntu 18.04+, Debian, Fedora)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ron-ai-assistant.git
cd ron-ai-assistant
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

#### Basic Installation
```bash
pip install -r requirements.txt
```

#### Manual Installation
```bash
# Core dependencies
pip install SpeechRecognition
pip install pyttsx3
pip install requests
pip install pyaudio

# Optional: For offline speech recognition
pip install pocketsphinx

# Optional: For enhanced audio processing
pip install sounddevice
pip install scipy
```

### 4. Platform-Specific Setup

#### Windows
- Install PyAudio wheel if pip install fails:
  ```bash
  # Download the appropriate wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
  pip install PyAudio‑0.2.11‑cp38‑cp38‑win_amd64.whl
  ```
- For volume control, download [nircmd.exe](https://www.nirsoft.net/utils/nircmd.html) and add to PATH

#### macOS
```bash
# Install PortAudio for microphone access
brew install portaudio

# Install PyAudio
pip install pyaudio
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-pyaudio
sudo apt-get install portaudio19-dev
sudo apt-get install python3-dev
sudo apt-get install espeak  # For TTS

# Fedora
sudo dnf install python3-pyaudio portaudio-devel
```

## ⚙️ Configuration

### 1. Create Configuration Directory
```bash
mkdir config
mkdir logs
mkdir notes
```

### 2. Set Up API Keys

#### Method 1: Environment Variables
```bash
# Windows
set OPENWEATHER_API_KEY=your_api_key_here

# macOS/Linux
export OPENWEATHER_API_KEY=your_api_key_here
```

#### Method 2: Configuration File
Create `config/preferences.json`:
```json
{
    "name": "User",
    "city": "New York",
    "preferred_voice": 0,
    "speech_rate": 180,
    "volume": 0.8,
    "language": "en-US",
    "wake_words": ["hey ron", "ron", "assistant"]
}
```

### 3. Get API Keys

#### OpenWeather API (Free)
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Generate an API key
3. Add to environment variables or config file

## 🎯 Usage

### Starting Ron AI
```bash
python ron_ai.py
```

### Basic Interaction Flow
1. **Start the assistant**: Run the script
2. **Wait for initialization**: "Hello! I'm Ron, your AI assistant"
3. **Activate with wake word**: Say "Hey Ron" or "Ron"
4. **Give command**: Speak your command clearly
5. **Exit**: Say "Goodbye" or "Exit"

### Example Commands
```
You: "Hey Ron"
Ron: "Yes, how can I help you?"
You: "What's the weather today?"
Ron: "The weather in New York is partly cloudy with a temperature of 72°F..."

You: "Hey Ron"
Ron: "Yes, how can I help you?"
You: "Search for Python tutorials"
Ron: "I've opened search results for Python tutorials"

You: "Hey Ron"
Ron: "Yes, how can I help you?"
You: "Take a note: Buy groceries tomorrow"
Ron: "I've saved your note: Buy groceries tomorrow"
```

## 📁 Project Structure
```
ron-ai-assistant/
├── ron_ai.py              # Main assistant implementation
├── requirements.txt        # Python dependencies
├── README.md              # Documentation
├── config/                # Configuration files
│   ├── preferences.json   # User preferences
│   └── .secrets          # API keys (git-ignored)
├── logs/                  # Application logs
│   └── ron_ai.log        # Main log file
├── notes/                 # Saved notes
│   └── note_*.txt        # Individual note files
└── tests/                 # Unit tests
    └── test_ron.py       # Test suite
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Microphone Not Detected
```bash
# Test microphone
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

#### 2. PyAudio Installation Fails
- **Windows**: Use pre-compiled wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
- **macOS**: Install Xcode command line tools: `xcode-select --install`
- **Linux**: Install development headers: `sudo apt-get install python3-dev`

#### 3. Speech Recognition Issues
- Check internet connection
- Verify microphone permissions
- Reduce background noise
- Speak clearly and at normal pace

#### 4. TTS Voice Issues
```python
# List available voices
import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    print(f"ID: {voice.id}, Name: {voice.name}")
```

### Debug Mode
Enable detailed logging:
```python
# In ron_ai.py, change logging level
logger.setLevel(logging.DEBUG)
```

## 🚀 Advanced Features

### Custom Wake Words
Edit `config/preferences.json`:
```json
{
    "wake_words": ["jarvis", "computer", "assistant"]
}
```

### Adding Custom Commands
```python
# In CommandProcessor class
def _handle_custom(self, command: str):
    """Handle custom commands"""
    if "special task" in command:
        # Your custom logic here
        self.speech.speak("Executing special task")
```

### Integration with Smart Home
```python
# Example: Philips Hue integration
from phue import Bridge

def control_lights(self, command: str):
    bridge = Bridge('YOUR_BRIDGE_IP')
    if "lights on" in command:
        bridge.set_light('all', 'on', True)
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=ron_ai tests/
```

### Manual Testing Checklist
- [ ] Wake word detection
- [ ] Command recognition accuracy
- [ ] TTS clarity
- [ ] Error recovery
- [ ] API integrations
- [ ] File operations
- [ ] Multi-platform compatibility

## 📈 Performance Optimization

### Reduce Latency
1. Use local speech recognition when possible
2. Implement command caching
3. Optimize TTS settings
4. Use threading for non-blocking operations

### Memory Management
- Clear command history periodically
- Limit log file sizes with rotation
- Implement garbage collection for long-running sessions

## 🔐 Security Considerations

### Best Practices
1. **Never hardcode API keys** in source code
2. **Use environment variables** for sensitive data
3. **Validate user input** before system commands
4. **Implement rate limiting** for API calls
5. **Use HTTPS** for all external requests
6. **Regular security updates** for dependencies

### Privacy
- Voice data is processed locally when possible
- Online services are used only when necessary
- No personal data is stored without permission
- Logs can be disabled or cleared

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add unit tests for new features
- Update documentation
- Test on multiple platforms
- Handle errors gracefully

## 📝 License

This project is licensed under the GPL License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [SpeechRecognition](https://github.com/Uberi/speech_recognition) - Speech recognition library
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3) - Text-to-speech library
- [OpenWeatherMap](https://openweathermap.org/) - Weather API
- Community contributors and testers

## 📮 Support

### Get Help
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/ron-ai/issues)
  

### Roadmap
- [ ] GUI interface
- [ ] Mobile app support
- [ ] Cloud sync capabilities
- [ ] Multi-language support
- [ ] Advanced NLP with transformers
- [ ] Offline mode improvements
- [ ] Plugin system
- [ ] Voice customization
- [ ] Conversation context memory
- [ ] Machine learning for command prediction

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Made with ❤️ by the Ron AI Team**

*Last Updated: November 2024*
