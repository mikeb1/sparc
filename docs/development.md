# Development Guidelines

## Coding Conventions
We follow the SPARC CLI conventions as outlined in [CONVENTIONS.md](../configuration/CONVENTIONS.md), which includes:
- Command-line interface patterns
- Task message formatting
- Context inclusion guidelines
- Provider/model selection

Additional coding standards:
- PEP 8 style guide for Python code
- Clear variable and function naming
- Consistent code formatting
- Error handling patterns

## Git Workflow
1. Create feature branch from main
   ```bash
   git checkout -b feature/my-feature
   ```
2. Make changes and commit with descriptive messages
3. Push branch and create PR
4. Get code review approval
5. Merge to main

## Code Review Checklist
- [ ] Documentation complete and up-to-date
- [ ] Unit tests added/updated
- [ ] Error handling implemented
- [ ] Security considerations addressed
- [ ] Performance impact assessed
- [ ] Code follows CLI conventions
- [ ] No hardcoded secrets/credentials
- [ ] Logging added appropriately

## Testing Requirements
- Unit tests required for all new code
- Integration tests for API endpoints
- Performance tests for critical paths
- Security tests for sensitive features
- Test coverage targets met

## Documentation Standards
- Docstrings for all public functions/classes
- Inline comments for complex logic
- README updates for new features
- API documentation kept current
- Architecture decisions documented

## Development Environment Setup
1. Python Requirements
   - Python 3.8+
   - pip and virtualenv
   - Install dependencies: `pip install -r requirements.txt`

2. Node.js Requirements (UI)
   - Node.js 16+
   - npm or yarn
   - Install dependencies: `npm install`

3. Development Tools
   - VS Code or PyCharm recommended
   - Black code formatter
   - pylint/flake8 linters
   - pre-commit hooks

4. Environment Variables
   ```bash
   export DEBUG=1
   export API_KEY=xxx
   ```
