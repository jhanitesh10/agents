import os
import sys
from pathlib import Path

# Add the parent directory to Python path for proper imports
sys.path.append(str(Path(__file__).parent.parent))

from typing import TypedDict, Annotated, Sequence, Dict, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
import operator
from langsmith import Client
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager
from langchain.globals import set_debug
from datetime import datetime
from dotenv import load_dotenv
from langgraph_agent.db import StateManager
from langgraph_agent.sub_agents import TaskAgent

# Load environment variables
load_dotenv()

# Enable debug mode for better error messages
set_debug(True)

# Initialize LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

# Initialize LangSmith client and callback manager
client = Client()
tracer = LangChainTracer(project_name="basic_agent_demo")
callback_manager = CallbackManager([tracer])

# Initialize state manager and task agent
state_manager = StateManager()
task_agent = TaskAgent(callback_manager=callback_manager)

# Define our state
class AgentState(TypedDict):
    """State definition for the agent."""
    messages: Annotated[Sequence[BaseMessage], operator.add]  # Conversation history
    auth: Dict  # User authentication info
    session_metadata: Dict  # Session information
    error: str | None  # Error tracking
    task_state: Dict | None  # Added for task tracking

def get_system_prompt() -> str:
    """Get the system prompt for the agent."""
    return """You are a helpful AI assistant with task management capabilities. You should:
    1. Provide clear and concise responses
    2. If you don't know something, say so
    3. Keep track of the conversation context
    4. Be friendly and professional
    5. For task-related queries, use your task management capabilities

    When a user asks about tasks, projects, or planning:
    1. Use your task management system to break down and plan the work
    2. Provide estimates and track progress
    3. Give clear status updates
    """

def authenticate_user(username: str, password: str) -> Dict:
    """Authenticate a user.

    Args:
        username: The username to authenticate
        password: The password to verify

    Returns:
        Dict containing authentication result and user info
    """
    # In a real implementation, this would check against a secure database
    if username == "demo" and password == "password":
        return {
            "authenticated": True,
            "username": username,
            "role": "user",
            "timestamp": datetime.now().isoformat(),
            "permissions": ["basic_access"]
        }
    return {
        "authenticated": False,
        "error": "Invalid credentials"
    }

def is_task_request(message: str) -> bool:
    """Check if a message is a task-related request."""
    task_keywords = [
        "task", "plan", "project", "schedule", "estimate",
        "breakdown", "steps", "track", "progress", "status"
    ]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in task_keywords)

def agent_node(state: AgentState) -> Dict:
    """Process messages and generate responses.

    Args:
        state: Current agent state

    Returns:
        Dict containing state updates
    """
    try:
        # Get the last message
        last_message = state["messages"][-1]

        # Add message to state storage
        state_manager.add_message(
            role="user" if isinstance(last_message, HumanMessage) else "assistant",
            content=last_message.content
        )

        # Check if this is a task-related request
        if isinstance(last_message, HumanMessage) and is_task_request(last_message.content):
            # Use task agent to handle the request
            task_result = task_agent.execute_task(last_message.content)

            # Format the response
            response_content = f"""Task Analysis:

Plan:
{task_result['plan']}

Estimates:
{task_result['estimates']}

Status:
{task_result['status_report']}
"""

            # Update task state
            state["task_state"] = task_result

            response = AIMessage(content=response_content)
        else:
            # Get session messages for context
            session_messages = state_manager.get_session_messages()

            # Initialize ChatOpenAI with callbacks
            chat = ChatOpenAI(
                temperature=0,
                model="gpt-3.5-turbo",
                callback_manager=callback_manager,
                streaming=True
            )

            # Add context about session history and task state
            context = f"""Session Info:
            - Messages in current session: {len(session_messages)}
            - Current session active since: {state['session_metadata']['session_start']}
            """

            if state.get("task_state"):
                context += f"\nActive Task: {state['task_state']['task']}"

            # Generate response
            messages = [
                SystemMessage(content=get_system_prompt() + "\n\n" + context),
                *state["messages"]
            ]
            response = chat.invoke(messages)

        # Add assistant's response to state storage
        state_manager.add_message(
            role="assistant",
            content=response.content
        )

        return {
            "messages": [response],
            "error": None,
            "task_state": state.get("task_state")
        }

    except Exception as e:
        return {
            "messages": [AIMessage(content=f"I apologize, but I encountered an error. Please try again.")],
            "error": str(e),
            "task_state": state.get("task_state")
        }

def create_agent_graph() -> StateGraph:
    """Create and configure the agent graph.

    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize the graph
    workflow = StateGraph(AgentState)

    # Add our nodes
    workflow.add_node("agent", agent_node)

    # Set the entry point
    workflow.set_entry_point("agent")

    # Add an edge from agent to END
    workflow.add_edge("agent", END)

    return workflow.compile()

def run_agent(username: str, password: str, message: str) -> Dict:
    """Run the agent with SQL-based state management."""
    try:
        # Start a new session
        session_id = state_manager.start_session(
            username=username,
            metadata={
                "client_info": "web",
                "start_time": datetime.now().isoformat()
            }
        )

        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "auth": {
                "username": username,
                "timestamp": datetime.now().isoformat()
            },
            "session_metadata": {
                "session_id": session_id,
                "session_start": datetime.now().isoformat(),
                "client_info": "web"
            },
            "error": None,
            "task_state": None  # Initialize task state as None
        }

        # Create and run the agent
        agent = create_agent_graph()
        result = agent.invoke(initial_state)

        # End session if there was an error
        if result.get("error"):
            state_manager.end_session()

        return result

    except Exception as e:
        # Ensure session is ended on error
        state_manager.end_session()
        return {
            "error": str(e),
            "messages": [AIMessage(content="I apologize, but something went wrong. Please try again later.")],
            "task_state": None
        }

def get_conversation_history(username: str) -> List[Dict]:
    """Get conversation history from persistent state."""
    return state_manager.get_user_history(username)["conversations"]

def get_session_info() -> Dict:
    """Get current session information from temporary state."""
    return {
        "session_start": state_manager.get_session_start(),
        "current_messages": len(state_manager.get_session_messages()),
        "username": state_manager.get_username()
    }

def format_message(msg: BaseMessage) -> str:
    """Format a message for display.

    Args:
        msg: Message to format

    Returns:
        Formatted message string
    """
    if isinstance(msg, HumanMessage):
        return f"Human: {msg.content}"
    elif isinstance(msg, AIMessage):
        return f"Assistant: {msg.content}"
    elif isinstance(msg, SystemMessage):
        return f"System: {msg.content}"
    return f"Unknown: {msg.content}"

# Example usage
if __name__ == "__main__":
    try:
        username = "demo"

        # Run the agent
        result = run_agent(
            username=username,
            password="password",
            message="Can you help me plan a software development project for a new web application?"
        )

        # Print session info
        print("\nCurrent Session Info:")
        print("=" * 50)
        session_messages = state_manager.get_session_messages()
        print(f"Messages in Session: {len(session_messages)}")

        # Print task info if available
        if result.get("task_state"):
            print("\nTask Information:")
            print("=" * 50)
            task_state = result["task_state"]
            print(f"Task: {task_state['task']}")
            print(f"Status: {task_state['status']}")
            print(f"Created: {task_state['created_at']}")

        # Print conversation
        print("\nConversation:")
        print("=" * 50)
        for msg in session_messages:
            print(f"{msg['role'].title()}: {msg['content']}")
            print("-" * 50)

    except Exception as e:
        print(f"Critical error: {str(e)}")
    finally:
        # Always end the session
        state_manager.end_session()
