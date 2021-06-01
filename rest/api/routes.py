import json
from secrets import token_hex

from flask import Response, render_template, send_from_directory
from flask import request
from fluent import sender

from about import properties, about_system
from rest.api import AppCreatorSingleton
from rest.api.constants.api_constants import ApiCode
from rest.api.constants.env_constants import EnvConstants
from rest.api.constants.header_constants import HeaderConstants
from rest.api.exception.api_exception import ApiException
from rest.api.jinja2.render import Render
from rest.api.loghelpers.message_dumper import MessageDumper
from rest.api.responsehelpers.error_codes import ErrorMessage
from rest.api.responsehelpers.http_response import HttpResponse
from rest.environment.environment import EnvironmentSingleton
from rest.service.eureka import Eureka
from rest.service.fluentd import Fluentd
from rest.utils.env_startup import EnvStartupSingleton
from rest.utils.thread_utils import ThreadUtils

app = AppCreatorSingleton.get_instance().get_app()

logger = \
    sender.FluentSender(tag=properties.get('name'),
                        host=EnvStartupSingleton.get_instance().get_config_env_vars().get(
                            EnvConstants.FLUENTD_IP_PORT).split(":")[0],
                        port=int(EnvStartupSingleton.get_instance().get_config_env_vars().get(
                            EnvConstants.FLUENTD_IP_PORT).split(":")[1])) \
        if EnvStartupSingleton.get_instance().get_config_env_vars().get(
        EnvConstants.FLUENTD_IP_PORT) else None
fluentd_service = Fluentd(logger)
message_dumper = MessageDumper()
env = EnvironmentSingleton.get_instance()


@app.errorhandler(ApiException)
def handle_api_error(e):
    return Response(json.dumps(
        HttpResponse().response(code=e.code, message=e.message,
                                description="Exception({})".format(e.exception.__str__()))),
        500, mimetype="application/json")


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
            EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.HTTP_AUTH_TOKEN)):
        # options is for preflight CORS
        # swagger should be permitted
        if not ("/apidocs" in request_uri or "/swagger/swagger.json" in request_uri or request.method == 'OPTIONS'):
            headers = {
                HeaderConstants.X_REQUEST_ID: message_dumper.get_header(HeaderConstants.X_REQUEST_ID)
            }
            return Response(json.dumps(http.response(ApiCode.UNAUTHORIZED.value,
                                                     ErrorMessage.HTTP_CODE.get(ApiCode.UNAUTHORIZED.value),
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


@app.route('/apidocs')
def swaggerui_index():
    return render_template('swaggerui.html')


@app.route('/viewer')
def viewer_index():
    return render_template('index.html')


@app.route('/js/<path:path>')
def viewer_js(path):
    return send_from_directory('templates/js', path)


@app.route('/css/<path:path>')
def viewer_css(path):
    return send_from_directory('templates/css', path)


@app.route('/img/<path:path>')
def viewer_img(path):
    return send_from_directory('templates/img', path)


@app.route('/fonts/<path:path>')
def viewer_fonts(path):
    return send_from_directory('templates/fonts', path)


@app.route('/swaggerui/<path:path>')
def swaggerui_resurces(path):
    return send_from_directory('templates/swaggerui', path)


@app.route('/swagger/swagger.json')
def get_swagger_json():
    return render_template('swaggerui/swagger.json')


@app.route('/ping')
def ping():
    return Response(
        json.dumps(
            HttpResponse().response(ApiCode.SUCCESS.value, ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value), "pong")),
        200, mimetype="application/json")


@app.route('/about')
def about():
    return Response(json.dumps(
        HttpResponse().response(ApiCode.SUCCESS.value, ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value),
                                about_system)), 200, mimetype="application/json")


@app.route('/render/<template>/<variables>', methods=['GET', 'POST'])
def get_content_with_env(template, variables):
    env.set_env_var(EnvConstants.TEMPLATE, template.strip())
    env.set_env_var(EnvConstants.VARIABLES, variables.strip())

    try:
        env_vars_attempted = request.get_json(force=True)
        for key, value in env_vars_attempted.items():
            env.set_env_var(key, value)
    except Exception as e:
        app.logger.debug(f"Exception: {e.__str__()}")

    try:
        r = Render(env.get_env_and_virtual_env().get(EnvConstants.TEMPLATE),
                   env.get_env_and_virtual_env().get(EnvConstants.VARIABLES))
        response = Response(r.rend_template(), 200, mimetype="text/plain")
    except Exception as e:
        raise ApiException(ApiCode.JINJA2_RENDER_FAILURE.value,
                           ErrorMessage.HTTP_CODE.get(ApiCode.JINJA2_RENDER_FAILURE.value), e)

    return response


@app.route('/env')
def get_vars():
    return Response(json.dumps(
        HttpResponse().response(code=ApiCode.SUCCESS.value, message=ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value),
                                description=env.get_env_and_virtual_env())), 200, mimetype="application/json")


