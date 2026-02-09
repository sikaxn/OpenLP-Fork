# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008 OpenLP Developers                                   #
# ---------------------------------------------------------------------- #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <https://www.gnu.org/licenses/>. #
##########################################################################
"""
The :mod:`~openlp.plugins.planningcenter.lib.planningcenter_api` module contains
an API interface for the V2API for Planning Center Online
"""
import logging
import os
import re
import ssl
import urllib.error
import urllib.request
from json import loads, load, dump

log = logging.getLogger(__name__)


class PlanningCenterAPI:
    """
    The :class:`PlanningCenterAPI` class is Planning Center Online API Class for
    the V2API.
    """
    def __init__(self, application_id, secret):
        """
        Initialize.

        :param application_id: The Application ID from Planning Center Online
        for API authentication.
        :param secret:  The secret key from Planning Center Online for API
        authentication
        """
        self.api_url = "https://api.planningcenteronline.com/services/v2/"
        self.application_id = application_id
        self.secret = secret
        """ airplane mode will cache responses from PCO such that if you request
            the same resource a second time, it will respond with the cached
            response.  This is useful for doing development work on an airplane,
            and for automated testing.
            The production default is False """
        self.airplane_mode = False
        module_directory = os.path.dirname(__file__)
        self.airplane_mode_directory = "{0}/airplane_mode".format(module_directory)
        if os.path.isdir(self.airplane_mode_directory):
            self.airplane_mode = True

    def get_from_services_api(self, url_suffix):
        """
        Gets the response from the API for the provided url_suffix and returns
        the response as an object.

        :param url_suffix: The query part of the URL for the API.  The base is
        in self.api_url, and this suffix is appended to that to make the query.
        """
        airplane_mode_suffix = re.sub(r'\W', '_', url_suffix)
        if len(airplane_mode_suffix) == 0:
            airplane_mode_suffix = 'null'
        airplane_mode_filename = "{0}/{1}.json".format(
            self.airplane_mode_directory, airplane_mode_suffix)
        if self.airplane_mode:
            if os.path.isfile(airplane_mode_filename):
                with open(airplane_mode_filename) as json_file:
                    api_response_object = load(json_file)
                    return api_response_object
            else:
                log.warning("Airplane Mode file not present:{filename}".format(filename=airplane_mode_filename))
        if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
                getattr(ssl, '_create_unverified_context', None)):
            ssl._create_default_https_context = ssl._create_unverified_context
        # create a password manager
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(realm=None, uri=self.api_url,
                                  user=self.application_id, passwd=self.secret)
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        # create "opener" (OpenerDirector instance)
        opener = urllib.request.build_opener(handler)
        # use the opener to fetch a URL
        opener.open(self.api_url + url_suffix)
        # Install the opener.
        # Now all calls to urllib.request.urlopen use our opener.
        urllib.request.install_opener(opener)
        api_response_string = urllib.request.urlopen(self.api_url + url_suffix,
                                                     timeout=30).read()
        api_response_object = loads(api_response_string.decode('utf-8'))
        # write out the responses as json files for airplane mode...
        if self.airplane_mode:
            with open(airplane_mode_filename, 'w') as outfile:
                dump(api_response_object, outfile)
        return api_response_object

    def check_credentials(self):
        """
        Attempts to connect to the base URL (self.api_url) with the credentials
        provided during initialization.
        If successful, it returns the name of the organization for the Planning
        Center Online account.  If failure, it returns an empty string.
        """
        try:
            response = self.get_from_services_api('')
            organization = response['data']['attributes']['name']
            return organization
        except urllib.error.HTTPError as error:
            if error.code == 401:
                return ''
            else:
                raise

    def get_service_type_list(self):
        """
        Gets the list of service types (i.e. sunday morning, sunday evening,
        special events, etc) configured in the Planning Center Online Interface
        and the IDs for those service types.
        """
        # Get ServiceTypes
        service_types_url_suffix = 'service_types'
        service_types = self.get_from_services_api(service_types_url_suffix)
        return service_types['data']

    def get_plan_list(self, service_type_id):
        """
        Returns the list of plans available for a given service_type_id.

        :param service_type_id: The ID of the service_type
        (from self.get_service_type_list) from which to list the available plans.
        """
        if service_type_id:
            self.current_service_type_id = service_type_id
            # get the 10 next future services (including today)
            future_plans_url_suffix = \
                "service_types/{0}/plans?filter=future&per_page=10&order=sort_date".format(service_type_id)
            future_plans = self.get_from_services_api(future_plans_url_suffix)
            # get the 10 most recent past services
            past_plans_url_suffix = \
                "service_types/{0}/plans?filter=past&per_page=10&order=-sort_date".format(service_type_id)
            past_plans = self.get_from_services_api(past_plans_url_suffix)
            plan_list = list(reversed(future_plans['data'])) + past_plans['data']
            return plan_list

    def get_items_dict(self, plan_id):
        """
        Gets all items for a given plan ID (from self.get_plan_list), along with
        their songs and arrangements

        :param plan_id: The ID of the Plan from which to query all Plan Items.
        """
        itemsURLSuffix = "service_types/{0}/plans/{1}/items?include=song,arrangement&per_page=100".\
            format(self.current_service_type_id, plan_id)
        items = self.get_from_services_api(itemsURLSuffix)
        return items
