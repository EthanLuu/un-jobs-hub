# Contributing to UNJobsHub

Thank you for your interest in contributing to UNJobsHub! 🎉

## 📋 Code of Conduct

Please be respectful and constructive in all interactions.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/un-jobs-hub.git`
3. Create a branch: `git checkout -b feature/amazing-feature`
4. Make your changes
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 🏗️ Development Setup

See [README.md](README.md#-quick-start) for detailed setup instructions.

```bash
# Install dependencies
make install

# Run development servers
make dev
```

## 🧪 Testing

Please ensure all tests pass before submitting a PR:

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm run test
```

## 📝 Commit Messages

Use clear and descriptive commit messages:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example: `feat: add job filtering by contract type`

## 🔍 Pull Request Guidelines

- Keep PRs focused on a single feature/fix
- Update documentation if needed
- Add tests for new features
- Ensure all tests pass
- Follow existing code style
- Reference related issues

## 🐛 Reporting Bugs

Open an issue with:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment details

## 💡 Suggesting Features

Open an issue with:
- Clear description of the feature
- Use case and benefits
- Possible implementation approach

## 📚 Documentation

Help improve our documentation:
- Fix typos and clarify explanations
- Add examples and use cases
- Update outdated information

## 🌐 Adding New Crawlers

To add a new UN organization crawler:

1. Create new spider in `backend/crawlers/`
2. Inherit from `BaseCrawler`
3. Implement `crawl_async()` method
4. Add to `celery_app.py`
5. Update documentation

Example:
```python
from crawlers.base_crawler import BaseCrawler

class NewOrgSpider(BaseCrawler):
    def __init__(self):
        super().__init__("NEW_ORG")
        
    async def crawl_async(self):
        # Implementation
        pass
```

## 🎨 UI/UX Contributions

- Follow existing design patterns
- Use Shadcn/UI components
- Maintain responsive design
- Test on multiple screen sizes

## ❓ Questions?

Feel free to open a discussion or reach out to maintainers.

Thank you for contributing! 🙏



