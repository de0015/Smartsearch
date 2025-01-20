# This is a test file using the DeepSeek API and Tavily agentic search tool to build a question based search solution. The tool will search for results and provide summaries of those results.
import tkinter as tk
from tkinter import scrolledtext
import requests
from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

# Load API keys from environment variables
DEEPSEEK_API_KEY = os.getenv("DeepSeek_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

#Create class for the search engine app
class SearchEngineApp:
    def __init__(self, master):
        self.master = master
        master.title("Dan's Search Engine")

        # Create GUI elements
        self.create_widgets()

#Let's get a GUI for the user

    def create_widgets(self):
        # Question Entry
        self.question_label = tk.Label(self.master, text="Enter your question:")
        self.question_label.pack(pady=5)
        
        self.question_entry = tk.Entry(self.master, width=70)
        self.question_entry.pack(pady=5)

        # Search Button
        self.search_button = tk.Button(self.master, text="Search", command=self.process_query)
        self.search_button.pack(pady=5)

        # Results Display
        self.results_text = scrolledtext.ScrolledText(self.master, width=80, height=20)
        self.results_text.pack(pady=10)

    def process_query(self):
        question = self.question_entry.get()
        if not question:
            return

        self.toggle_ui_state(False)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Searching... Please wait...\n")

#Steps involved in the tool
        try:
            # Step 1: Web search with Tavily
            search_results = self.web_search(question)
            
            # Step 2: Generate answer with DeepSeek
            answer = self.generate_answer(question, search_results)
            
            # Display results
            self.display_results(question, search_results, answer)
            
        except Exception as e:
            self.results_text.insert(tk.END, f"\nError: {str(e)}")
        finally:
            self.toggle_ui_state(True)

    def web_search(self, query):
        tavily = TavilyClient(api_key=TAVILY_API_KEY)
        response = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=5
        )
        return response

    def generate_answer(self, question, context):
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        system_prompt = """You are a helpful assistant that answers questions based on web search results. 
        Use the provided context to form your answer. Be comprehensive but concise."""
        
        user_content = f"Web search results:\n{context['results']}\n\nQuestion: {question}\nAnswer:"

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.7
        }

        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def display_results(self, question, search_data, answer):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Question: {question}\n\n")
        self.results_text.insert(tk.END, "AI Answer:\n")
        self.results_text.insert(tk.END, f"{answer}\n\n")
        self.results_text.insert(tk.END, "Web References:\n")
        
        for idx, result in enumerate(search_data['results'][:3], 1):
            self.results_text.insert(tk.END, f"{idx}. {result['title']}\n")
            self.results_text.insert(tk.END, f"   URL: {result['url']}\n\n")

    def toggle_ui_state(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.question_entry.config(state=state)
        self.search_button.config(state=state)

if __name__ == "__main__":
    root = tk.Tk()
    app = SearchEngineApp(root)
    root.mainloop()