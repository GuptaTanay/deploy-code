import logging
logger = logging.getLogger(__name__)


def push(channel, data, event='misc', expo=False):

    assert None not in [channel, event, data]

    from square1.utils.configuration import get_configuration
    import pusher

    c = get_configuration()

    # Send to web clients
    try:

        data['icon'] = c.merchant_favicon_large.url if c.merchant_logo_large else ""

        pusher_client = pusher.Pusher(
            app_id=c.pusher_app_id,
            key=c.pusher_key,
            secret=c.pusher_secret,
            cluster=c.pusher_cluster,
            ssl=True
        )

        pusher_client.trigger(channel, event, data)
    except Exception as e:
        logger.error(e)
        pass

    # Send to mobile clients
    if expo:
        try:
            import requests, json
            from config.models import ModelKeyVal

            recipients = ModelKeyVal.objects.filter(key='expo_notification_token')
            chunks = [recipients[x:x + 100] for x in range(0, len(recipients), 100)]

            for chunk in chunks:

                data = [
                    {
                        'to': recipient.value,
                        'body': data['body'],
                        'title': data['title'],
                        'sound': 'default',
                        'badge': 1,
                        'data': data['extra_data']
                    } for recipient in chunk
                ]
                data = json.dumps(data)

                requests.post("https://exp.host/--/api/v2/push/send", headers={
                        'host': 'exp.host',
                        'accept': 'application/json',
                        'accept-encoding': 'gzip, deflate',
                        'content-type': 'application/json'
                    }, data=data)
        except Exception as e:
            logger.error(e)
