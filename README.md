# Quest Narrative Designer

A web tool that generates structured, production-ready quests from high-level design briefs using a Large Language Model (LLM).

The app is built with **FastAPI** on the backend and vanilla **HTML/CSS/JS** on the frontend. It produces quests in a strict JSON structure suitable for game pipelines and allows you to regenerate specific sections (title, summary, individual steps) while keeping the rest of the quest intact.

## Features

- **Quest Generation**: Create complete quest structures from design briefs
- **LLM Integration**: Uses OpenAI API for intelligent quest design
- **Section Regeneration**: Update quest title, summary, or individual steps without regenerating the entire quest
- **JSON Schema Validation**: Ensures generated quests conform to the expected structure
- **Web Interface**: Simple, intuitive UI for quest creation and editing

## Requirements

- Python 3.8+
- OpenAI API key

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd quest-narrative-designer
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Copy the example environment file and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 6. Run the Application

```bash
uvicorn app.main:app --reload
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

## Project Structure

```
quest-narrative-designer/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and routes
│   ├── models.py            # Pydantic data models
│   ├── llm_client.py        # OpenAI API client
│   └── quest_generator.py   # Quest generation logic
├── static/
│   ├── index.html           # Frontend UI
│   ├── app.js               # Frontend JavaScript
│   └── style.css            # Frontend styling
├── .env.example             # Example environment variables
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## API Endpoints

### Generate Quest

**POST** `/api/generate-quest`

Request body:
```json
{
  "zone": "Swamp",
  "faction": "Explorers Guild",
  "tone": "dark and mysterious",
  "player_level_min": 10,
  "player_level_max": 15,
  "number_of_steps": 5
}
```

Response: Complete quest JSON object

### Regenerate Section

**POST** `/api/regenerate-section`

Request body:
```json
{
  "brief": { /* QuestDesignBrief object */ },
  "quest": { /* Quest object */ },
  "section": "title",
  "step_index": null
}
```

## Recent Updates

### OpenAI API Compatibility (v1.0.0+)
- Updated `llm_client.py` to use the new OpenAI Python SDK (v1.0.0 and later)
- Changed from the deprecated `openai.ChatCompletion.create()` to `client.chat.completions.create()`
- API key is now initialized using `OpenAI(api_key=api_key)` instead of setting `openai.api_key`
- Response handling updated to use object attributes instead of dictionary access

### Schema Validation Improvements
- Enhanced the quest schema description to explicitly clarify that NPC dialogue speaker fields must be exactly `"NPC"` or `"PLAYER"`
- Character names (e.g., "Jora", "Swamp Guardian") should appear in the dialogue text, not as speaker values
- Added emphasis in system prompts to prevent the LLM from using character names as speaker field values

## Development

### Running Tests

```bash
pytest
```

### Code Style

This project uses standard Python conventions. Please ensure code is formatted and follows PEP 8 guidelines.

## Troubleshooting

### `OPENAI_API_KEY not set`

Make sure you have:
1. Created a `.env` file from `.env.example`
2. Added your OpenAI API key to the `.env` file
3. The file is in the correct directory (root of the project)

### Quest validation errors

If you receive validation errors from the LLM response, check:
- The LLM is returning valid JSON
- The JSON structure matches the expected Quest schema
- The `speaker` field in dialogue is exactly `"NPC"` or `"PLAYER"`


## Support

For issues and questions, please open an issue on the GitHub repository.
