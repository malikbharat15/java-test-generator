"""
GraphQL API Smoke Test Prompt

Specializes in generating smoke tests for GraphQL APIs (Spring GraphQL, Netflix DGS).
"""

GRAPHQL_PROMPT = """
SPECIALIZATION: GraphQL API Smoke Tests
=======================================

TEST APPROACH:
- Send GraphQL queries/mutations to deployed GraphQL endpoint
- Verify endpoint responds (200 OK)
- Check for GraphQL errors in response
- Test introspection query (if enabled)

NEWMAN/POSTMAN APPROACH (Preferred):
- POST request to /graphql endpoint
- Content-Type: application/json
- Body: {"query": "{ __typename }", "variables": {}}
- Assert: response.data exists, no errors array

EXAMPLE QUERY TEST:
```json
{
  "name": "GraphQL Introspection Query",
  "request": {
    "method": "POST",
    "header": [{"key": "Content-Type", "value": "application/json"}],
    "body": {
      "mode": "raw",
      "raw": "{\\"query\\": \\"{ __typename }\\"}"
    },
    "url": "{{baseUrl}}/graphql"
  },
  "event": [{
    "listen": "test",
    "script": {
      "exec": [
        "pm.test('GraphQL endpoint responds', () => {",
        "  pm.response.to.have.status(200);",
        "});",
        "pm.test('No GraphQL errors', () => {",
        "  var jsonData = pm.response.json();",
        "  pm.expect(jsonData.errors).to.be.undefined;",
        "});"
      ]
    }
  }]
}
```

DETECTION:
- Look for @QueryMapping, @MutationMapping, @SchemaMapping annotations
- Check for graphql-java, spring-boot-starter-graphql dependencies
"""

def get_graphql_prompt():
    return GRAPHQL_PROMPT
