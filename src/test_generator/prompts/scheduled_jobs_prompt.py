"""Scheduled Jobs Smoke Test Prompt"""
SCHEDULED_JOBS_PROMPT = """
SPECIALIZATION: Scheduled Tasks Smoke Tests
Detection: @Scheduled annotation, cron expressions
Approach: Verify scheduled method can be invoked manually, check execution logs
Note: Don't wait for actual schedule, just verify method works
"""
def get_scheduled_jobs_prompt(): return SCHEDULED_JOBS_PROMPT
