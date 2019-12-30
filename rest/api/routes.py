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
from rest.api.definitions import env_vars, swagger_file_content
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
    ctx.g.cid = token_hex(8)
    message_dumper.set_correlation_id(ctx.g.cid)

    response = fluentd_utils.debug(tag="api", msg=message_dumper.dump(request=request))
    app.logger.debug(response)


@app.after_request
def after_request(http_response):
    # if not json, do not alter
    try:
        headers = dict(http_response.headers)
        headers['Correlation-Id'] = message_dumper.get_correlation_id()
        http_response.headers = headers
    except:
        pass

    response = fluentd_utils.debug(tag="api", msg=message_dumper.dump(http_response))
    app.logger.debug(response)

    return http_response


@app.route('/swagger/swagger.yml')
def get_swagger():
    return Response(swagger_file_content, 200, mimetype="application/json")


@app.route('/env')
def get_vars():
    http_response = HttpResponse.success(Constants.SUCCESS, ErrorCodes.HTTP_CODE.get(Constants.SUCCESS), env_vars)

    return Response(json.dumps(http_response), 200, mimetype="application/json")


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


@app.route('/rend/<template>/<variables>', methods=['GET'])
def get_content(template, variables):
    os.environ['TEMPLATE'] = template.strip()
    os.environ['VARIABLES'] = variables.strip()
    http = HttpResponse()
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


@app.route('/rendwithenv/<template>/<variables>', methods=['POST'])
def get_content_with_env(template, variables):
    try:
        input_json = request.get_json(force=True)
        for key, value in input_json.items():
            if key not in env_vars:
                os.environ[key] = value
    except:
        pass

    os.environ['TEMPLATE'] = template.strip()
    os.environ['VARIABLES'] = variables.strip()

    http = HttpResponse()
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


@app.route('/getenv/<name>', methods=['GET'])
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


@app.route('/geteurekaapps', methods=['GET'])
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


@app.route('/geteurekaapps/<type>', methods=['GET'])
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
@app.route('/gettests', methods=['GET'])
def get_tests():
    http = HttpResponse()
    application = "testrunner"
    eureka_utils = EurekaUtils(os.environ.get('EUREKA_SERVER'))

    try:
        testrunner_apps = eureka_utils.get_type_eureka_apps(application)
        thread_utils = ThreadUtils(testrunner_apps)
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
@app.route('/getdeployments', methods=['GET'])
def get_deployments():
    http = HttpResponse()
    application = "deployer"
    eureka_utils = EurekaUtils(os.environ.get('EUREKA_SERVER'))

    try:
        deployer_apps = eureka_utils.get_type_eureka_apps(application)
        thread_utils = ThreadUtils(deployer_apps)
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
@app.route('/testrunner/<path:text>', methods=['GET', 'POST'])
def testrunner_request(text):
    http = HttpResponse()
    eureka_utils = EurekaUtils(os.environ.get('EUREKA_SERVER'))
    uri = text.lstrip("/")
    input_data = ""
    application = "testrunner"
    try:
        input_data = request.get_data()
    except:
        pass

    try:
        headers = request.headers
        request_object = {
            "uri": f'{uri}',
            "method": request.method,
            "headers": headers,
            "data": input_data
        }
        app.logger.debug({"msg": f"{request_object}"})
        test_runner_apps = eureka_utils.get_type_eureka_apps(application)
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
