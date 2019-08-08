from __future__ import unicode_literals

from celery.decorators import task
import logging
logger = logging.getLogger(__name__)


@task()
def msg91_send_otp(url, payload, headers):
    import http.client, json
    conn = http.client.HTTPConnection("api.msg91.com")
    conn.request(
        "POST",
        url,
        json.dumps(payload),
        headers
    )

    res = conn.getresponse()
    data = res.read()
    logger.debug(data)