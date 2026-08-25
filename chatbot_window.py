import tkinter as tk
from google import genai
from google.genai import types
from pypdf import PdfReader

import os
import re
import datetime
import ast
import operator
import webbrowser


# ==================================================
# GEMINI API SETUP
# ==================================================

API_KEY = "YOUR API KEY"

client = genai.Client(
    api_key=API_KEY
)

MODEL_NAME = "gemini-3.6-flash"


# ==================================================
# PDF KNOWLEDGE BASE
# ==================================================

PDF_FILE = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)
    ),
    "knowledge.pdf"
)


def load_pdf():

    if not os.path.exists(PDF_FILE):
        return "Knowledge PDF not found."

    try:

        reader = PdfReader(PDF_FILE)

        all_text = ""

        for page in reader.pages:

            text = page.extract_text()

            if text:
                all_text += text + "\n"

        return all_text

    except Exception as e:

        return "Error reading PDF: " + str(e)


# Load PDF
knowledge_text = load_pdf()


# ==================================================
# SPLIT PDF INTO CHUNKS
# ==================================================

def create_chunks(
    text,
    chunk_size=1500
):

    words = text.split()

    chunks = []

    current_chunk = []

    current_length = 0

    for word in words:

        current_chunk.append(word)

        current_length += len(word)

        if current_length >= chunk_size:

            chunks.append(
                " ".join(current_chunk)
            )

            current_chunk = []

            current_length = 0

    if current_chunk:

        chunks.append(
            " ".join(current_chunk)
        )

    return chunks


knowledge_chunks = create_chunks(
    knowledge_text
)


# ==================================================
# SEARCH PDF KNOWLEDGE
# ==================================================

def search_knowledge(question):

    question_words = set(
        re.findall(
            r"\b[a-zA-Z0-9]+\b",
            question.lower()
        )
    )

    scored_chunks = []

    for chunk in knowledge_chunks:

        chunk_words = set(
            re.findall(
                r"\b[a-zA-Z0-9]+\b",
                chunk.lower()
            )
        )

        score = len(
            question_words.intersection(
                chunk_words
            )
        )

        scored_chunks.append(
            (score, chunk)
        )

    scored_chunks.sort(
        key=lambda x: x[0],
        reverse=True
    )

    best_chunks = [
        chunk
        for score, chunk in scored_chunks[:3]
        if score > 0
    ]

    return "\n\n".join(
        best_chunks
    )


# ==================================================
# 🕐 SYSTEM TIME TOOL
# ==================================================

def get_system_time():

    now = datetime.datetime.now()

    return (
        "🕐 Current system date: "
        + now.strftime("%d-%m-%Y")
        + "\n"
        "Current system time: "
        + now.strftime("%I:%M:%S %p")
    )


# ==================================================
# 🧮 CALCULATOR TOOL
# ==================================================

def calculate(expression):

    try:

        allowed_operators = {

            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.USub: operator.neg
        }


        def solve(node):

            if isinstance(
                node,
                ast.Constant
            ):

                if isinstance(
                    node.value,
                    (int, float)
                ):

                    return node.value

                raise ValueError(
                    "Invalid number"
                )


            if isinstance(
                node,
                ast.BinOp
            ):

                left = solve(
                    node.left
                )

                right = solve(
                    node.right
                )

                operation = (
                    allowed_operators.get(
                        type(node.op)
                    )
                )

                if operation is None:

                    raise ValueError(
                        "Operator not allowed"
                    )

                return operation(
                    left,
                    right
                )


            if isinstance(
                node,
                ast.UnaryOp
            ):

                value = solve(
                    node.operand
                )

                operation = (
                    allowed_operators.get(
                        type(node.op)
                    )
                )

                if operation is None:

                    raise ValueError(
                        "Operator not allowed"
                    )

                return operation(
                    value
                )


            raise ValueError(
                "Invalid calculation"
            )


        expression = expression.replace(
            "^",
            "**"
        )

        tree = ast.parse(
            expression,
            mode="eval"
        )

        result = solve(
            tree.body
        )

        return f"🧮 Answer: {result}"


    except Exception:

        return (
            "❌ I couldn't calculate that.\n"
            "Please enter a simple mathematical expression."
        )


# ==================================================
# LOCAL TOOL DETECTION
# ==================================================

