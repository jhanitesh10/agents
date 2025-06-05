from google.adk.agents import Agent


def get_questions_with_view(ticker: str) -> dict:
    """Retrieves current question with data preview and query suggestion."""
    print(f"--- Tool: get_questions_with_view called for {ticker} ---")

    try:

    # confirmation: ''
        return [{
            "status": "success",
            "question": "how do you identify customer account?",
            "expression": "select * from account where (accountType | type) = 'customer'",
            "dataPreview": [
                {"id": '1', "name": 'wework', "type": 'prospect', 'ownerId': '1', 'owner': 'Amit Dugar', 'cs_owner_c': 'Amit Dugar'},
                {"id": '2', "name": 'narvar', "type": 'customer', 'ownerId': '2', 'owner': 'Amit Dugar', 'cs_owner_c': 'Amit Dugar'},
                {"id": '3', "name": 'litera', "type": 'customer', 'ownerId': '3', 'owner': 'Amit Dugar', 'cs_owner_c': 'Amit Dugar'},
             ],
            "confirmation": [{'text': "Account type is customer", 'value': "account.customerType", 'prompt': 'Account type is customer'}],
        }]

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error fetching question data: {str(e)}",
        }


# Create the root agent
question_viewer = Agent(
    name="question_viewer",
    model="gemini-2.0-flash",
    description="An agent that can build a query to get list of question in specific workspace context.",
    instruction="""
    You are a helpful assistant that helps users build a query to get list of question in specific workspace context.

    When asked about question:
    1. Use the get_questions_with_view tool to fetch the latest question for the requested workspace(s)
    2. Format the response to show question,  expression and data preview and confirmation
    3. If a question couldn't be fetched, mention this in your response

    Example response format:
    "Here are the current question for your workspace:
    question: 'how do you identify customer account?',
    expression: 'select * from account where accountType = 'customer'',
    dataPreview: [
                {"id": '1', "name": 'wework', "type": 'prospect', 'ownerId': '1', 'owner': 'Amit Dugar', 'cs_owner_c': 'Amit Dugar'},
                {"id": '2', "name": 'narvar', "type": 'customer', 'ownerId': '2', 'owner': 'Amit Dugar', 'cs_owner_c': 'Amit Dugar'},
                {"id": '3', "name": 'litera', "type": 'customer', 'ownerId': '3', 'owner': 'Amit Dugar', 'cs_owner_c': 'Amit Dugar'},
    ]
    confirmation: [{text: ""}]
    """,
    tools=[get_questions_with_view],
)