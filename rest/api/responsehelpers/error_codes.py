from rest.api.constants.api_constants import ApiConstants


class ErrorCodes:
    HTTP_CODE = {
        ApiConstants.SUCCESS: "Success",
        ApiConstants.JINJA2_RENDER_FAILURE: "jinja2 render failed",
        ApiConstants.GET_EUREKA_APPS_FAILED: "Failed to get apps from Eureka server '%s'",
        ApiConstants.GET_CONTAINER_ENV_VAR_FAILURE: "Failed to get env var '%s'",
        ApiConstants.GET_TESTS_FAILED: "Failed to get tests list",
        ApiConstants.GET_DEPLOYMENTS_FAILED: "Failed to get deployments list",
        ApiConstants.GET_TEST_RESULTS_FAILED: "Failed to get test results list",
        ApiConstants.HTTP_HEADER_NOT_PROVIDED: "Http header value not provided: '%s'",
        ApiConstants.DISCOVERY_ERROR: "Estuary discovery: error aggregating results",
        ApiConstants.UNAUTHORIZED: "Unauthorized",
        ApiConstants.TARGET_UNREACHABLE: "The requested target %s was unreachable",
    }
