"""ESB/Integration Framework Smoke Test Prompt"""
ESB_PROMPT = """
SPECIALIZATION: Apache Camel/Mule ESB Smoke Tests
Detection: RouteBuilder, from(), to(), Camel context
Approach: Send test message through route, verify output
"""
def get_esb_prompt(): return ESB_PROMPT
