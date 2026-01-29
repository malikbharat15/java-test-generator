"""Spring Batch Job Smoke Test Prompt"""
BATCH_TEST_PROMPT = """
SPECIALIZATION: Spring Batch Job Smoke Tests
Detection: @EnableBatchProcessing, Job, Step beans
Approach: Launch job with test parameters, verify completion status
"""
def get_batch_test_prompt(): return BATCH_TEST_PROMPT
