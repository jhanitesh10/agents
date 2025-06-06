from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
import random


def get_random_records(data: list, count: int) -> list:
    """Randomly select a specified number of records from the data."""
    if count > len(data):
        return data
    return random.sample(data, count)

def getDataFromQuery(query: str, tool_context: ToolContext) -> dict:
    """get data for specific query."""
    print(f"--- Tool: getDataFromQuery called for query: {query} ---")
    print(f"Tool Context Stream: {tool_context}")
    data = [                {
                    "Id": "0011X000003ABCDQ1",
                    "Name": "Acme Corporation",
                    "AccountNumber": "ACM-001",
                    "Type": "Customer",
                    "Industry": "Manufacturing",
                    "BillingCity": "Chicago",
                    "BillingState": "IL",
                    "Phone": "(312) 555-0142",
                    "Website": "https://www.acmecorp.com"
                },
                {
                    "Id": "0011X000003EFGHQ2",
                    "Name": "BrightTech Solutions",
                    "AccountNumber": "BTS-002",
                    "Type": "Customer",
                    "Industry": "Technology",
                    "BillingCity": "San Francisco",
                    "BillingState": "CA",
                    "Phone": "(415) 555-0199",
                    "Website": "https://www.brighttech.io"
                },
                {
                    "Id": "0011X000003IJKLQ3",
                    "Name": "GreenFields Inc.",
                    "AccountNumber": "GFI-003",
                    "Type": "Customer",
                    "Industry": "Agriculture",
                    "BillingCity": "Des Moines",
                    "BillingState": "IA",
                    "Phone": "(515) 555-0173",
                    "Website": "https://www.greenfieldsag.com"
                },
                {
                    "Id": "0011X000003MNOPQ4",
                    "Name": "UrbanEdge Realty",
                    "AccountNumber": "UER-004",
                    "Type": "Customer",
                    "Industry": "Real Estate",
                    "BillingCity": "Austin",
                    "BillingState": "TX",
                    "Phone": "(512) 555-0128",
                    "Website": "https://www.urbanedge.com"
                },
                {
                    "Id": "0011X000003QRSTQ5",
                    "Name": "MedCare Partners",
                    "AccountNumber": "MCP-005",
                    "Type": "Customer",
                    "Industry": "Healthcare",
                    "BillingCity": "Boston",
                    "BillingState": "MA",
                    "Phone": "(617) 555-0139",
                    "Website": "https://www.medcarepartners.org"
                },
                {
                    "Id": "0011X000003UVWXQ6",
                    "Name": "Nimbus Financial",
                    "AccountNumber": "NBF-006",
                    "Type": "Customer",
                    "Industry": "Finance",
                    "BillingCity": "New York",
                    "BillingState": "NY",
                    "Phone": "(212) 555-0183",
                    "Website": "https://www.nimbusfinance.com"
                },
                {
                    "Id": "0011X000003YZABQ7",
                    "Name": "Sunset Hospitality",
                    "AccountNumber": "SHO-007",
                    "Type": "Customer",
                    "Industry": "Hospitality",
                    "BillingCity": "Miami",
                    "BillingState": "FL",
                    "Phone": "(305) 555-0111",
                    "Website": "https://www.sunsethospitality.com"
                },
                {
                    "Id": "0011X000003CDEFQ8",
                    "Name": "Orion Retail Group",
                    "AccountNumber": "ORG-008",
                    "Type": "Customer",
                    "Industry": "Retail",
                    "BillingCity": "Seattle",
                    "BillingState": "WA",
                    "Phone": "(206) 555-0164",
                    "Website": "https://www.orionretail.com"
                },
                {
                    "Id": "0011X000003GHIJQ9",
                    "Name": "Peak Performance Gear",
                    "AccountNumber": "PPG-009",
                    "Type": "Customer",
                    "Industry": "Sports",
                    "BillingCity": "Denver",
                    "BillingState": "CO",
                    "Phone": "(720) 555-0192",
                    "Website": "https://www.peakgear.com"
                },
                {
                    "Id": "0011X000003KLMNQ0",
                    "Name": "TerraEnergy Solutions",
                    "AccountNumber": "TES-010",
                    "Type": "Customer",
                    "Industry": "Energy",
                    "BillingCity": "Houston",
                    "BillingState": "TX",
                    "Phone": "(713) 555-0155",
                    "Website": "https://www.terraenergy.com"
                }
]

    # If the query contains "random" or similar keywords, return random records
    if "random" in query.lower():
        count = 5  # Default to 5 records
        return {"status": "success", "data": get_random_records(data, count)}

    return {"status": "success", "data": data}

def buildquery(query: str, tool_context: ToolContext) -> dict:
    """geq data for specific  query."""
    print(f"--- Tool: buildquery called for query: {query} ---")
    print(f"Tool Context Stream: {tool_context}")

    return {"status": "success", "query": query, "data": getDataFromQuery(query, tool_context)["data"],             "expression": {
                "query": query,
                "expression": ""
            },}


# Create the funny nerd agent
query_builder_with_data = Agent(
    name="query_builder_with_data",
    model="gemini-2.0-flash",
    description="An agent that build query to get data.",
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

pass generated query to buildquery tool. make sure you are using buildquery to return the data. It should be in the same format as the data in the tool.
    """,
    tools=[buildquery],
)

# opportunity: entity to get closed lost opporunity account.
# this year and one opportunity win in this year.
# convert query to human readable text tool.