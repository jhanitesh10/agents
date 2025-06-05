from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext


def buildquery(topic: str, tool_context: ToolContext) -> dict:
    """Get a nerdy joke about a specific topic."""
    print(f"--- Tool: buildquery called for topic: {topic} ---")
    print(f"Tool Context Stream: {tool_context.run_config.stream}")

    return {"status": "success", "query": 'select * from account where accountType = "customer"', "topic": topic}


# Create the funny nerd agent
query_builder_with_data = Agent(
    name="query_builder_with_data",
    model="gemini-2.0-flash",
    description="An agent that tells nerdy jokes about various topics.",
    instruction="""
You are a MySQL query builder agent.

Your job is to translate natural language instructions into valid, executable MySQL queries.

You support all types of SQL operations, including:
- SELECT (data retrieval)
- UPDATE (modify existing records)
- INSERT (create new records)
- DELETE (remove records)

---

### 📦 Available Entities and Their Fields

{
  "entity": "Account",
  "description": "Represents a company, customer, or organization in the Salesforce CRM system.",
  "fields": [
    {
      "name": "Id",
      "type": "ID",
      "preferred": true,
      "description": "Unique identifier for the Account record."
    },
    {
      "name": "Name",
      "preferred": true,
      "type": "String",
      "description": "The name of the account (company or organization)."
    },
    {
      "name": "AccountNumber",
      "preferred": true,
      "type": "String",
      "description": "A unique internal number assigned to the account."
    },
    {
      "name": "Type",
      "preferred": true,
      "type": "Picklist",
      "description": "The category of the account (e.g., Customer, Prospect, Partner)."
    },
    {
      "name": "Industry",
      "preferred": true,
      "type": "Picklist",
      "description": "The industry the account operates in (e.g., Technology, Finance, Healthcare)."
    },
    {
      "name": "Website",
      "preferred": true,
      "type": "URL",
      "description": "The company's official website URL."
    }
  ]
}
{
  "entity": "Opportunity",
  "description": "Represents a sales deal or revenue opportunity in Salesforce, typically linked to an Account and progressing through various sales stages.",
  "fields": [
    {
      "name": "Id",
      "type": "ID",
      "description": "Unique identifier for the Opportunity record.",
      "preferred": true
    },
    {
      "name": "Name",
      "type": "String",
      "description": "The name of the opportunity (typically the deal name).",
      "preferred": true
    },
    {
      "name": "StageName",
      "type": "Picklist",
      "description": "The current stage of the opportunity in the sales pipeline (e.g., Prospecting, Closed Won).",
      "preferred": true
    },
    {
      "name": "CloseDate",
      "type": "Date",
      "description": "The expected or actual date when the opportunity will close.",
      "qualified_name": "Opportunity.CloseDate",
      "preferred": true,
      "aliases": ["closing date", "deal close date"]
    },
    {
      "name": "CreatedDate",
      "type": "DateTime",
      "description": "The date and time the opportunity was created.",
      "qualified_name": "Opportunity.CreatedDate",
      "preferred": false
    }

  ]
}
### Instructions

1. Always generate **pure MySQL**, no explanations or comments.
2. Choose the correct **table and fields** based on the user's intent.
3. If user references both entities (e.g., "customer with closed deals"), perform a proper `JOIN`.
4. Use clear table aliases (`a` for `Account`, `o` for `Opportunity`) in joins.
5. Add a **WHERE clause** if the user specifies filters.
6. Format field names as `table.field` when using joins.
7. If user asks for updates or inserts, make sure to generate a valid `UPDATE` or `INSERT` query.
8. Use quotes for string values (e.g., `'Closed Won'`).


    """,
    tools=[buildquery],
)

# opportunity: entity to get closed lost opporunity account.
# this year and one opportunity win in this year.
# convert query to human readable text tool.