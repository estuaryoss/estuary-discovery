from rest.api.apiresponsehelpers.constants import Constants


class ErrorCodes:
    HTTP_CODE = {
        Constants.SUCCESS: "success",
        Constants.JINJA2_RENDER_FAILURE: "jinja2 render failed",
        Constants.GET_EUREKA_APPS_FAILED: "Failed to get apps from Eureka server '%s'",
        Constants.GET_CONTAINER_ENV_VAR_FAILURE: "Failed to get env var '%s'",
        Constants.GET_TESTS_FAILED: "Failed to get tests list",
        Constants.GET_DEPLOYMENTS_FAILED: "Failed to get deployments list",
        Constants.GET_TEST_RESULTS_FAILED: "Failed to get test results list",
        Constants.HTTP_HEADER_NOT_PROVIDED: "Http header value not provided: '%s'",
        Constants.DISCOVERY_ERROR: "Estuary discovery: error aggregating results",
        Constants.UNAUTHORIZED: "Unauthorized",
    }