@app.route('/env/<name>', methods=['GET'])
def get_env(name):
    return Response(json.dumps(
        HttpResponse().response(ApiCode.SUCCESS.value, ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value),
                                env.get_env_and_virtual_env().get(name))), 200, mimetype="application/json")


@app.route('/env', methods=['POST'])
def set_env():
    http = HttpResponse()
    input_data = request.data.decode("UTF-8", "replace").strip()

    try:
        env_vars_attempted = json.loads(input_data)
    except Exception as e:
        raise ApiException(ApiCode.INVALID_JSON_PAYLOAD.value,
                           ErrorMessage.HTTP_CODE.get(ApiCode.INVALID_JSON_PAYLOAD.value) % str(input_data), e)

    try:
        for key, value in env_vars_attempted.items():
            env.set_env_var(key, value)
        env_vars_added = {key: value for key, value in env_vars_attempted.items() if key in env.get_virtual_env()}
    except Exception as e:
        raise ApiException(ApiCode.SET_ENV_VAR_FAILURE.value,
                           ErrorMessage.HTTP_CODE.get(ApiCode.SET_ENV_VAR_FAILURE.value) % str(input_data), e)
    return Response(
        json.dumps(http.response(ApiCode.SUCCESS.value, ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value),
                                 env_vars_added)), 200, mimetype="application/json")


@app.route('/eurekaapps', methods=['GET'])
def get_eureka_apps():
    http = HttpResponse()
    eureka = Eureka(EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.EUREKA_SERVER))

    try:
        apps_list = eureka.get_eureka_apps()
    except Exception as e:
        raise ApiException(ApiCode.GET_EUREKA_APPS_FAILED.value,
                           ErrorMessage.HTTP_CODE.get(ApiCode.GET_EUREKA_APPS_FAILED.value) % eureka.get_eureka_host(),
                           e)

    return Response(
        json.dumps(http.response(ApiCode.SUCCESS.value, ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value), apps_list)),
        200,
        mimetype="application/json")


@app.route('/eurekaapps/<eureka_app_name>', methods=['GET'])
def get_eureka_apps_name(eureka_app_name):
    eureka_app_name = eureka_app_name.strip()
    eureka = Eureka(EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.EUREKA_SERVER))

    try:
        apps_list = eureka.get_type_eureka_apps(eureka_app_name)
    except Exception as e:
        raise ApiException(ApiCode.GET_EUREKA_APPS_FAILED.value,
                           ErrorMessage.HTTP_CODE.get(ApiCode.GET_EUREKA_APPS_FAILED.value) % eureka.get_eureka_host(),
                           e)
    return Response(json.dumps(
        HttpResponse().response(ApiCode.SUCCESS.value, ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value), apps_list)),
        200,
        mimetype="application/json")


# aggregator of command detached info from the agent(s)
@app.route('/commandsdetached', methods=['GET'])
def get_commands_detached():
    application = "agent"
    eureka = Eureka(EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.EUREKA_SERVER))

    try:
        agent_apps = eureka.get_type_eureka_apps(application)
        thread_utils = ThreadUtils(apps=agent_apps, headers=request.headers)
        thread_utils.spawn_threads_get_test_info()
        commands_detached = thread_utils.get_threads_response()
    except Exception as e:
        raise ApiException(ApiCode.GET_COMMANDS_DETACHED_FAILED.value,
                           ErrorMessage.HTTP_CODE.get(ApiCode.GET_COMMANDS_DETACHED_FAILED.value), e)

    return Response(json.dumps(
        HttpResponse().response(ApiCode.SUCCESS.value, ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value),
                                commands_detached)), 200,
        mimetype="application/json")


