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

        # Execute the query (placeholder for actual Salesforce API call)
        # In a real implementation, this would call the Salesforce API
        query_results = {
            "query": soql_query,
            "results": "Query execution results would go here",
            "timestamp": datetime.now().isoformat()
        }

        state.query_results = query_results
        await copilotkit_emit_state(config, state)

        return state, query_results

    except Exception as e:
        logging.error(f"Error in buildQuery: {str(e)}")
        raise

class ExecuteQueryInput(BaseModel):
    soql_query: str = Field(description="SOQL query to execute")
    state: Optional[Dict] = Field(description="State of the query execution")


async def executeQuery(soql_query: str, state: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Executes a SOQL query and returns results.

    Args:
        soql_query (str): SOQL query to execute
        state (Optional[Dict]): State of the query execution

    Returns:
        Dict[str, Any]: Query results
    """
    try:
        if state is None:
            state = {}

        logging.info(f"Executing query: {soql_query}")

        config = RunnableConfig()
        await copilotkit_emit_state(config, state)

        # Placeholder for actual Salesforce API call
        # In a real implementation, this would:
        # 1. Validate the SOQL query
        # 2. Call the Salesforce API
        # 3. Process and return the results
        results = {
            "query": soql_query,
            "results": "Query execution results would go here",
            "timestamp": datetime.now().isoformat()
        }

        state.query_results = results
        await copilotkit_emit_state(config, state)

        return state, results

    except Exception as e:
        logging.error(f"Error in executeQuery: {str(e)}")
        raise