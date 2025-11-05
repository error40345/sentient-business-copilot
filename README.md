# AI Business Copilot

Professional AI-powered business planning assistant that helps entrepreneurs plan and launch their businesses from idea to execution.

## Features

- **ROMA Multi-Agent AI**: Recursive task decomposition with Atomizer → Planner → Executor → Aggregator pipeline
- **Market Research**: Automated web research and competitive analysis
- **Financial Projections**: Detailed cost breakdowns and revenue estimates with Calculator toolkit
- **Location-Specific Guidance**: Region-specific regulatory and legal requirements
- **Professional PDF Export**: Generate comprehensive business plans in PDF format
- **PostgreSQL Storage**: Execution tracking and observability data persistence

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-business-copilot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys:

Create a `.env` file in the project root or set environment variables:

```bash
# Required for AI analysis
FIREWORKS_API_KEY=your_fireworks_api_key

# Required for market research
SERPER_API_KEY=your_serper_api_key

# Optional for enhanced search ranking
JINA_API_KEY=your_jina_api_key

# Optional for additional LLM capabilities
OPENROUTER_API_KEY=your_openrouter_api_key
```

### Getting API Keys

- **Fireworks AI**: Sign up at [fireworks.ai](https://fireworks.ai/) for Llama 3.3 70B access
- **Serper**: Get your API key at [serper.dev](https://serper.dev/)
- **Jina AI**: Register at [jina.ai](https://jina.ai/) for semantic search
- **OpenRouter**: Optional - get a key at [openrouter.ai](https://openrouter.ai/)

## Usage

1. Start the application:
```bash
streamlit run app.py --server.port 5000
```

2. Open your browser and navigate to `http://localhost:5000`

3. Start planning your business by chatting with the AI assistant

4. Export your business plan as PDF when ready

## Architecture

Built on **ROMA** (Recursive Open Meta-Agent) framework from [sentient-agi/ROMA](https://github.com/sentient-agi/ROMA):

- **Atomizer**: Classifies tasks and decides decomposition strategy using Llama 3.3 70B
- **Planner**: Breaks complex business tasks into subtasks using Llama 3.3 70B
- **Executor**: Executes atomic tasks using Llama 3.3 70B with Calculator toolkit
- **Aggregator**: Synthesizes results from multiple subtasks using Llama 3.3 70B
- **Verifier**: Validates business plans and outputs using Llama 3.3 70B
- **PostgreSQL Storage**: Tracks execution history and observability data

## Technology Stack

- **Frontend**: Streamlit
- **AI Framework**: ROMA (Recursive Open Meta-Agent) from sentient-agi
- **AI Models**: Llama 3.3 70B (Fireworks AI) for all ROMA agents
- **Search**: Serper API, Jina AI Reranker
- **PDF Generation**: ReportLab
- **Data Storage**: PostgreSQL (execution tracking), JSON (business plans)

## Project Structure

```
ai-business-copilot/
├── agents/              # ROMA multi-agent system
│   └── roma_orchestrator.py   # ROMA-based orchestration
├── roma_dspy/          # ROMA framework core
│   ├── core/           # Engine, modules, observability
│   ├── config/         # Configuration management
│   └── tools/          # Toolkits for agents
├── config/             # ROMA configuration profiles
│   └── profiles/
│       └── business_copilot.yaml
├── services/           # External service integrations
│   ├── dobby_service.py
│   ├── opendeepsearch_service.py
│   └── pdf_generator.py
├── utils/              # Utility modules
│   ├── config.py
│   └── state_manager.py
├── data/               # Data persistence
├── .streamlit/         # Streamlit configuration
├── app.py              # Main application
└── pyproject.toml      # Python dependencies
```

## Configuration

Configure the application via `.streamlit/config.toml`:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
base = "light"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open an issue on the GitHub repository.

## Acknowledgments

- Built with Streamlit framework
- Powered by ROMA multi-agent architecture
- AI capabilities provided by Fireworks AI and OpenRouter
