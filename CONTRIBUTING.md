# Contributing to Skill Aggregator

## Development Setup
```bash
git clone https://github.com/your-username/skill-aggregator.git
cd skill-aggregator
python3 -m venv .venv
source .venv/bin/activate
```

## Adding a New Skill
When you add a new skill to Hermes or Claude Code, the aggregator's index is automatically rebuilt on next invocation. To rebuild immediately:
```bash
python3 scripts/build_index.py
```

## Code Style
- Follow PEP 8
- Type hints on all public functions
- Docstrings in Google style
- Keep it simple — no unnecessary dependencies

## Testing
```bash
python3 -m pytest tests/
```

## Pull Request Process
1. Ensure index rebuilds correctly with your changes
2. Update README.md if adding new features
3. Add tests for new matching patterns
