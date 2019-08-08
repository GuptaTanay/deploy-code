from __future__ import absolute_import
from __future__ import unicode_literals
from builtins import str
from builtins import object
import logging
logger = logging.getLogger(__name__)


class Message91(object):
    '''
    Send an SMS via the message 91 API.

    Params:

    1. Country code: "+91"
    2. To: [+918527661224,8527666906]
    3. Text: "message"
    '''

    key = '287831ACOT0B2VW85d42d24b'

    def send_otp(self, country=None, to=None, player=None):
        from comms.models import SmsTemplate
        from comms.models import SMS
        from player.models import OTP
        template = SmsTemplate.objects.filter(slug="send-otp").first()
        template = template.body

        for mobile in to:

            logger.debug("Trying to send OTP to number " + str(to))

            SMS.objects.create(message=template, to=country+mobile)

            otp = OTP.create(player)

            template = template.replace("*|otp|*", otp.otp)

            payload = {
                "sender": "FQUIZZ",
                "message": template,
                "mobile": country + mobile,
                "otp": otp.otp
            }

            headers = {
                "authkey": self.key,
                "content-type": "application/json"
            }

            url = "/api/sendotp.php?"
            for key in list(payload.keys()):
                url += key + "=" + payload[key] + "&"

            from .tasks import msg91_send_otp
            msg91_send_otp.delay(url, payload, headers)

        return None