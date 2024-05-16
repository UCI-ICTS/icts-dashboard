#!/usr/bin/env python3

"""Generalized API Response Object
"""
class ApiResponse:
    """Class for creating the API response object"""
    def __init__(self, operation):
        self.response = {
            "operation": operation,
            "errors": {},
            "successes": []
        }

    def add_error(self, identifier, error_message):
        if identifier not in self.response['errors']:
            self.response['errors'][identifier] = {
                "number_of_errors": 0,
                "error_detail": []
            }
        self.response['errors'][identifier]["number_of_errors"] += 1
        self.response['errors'][identifier]["error_detail"].append(error_message)

    def add_success(self, identifier):
        self.response['successes'].append(identifier)

    def get_response(self):
        return self.response
