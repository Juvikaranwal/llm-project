import sqlite3
import os
import crewai
from dataclasses import dataclass

class SharedContext:
    def __init__(self, db_path='conversation_history.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database and create table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table for storing messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_message(self, role, message):
        """Add a message to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (role, message)
            VALUES (?, ?)
        ''', (role, message))
        
        conn.commit()
        conn.close()

    def get_memory(self):
        """Retrieve all messages from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT role, message FROM messages ORDER BY timestamp')
        messages = cursor.fetchall()
        
        conn.close()
        
        return [{"role": role, "message": message} for role, message in messages]

    def display_memory(self):
        """Display all messages in the database"""
        messages = self.get_memory()
        
        print("\n=== Conversation History ===")
        if not messages:
            print("No conversation history.")
        else:
            for entry in messages:
                print(f"{entry['role']}: {entry['message']}")
        print("============================\n")

    def clear_memory(self):
        """Clear all messages from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM messages')
        
        conn.commit()
        conn.close()

    def get_latest_messages(self, limit=5):
        """Retrieve the latest messages from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, message 
            FROM messages 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        messages = cursor.fetchall()
        conn.close()
        
        return [{"role": role, "message": message} for role, message in reversed(messages)]


# Define the Agent Base Class for all other agents to inherit from
import crewai

# Define the Agent Base Class for all other agents to inherit from
class Agent:
    def __init__(self, name, role, shared_context):
        self.name = name
        self.role = role
        self.shared_context = shared_context  # Shared context to be accessed by all agents

    def display_shared_context(self):
        """Display the shared context that all agents use."""
        self.shared_context.display_memory()

class EditorAgent(Agent):
    def __init__(self, name, role, shared_context):
        super().__init__(name, role, shared_context)

    def initiate_conversation(self):
        # Editor asks questions and stores responses in shared context
        self.shared_context.add_message("Editor", "Hello, Dr. Stransky! Let's begin by discussing your ideas for the first chapter.")
        print("Editor: Hello, Dr. Stransky! Let's begin by discussing your ideas for the first chapter.")
        self.ask_open_ended_questions()

    def ask_open_ended_questions(self):
        questions = [
            "Can you share the outline of the chapter you want to write?",
            "What is the title of the chapter?",
            "What is the target length of the chapter?",
            "Do you have any specific instructions for the chapter?"
        ]
        
        for question in questions:
            print(f"Editor: {question}")
            author_input = input("Author: ")
            self.shared_context.add_message("Author", author_input)  # Store author's response
            self.shared_context.add_message("Editor", question)  # Store the question
            self.display_shared_context()  # Display memory after each input

        self.check_author_readiness()

    def check_author_readiness(self):
        print("Editor: Are you ready to begin the process of writing the chapter?")
        ready_response = input("Author: ")
        self.shared_context.add_message("Author", ready_response)  # Store readiness response

        if "yes" in ready_response.lower():
            print("Editor: Great! Let's begin the writing process!")
            self.proceed_with_writing()
        else:
            print("Editor: No problem. Let me know if you have more thoughts.")
            self.ask_open_ended_questions()

    def proceed_with_writing(self):
        print("\nSummary of our discussion:")
        self.display_shared_context()  # Display the entire conversation history

if __name__ == "__main__":
    # Initialize the shared context (this will be shared across all agents)
    shared_context = SharedContext()

    # Initialize the EditorAgent with the shared context
    role = "Editor"
    
    # Now let's start the conversation between the Editor and the Author
    editor = EditorAgent(name="Editor", role=role, shared_context=shared_context) 
    editor.initiate_conversation()
