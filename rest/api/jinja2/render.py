#!/usr/bin/env python3

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import os
import sys

import jinja2
import yaml

from rest.environment.environment import EnvironmentSingleton


class Render:

    def __init__(self, template=None, variables=None):
        """

        Custom jinja2 render
        """

        self.template = template
        self.variables = variables
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                EnvironmentSingleton.get_instance().get_env_and_virtual_env().get('TEMPLATES_DIR')),
            extensions=['jinja2.ext.autoescape', 'jinja2.ext.do', 'jinja2.ext.loopcontrols', 'jinja2.ext.with_'],
            autoescape=True,
            trim_blocks=True)

    def yaml_filter(self, value):
        return yaml.dump(value, Dumper=yaml.RoundTripDumper, indent=4)

    def env_override(self, value, key):
        return os.getenv(key, value)

    def rend_template(self, vars_dir=EnvironmentSingleton.get_instance().get_env_and_virtual_env().get('VARS_DIR')):
        with open(vars_dir + "/" + self.variables, closefd=True) as f:
            data = yaml.safe_load(f)

        self.env.filters['yaml'] = self.yaml_filter
        self.env.globals["environ"] = lambda key: EnvironmentSingleton.get_instance().get_env_and_virtual_env().get(key)
        self.env.globals["get_context"] = lambda: data

        try:
            template = self.env.get_template(self.template).render(data)
        except Exception as e:
            raise e
        sys.stdout.write(template)

        return template

    def get_jinja2env(self):
        return self.env


if __name__ == '__main__':
    render = Render(EnvironmentSingleton.get_instance().get_env_and_virtual_env().get('TEMPLATE'),
                    EnvironmentSingleton.get_instance().get_env_and_virtual_env().get('VARIABLES')).rend_template()
