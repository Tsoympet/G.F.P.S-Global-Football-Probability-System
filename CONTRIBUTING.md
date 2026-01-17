# Contributing to G.F.P.S

Thank you for your interest in contributing to G.F.P.S – Global Football Probability System! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Community Discussions](#community-discussions)
- [Reporting Issues](#reporting-issues)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and collaborative environment. Please be kind and courteous to others.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/G.F.P.S-Global-Football-Probability-System.git`
3. Set up your development environment following the instructions in [README.md](README.md)
4. Create a new branch for your work: `git checkout -b feature/your-feature-name`

## How to Contribute

There are many ways to contribute to G.F.P.S:

- **Report bugs** - Help us identify and fix issues
- **Suggest features** - Share your ideas for improvements
- **Improve documentation** - Help make our docs better
- **Write code** - Submit bug fixes or new features
- **Answer questions** - Help other users in Discussions
- **Share your experience** - Show how you're using G.F.P.S

## Development Workflow

### Backend Development

1. Set up a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r backend/requirements-dev.txt
   ```

3. Run tests:
   ```bash
   pytest backend/tests/
   ```

4. Run the linter:
   ```bash
   pre-commit run --all-files
   ```

### Frontend Development

1. Navigate to the desktop client:
   ```bash
   cd GFPS/desktop
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run tests:
   ```bash
   npm test
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

## Community Discussions

We use **GitHub Discussions** for community engagement. This is the best place to:

- **Ask questions** - Get help from maintainers and the community
- **Share ideas** - Propose new features or improvements
- **Show and tell** - Share how you're using G.F.P.S
- **General discussions** - Talk about anything related to the project

### Discussion Categories

- **💡 Ideas** - Feature requests and enhancement proposals
- **❓ Q&A** - Ask and answer questions about usage and configuration
- **📢 Announcements** - Important updates and releases
- **🎯 Show and Tell** - Share your projects and use cases
- **💬 General** - Everything else related to G.F.P.S

Please use Discussions before opening an issue - it helps us keep the issue tracker focused on bugs and confirmed feature requests.

## Reporting Issues

Before creating an issue, please:

1. **Check existing issues** - Your issue may already be reported
2. **Use Discussions for questions** - Issues should be for bugs and confirmed features
3. **Search closed issues** - Your issue might already be solved

When creating an issue:

- Use a clear and descriptive title
- Provide detailed steps to reproduce (for bugs)
- Include your environment details (OS, G.F.P.S version, deployment method)
- Add screenshots or logs if relevant
- Mention if you're willing to submit a PR

## Pull Request Process

1. **Discuss first** - For large changes, open a Discussion or Issue first
2. **Keep changes focused** - One feature or fix per PR
3. **Follow style guidelines** - See below
4. **Write tests** - Add tests for new functionality
5. **Update documentation** - Update relevant docs in `docs/` or README
6. **Ensure CI passes** - All tests and checks must pass
7. **Write a clear PR description** - Explain what and why

### PR Checklist

- [ ] Code follows the project's style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated (if needed)
- [ ] No breaking changes (or clearly documented)
- [ ] Commits are clear and descriptive
- [ ] CI/CD checks pass

## Style Guidelines

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for function signatures
- Write docstrings for public functions and classes
- Maximum line length: 88 characters (Black formatter)
- Use meaningful variable and function names

Example:
```python
def calculate_expected_value(
    probability: float, 
    odds: float,
    stake: float = 1.0
) -> float:
    """
    Calculate expected value for a bet.
    
    Args:
        probability: Win probability (0-1)
        odds: Decimal odds
        stake: Bet stake amount
        
    Returns:
        Expected value in currency units
    """
    return (probability * odds * stake) - stake
```

### TypeScript/JavaScript (Frontend)

- Use TypeScript for type safety
- Follow the existing code style
- Use functional components with hooks (React)
- Use meaningful component and variable names
- Add comments for complex logic

### Documentation

- Use clear, concise language
- Include code examples where helpful
- Keep line length reasonable (80-100 characters)
- Use proper Markdown formatting
- Add links to related docs

### Commit Messages

- Use present tense: "Add feature" not "Added feature"
- Keep the first line under 50 characters
- Add detailed description if needed (after blank line)
- Reference issues: "Fixes #123" or "Relates to #456"

Examples:
```
Add Dixon-Coles model implementation

Implements the Dixon-Coles model for goal prediction with:
- Low-score correlation adjustment
- Team strength parameters
- Recent form weighting

Fixes #123
```

## Testing

- Write unit tests for new functions and classes
- Add integration tests for new features
- Ensure all tests pass before submitting PR
- Aim for good code coverage (but focus on meaningful tests)

### Running Tests

Backend:
```bash
pytest backend/tests/ -v
```

Frontend:
```bash
cd GFPS/desktop && npm test
```

## Documentation

When adding features or making changes:

- Update the main README.md if it affects setup or usage
- Add or update files in `docs/` for detailed documentation
- Update API documentation in `docs/API_REFERENCE.md` if needed
- Include inline code comments for complex logic

## Security

If you discover a security vulnerability, please **do not open a public issue**. Instead:

1. Email the maintainers privately
2. Include detailed information about the vulnerability
3. Allow time for a fix before public disclosure

See [docs/SECURITY.md](docs/SECURITY.md) for more information.

## Questions?

- **Documentation**: Check [README.md](README.md) and files in `docs/`
- **Questions**: Use [GitHub Discussions](../../discussions)
- **Bugs**: Open an [issue](../../issues)
- **Features**: Start a [Discussion](../../discussions) first

## License

By contributing to G.F.P.S, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to G.F.P.S! 🎉
