#!/usr/bin/env python
# search/apis.py

import json
from django.db.models import Q
from django.contrib.auth.models import User
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from itertools import chain
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

class SearchTablesAPI(APIView):
    """
    """

    permission_classes = [AllowAny]

    def get(self, request) -> Response:
        
        query = Q()

        for field in return_values:
           values = request.GET.getlist(field)
           if values:
              field_query = Q()
              for value in values:
                    field_query |= Q(**{f'{field}__icontains': value})
              query &= field_query

        return_bco = viewable_bcos.filter(query)
        bco_data = chain(return_bco.values(*return_values))
        return Response(status=status.HTTP_200_OK, data=bco_data)