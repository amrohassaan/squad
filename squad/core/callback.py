import requests
import json


from django.core.exceptions import ValidationError


def __generic_callback_validator__(value, attr, allowed_values):
    if value is None or len(value) == 0:
        raise ValidationError('Callback %s should not be None' % attr)

    if value not in allowed_values:
        raise ValidationError('Callback %s should be one of %s' % (attr, allowed_values))


class callback_methods:
    GET = 'get'
    POST = 'post'

    @classmethod
    def all(cls):
        return [cls.GET, cls.POST]

    @classmethod
    def validator(cls, value):
        return __generic_callback_validator__(value, 'method', cls.all())


class callback_events:
    ON_BUILD_FINISHED = 'on_build_finished'

    @classmethod
    def all(cls):
        return [cls.ON_BUILD_FINISHED]

    @classmethod
    def validator(cls, value):
        return __generic_callback_validator__(value, 'event', cls.all())


def dispatch_callback(callback_object):
    if callback_object.is_sent:
        return

    args = {}

    if callback_object.headers is not None:
        args['headers'] = json.loads(callback_object.headers)

    if callback_object.method == callback_methods.POST and callback_object.payload is not None:
        if callback_object.payload_is_json:
            args['json'] = callback_object.payload
        else:
            args['data'] = json.loads(callback_object.payload)

    request = getattr(requests, callback_object.method)
    response = request(callback_object.url, **args)

    if callback_object.record_response:
        callback_object.response_code = response.status_code
        callback_object.response_content = response.content

    callback_object.is_sent = True
    callback_object.save()
