import json
import os
import traceback
from secrets import token_hex

from flask import Response
from flask import request
from fluent import sender

from about import properties
from entities.render import Render
from rest.api import create_app
from rest.api.apiresponsehelpers.constants import Constants
from rest.api.apiresponsehelpers.error_codes import ErrorCodes
from rest.api.apiresponsehelpers.http_response import HttpResponse
from rest.api.definitions import swagger_file_content, unmodifiable_env_vars
from rest.api.logginghelpers.message_dumper import MessageDumper
from rest.utils.eureka_utils import EurekaUtils
from rest.utils.fluentd_utils import FluentdUtils
from rest.utils.thread_utils import ThreadUtils

app = create_app()
logger = sender.FluentSender(properties.get('name'), host=properties["fluentd_ip"],
                             port=int(properties["fluentd_port"]))
fluentd_utils = FluentdUtils(logger)
message_dumper = MessageDumper()


@app.before_request
def before_request():
    ctx = app.app_context()
    ctx.g.xid = token_hex(8)
    http = HttpResponse()
    request_uri = request.environ.get("REQUEST_URI")

    # add here your custom header to be logged with fluentd
    message_dumper.set_header("X-Request-ID",
                              request.headers.get('X-Request-ID') if request.headers.get('X-Request-ID') else ctx.g.xid)
    message_dumper.set_header("Request-Uri", request_uri)

    response = fluentd_utils.debug(tag="api", msg=message_dumper.dump(request=request))
    app.logger.debug(response)
    if not str(request.headers.get("Token")) == str(os.environ.get("HTTP_AUTH_TOKEN")):
        if not ("/api/docs" in request_uri or "/swagger/swagger.yml" in request_uri):  # exclude swagger
            headers = {
                'X-Request-ID': message_dumper.get_header("X-Request-ID")
            }
            return Response(json.dumps(http.failure(Constants.UNAUTHORIZED,
                                                    ErrorCodes.HTTP_CODE.get(Constants.UNAUTHORIZED),
                                                    "Invalid Token",
                                                    str(traceback.format_exc()))), 401, mimetype="application/json",
                            headers=headers)


@app.after_request
def after_request(http_response):
    # if not json, do not alter
    try:
        headers = dict(http_response.headers)
        headers['X-Request-ID'] = message_dumper.get_header("X-Request-ID")
        http_response.headers = headers
    except:
        app.logger.debug("Message was not altered: " + message_dumper.dump(http_response))

    response = fluentd_utils.debug(tag="api", msg=message_dumper.dump(http_response))
    app.logger.debug(response)

    return http_response


@app.route('/swagger/swagger.yml')
def get_swagger():
    return Response(swagger_file_content, 200, mimetype="application/json")


@app.route('/ping')
def ping():
    http = HttpResponse()

    return Response(json.dumps(http.success(Constants.SUCCESS, ErrorCodes.HTTP_CODE.get(Constants.SUCCESS), "pong")),
                    200, mimetype="application/json")


@app.route('/about')
def about():
    http = HttpResponse()

    return Response(json.dumps(
        http.success(Constants.SUCCESS, ErrorCodes.HTTP_CODE.get(Constants.SUCCESS), properties["name"])), 200,
        mimetype="application/json")


@app.route('/render/<template>/<variables>', methods=['GET', 'POST'])
def get_content_with_env(template, variables):
    http = HttpResponse()
    try:
        input_json = request.get_json(force=True)
        for key, value in input_json.items():
            if key not in unmodifiable_env_vars:
                os.environ[key] = value
    except:
        pass

    os.environ['TEMPLATE'] = template.strip()
    os.environ['VARIABLES'] = variables.strip()

    try:
        r = Render(os.environ['TEMPLATE'], os.environ['VARIABLES'])
        response = Response(r.rend_template(), 200, mimetype="text/plain")
        # response = http.success(Constants.SUCCESS, ErrorCodes.HTTP_CODE.get(Constants.SUCCESS), result), 200
    except Exception as e:
        result = "Exception({0})".format(e.__str__())
        response = Response(json.dumps(http.failure(Constants.JINJA2_RENDER_FAILURE,
                                                    ErrorCodes.HTTP_CODE.get(Constants.JINJA2_RENDER_FAILURE), result,
                                                    str(traceback.format_exc()))), 404, mimetype="application/json")

    return response


@app.route('/env')
def get_vars():
    http_response = HttpResponse.success(Constants.SUCCESS, ErrorCodes.HTTP_CODE.get(Constants.SUCCESS),
                                         dict(os.environ))

    return Response(json.dumps(http_response), 200, mimetype="application/json")


@app.route('/env/<name>', methods=['GET'])
def get_env(name):
    name = name.upper().strip()
    http = HttpResponse()
    try:
        response = Response(json.dumps(
            http.success(Constants.SUCCESS, ErrorCodes.HTTP_CODE.get(Constants.SUCCESS), os.environ[name])), 200,
            mimetype="application/json")
    except Exception as e:
        result = "Exception({0})".format(e.__str__())
        response = Response(json.dumps(http.failure(Constants.GET_CONTAINER_ENV_VAR_FAILURE,
                                                    ErrorCodes.HTTP_CODE.get(
                                                        Constants.GET_CONTAINER_ENV_VAR_FAILURE) % name,
                                                    result,
                                                    str(traceback.format_exc()))), 404, mimetype="application/json")
    return response


