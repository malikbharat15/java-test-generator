"""
Prompt Templates Module

Contains all specialized prompts for different Java application types.
Each prompt is optimized for generating production-grade smoke tests.
"""

from .base_prompt import BASE_SYSTEM_PROMPT, BASE_OUTPUT_FORMAT
from .rest_api_prompt import REST_API_PROMPT
from .graphql_prompt import GRAPHQL_PROMPT
from .grpc_prompt import GRPC_PROMPT
from .kafka_test_prompt import KAFKA_TEST_PROMPT
from .jms_prompt import JMS_PROMPT
from .scheduled_jobs_prompt import SCHEDULED_JOBS_PROMPT
from .reactive_prompt import REACTIVE_PROMPT
from .ui_test_prompt import UI_TEST_PROMPT
from .websocket_prompt import WEBSOCKET_PROMPT
from .soap_prompt import SOAP_PROMPT
from .batch_test_prompt import BATCH_TEST_PROMPT
from .cli_test_prompt import CLI_TEST_PROMPT
from .esb_prompt import ESB_PROMPT

__all__ = [
    'BASE_SYSTEM_PROMPT',
    'BASE_OUTPUT_FORMAT',
    'REST_API_PROMPT',
    'GRAPHQL_PROMPT',
    'GRPC_PROMPT',
    'KAFKA_TEST_PROMPT',
    'JMS_PROMPT',
    'SCHEDULED_JOBS_PROMPT',
    'REACTIVE_PROMPT',
    'UI_TEST_PROMPT',
    'WEBSOCKET_PROMPT',
    'SOAP_PROMPT',
    'BATCH_TEST_PROMPT',
    'CLI_TEST_PROMPT',
    'ESB_PROMPT'
]
