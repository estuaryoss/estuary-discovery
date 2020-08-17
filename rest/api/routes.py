import json
import os
from secrets import token_hex

from flask import Response
from flask import request
from fluent import sender

from about import properties
from entities.render import Render
from rest.api import create_app
from rest.api.responsehelpers.error_codes import ErrorCodes
from rest.api.responsehelpers.http_response import HttpResponse
from rest.api.constants.api_constants import ApiConstants
from rest.api.constants.env_constants import EnvConstants
from rest.api.constants.header_constants import HeaderConstants
from rest.api.definitions import unmodifiable_env_vars
from rest.api.loghelpers.message_dumper import MessageDumper
from rest.api.swagger import swagger_file_content
from rest.service.eureka import Eureka
from rest.service.fluentd import Fluentd
from rest.utils.env_startup import EnvStartup
from rest.utils.thread_utils import ThreadUtils

app = create_app()
logger = \
    sender.FluentSender(tag=properties.get('name'),
                        host=EnvStartup.get_instance().get(EnvConstants.FLUENTD_IP_PORT).split(":")[0],
                        port=int(EnvStartup.get_instance().get(EnvConstants.FLUENTD_IP_PORT).split(":")[1])) \
        if EnvStartup.get_instance().get(EnvConstants.FLUENTD_IP_PORT) else None
fluentd_service = Fluentd(logger)
message_dumper = MessageDumper()


@app.before_request
def before_request():
    ctx = app.app_context()
    ctx.g.xid = token_hex(8)
    http = HttpResponse()
    request_uri = request.full_path

    # add here your custom header to be logged with fluentd
    message_dumper.set_header(HeaderConstants.X_REQUEST_ID,
                              request.headers.get(HeaderConstants.X_REQUEST_ID) if request.headers.get(
                                  HeaderConstants.X_REQUEST_ID) else ctx.g.xid)
    message_dumper.set_header(HeaderConstants.REQUEST_URI, request_uri)

    response = fluentd_service.emit(tag="api", msg=message_dumper.dump(request=request))
    app.logger.debug(response)
    if not str(request.headers.get(HeaderConstants.TOKEN)) == str(
            EnvStartup.get_instance().get(EnvConstants.HTTP_AUTH_TOKEN)):
        if not ("/api/docs" in request_uri or "/swagger/swagger.yml" in request_uri):  # exclude swagger
            headers = {
                HeaderConstants.X_REQUEST_ID: message_dumper.get_header(HeaderConstants.X_REQUEST_ID)
            }
            return Response(json.dumps(http.response(ApiConstants.UNAUTHORIZED,
                                                     ErrorCodes.HTTP_CODE.get(ApiConstants.UNAUTHORIZED),
                                                     "Invalid Token")), 401, mimetype="application/json",
                            headers=headers)


@app.after_request
def after_request(http_response):
    # if not json, do not alter
    try:
        headers = dict(http_response.headers)
        headers[HeaderConstants.X_REQUEST_ID] = message_dumper.get_header(HeaderConstants.X_REQUEST_ID)
        http_response.headers = headers
    except:
        app.logger.debug("Message was not altered: " + message_dumper.dump(http_response))

    http_response.direct_passthrough = False
    response = fluentd_service.emit(tag="api", msg=message_dumper.dump(http_response))
    app.logger.debug(response)

    return http_response


@app.route('/swagger/swagger.yml')
def get_swagger():
    return Response(swagger_file_content, 200, mimetype="application/json")


@app.route('/ping')
def ping():
    http = HttpResponse()

    return Response(
        json.dumps(http.response(ApiConstants.SUCCESS, ErrorCodes.HTTP_CODE.get(ApiConstants.SUCCESS), "pong")),
        200, mimetype="application/json")