@app.route('/eurekaapps', methods=['GET'])
def get_eureka_apps():
    http = HttpResponse()
    eureka_utils = EurekaUtils(os.environ.get('EUREKA_SERVER'))

    try:
        apps_list = eureka_utils.get_eureka_apps()
        response = Response(json.dumps(
            http.success(Constants.SUCCESS, ErrorCodes.HTTP_CODE.get(Constants.SUCCESS), apps_list)), 200,
            mimetype="application/json")
    except Exception as e:
        exception = "Exception({0})".format(e.__str__())
        response = Response(json.dumps(http.failure(Constants.GET_EUREKA_APPS_FAILED,
                                                    ErrorCodes.HTTP_CODE.get(
                                                        Constants.GET_EUREKA_APPS_FAILED) % eureka_utils.get_eureka_host(),
                                                    exception,
                                                    str(traceback.format_exc()))), 404, mimetype="application/json")
    return response


@app.route('/eurekaapps/<type>', methods=['GET'])
def get_type_eureka_apps(type):
    http = HttpResponse()
    type = type.strip()
    eureka_utils = EurekaUtils(os.environ.get('EUREKA_SERVER'))

    try:
        apps_list = eureka_utils.get_type_eureka_apps(type)
        response = Response(json.dumps(
            http.success(Constants.SUCCESS, ErrorCodes.HTTP_CODE.get(Constants.SUCCESS), apps_list)), 200,
            mimetype="application/json")
    except Exception as e:
        exception = "Exception({0})".format(e.__str__())
        return Response(json.dumps(http.failure(Constants.GET_EUREKA_APPS_FAILED,
                                                ErrorCodes.HTTP_CODE.get(
                                                    Constants.GET_EUREKA_APPS_FAILED) % eureka_utils.get_eureka_host(),
                                                exception,
                                                str(traceback.format_exc()))), 404, mimetype="application/json")
    return response


# aggregator of the testrunner(s) tests
@app.route('/tests', methods=['GET'])
def get_tests():
    http = HttpResponse()
    application = "testrunner"
    eureka_utils = EurekaUtils(os.environ.get('EUREKA_SERVER'))

    try:
        testrunner_apps = eureka_utils.get_type_eureka_apps(application)
        thread_utils = ThreadUtils(testrunner_apps, headers=request.headers)
        thread_utils.spawn_threads_get_test_info()
        tests = thread_utils.get_threads_response()
        response = Response(json.dumps(
            http.success(Constants.SUCCESS, ErrorCodes.HTTP_CODE.get(Constants.SUCCESS), tests)), 200,
            mimetype="application/json")
    except Exception as e:
        exception = "Exception({0})".format(e.__str__())
        return Response(json.dumps(http.failure(Constants.GET_TESTS_FAILED,
                                                ErrorCodes.HTTP_CODE.get(
                                                    Constants.GET_TESTS_FAILED),
                                                exception,
                                                str(traceback.format_exc()))), 404, mimetype="application/json")

    return response


# aggregator of the deployer(s) data.
@app.route('/deployments', methods=['GET'])
def get_deployments():
    http = HttpResponse()
    application = "deployer"
    eureka_utils = EurekaUtils(os.environ.get('EUREKA_SERVER'))

    try:
        deployer_apps = eureka_utils.get_type_eureka_apps(application)
        thread_utils = ThreadUtils(deployer_apps, headers=request.headers)
        thread_utils.spawn_threads_get_deployment_info()
        deployments = thread_utils.get_threads_response()
        response = Response(json.dumps(
            http.success(Constants.SUCCESS, ErrorCodes.HTTP_CODE.get(Constants.SUCCESS), deployments)), 200,
            mimetype="application/json")
    except Exception as e:
        exception = "Exception({0})".format(e.__str__())
        return Response(json.dumps(http.failure(Constants.GET_DEPLOYMENTS_FAILED,
                                                ErrorCodes.HTTP_CODE.get(
                                                    Constants.GET_DEPLOYMENTS_FAILED),
                                                exception,
                                                str(traceback.format_exc()))), 404, mimetype="application/json")

    return response


# aggregator of all testrunners endpoints
@app.route('/testrunners/<path:text>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def testrunners_request(text):
    text = text.strip()
    http = HttpResponse()
    eureka_utils = EurekaUtils(os.environ.get('EUREKA_SERVER'))
    header_key = 'IpAddr-Port'  # target specific testrunner
    application = "testrunner"
    try:
        input_data = request.get_data()
    except:
        input_data = ""

    try:
        request_object = {
            "uri": text.lstrip("/"),
            "method": request.method,
            "headers": request.headers,
            "data": input_data
        }
        app.logger.debug({"msg": f"{request_object}"})
        test_runner_apps = eureka_utils.get_type_eureka_apps(application)
        if request.headers.get(f"{header_key}"):  # not mandatory
            ip_port = request.headers.get(f"{header_key}").split(":")
            test_runner_apps = list(filter(lambda x: x.get('ipAddr') == ip_port[0] and x.get('port') == ip_port[1],
                                           test_runner_apps))
        thread_utils = ThreadUtils(test_runner_apps)
        thread_utils.spawn_threads_send_testrunner_request(request_object)

        response = Response(json.dumps(
            http.success(Constants.SUCCESS, ErrorCodes.HTTP_CODE.get(Constants.SUCCESS),
                         thread_utils.get_threads_response())), 200,
            mimetype="application/json")

    except Exception as e:
        exception = "Exception({0})".format(e.__str__())
        response = Response(json.dumps(http.failure(Constants.DISCOVERY_ERROR,
                                                    ErrorCodes.HTTP_CODE.get(Constants.DISCOVERY_ERROR),
                                                    exception,
                                                    exception)), 404, mimetype="application/json")
    return response
