# Agent System with LangGraph

This repository contains an implementation of a complex agent system using LangGraph and LangChain. The system is designed to handle complex problem-solving tasks through a network of specialized agents.

## Project Structure

```
.
├── src/
│   ├── agents/         # Individual agent implementations
│   ├── workflows/      # Agent workflow definitions
│   ├── tools/          # Custom tools for agents
│   ├── config/         # Configuration files
│   └── utils/          # Utility functions
├── tests/              # Test files
├── examples/           # Example usage and demos
└── notebooks/          # Jupyter notebooks for experimentation
```

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file and add your API keys:

```
OPENAI_API_KEY=your_key_here
```

## Usage

The project includes several components:

- Agent implementations for different tasks
- Workflow definitions using LangGraph
- Custom tools and utilities
- Example notebooks demonstrating usage

## Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License