def use_local_tool(user_message):

    text = (
        user_message
        .lower()
        .strip()
    )


    # ==================================================
    # TIME
    # ==================================================

    time_words = [

        "what time",

        "current time",

        "time now",

        "time is it",

        "what's the time",

        "whats the time",

        "today's date",

        "todays date",

        "current date",

        "what date is it"
    ]


    if any(
        word in text
        for word in time_words
    ):

        return get_system_time()


    # ==================================================
    # CALCULATOR
    # ==================================================

    calculator_words = [

        "calculate",

        "solve",

        "how much is",

        "what is"
    ]


    math_symbols = [

        "+",
        "-",
        "*",
        "/",
        "%",
        "^"
    ]


    contains_number = any(
        char.isdigit()
        for char in text
    )


    contains_math_symbol = any(
        symbol in text
        for symbol in math_symbols
    )


    looks_like_math = (

        (
            any(
                word in text
                for word in calculator_words
            )

            and contains_number
        )

        or

        (
            contains_math_symbol
            and contains_number
        )
    )


    if looks_like_math:

        expression = text

        for word in [

            "calculate",

            "solve",

            "how much is",

            "what is"
        ]:

            expression = expression.replace(
                word,
                ""
            )

        expression = (
            expression
            .replace("?", "")
            .strip()
        )

        return calculate(
            expression
        )


    return None


# ==================================================
# 🌐 GOOGLE SEARCH TOOL
# ==================================================

def google_search_answer(user_message):

    try:

        # ------------------------------------------
        # Enable native Google Search grounding
        # ------------------------------------------

        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )


        config = types.GenerateContentConfig(
            tools=[
                grounding_tool
            ]
        )


        # ------------------------------------------
        # Send question to Gemini
        # ------------------------------------------

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=user_message,

            config=config
        )


        answer = response.text

        sources = []


        # ------------------------------------------
        # Extract grounding metadata
        # ------------------------------------------

        if response.candidates:

            candidate = response.candidates[0]

            metadata = (
                getattr(
                    candidate,
                    "grounding_metadata",
                    None
                )
            )


            if metadata:

                grounding_chunks = (
                    getattr(
                        metadata,
                        "grounding_chunks",
                        []
                    )
                )


                for chunk in grounding_chunks:

                    web_data = getattr(
                        chunk,
                        "web",
                        None
                    )

                    if web_data:

                        title = getattr(
                            web_data,
                            "title",
                            "Web Source"
                        )

                        url = getattr(
                            web_data,
                            "uri",
                            None
                        )


                        if url:

                            sources.append(
                                (
                                    title,
                                    url
                                )
                            )


        # ------------------------------------------
        # Remove duplicate sources
        # ------------------------------------------

        unique_sources = []

        seen_urls = set()

        for title, url in sources:

            if url not in seen_urls:

                unique_sources.append(
                    (
                        title,
                        url
                    )
                )

                seen_urls.add(url)


        # ------------------------------------------
        # Return answer + sources
        # ------------------------------------------

        return answer, unique_sources


    except Exception as e:

        return (
            "Oops 😅 Google Search encountered an error:\n"
            + str(e),
            []
        )


# ==================================================
# DETERMINE WHETHER WEB SEARCH IS NEEDED
# ==================================================

def needs_web_search(user_message):

    text = (
        user_message
        .lower()
        .strip()
    )


    # Questions that normally need live information

    live_keywords = [

        "today",

        "latest",

        "current",

        "recent",

        "news",

        "headlines",

        "right now",

        "this week",

        "this month",

        "yesterday",

        "tomorrow",

        "live",

        "score",

        "match",

        "sports",

        "stock",

        "share price",

        "weather",

        "trending",

        "breaking",

        "update",

        "updates"
    ]


    for keyword in live_keywords:

        if keyword in text:

            return True


    return False


# ==================================================
# GEMINI PDF RESPONSE
# ==================================================

def get_pdf_reply(user_message):

    relevant_knowledge = search_knowledge(
        user_message
    )


    if not relevant_knowledge:

        relevant_knowledge = (
            "No directly relevant information "
            "was found in the knowledge PDF."
        )


    prompt = f"""

You are Navya GPT, a friendly AI chatbot.

Answer the user's question using the knowledge
provided from the PDF.

IMPORTANT RULES:

1. Use the PDF information when relevant.

2. Do not invent facts that are not in the PDF
   when answering PDF-related questions.

3. If the information is not available in the PDF,
   clearly say so.

4. Explain information in simple language.

5. Be friendly and conversational.

6. Use emojis when appropriate.

KNOWLEDGE FROM PDF:
-------------------

{relevant_knowledge}

-------------------

USER QUESTION:

{user_message}

Answer naturally.
"""


    response = client.models.generate_content(

        model=MODEL_NAME,

        contents=prompt
    )


    return response.text


# ==================================================
# MAIN RESPONSE FUNCTION
# ==================================================

