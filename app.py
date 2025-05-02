import gradio as gr
from search_engine import SearchEngine

engine = SearchEngine()

def ask(query):
    results = engine.search(query)
    return "\n\n".join([f"📄 {item['path']}" for item in results])

iface = gr.Interface(
    fn=ask,
    inputs=gr.Textbox(label="Ask about your files...", placeholder="e.g., 'Show me Python scripts'"),
    outputs=gr.Textbox(label="Results"),
    title="🦾 AI File Assistant"
)

if __name__ == "__main__":
    iface.launch()