# aggregator of the deployer(s) data.
@app.route('/deployments', methods=['GET'])
def get_deployments():
    application = "deployer"
    eureka = Eureka(EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.EUREKA_SERVER))

    try:
        deployer_apps = eureka.get_type_eureka_apps(application)
        thread_utils = ThreadUtils(apps=deployer_apps, headers=request.headers)
        thread_utils.spawn_threads_get_deployment_info()
        deployments = thread_utils.get_threads_response()
    except Exception as e:
        raise ApiException(ApiCode.GET_DEPLOYMENTS_FAILED.value,
                           ErrorMessage.HTTP_CODE.get(ApiCode.GET_DEPLOYMENTS_FAILED.value), e)

    return Response(json.dumps(
        HttpResponse().response(ApiCode.SUCCESS.value, ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value), deployments)),
        200,
        mimetype="application/json")


# aggregator of all agents endpoints
@app.route('/agents/<path:text>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def agents_request(text):
    text = text.strip()
    eureka = Eureka(EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.EUREKA_SERVER))
    ip_addr_port_header_key = 'IpAddr-Port'  # target specific agent
    home_page_url_header_key = 'HomePageUrl'  # target specific agent
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
        agent_apps = eureka.get_type_eureka_apps(application)
        if request.headers.get(f"{ip_addr_port_header_key}"):  # not mandatory
            ip_port = request.headers.get(f"{ip_addr_port_header_key}").split(":")
            agent_apps = list(filter(lambda x: x.get('ipAddr') == ip_port[0] and x.get('port') == ip_port[1],
                                     agent_apps))
        if request.headers.get(f"{home_page_url_header_key}"):  # not mandatory
            home_page_url = request.headers.get(f"{home_page_url_header_key}")
            agent_apps = list(filter(lambda x: x.get('homePageUrl') == home_page_url, agent_apps))
        thread_utils = ThreadUtils(apps=agent_apps, headers={})
        thread_utils.spawn_threads_send_request(request_object)

    except Exception as e:
        raise ApiException(ApiCode.DISCOVERY_ERROR.value,
                           ErrorMessage.HTTP_CODE.get(ApiCode.DISCOVERY_ERROR.value), e)

    return Response(json.dumps(
        HttpResponse().response(ApiCode.SUCCESS.value, ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value),
                                thread_utils.get_threads_response())), 200, mimetype="application/json")


# aggregator of all deployers endpoints
@app.route('/deployers/<path:text>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def deployers_request(text):
    text = text.strip()
    eureka = Eureka(EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.EUREKA_SERVER))
    ip_addr_port_header_key = 'IpAddr-Port'  # target specific deployer
    home_page_url_header_key = 'HomePageUrl'  # target specific agent
    application = "deployer"
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
        deployer_apps = eureka.get_type_eureka_apps(application)
        if request.headers.get(f"{ip_addr_port_header_key}"):  # not mandatory
            ip_port = request.headers.get(f"{ip_addr_port_header_key}").split(":")
            deployer_apps = list(filter(lambda x: x.get('ipAddr') == ip_port[0] and x.get('port') == ip_port[1],
                                        deployer_apps))
        if request.headers.get(f"{home_page_url_header_key}"):  # not mandatory
            home_page_url = request.headers.get(f"{home_page_url_header_key}")
            deployer_apps = list(filter(lambda x: x.get('homePageUrl') == home_page_url, deployer_apps))
        thread_utils = ThreadUtils(apps=deployer_apps, headers={})
        thread_utils.spawn_threads_send_request(request_object)

    except Exception as e:
        raise ApiException(ApiCode.DISCOVERY_ERROR.value,
                           ErrorMessage.HTTP_CODE.get(ApiCode.DISCOVERY_ERROR.value), e)

    return Response(json.dumps(
        HttpResponse().response(ApiCode.SUCCESS.value, ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value),
                                thread_utils.get_threads_response())), 200, mimetype="application/json")
