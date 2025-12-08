#!/usr/bin/env python3

import requests
import sys


def get_dashboard_token(dashboard_login):
    """
    Get bearer token for API calls
    """
    login_url = f"{dashboard_login['server']}/api/auth/token/login/"
    response = requests.post(login_url, data=dashboard_login['credentials'], verify=dashboard_login['verify'])
    if response.ok:
        dashboard_login['header'] = {'Authorization': f"Bearer {response.json()['access']}"}
        return dashboard_login
    else:
        print(response.text)
        sys.exit(1)


def get_all_dashboard_tables(dashboard_login, dashboard_tables):
    """
    Get all tables to minimize API calls
    """
    if not dashboard_tables:
        tables_url = f"{dashboard_login['server']}/api/search/get_all_tables/"
        response = requests.get(tables_url, verify=dashboard_login['verify'])
        if response.ok:
            return response.json()
        else:
            print(response.text)
            sys.exit(1)
    else:
        for app in dashboard_tables:
            for model in dashboard_tables[app]:
                table_url = f"{dashboard_login['server']}/api/{app}/{model}/all/"
                response = requests.get(table_url, headers=dashboard_login['header'], verify=dashboard_login['verify'])
                if response.ok:
                    dashboard_tables[app][model] = response.json()
                else:
                    print(response.text)
                    sys.exit(1)
        return dashboard_tables


def table_query(table, attribute, key):
    """
    Query any dashboard table for one or many rows based on a provided attribute matching a key
    """
    return_rows = []
    for row in table:
        if row[attribute] == key:
            return_rows.append(row)
    return return_rows