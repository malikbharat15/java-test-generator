"""SOAP Web Service Smoke Test Prompt"""
SOAP_PROMPT = """
SPECIALIZATION: SOAP/WSDL Web Service Smoke Tests
Detection: @WebService, @SOAPBinding, JAX-WS imports
Approach: Invoke SOAP endpoint with SoapUI or generate SOAP client test
"""
def get_soap_prompt(): return SOAP_PROMPT
