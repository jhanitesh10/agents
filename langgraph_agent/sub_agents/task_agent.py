from typing import Dict, List
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain.callbacks.manager import CallbackManager
from datetime import datetime

class TaskAgent:
    """A simple task-specific sub-agent."""

    def __init__(self, callback_manager: CallbackManager = None):
        """Initialize the task agent.

        Args:
            callback_manager: Optional callback manager for tracing
        """
        self.chat = ChatOpenAI(
            temperature=0,
            model="gpt-3.5-turbo",
            callback_manager=callback_manager,
            streaming=True
        )

        self.system_prompt = """You are a task-specific agent that helps with:
1. Task planning and breakdown
2. Progress tracking
3. Resource estimation
4. Status reporting

When given a task:
1. Break it down into smaller steps
2. Estimate time for each step
3. Track dependencies between steps
4. Provide clear status updates
"""

    def plan_task(self, task_description: str) -> Dict:
        """Plan a task by breaking it down into steps.

        Args:
            task_description: Description of the task to plan

        Returns:
            Dict containing task plan and metadata
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Plan this task: {task_description}")
        ]

        response = self.chat.invoke(messages)

        return {
            "task": task_description,
            "plan": response.content,
            "created_at": datetime.now().isoformat(),
            "status": "planned"
        }

    def estimate_task(self, task_plan: Dict) -> Dict:
        """Estimate time and resources for a task plan.

        Args:
            task_plan: The task plan to estimate

        Returns:
            Dict containing estimates
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""
                Provide time and resource estimates for this task plan:
                {task_plan['plan']}
            """)
        ]

        response = self.chat.invoke(messages)

        task_plan.update({
            "estimates": response.content,
            "estimated_at": datetime.now().isoformat(),
            "status": "estimated"
        })

        return task_plan

    def get_status(self, task_plan: Dict) -> Dict:
        """Get status report for a task plan.

        Args:
            task_plan: The task plan to report on

        Returns:
            Dict containing status report
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""
                Provide a status report for this task:
                Task: {task_plan['task']}
                Plan: {task_plan['plan']}
                Estimates: {task_plan.get('estimates', 'Not estimated')}
            """)
        ]

        response = self.chat.invoke(messages)

        return {
            **task_plan,
            "status_report": response.content,
            "reported_at": datetime.now().isoformat()
        }

    def execute_task(self, task_description: str) -> Dict:
        """Execute a complete task workflow.

        Args:
            task_description: Description of the task to execute

        Returns:
            Dict containing complete task execution details
        """
        # Step 1: Plan the task
        task_plan = self.plan_task(task_description)

        # Step 2: Estimate the task
        task_plan = self.estimate_task(task_plan)

        # Step 3: Get status report
        task_result = self.get_status(task_plan)

        return task_result