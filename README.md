# ChatBot 🤖

A simple rule-based chatbot built using Python. It provides an easy way to interact with a computer through predefined responses and basic conversation logic.

This project is designed as a beginner-friendly introduction to chatbot development and demonstrates how Python can be used to create a simple conversational application.

## Features

* Simple rule-based conversation system
* Responds to common greetings and questions
* Recognizes different user inputs using keywords
* Remembers basic information such as the user's name
* Provides different responses for better interaction
* Handles unknown inputs with a default response
* Easy-to-use terminal interface
* Simple and beginner-friendly Python code
* No API key or internet connection required

## Files

| File               | Description                                     |
| ------------------ | ----------------------------------------------- |
| `chatbot.py`       | Main Python file containing the chatbot logic   |
| `chatbot_gui.py`   | Graphical user interface version of the chatbot |
| `chatbot_logic.py` | Contains rules, keywords, and response handling |
| `README.md`        | Project documentation and instructions          |

## How to Run

### Requirements

* Python 3.10 or above
* Tkinter for the graphical interface

### Run the chatbot

**Terminal version:**

```bash
python chatbot.py
```

**GUI version:**

```bash
python chatbot_gui.py
```

## Example

```text
ChatBot: Hi! I am your ChatBot. What is your name?
You: Navya
ChatBot: Nice to meet you, Navya!

You: hello
ChatBot: Hello! How are you?

You: tell me a joke
ChatBot: Why did the programmer quit?
ChatBot: Because they didn't get enough bytes!

You: bye
ChatBot: Goodbye, Navya! Have a great day!
```

## How It Works

The chatbot takes the user's message as input and compares it with predefined keywords or patterns. Based on the detected input, it selects a suitable response from the available responses.

For example:

* If the user says **"hello"**, the chatbot gives a greeting.
* If the user asks for a **joke**, it provides a predefined joke.
* If the user says **"bye"**, the chatbot ends the conversation.
* If the input is not recognized, the chatbot gives a default response.

## About

This project is a beginner-level Python chatbot created to understand the basic concepts of conversational applications, conditional statements, functions, pattern matching, and GUI development.
