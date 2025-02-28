from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_ollama import ChatOllama
import math
import random

app = FastAPI(title="LangChain API with FastAPI & Ollama")

llm = ChatOllama(temperature=0, model="deepseek-r1:1.5b")

def web_search(query: str) -> str:
    """Search the web using DuckDuckGo."""
    from duckduckgo_search import DDGS
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
    return str(results[:3])

def calculate_square_root(number: str) -> str:
    """Calculates the square root of a number."""
    try:
        num = float(number)
        return f"The square root of {num} is {math.sqrt(num)}"
    except ValueError:
        return "Please provide a valid number."

def generate_joke(_: str) -> str:
    """Returns a random joke."""
    jokes = [
        "Why don’t scientists trust atoms? Because they make up everything!",
        "What do you get if you cross a snowman and a vampire? Frostbite!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!"
    ]
    return random.choice(jokes)

def mysql_lookup(query: str) -> str:
    """Executes a given SQL query on the database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="your_user",
            password="your_password",
            database="your_database"
        )
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        connection.close()
        return str(results)
    except Exception as e:
        return f"Error: {str(e)}"

MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
    '9': '----.', '0': '-----', ' ': ' / '
}
def text_to_morse(text: str) -> str:
    """Converts text to Morse code."""
    return ' '.join(MORSE_CODE_DICT.get(char.upper(), '?') for char in text)

tools = [
    Tool(name="Web Search", func=web_search, description="Search the web using DuckDuckGo."),
    Tool(name="Square Root Calculator", func=calculate_square_root, description="Calculates the square root of a number."),
    Tool(name="Random Joke Generator", func=generate_joke, description="Generates a random joke."),
    Tool(name="MySQL Lookup", func=mysql_lookup, description="Executes SQL queries in a MySQL database."),
    Tool(name="Morse Code Converter", func=text_to_morse, description="Converts text to Morse code."),
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def query_agent(request: QueryRequest):
    """Handles user queries and processes them using the LangChain agent."""
    try:
        response = agent.run(request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
