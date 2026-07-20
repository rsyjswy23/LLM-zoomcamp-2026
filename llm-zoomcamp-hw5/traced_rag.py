import os
from dotenv import load_dotenv
load_dotenv()

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from sqlite_exporter import SQLiteSpanExporter

from starter import RAGBase, index, client
from rag_helper import INSTRUCTIONS, PROMPT_TEMPLATE

# Setup OTel
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(SQLiteSpanExporter("traces.db")))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("llm-zoomcamp")

class RAGTraced(RAGBase):
    def search(self, query, num_results=5):
        with tracer.start_as_current_span("search") as span:
            span.set_attribute("query", query)
            return super().search(query, num_results)
    
    def llm(self, prompt):
        with tracer.start_as_current_span("llm") as span:
            span.set_attribute("prompt", prompt[:200])
            
            input_messages = [
                {'role': 'developer', 'content': self.instructions},
                {'role': 'user', 'content': prompt}
            ]
            
            response = self.llm_client.responses.create(
                model=self.model,
                input=input_messages
            )
            
            # Capture token usage
            usage = response.usage
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
            
            span.set_attribute("input_tokens", input_tokens)
            span.set_attribute("output_tokens", output_tokens)
            
            cost = (input_tokens * 0.15 / 1_000_000) + (output_tokens * 0.60 / 1_000_000)
            span.set_attribute("cost", cost)
            
            return response  # Return the full response object, not output_text
        
    def rag(self, query):
        with tracer.start_as_current_span("rag") as span:
            span.set_attribute("query", query)
            return super().rag(query)

# Create the traced RAG instance
rag = RAGTraced(
    index=index,
    llm_client=client,
    instructions=INSTRUCTIONS,
    prompt_template=PROMPT_TEMPLATE,
)

if __name__ == "__main__":
    query = "How does the agentic loop keep calling the model until it stops?"
    answer = rag.rag(query)
    print("\nAnswer:", answer[:100])