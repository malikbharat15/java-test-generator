"""WebSocket/STOMP Smoke Test Prompt"""
WEBSOCKET_PROMPT = """
SPECIALIZATION: WebSocket/STOMP Smoke Tests
Detection: @MessageMapping, @SubscribeMapping, WebSocket config
Approach: Connect to WebSocket endpoint, send message, verify response
"""
def get_websocket_prompt(): return WEBSOCKET_PROMPT
