#!/usr/bin/env python
# server/common/api_mixins.py

from drf_yasg import openapi
from rest_framework.exceptions import ValidationError


SUPPRESS_FIELDS_PARAMETER = openapi.Parameter(
    name="suppress",
    in_=openapi.IN_QUERY,
    description=(
        "Comma-separated serializer field names to omit from every record "
        "in the response. Example: `created_at, needs_review`."
    ),
    required=False,
    type=openapi.TYPE_STRING,
)

class SuppressSerializerFieldsMixin:
    """
    Allow selected serializer fields to be omitted from list `/all/` responses.

    Examples:

        ?suppress=field_one,field_two

        ?suppress=field_one&suppress=field_two
    """

    suppress_query_parameter = "suppress"
    suppress_actions = {"list_all", "list"}

    def get_suppressed_fields(self) -> set[str]:
        raw_values = self.request.query_params.getlist(
            self.suppress_query_parameter
        )

        return {
            field_name.strip()
            for raw_value in raw_values
            for field_name in raw_value.split(",")
            if field_name.strip()
        }

    def suppress_mapping_fields(self, data: dict) -> dict:
        """
        Return a copy of a serialized record with requested fields removed.
        """
        if getattr(self, "action", None) not in self.suppress_actions:
            return data

        suppressed_fields = self.get_suppressed_fields()

        if not suppressed_fields:
            return data

        return {
            key: value
            for key, value in data.items()
            if key not in suppressed_fields
        }
    
    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)

        if getattr(self, "action", None) not in self.suppress_actions:
            return serializer

        suppressed_fields = self.get_suppressed_fields()

        if not suppressed_fields:
            return serializer

        # `many=True` returns a ListSerializer. Its model serializer is `child`.
        model_serializer = getattr(serializer, "child", serializer)
        available_fields = set(model_serializer.fields)

        unknown_fields = suppressed_fields - available_fields

        if unknown_fields:
            raise ValidationError({
                self.suppress_query_parameter: [
                    "Unknown field(s): "
                    + ", ".join(sorted(unknown_fields))
                ]
            })

        for field_name in suppressed_fields:
            model_serializer.fields.pop(field_name, None)

        return serializer
