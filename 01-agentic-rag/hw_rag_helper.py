INSTRUCTIONS = '''
Your task is to answer questions from the course participants
based on the provided context.

Use the context to find relevant information and provide accurate
answers. If the answer is not found in the context,
respond with "I don't know."
'''

PROMPT_TEMPLATE = '''
QUESTION: {question}

CONTEXT:
{context}
'''.strip()


class RAGBase:

    def __init__(
        self,
        index,
        llm_client,
        instructions=INSTRUCTIONS,
        prompt_template=PROMPT_TEMPLATE,
        model='gpt-5.4-mini'
    ):
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.prompt_template = prompt_template
        self.model = model

    def search(self, query, num_results=5):
        # Modified for lesson schema: content is the only text field
        boost_dict = {'content': 1.0}
        filter_dict = {}  # No filter needed for lessons
        
        return self.index.search(
            query,
            num_results=num_results,
            boost_dict=boost_dict,
            filter_dict=filter_dict
        )

    def build_context(self, search_results):
        # Modified for lesson schema: using filename and content
        lines = []
        
        for doc in search_results:
            # Try different possible field names for the file name
            if 'filename' in doc:
                filename = doc['filename']
            elif 'name' in doc:
                filename = doc['name']
            elif 'path' in doc:
                filename = doc['path']
            else:
                filename = 'Unknown file'
                
            lines.append(f"From: {filename}")
            lines.append(doc['content'])
            lines.append('')
        
        return '\n'.join(lines).strip()

    def build_prompt(self, query, search_results):
        context = self.build_context(search_results)
        return self.prompt_template.format(
            question=query, context=context
        )

    def llm(self, prompt):
        input_messages = [
            {'role': 'developer', 'content': self.instructions},
            {'role': 'user', 'content': prompt}
        ]

        response = self.llm_client.responses.create(
            model=self.model,
            input=input_messages
        )

        # Return full response to access usage information
        return response

    def rag(self, query):
        search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)
        response = self.llm(prompt)
        
        # Extract answer and usage information
        answer = response.output_text
        usage = {
            'input_tokens': response.usage.input_tokens,
            'output_tokens': response.usage.output_tokens,
            'total_tokens': response.usage.total_tokens,
            'prompt_tokens': response.usage.input_tokens,  # Alias for clarity
        }
        
        return answer, usage