# AI Companion 🤖

AI Companion is a command-line interface tool that allows you to communicate with locally hosted Language Learning Models (LLMs) through LM Studio's API.

## Prerequisites 📋

- [LM Studio](https://lmstudio.ai/)
- Python 3.x
- Git

## Setup 🛠️

1. Clone the repository:
```bash
git clone https://github.com/JackScott7/ai-companion.git
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up LM Studio:
   - Install LM Studio from [https://lmstudio.ai/download](https://lmstudio.ai/download)
   - Download your preferred LLM Model from the Discover tab
   - Navigate to the Developer tab
   - Start the local server either by:
     - Pressing `Ctrl + R`
     - Clicking the "Start" button
   - Load your model using `Ctrl + L`

## Configuration ⚙️

You can customize the LLM's behavior and responses using the `jarvis_config.json` file. This configuration file allows you to modify various parameters:

- Model selection
- Temperature settings
- Behavior parameters
- Response characteristics

Adjust these settings to tailor the LLM's responses to your preferences.

## Usage 💬

The tool provides several ways to interact with your LLM:

### Basic Conversation (Stateless)
For a simple, non-persistent conversation:
```bash
jarvis.py -p "Hi there"
```

### Save Conversations
To save your chat history:
```bash
jarvis.py -p "Hello, Im Jack" --save-chat
```
Saved conversations are stored in the `/conversations` directory.

### Continue Previous Conversations
To continue a previous conversation using its UUID:
```bash
jarvis.py -p "lets continue on..." --save-chat -c {uuid of the chat conversation}
```

### Plain Text Output
To get responses in plain text instead of markdown:
```bash
jarvis.py -p "what is markdown" -md
```

### Verbose Mode
To see server and LLM status information:
```bash
jarvis.py -p "server stats?" -v
```

## Additional Information

- Conversations can be either stateless (default) or persistent (using `--save-chat`)
- Previous conversations can be referenced using their UUID
- The tool supports both markdown and plain text output formats
- Verbose mode provides additional debugging information

## Directory Structure 📂
```
ai-companion/
├── conversations/      # Stored chat histories
├── requirements.txt    # Python dependencies
├── jarvis.py           # Main script
├── companion.py        # Actual logic of the script
└── jarvis_config.json  # Configuration file
```

## License 📜
This project is licensed under the MIT License. ⭐ start it if you like it :)
