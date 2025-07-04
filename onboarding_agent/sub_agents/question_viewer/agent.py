from google.adk.agents import Agent
# SELECT Id, Name, Industry, BillingCity, BillingState
# FROM Account
# WHERE Id IN (
#     SELECT AccountId
#     FROM Opportunity
#     WHERE
#         StageName = 'Closed Won' AND
#         CloseDate = LAST_N_DAYS:365
# )

def get_questions_with_view() -> dict:
    """Retrieves current question with data preview and query suggestion."""
    print(f"--- Tool: get_questions_with_view called for ---")

    try:
    # confirmation: ''
        return {
            "status": "success",
            "question": "How do you identify your customer accounts?",
            "description": "This helps Boomerang understand how to determine which accounts in your CRM represent actual customers versus prospects, partners, or other entities",
            "expression": {
                "query": "SELECT Id, Name, AccountNumber, Type, Industry, BillingCity, BillingState, Phone, Website FROM Account WHERE Type = 'Customer'",
                "expression": "Account.Type = 'Customer'"
            },

            "data": [
                {
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
            ],
            "actions": [
                {
                    "text": "Accept Suggestion",
                    "value": "account.customerType",
                    "prompt": "Account type is customer",
                    "action": "accept_suggestion",
                    "meta": {
                        "id": "question_id"
                    }
                },
                {
                    "text": "Edit Suggestion",
                    "action": "edit_suggestion",
                    "meta": {
                        "id": "question_id"
                    }
                }
            ]
        }

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
    You are a helpful assistant that helps users get questions in specific workspace context. You have to call get_questions_with_view tool to get questions.

    Your ONLY job is to:
    1. Call the get_questions_with_view tool
    2. Return its response EXACTLY as received without any modifications
    3. Do not add, remove, or modify any fields in the response
    4. Do not format or restructure the response
    5. Do not add any additional text or commentary

    Simply pass through the raw response from get_questions_with_view.
    """,
    tools=[get_questions_with_view],
)