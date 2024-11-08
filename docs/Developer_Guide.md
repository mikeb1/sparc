# Developer Guide

## Code Structure

- `cli/sparc_cli.py` - Main CLI implementation
- `architecture/` - Generated architecture files
- `src/` - Generated source code
- `tests/` - Generated test files

## Components

### SPARCConfig Class
Configuration dataclass with settings for:
- Core directories
- Development settings
- LiteLLM settings
- Git integration
- Testing configuration

### Architecture Generation
- `generate_sparc_content()` - Generates architecture documentation
- `_detect_tech_stack()` - Detects technology stack from project description
- `_generate_guidance_toml()` - Generates guidance configuration

### Main Functions
- `architect` mode - Generates architecture documentation
- `implement` mode - Generates implementation code
- Component generators for source and test code

### Implementation Components
- `AgentManager` - Manages swarm of AI agents
- `MonitoringService` - Handles system monitoring
- `StateManager` - Manages conversation state
- `CommunicationService` - Handles inter-agent communication

### Testing Strategy
- Unit tests for each service
- Integration tests for agent interactions
- Monitoring service tests
- State management tests

## Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Run tests
5. Submit pull request

## Testing

Run tests:
```bash
pytest tests/
```

## Git Integration

The CLI supports automatic Git integration:
- Repository initialization
- Automatic commits
- Dirty state handling
