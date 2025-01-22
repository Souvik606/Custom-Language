# 🌐 **Browser-Based Custom Python Interpreter with Pyodide**

_This repository contains a Custom Programming Language Interpreter built with Python. The interpreter runs entirely in the browser using Pyodide, making it a serverless, lightweight, and portable solution. The front-end code editor is developed using Next.js, and it enables users to write, execute, and debug their code seamlessly._

## 🚀 Features
### 1. Custom Python Interpreter
- A fully modular Python interpreter implemented in interpreter.py.
- Supports code tokenization (lexer.py) and parsing (parser.py).
- Modular design makes it easy to extend and add custom logic.
### 2. Fully Serverless
-Powered by Pyodide, a WebAssembly-based Python runtime, eliminating the need for server-side processing.
-All Python code runs securely in the browser’s sandboxed environment.
### 3. Dynamic Module Loading
-Automatically fetch and load dependent Python modules like lexer.py and parser.py into the interpreter.
-Designed for modularity, allowing you to manage complex projects directly in the browser.
### 4. Real-Time Execution
-Input code, click "Run," and instantly see the output.
-Error handling and debugging are seamlessly integrated.
### 5. Extensible Design
-Add new features such as syntax highlighting, external libraries, or advanced interpreters.
### 6. User-Friendly Interface
-A clean and responsive web-based code editor built using React and Tailwind CSS.
-Editable code input area and a real-time output display for quick feedback.
