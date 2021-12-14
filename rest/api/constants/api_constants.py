from enum import Enum


class ApiCode(Enum):
    SUCCESS = 1000
    JINJA2_RENDER_FAILURE = 1001
    GET_EUREKA_APPS_FAILED = 1002
    GET_CONTAINER_ENV_VAR_FAILURE = 1003
    GET_COMMANDS_FAILED = 1004
    GET_DEPLOYMENTS_FAILED = 1005
    GET_TEST_RESULTS_FAILED = 1006
    HTTP_HEADER_NOT_PROVIDED = 1007
    DISCOVERY_ERROR = 1008
    UNAUTHORIZED = 1009
    TARGET_UNREACHABLE = 1010
    INVALID_JSON_PAYLOAD = 1011
    SET_ENV_VAR_FAILURE = 1012
