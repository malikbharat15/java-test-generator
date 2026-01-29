"""Reactive/WebFlux Smoke Test Prompt"""
REACTIVE_PROMPT = """
SPECIALIZATION: Spring WebFlux Reactive API Smoke Tests
Detection: WebFlux, Mono/Flux return types, @RestController with reactive
Approach: Use WebTestClient or Newman/Postman (same as REST but async)
"""
def get_reactive_prompt(): return REACTIVE_PROMPT