def get_reply(user_message):

    try:

        # ==================================================
        # 1. CHECK LOCAL TOOLS
        # ==================================================

        local_result = use_local_tool(
            user_message
        )


        if local_result:

            return local_result, []


        # ==================================================
        # 2. CHECK LIVE WEB SEARCH
        # ==================================================

        if needs_web_search(
            user_message
        ):

            return google_search_answer(
                user_message
            )


        # ==================================================
        # 3. USE PDF + GEMINI
        # ==================================================

        answer = get_pdf_reply(
            user_message
        )

        return answer, []


    except Exception as e:

        return (
            "Oops 😅 Something went wrong:\n"
            + str(e),
            []
        )


# ==================================================
# OPEN SOURCE IN BROWSER
# ==================================================

def open_source(url):

    webbrowser.open_new_tab(
        url
    )


# ==================================================
# CREATE CHATBOT WINDOW
# ==================================================

window = tk.Tk()

window.title(
    "Navya GPT"
)

window.geometry(
    "600x650"
)

window.configure(
    bg="#1e1e2e"
)


# ==================================================
# CONVERSATION DISPLAY
# ==================================================

chat_area = tk.Text(

    window,

    width=65,

    height=28,

    bg="#282a36",

    fg="#f8f8f2",

    font=("Consolas", 11),

    wrap="word",

    state="disabled"
)


chat_area.pack(

    padx=10,

    pady=10,

    fill="both",

    expand=True
)


# ==================================================
# ADD MESSAGE
# ==================================================

def add_line(text):

    chat_area.configure(
        state="normal"
    )

    chat_area.insert(

        tk.END,

        text + "\n\n"
    )

    chat_area.configure(
        state="disabled"
    )

    chat_area.see(
        tk.END
    )


# ==================================================
# ADD WEB SOURCES
# ==================================================

def add_sources(sources):

    if not sources:

        return


    chat_area.configure(
        state="normal"
    )


    chat_area.insert(
        tk.END,
        "🌐 Sources:\n"
    )


    for index, (
        title,
        url
    ) in enumerate(
        sources,
        start=1
    ):

        tag_name = (
            f"source_{id(url)}"
        )


        chat_area.insert(

            tk.END,

            f"[{index}] {title}\n",

            tag_name
        )


        chat_area.tag_config(

            tag_name,

            foreground="#8be9fd",

            underline=True
        )


        chat_area.tag_bind(

            tag_name,

            "<Button-1>",

            lambda event,
            link=url: open_source(link)
        )


    chat_area.insert(
        tk.END,
        "\n"
    )


    chat_area.configure(
        state="disabled"
    )

    chat_area.see(
        tk.END
    )


# ==================================================
# SEND MESSAGE
# ==================================================

def send_message(event=None):

    user_text = (
        entry.get()
        .strip()
    )


    if not user_text:

        return


    add_line(
        "You: "
        + user_text
    )


    entry.delete(
        0,
        tk.END
    )


    # ==================================================
    # EXIT
    # ==================================================

    if user_text.lower() == "bye":

        add_line(
            "ChatBot: Goodbye! 👋"
        )

        return


    # ==================================================
    # GET RESPONSE
    # ==================================================

    reply, sources = get_reply(
        user_text
    )


    # ==================================================
    # DISPLAY ANSWER
    # ==================================================

    add_line(
        "ChatBot: "
        + reply
    )


    # ==================================================
    # DISPLAY SOURCES
    # ==================================================

    add_sources(
        sources
    )


# ==================================================
# INPUT AREA
# ==================================================

bottom_frame = tk.Frame(

    window,

    bg="#1e1e2e"
)


bottom_frame.pack(

    padx=10,

    pady=(0, 10),

    fill="x"
)


# ==================================================
# TEXT INPUT
# ==================================================

entry = tk.Entry(

    bottom_frame,

    font=("Consolas", 11)
)


entry.pack(

    side="left",

    fill="x",

    expand=True,

    ipady=7
)


entry.bind(

    "<Return>",

    send_message
)


# ==================================================
# SEND BUTTON
# ==================================================

send_button = tk.Button(

    bottom_frame,

    text="Send",

    command=send_message,

    bg="#50fa7b",

    fg="#1e1e2e",

    font=(
        "Consolas",
        10,
        "bold"
    )
)


send_button.pack(

    side="right",

    padx=(6, 0)
)


# ==================================================
# WELCOME MESSAGE
# ==================================================

if (
    "Knowledge PDF not found"
    in knowledge_text
):

    welcome = (

        "ChatBot: Hi! 👋 "
        "I am Navya GPT.\n"

        "⚠️ I couldn't find "
        "knowledge.pdf."
    )

else:

    welcome = (

        "ChatBot: Hi! 👋 "
        "I am Navya GPT.\n"

        "📚 PDF knowledge loaded.\n"

        "🕐 System time available.\n"

        "🧮 Calculator available.\n"

        "🌐 Live Google Search available.\n\n"

        "Ask me anything!"
    )


add_line(
    welcome
)


# ==================================================
# START PROGRAM
# ==================================================

window.mainloop()
