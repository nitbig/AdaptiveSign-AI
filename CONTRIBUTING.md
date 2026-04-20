# 🤝 Contributing to ANNI

First off, thank you for considering contributing to ANNI! It's people like you that make ANNI such a great tool.

## 📋 Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). By participating, you are expected to uphold this code.

---

## 🚀 Getting Started

### **1. Fork the Repository**
Click the "Fork" button at the top right of the repository page.

### **2. Clone Your Fork**
```bash
git clone https://github.com/YOUR_USERNAME/ANNI.git
cd ANNI
```

### **3. Add Upstream Remote**
```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/ANNI.git
```

### **4. Create a Virtual Environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### **5. Install Development Dependencies**
```bash
pip install -r requirements.txt
pip install pytest black flake8 pylint
```

---

## 🔧 Development Workflow

### **1. Create a Feature Branch**
```bash
git checkout -b feature/your-feature-name
# or for bugfixes:
git checkout -b bugfix/issue-description
```

### **2. Make Your Changes**
- Write clean, readable code
- Follow Python PEP 8 style guide
- Add comments for complex logic
- Update docstrings

### **3. Format Code**
```bash
# Format with black
black .

# Check style with flake8
flake8 .

# Lint with pylint
pylint src/
```

### **4. Test Your Changes**
```bash
# Run tests
pytest

# Manual testing
python main.py
```

### **5. Commit Your Changes**
```bash
git add .
git commit -m "Add: descriptive message of changes"
```

**Commit Message Format:**
```
[Type]: Brief description

Detailed explanation of changes (if needed)

Fixes #123
```

**Types:** `Add`, `Fix`, `Improve`, `Refactor`, `Docs`, `Style`, `Test`

### **6. Push to Your Fork**
```bash
git push origin feature/your-feature-name
```

### **7. Create a Pull Request**
- Go to your fork on GitHub
- Click "New Pull Request"
- Select your branch
- Fill in the PR template
- Submit!

---

## 📝 Pull Request Guidelines

### **PR Title**
```
[Type] Brief description of changes
```
Example: `[Add] Hand gesture auto-save feature`

### **PR Description**
Include:
- ✅ What problem does this solve?
- ✅ What changes were made?
- ✅ How to test the changes?
- ✅ Any breaking changes?
- ✅ Screenshots/videos (if applicable)

### **PR Checklist**
```markdown
- [ ] Code follows PEP 8 style guide
- [ ] All tests pass locally
- [ ] New features have tests
- [ ] Documentation updated
- [ ] No unnecessary dependencies added
- [ ] Commit messages are clear
```

---

## 🐛 Bug Reports

### **Submit a Bug Report**
1. Check if the issue already exists
2. Use the bug report template
3. Include:
   - OS and Python version
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots/logs if applicable

### **Bug Report Template**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment**
- OS: [e.g., Windows 10]
- Python: [e.g., 3.9]
- ANNI version: [e.g., 1.0.0]

**Additional context**
Add any other context about the problem here.
```

---

## 💡 Feature Requests

### **Suggest an Enhancement**
1. Use a clear, descriptive title
2. Provide detailed description
3. List possible use cases
4. Include examples if applicable

### **Feature Request Template**
```markdown
**Is your feature request related to a problem?**
Description of the problem.

**Describe the solution you'd like**
Clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request.
```

---

## 📚 Coding Standards

### **Python Style Guide**
- Follow [PEP 8](https://pep8.org/)
- Use meaningful variable names
- Maximum line length: 100 characters
- Use type hints where applicable

### **Example:**
```python
def calculate_confidence(landmarks: List[float], threshold: float = 0.5) -> float:
    """
    Calculate confidence score from landmarks.
    
    Args:
        landmarks: List of landmark coordinates
        threshold: Confidence threshold
        
    Returns:
        float: Calculated confidence score
    """
    # Implementation here
    pass
```

### **Docstring Format**
```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Longer description if needed, explaining the function's
    behavior and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        bool: Description of return value
        
    Raises:
        ValueError: When invalid input provided
        
    Example:
        >>> result = my_function("test", 42)
        >>> result
        True
    """
    pass
```

---

## 🧪 Testing

### **Write Tests**
```python
import pytest
from src.gesture_recognizer import GestureRecognizer

class TestGestureRecognizer:
    def test_count_fingers_returns_list(self):
        recognizer = GestureRecognizer()
        result = recognizer.count_fingers([...])
        assert isinstance(result, list)
        assert len(result) == 5
        
    def test_invalid_landmarks(self):
        recognizer = GestureRecognizer()
        with pytest.raises(ValueError):
            recognizer.count_fingers([])
```

### **Run Tests**
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_gesture_recognizer.py

# Run with coverage
pytest --cov=src/
```

---

## 📦 Adding Dependencies

If you need to add a new dependency:

1. **Verify it's necessary** - Check if existing libraries can do it
2. **Minimal size** - Prefer smaller, focused libraries
3. **Active maintenance** - Choose well-maintained packages
4. **Update requirements.txt**:
   ```bash
   pip freeze > requirements.txt
   ```
5. **Document why** in the PR description

---

## 🔄 Keeping Your Fork Updated

### **Sync with Upstream**
```bash
# Fetch upstream changes
git fetch upstream

# Rebase on main
git rebase upstream/main

# Push to your fork
git push origin main
```

---

## 💬 Communication

- **GitHub Issues** - For bugs and features
- **GitHub Discussions** - For questions and ideas
- **Pull Requests** - For code reviews
- **Email** - For private concerns

---

## 🎓 Learning Resources

- [GitHub Guides](https://guides.github.com/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Real Python](https://realpython.com/)
- [MediaPipe Documentation](https://mediapipe.dev/)
- [OpenCV Tutorials](https://docs.opencv.org/master/d9/df8/tutorial_root.html)

---

## ✨ Recognition

Contributors will be recognized in:
- README.md (Contributors section)
- GitHub's Contributors page
- Release notes (if applicable)

---

## ❓ Questions?

Feel free to:
- Open a discussion on GitHub
- Check existing issues for answers
- Review the documentation

---

**Thank you for contributing to ANNI! 🚀**

*Happy coding! If you have any questions, feel free to reach out.*
