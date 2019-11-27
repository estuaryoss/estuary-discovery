#!/usr/bin/env python3
import os

from about import properties
from rest.api.routes import app, fluentd_utils
from rest.api.routes import logger

if __name__ == "__main__":
    host = '0.0.0.0'
    port = properties["port"]

    fluentd_tag = "startup"
    logger.emit(fluentd_tag, {"msg": f"Sending logs to fluentd instance: host={properties['fluentd_ip']}, port={properties['fluentd_port']}"})

    app.run(host=host, port=port)