@app.route('/about')
def about():
    http = HttpResponse()

    return Response(json.dumps(
        http.response(ApiConstants.SUCCESS, ErrorCodes.HTTP_CODE.get(ApiConstants.SUCCESS), properties["name"])), 200,
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
        # response = http.response(ApiApiConstants.SUCCESS, ErrorCodes.HTTP_CODE.get(ApiApiConstants.SUCCESS), result), 200
    except Exception as e:
        result = "Exception({0})".format(e.__str__())
        response = Response(json.dumps(
            http.response(ApiConstants.JINJA2_RENDER_FAILURE,
                          ErrorCodes.HTTP_CODE.get(ApiConstants.JINJA2_RENDER_FAILURE),
                          result)), 404, mimetype="application/json")

    return response


@app.route('/env')
def get_vars():
    http_response = HttpResponse.response(ApiConstants.SUCCESS, ErrorCodes.HTTP_CODE.get(ApiConstants.SUCCESS),
                                          dict(os.environ))

    return Response(json.dumps(http_response), 200, mimetype="application/json")


@app.route('/env/<name>', methods=['GET'])
def get_env(name):
    name = name.upper().strip()
    http = HttpResponse()
    try:
        response = Response(json.dumps(
            http.response(ApiConstants.SUCCESS, ErrorCodes.HTTP_CODE.get(ApiConstants.SUCCESS), os.environ[name])), 200,
            mimetype="application/json")
    except Exception as e:
        result = "Exception({0})".format(e.__str__())
        response = Response(json.dumps(http.response(ApiConstants.GET_CONTAINER_ENV_VAR_FAILURE,
                                                     ErrorCodes.HTTP_CODE.get(
                                                         ApiConstants.GET_CONTAINER_ENV_VAR_FAILURE) % name,
                                                     result)), 404, mimetype="application/json")
    return response


@app.route('/eurekaapps', methods=['GET'])
def get_eureka_apps():
    http = HttpResponse()
    eureka_utils = Eureka(EnvStartup.get_instance().get(EnvConstants.EUREKA_SERVER))

    try:
        apps_list = eureka_utils.get_eureka_apps()
        response = Response(json.dumps(
            http.response(ApiConstants.SUCCESS, ErrorCodes.HTTP_CODE.get(ApiConstants.SUCCESS), apps_list)), 200,
            mimetype="application/json")
    except Exception as e:
        exception = "Exception({0})".format(e.__str__())
        response = Response(json.dumps(http.response(ApiConstants.GET_EUREKA_APPS_FAILED,
                                                     ErrorCodes.HTTP_CODE.get(
                                                         ApiConstants.GET_EUREKA_APPS_FAILED) % eureka_utils.get_eureka_host(),
                                                     exception)), 404, mimetype="application/json")
    return response


@app.route('/eurekaapps/<type>', methods=['GET'])
def get_type_eureka_apps(type):
    http = HttpResponse()
    type = type.strip()
    eureka_utils = Eureka(EnvStartup.get_instance().get(EnvConstants.EUREKA_SERVER))

    try:
        apps_list = eureka_utils.get_type_eureka_apps(type)
        response = Response(json.dumps(
            http.response(ApiConstants.SUCCESS, ErrorCodes.HTTP_CODE.get(ApiConstants.SUCCESS), apps_list)), 200,
            mimetype="application/json")
    except Exception as e:
        exception = "Exception({})".format(e.__str__())
        return Response(json.dumps(http.response(ApiConstants.GET_EUREKA_APPS_FAILED,
                                                 ErrorCodes.HTTP_CODE.get(
                                                     ApiConstants.GET_EUREKA_APPS_FAILED) % eureka_utils.get_eureka_host(),
                                                 exception)), 404, mimetype="application/json")
    return response


# aggregator of command detached info from the agent(s)
@app.route('/commandsdetached', methods=['GET'])
def get_tests():
    http = HttpResponse()
    application = "agent"
    eureka_utils = Eureka(EnvStartup.get_instance().get(EnvConstants.EUREKA_SERVER))

    try:
        agent_apps = eureka_utils.get_type_eureka_apps(application)
        thread_utils = ThreadUtils(agent_apps, headers=request.headers)
        thread_utils.spawn_threads_get_test_info()
        tests = thread_utils.get_threads_response()
        response = Response(json.dumps(
            http.response(ApiConstants.SUCCESS, ErrorCodes.HTTP_CODE.get(ApiConstants.SUCCESS), tests)), 200,
            mimetype="application/json")
    except Exception as e:
        exception = "Exception({0})".format(e.__str__())
        return Response(json.dumps(http.response(ApiConstants.GET_TESTS_FAILED,
                                                 ErrorCodes.HTTP_CODE.get(
                                                     ApiConstants.GET_TESTS_FAILED),
                                                 exception)), 404, mimetype="application/json")

    return response


# aggregator of the deployer(s) data.
@app.route('/deployments', methods=['GET'])
def get_deployments():
    http = HttpResponse()
    application = "deployer"
    eureka_utils = Eureka(EnvStartup.get_instance().get(EnvConstants.EUREKA_SERVER))

    try:
        deployer_apps = eureka_utils.get_type_eureka_apps(application)
        thread_utils = ThreadUtils(deployer_apps, headers=request.headers)
        thread_utils.spawn_threads_get_deployment_info()
        deployments = thread_utils.get_threads_response()
        response = Response(json.dumps(
            http.response(ApiConstants.SUCCESS, ErrorCodes.HTTP_CODE.get(ApiConstants.SUCCESS), deployments)), 200,
            mimetype="application/json")
    except Exception as e:
        exception = "Exception({0})".format(e.__str__())
        return Response(json.dumps(http.response(ApiConstants.GET_DEPLOYMENTS_FAILED,
                                                 ErrorCodes.HTTP_CODE.get(
                                                     ApiConstants.GET_DEPLOYMENTS_FAILED),
                                                 exception)), 404, mimetype="application/json")

    return response


# aggregator of all agents endpoints
@app.route('/agents/<path:text>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def agents_request(text):
    text = text.strip()
    http = HttpResponse()
    eureka_service = Eureka(EnvStartup.get_instance().get(EnvConstants.EUREKA_SERVER))
    header_key = 'IpAddr-Port'  # target specific agent
    application = "agent"
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
        test_agent_apps = eureka_service.get_type_eureka_apps(application)
        if request.headers.get(f"{header_key}"):  # not mandatory
            ip_port = request.headers.get(f"{header_key}").split(":")
            test_agent_apps = list(filter(lambda x: x.get('ipAddr') == ip_port[0] and x.get('port') == ip_port[1],
                                          test_agent_apps))
        thread_utils = ThreadUtils(test_agent_apps)
        thread_utils.spawn_threads_send_agent_request(request_object)

        response = Response(json.dumps(
            http.response(ApiConstants.SUCCESS, ErrorCodes.HTTP_CODE.get(ApiConstants.SUCCESS),
                          thread_utils.get_threads_response())), 200,
            mimetype="application/json")

    except Exception as e:
        exception = "Exception({0})".format(e.__str__())
        response = Response(json.dumps(http.response(ApiConstants.DISCOVERY_ERROR,
                                                     ErrorCodes.HTTP_CODE.get(ApiConstants.DISCOVERY_ERROR),
                                                     exception)), 404, mimetype="application/json")
    return response
