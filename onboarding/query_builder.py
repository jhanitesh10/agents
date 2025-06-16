from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import logging
from datetime import datetime
from copilotkit.langchain import copilotkit_emit_state
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

# Base schema for common Salesforce objects
SALESFORCE_SCHEMA = {
    "Opportunity": {
        "standard_fields": [
            "Id", "Name", "AccountId", "Amount", "CloseDate",
            "CreatedBy.Name", "CreatedDate", "LastModifiedBy.Name",
            "LastModifiedDate", "StageName", "IsClosed"
        ],
        "common_filters": {
            "open_opportunities": "IsClosed = false",
            "closed_won": "StageName = 'Closed Won'",
            "closed_lost": "StageName = 'Closed Lost'"
        }
    },
    "Account": {
        "standard_fields": [
            "Id", "Name", "Type", "Industry", "BillingCity",
            "BillingState", "BillingCountry", "Phone", "Website"
        ]
    },
    "Contact": {
        "standard_fields": [
            "Id", "Name", "Email", "Phone", "Title",
            "Department", "AccountId", "CreatedDate"
        ]
    }
}

class QueryBuilderInput(BaseModel):
    query_description: str = Field(description="Natural language description of the query")
    state: Optional[Dict] = Field(description="State of the query builder")

async def buildQuery(query_description: str, state: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Converts natural language to SOQL query and executes it.

    Args:
        query_description (str): Natural language description of the query
        state (Optional[Dict]): State of the query builder

    Returns:
        Dict[str, Any]: Query and results
    """
    try:
        if state is None:
            state = {}

        logging.info(f"Building query for: {query_description}")

        config = RunnableConfig()
        await copilotkit_emit_state(config, state)

        # Create prompt for the LLM
        prompt = [
            {
                "role": "system",
                "content": """You are a SOQL query expert. Convert natural language to SOQL queries.
                Use the following schema as reference:
                {schema}

                Rules:
                1. Always include Id in the SELECT clause
                2. Use standard fields from the schema
                3. Add appropriate WHERE clauses based on the description
                4. Return only the SOQL query without any explanation
                """.format(schema=SALESFORCE_SCHEMA)
            },
            {
                "role": "user",
                "content": f"Convert this to SOQL: {query_description}"
            }
        ]

        # Generate SOQL query using LLM
        llm = ChatOpenAI(model='gpt-4', temperature=0)
        response = llm.invoke(prompt)
        soql_query = response.content.strip()

        # Store the generated query in state
        state.generated_query = soql_query
        await copilotkit_emit_state(config, state)

        # Execute the query using getQueryData tool
        state, query_results = await getQueryData(soql_query, state)

        # Combine all results
        final_results = {
            "query": soql_query,
            "results": query_results["results"],
            "timestamp": datetime.now().isoformat()
        }

        # Update state with final results
        state.final_results = final_results
        await copilotkit_emit_state(config, state)

        return state, final_results

    except Exception as e:
        logging.error(f"Error in buildQuery: {str(e)}")
        raise

class GetQueryDataInput(BaseModel):
    soql_query: str = Field(description="The SOQL query to execute")
    state: Optional[Dict] = Field(description="State of the query data")

@tool(
    "getQueryData",
    args_schema=GetQueryDataInput,
    return_direct=True,
    description="Execute a SOQL query and return mock data results."
)
async def getQueryData(soql_query: str, state: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Executes a SOQL query and returns mock data results.

    Args:
        soql_query (str): The SOQL query to execute
        state (Optional[Dict]): State of the query data

    Returns:
        Dict[str, Any]: Mock query results
    """
    try:
        if state is None:
            state = {}

        logging.info(f"Getting data for query: {soql_query}")

        config = RunnableConfig()
        await copilotkit_emit_state(config, state)

        # Mock data generation based on the query
        mock_data = {
            "Opportunity": [
                {
                    "Id": "0061a00000A1B2C3",
                    "Name": "Sample Opportunity 1",
                    "AccountId": "0011a00000X1Y2Z3",
                    "Amount": 50000,
                    "CloseDate": "2024-12-31",
                    "StageName": "Prospecting",
                    "IsClosed": False
                },
                {
                    "Id": "0061a00000D4E5F6",
                    "Name": "Sample Opportunity 2",
                    "AccountId": "0011a00000G7H8I9",
                    "Amount": 75000,
                    "CloseDate": "2024-11-30",
                    "StageName": "Closed Won",
                    "IsClosed": True
                }
            ],
            "Account": [
                {
                    "Id": "0011a00000X1Y2Z3",
                    "Name": "Acme Corporation",
                    "Type": "Customer",
                    "Industry": "Technology",
                    "BillingCity": "San Francisco",
                    "BillingState": "CA",
                    "BillingCountry": "USA",
                    "Phone": "555-0123",
                    "Website": "www.acme.com"
                },
                {
                    "Id": "0011a00000G7H8I9",
                    "Name": "Tech Solutions Inc",
                    "Type": "Customer",
                    "Industry": "Technology",
                    "BillingCity": "New York",
                    "BillingState": "NY",
                    "BillingCountry": "USA",
                    "Phone": "555-0456",
                    "Website": "www.techsolutions.com"
                }
            ],
            "Contact": [
                {
                    "Id": "0031a00000J1K2L3",
                    "Name": "John Doe",
                    "Email": "john.doe@acme.com",
                    "Phone": "555-0789",
                    "Title": "CEO",
                    "Department": "Executive",
                    "AccountId": "0011a00000X1Y2Z3"
                },
                {
                    "Id": "0031a00000M4N5O6",
                    "Name": "Jane Smith",
                    "Email": "jane.smith@techsolutions.com",
                    "Phone": "555-0123",
                    "Title": "CTO",
                    "Department": "Technology",
                    "AccountId": "0011a00000G7H8I9"
                }
            ]
        }

        # Determine which object is being queried
        object_type = None
        if "FROM Opportunity" in soql_query:
            object_type = "Opportunity"
        elif "FROM Account" in soql_query:
            object_type = "Account"
        elif "FROM Contact" in soql_query:
            object_type = "Contact"

        # Get mock data for the queried object
        results = mock_data.get(object_type, []) if object_type else []

        query_results = {
            "query": soql_query,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

        state.query_results = query_results
        await copilotkit_emit_state(config, state)

        return state, query_results

    except Exception as e:
        logging.error(f"Error in getQueryData: {str(e)}")
        raise

# Register the tools
tools = [
    buildQuery,
    getQueryData
]

# Create a QueryBuilder agent that can use both tools
class QueryBuilderAgent:
    def __init__(self):
        self.tools = [buildQuery, getQueryData]

    async def execute(self, query_description: str, state: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute a natural language query using the QueryBuilder tools.

        Args:
            query_description (str): Natural language description of the query
            state (Optional[Dict]): State of the query builder

        Returns:
            Dict[str, Any]: Query results containing both the generated query and data
        """
        try:
            if state is None:
                state = {}

            # Use buildQuery which will internally use getQueryData
            state, result = await buildQuery(query_description, state)

            # Verify we have both query and results
            if not result.get("query") or not result.get("results"):
                raise ValueError("Missing query or results in the response")

            return state, result

        except Exception as e:
            logging.error(f"Error in QueryBuilderAgent: {str(e)}")
            raise

# Example usage:
"""
agent = QueryBuilderAgent()
state, result = await agent.execute("Show me all accounts in California")
print(f"Generated SOQL: {result['query']}")
print(f"Query Results: {result['results']}")
"""
