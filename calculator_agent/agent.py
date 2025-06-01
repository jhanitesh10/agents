from google.adk.agents import Agent



root_agent = Agent(
  name="calculator_agent",
  model="gemini-2.0-flash",
  description="A calculator agent that can add two numbers.",
  instruction="You are a helpful assistant that can perform arithmetic operations like addition, subtraction, multiplication, and division. Ask user for two numbers and arithmetic operation. According to arithmetic operation, share the result with them",
)
