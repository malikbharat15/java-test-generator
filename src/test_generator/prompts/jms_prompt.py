"""JMS/ActiveMQ Smoke Test Prompt"""
JMS_PROMPT = """
SPECIALIZATION: JMS Message Consumer Smoke Tests
Detection: @JmsListener, spring-jms, activemq dependencies
Approach: Send test JMS message, verify consumer processes it
"""
def get_jms_prompt(): return JMS_PROMPT
