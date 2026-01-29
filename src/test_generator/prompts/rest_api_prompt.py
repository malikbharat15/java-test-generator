"""
REST API Smoke Test Prompt - Newman/Postman Priority

Specializes in generating Postman collections for REST API smoke testing.
This is the HIGHEST PRIORITY test type (90% of enterprise Java apps).
"""

REST_API_PROMPT = """
SPECIALIZATION: REST API Smoke Tests using Newman/Postman
=========================================================

TEST FRAMEWORK PRIORITY:
1. Newman/Postman Collection (PREFERRED - no build changes needed)
2. RestAssured + JUnit (if RestAssured already in dependencies)
3. Spring MockMvc (fallback if nothing else available)

FOR NEWMAN/POSTMAN (Recommended):
================================

GENERATE:
1. Postman Collection v2.1.0 JSON format
2. Postman Environment JSON with variables
3. Optional: GitHub Actions workflow for newman
4. Optional: README with run instructions

COLLECTION STRUCTURE:
- info.name: "{ApplicationName} Smoke Tests"
- info.schema: "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
- variable: baseUrl (from deployment route)
- item: Array of test requests

PER ENDPOINT TEST REQUIREMENTS:
- GET requests: 
  * Verify status code 200/401/403 (not 500)
  * Verify response time < 5000ms
  * Check Content-Type header
  * Optional: Basic response structure check

- POST requests:
  * Send minimal valid payload (infer from parameter names)
  * Verify status code 200/201/401 (not 500)
  * Verify response has expected structure
  * Use pm.collectionVariables for test data

- PUT/PATCH requests:
  * Use realistic path parameters
  * Send minimal valid payload
  * Verify status code 200/204/401

- DELETE requests:
  * Use test data ID (can be non-existent, 404 is acceptable)
  * Verify status code 200/204/404

POSTMAN TEST SCRIPTS (pm.test):
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response time is less than 5000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(5000);
});

pm.test("Content-Type is application/json", function () {
    pm.response.to.have.header("Content-Type");
    pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json");
});

pm.test("Response is valid JSON", function () {
    pm.response.to.be.json;
});
```

PATH PARAMETER HANDLING:
- {id} → Use "12345" or "{{testOrderId}}" variable
- {customerId} → Use "{{testCustomerId}}"
- {orderId} → Use "{{testOrderId}}"
- Store IDs in environment variables for reuse

REQUEST BODY GENERATION:
- Infer structure from @RequestBody parameter name
- If parameter is "Order" → Generate minimal Order JSON
- Use realistic but simple test data:
  * Strings: "test_value", "smoke_test_{field}"
  * Numbers: 123, 99.99
  * Booleans: true/false
  * Arrays: Single item []
  * Objects: Minimal required fields only

ENVIRONMENT FILE:
```json
{
  "name": "{ApplicationName} DEV Environment",
  "values": [
    {
      "key": "baseUrl",
      "value": "{ACTUAL_OCP_ROUTE_FROM_DEPLOYMENT_CONFIG}",
      "enabled": true
    },
    {
      "key": "testOrderId",
      "value": "12345",
      "enabled": true
    }
  ]
}
```

EXAMPLE POSTMAN COLLECTION:
```json
{
  "info": {
    "name": "Order Service Smoke Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get All Orders",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/orders",
          "host": ["{{baseUrl}}"],
          "path": ["orders"]
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status code is 200', function () {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test('Response time < 5s', function () {",
              "    pm.expect(pm.response.responseTime).to.be.below(5000);",
              "});",
              "",
              "pm.test('Response is JSON', function () {",
              "    pm.response.to.be.json;",
              "});"
            ],
            "type": "text/javascript"
          }
        }
      ]
    },
    {
      "name": "Create Order (Smoke Test)",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\\n  \\"customerId\\": \\"{{testCustomerId}}\\",\\n  \\"items\\": [],\\n  \\"total\\": 0.0\\n}"
        },
        "url": {
          "raw": "{{baseUrl}}/orders",
          "host": ["{{baseUrl}}"],
          "path": ["orders"]
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status code is 200 or 201', function () {",
              "    pm.expect(pm.response.code).to.be.oneOf([200, 201, 401]);",
              "});",
              "",
              "if (pm.response.code === 201) {",
              "    pm.test('Response has orderId', function () {",
              "        var jsonData = pm.response.json();",
              "        pm.expect(jsonData).to.have.property('orderId');",
              "    });",
              "}"
            ],
            "type": "text/javascript"
          }
        }
      ]
    }
  ]
}
```

NEWMAN EXECUTION:
- Include instructions: `newman run collection.json -e environment.json`
- Optional GitHub Actions workflow for CI/CD
- Exit code 0 if all tests pass, non-zero if any fail

ADVANTAGES OF NEWMAN/POSTMAN:
✅ No pom.xml modifications needed
✅ No Java compilation required
✅ Easy to run in CI/CD (newman CLI)
✅ Human-readable JSON format
✅ Can be imported into Postman for manual testing
✅ Language-agnostic (works for any REST API)
"""

def get_rest_api_prompt():
    """Return REST API specialized prompt"""
    return REST_API_PROMPT
