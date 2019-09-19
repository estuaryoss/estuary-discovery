import json
import os
import traceback

from flask import Response
from flask import request

from about import properties
from entities.render import Render
from rest.api import create_app
from rest.api.apiresponsehelpers.constants import Constants
from rest.api.apiresponsehelpers.error_codes import ErrorCodes
from rest.api.apiresponsehelpers.estuary_stack_apps import EstuaryStackApps
from rest.api.apiresponsehelpers.http_response import HttpResponse
from rest.api.definitions import env_vars
from rest.utils.eureka_utils import EurekaUtils
from rest.utils.thread_utils import ThreadUtils

app = create_app()


@app.route('/swagger/swagger.yml')
def get_swagger():
    return app.send_static_file("swagger.yml")


@app.route('/env')
def get_vars():
    http = HttpResponse()
    return Response(json.dumps(http.success(Constants.SUCCESS, ErrorCodes.HTTP_CODE.get(Constants.SUCCESS), env_vars)),
                    200, mimetype="application/json")


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

    try:
        host = os.environ.get('EUREKA_SERVER')
        print(f"Getting apps from eureka server {host} ... \n")
        apps_list = EurekaUtils.get_eureka_apps(host)
        response = Response(json.dumps(
            http.success(Constants.SUCCESS, ErrorCodes.HTTP_CODE.get(Constants.SUCCESS), apps_list)), 200,
            mimetype="application/json")
    except Exception as e:
        exception = "Exception({0})".format(e.__str__())
        response = Response(json.dumps(http.failure(Constants.GET_EUREKA_APPS_FAILED,
                                                    ErrorCodes.HTTP_CODE.get(
                                                        Constants.GET_EUREKA_APPS_FAILED) % host,
                                                    exception,
                                                    str(traceback.format_exc()))), 404, mimetype="application/json")
    return response


@app.route('/geteurekaapps/<type>', methods=['GET'])
def get_type_eureka_apps(type):
    http = HttpResponse()

    try:
        host = os.environ.get('EUREKA_SERVER')
        supported_apps = EstuaryStackApps.get_supported_apps();
        if type.strip() not in supported_apps:
            return Response(json.dumps(http.failure(Constants.EUREKA_APP_NOT_SUPPORTED,
                                                    ErrorCodes.HTTP_CODE.get(
                                                        Constants.EUREKA_APP_NOT_SUPPORTED) % (
                                                        type, json.dumps(supported_apps)),
                                                    ErrorCodes.HTTP_CODE.get(
                                                        Constants.EUREKA_APP_NOT_SUPPORTED) % (
                                                        type, json.dumps(supported_apps)),
                                                    str(traceback.format_exc()))), 404, mimetype="application/json")
        apps_list = EurekaUtils.get_type_eureka_apps(host, type)
        response = Response(json.dumps(
            http.success(Constants.SUCCESS, ErrorCodes.HTTP_CODE.get(Constants.SUCCESS), apps_list)), 200,
            mimetype="application/json")
    except Exception as e:
        exception = "Exception({0})".format(e.__str__())
        return Response(json.dumps(http.failure(Constants.GET_EUREKA_APPS_FAILED,
                                                ErrorCodes.HTTP_CODE.get(
                                                    Constants.GET_EUREKA_APPS_FAILED) % host,
                                                exception,
                                                str(traceback.format_exc()))), 404, mimetype="application/json")
    return response


# this might not be reliable ?
# aggregator of the testrunner(s) data
@app.route('/gettests', methods=['GET'])
def get_tests():
    http = HttpResponse()

    try:
        host = os.environ.get('EUREKA_SERVER')
        testrunner_apps = EurekaUtils.get_type_eureka_apps(host, EstuaryStackApps.get_supported_apps()[0])
        thread_utils = ThreadUtils(testrunner_apps)
        thread_utils.spawn_threads_testrunners()
        tests = thread_utils.get_list()
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


# this might not be reliable ?
# aggregator of the deployer(s) data.
@app.route('/getdeployments', methods=['GET'])
def get_deployments():
    http = HttpResponse()

    try:
        host = os.environ.get('EUREKA_SERVER')
        deployer_apps = EurekaUtils.get_type_eureka_apps(host, EstuaryStackApps.get_supported_apps()[1])
        thread_utils = ThreadUtils(deployer_apps)
        thread_utils.spawn_threads_deployers()
        deployments = thread_utils.get_list()
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
