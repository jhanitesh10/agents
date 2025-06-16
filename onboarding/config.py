from langchain_openai import ChatOpenAI

class Config:
    def __init__(self):
        self.FACTUAL_LLM = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            streaming=True
        )