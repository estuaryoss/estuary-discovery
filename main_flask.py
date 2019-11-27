#!/usr/bin/env python3
import os

from about import properties
from rest.api.routes import app, fluentd_utils

if __name__ == "__main__":
    host = '0.0.0.0'
    port = properties["port"]
    fluentd_tag = "startup"

    fluentd_utils.emit(fluentd_tag, {"msg": dict(os.environ)})
    fluentd_utils.emit(fluentd_tag, {"msg": {"host": host, "port": port}})
    fluentd_utils.emit(fluentd_tag, {"msg": {
        "fluentd_enabled": str(True if os.environ.get('FLUENTD_IP_PORT') else False).lower(),
        "fluentd_ip": properties["fluentd_ip"],
        "fluentd_port": properties["fluentd_port"]
    }
    })

    app.run(host=host, port=port)
