# Auto Coder Project

This project implements an AI-powered code generation system using the DeepSeek v3 model through OpenRouter's API. It consists of two implementations: a single-iteration version and an iterative version with code improvement capabilities.

## ⚠️ IMPORTANT SECURITY WARNING

**This project executes AI-generated code on your machine. This can be potentially dangerous!**

- AI-generated code could contain harmful operations
- You can consider adding a code review step before code execution
- Use in an isolated environment (virtual machine) for maximum safety possibly

**Use at your own risk. The authors are not responsible for any damage caused by AI-generated code.**

## 🤖 Model Flexibility

While this project defaults to using **DeepSeek v3** through OpenRouter, it's designed to work with **any model available on OpenRouter**! You can easily switch models by changing the `MODEL` constant in either script:

```python
MODEL = "deepseek/deepseek-chat"  # Default
```

- Any other model supported by OpenRouter

The code generation, error fixing, and improvement capabilities will adapt to whatever model you choose!

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set environment variable:

```bash
export OPENROUTER_API_KEY="your_api_key_here"  # Linux/Mac
set OPENROUTER_API_KEY="your_api_key_here"     # Windows
```

## ❤️ Support & Get 400+ AI Projects

This is one of 400+ fascinating projects in my collection! [Support me on Patreon](https://www.patreon.com/c/echohive42/membership) to get:

- 🎯 Access to 400+ AI projects (and growing daily!)
  - Including advanced projects like [2 Agent Real-time voice template with turn taking](https://www.patreon.com/posts/2-agent-real-you-118330397)
- 📥 Full source code & detailed explanations
- 📚 1000x Cursor Course
- 🎓 Live coding sessions & AMAs
- 💬 1-on-1 consultations (higher tiers)
- 🎁 Exclusive discounts on AI tools & platforms (up to $180 value)

## 1. Single Iteration Auto Coder (`1_auto_coder_single_iteration.py`)

A basic implementation that generates code once based on a user prompt.

### Features:

- Takes user input as a constant variable (`USER_PROMPT`)
- Uses DeepSeek model for code generation
- Streams model responses in real-time
- Extracts code from between `<code>` and `</code>` tags
- Saves generated code to files in the `generated_code` directory

### Usage:

1. Set your desired prompt in the `USER_PROMPT` constant
2. Run the script:

```bash
python 1_auto_coder_single_iteration.py
```

## 2. Iterative Auto Coder (`2_auto_coder_iterative.py`)

An advanced implementation that iteratively improves generated code through execution feedback.

### Features:

- All features from the single iteration version, plus:
- Executes generated code with a 5-second timeout
- Provides execution feedback to the model
- Uses separate API calls for:
  - Initial code generation
  - Error fixing
  - Code improvements
- Saves each iteration as numbered files (e.g., `generated_code_1.py`, `generated_code_2.py`)
- Maximum 5 iterations for improvements
- Handles timeouts gracefully (not treated as errors)

### Execution Flow:

1. Generate initial code
2. Execute the code
3. Based on execution result:
   - If timeout: Attempt to improve efficiency
   - If errors: Make fresh API call to fix errors
   - If success: Make fresh API call to add features
4. Save new iteration
5. Repeat until:
   - Max iterations reached
   - No more improvements needed
   - Error can't be fixed

### Usage:

1. Set your desired prompt in the `USER_PROMPT` constant
2. Run the script:

```bash
python 2_auto_coder_iterative.py
```

## System Prompts

The iterative version uses three distinct system prompts:

1. `SYSTEM_PROMPT_GENERATE`: For initial code generation
2. `SYSTEM_PROMPT_FIX`: For fixing errors (fresh context)
3. `SYSTEM_PROMPT_IMPROVE`: For adding features (fresh context)

## Output Directory Structure

```
generated_code/
├── generated_code_1.py  # Initial generation
├── generated_code_2.py  # First improvement/fix
├── generated_code_3.py  # Second improvement/fix
└── ...
```

## Error Handling

Both versions include comprehensive error handling:

- API call errors
- Code extraction errors
- File saving errors
- Code execution errors (iterative version)
- Timeout handling (iterative version)

## Terminal Output

Both versions provide colored terminal output using `termcolor`:

- Cyan: Informational messages
- Yellow: Processing status
- Green: Success messages
- Red: Error messages

## Limitations

1. 5-second execution timeout
2. Maximum 5 improvement iterations
3. No persistent context between API calls
4. Code must be complete and self-contained
5. Generated code must be valid Python

## Dependencies

- `openai`: For API communication
- `termcolor`: For colored terminal output
- Python standard library modules:
  - `os`
  - `subprocess` (iterative version)
  - `time` (iterative version)
