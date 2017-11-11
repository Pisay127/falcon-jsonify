import json
import re
import sys

import falcon


class Middleware(object):
    def __init__(self, help_messages=True):
        """
        help_messages: display validation/error messages in the response in case of bad requests
        """
        self.debug = bool(help_messages)
        self.req = None

        if sys.version_info[0] == 3:
            # We are running under Python 3.x.
            self.pystring = str
        else:
            # We are running under Python 2.x.
            self.pystring = unicode

    def bad_request(self, title, description):
        """
        Responds with 400 Bad Request
        """
        if self.debug:
            raise falcon.HTTPBadRequest(title, description)
        else:
            raise falcon.HTTPBadRequest()

    def get_json(self, field, default=None, **validators):
        """
        Helper to access JSON fields in the request body
        Optional built-in validators
        """
        value = None

        if default:
            value = default
        elif field not in self.req.json:
            self.bad_request("Missing JSON field", "Field '{}' is required".format(field))
        else:
            value = self.req.json[field]

        return self._validate(field, value, **validators)

    def _validate(self, field, value, data_type=None, min_value=None, max_value=None, match=None):
        """
        JSON field validators:

        data_type  data type
        default    value used if field is not provided in the request body
        min_value  minimum length (str) or value (int, float)
        max_value  maximum length (str) or value (int, float)
        match      regular expression
        """
        err_title = "Validation error"

        if data_type:
            if data_type == str and type(value) == self.pystring:
                pass

            elif type(value) is not data_type:
                msg = "Data type for '{}' is '{}' but should be '{}'"
                self.bad_request(err_title, msg.format(field, type(value).__name__, data_type.__name__))

        if type(value) == self.pystring:
            if min_value and len(value) < min_value:
                self.bad_request(err_title, "Minimum length for '{}' is '{}'".format(field, min_value))

            if max_value and len(value) > max_value:
                self.bad_request(err_title, "Maximum length for '{}' is '{}'".format(field, max_value))
        elif type(value) in (int, float):
            if min_value and value < min_value:
                self.bad_request(err_title, "Minimum value for '{}' is '{}'".format(field, min_value))

            if max_value and value > max_value:
                self.bad_request(err_title, "Maximum value for '{}' is '{}'".format(field, max_value))

        if match and not re.match(match, re.escape(value)):
            self.bad_request(err_title, "'{}' does not match Regex: {}".format(field, match))

        return value

    def process_request(self, req, resp):
        """
        Middleware request
        """
        if not req.content_length:
            return

        body = req.stream.read()
        req.json = {}
        self.req = req
        req.get_json = self.get_json  # helper function

        try:
            req.json = json.loads(body.decode('utf-8'))
        except ValueError:
            self.bad_request("Malformed JSON", "Syntax error")
        except UnicodeDecodeError:
            self.bad_request("Invalid encoding", "Could not decode as UTF-8")

    def process_response(self, req, resp, resource, req_succeeded):
        """
        Middleware response
        """
        try:
            resp.body = json.dumps(resp.json)
        except AttributeError:
            pass
