from rest.api.constants.api_constants import ApiCode


class ErrorMessage:
    HTTP_CODE = {
        ApiCode.SUCCESS.value: "Success",
        ApiCode.JINJA2_RENDER_FAILURE.value: "Jinja2 render failed",
        ApiCode.GET_EUREKA_APPS_FAILED.value: "Failed to get apps from Eureka server '%s'",
        ApiCode.GET_CONTAINER_ENV_VAR_FAILURE.value: "Failed to get env var '%s'",
        ApiCode.GET_COMMANDS_DETACHED_FAILED.value: "Failed to get the list of the commands running in background",
        ApiCode.GET_DEPLOYMENTS_FAILED.value: "Failed to get deployments list",
        ApiCode.GET_TEST_RESULTS_FAILED.value: "Failed rto get test results list",
        ApiCode.HTTP_HEADER_NOT_PROVIDED.value: "Http header value not provided.value: '%s'",
        ApiCode.DISCOVERY_ERROR.value: "Estuary discovery.value: error aggregating results",
        ApiCode.UNAUTHORIZED.value: "Unauthorized",
        ApiCode.TARGET_UNREACHABLE.value: "The requested target %s was unreachable",
        ApiCode.INVALID_JSON_PAYLOAD.value: "The payload '%s' is not JSON",
        ApiCode.SET_ENV_VAR_FAILURE.value: "Could not set env vars '%s'",
    }
