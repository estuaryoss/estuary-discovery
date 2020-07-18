from tests.rest.constants import Constants


class ErrorCodes:
    HTTP_CODE = {
        Constants.SUCCESS: "Success",
        Constants.JINJA2_RENDER_FAILURE: "jinja2 render failed",
        Constants.GET_EUREKA_APPS_FAILED: "Failed to get apps from Eureka server '%s'",
        Constants.GET_CONTAINER_ENV_VAR_FAILURE: "Failed to get env var '%s'",
        Constants.UNAUTHORIZED: "Unauthorized"
    }
