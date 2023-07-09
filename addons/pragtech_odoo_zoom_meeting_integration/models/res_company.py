# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime
import requests
import base64
from dateutil.parser import parse as duparse
from odoo import api, fields, models
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def _default_update_datetime(self):
        date = str(datetime.strptime("1870-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"))
        return datetime.strptime("1870-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

    # Company level Zoom Configuration fields
    zoom_client_id = fields.Char(help="The client ID you obtain from the developer dashboard.", string="Consumer Key")
    zoom_client_secret = fields.Char(help="The client secret you obtain from the developer dashboard.", string="Consumer Secret")

    zoom_auth_base_url = fields.Char('Authorization URL', default="https://zoom.us/oauth/authorize",
                                   help="User authenticate uri")
    zoom_access_token_url = fields.Char('Authorization Token URL', default="https://zoom.us/oauth/token",
                                      help="Exchange code for refresh and access tokens")
    zoom_request_token_url = fields.Char('Redirect URL', default="http://localhost:8069/get_auth_code",
                                       help="One of the redirect URIs listed for this project in the developer dashboard.")
    # used for api calling, generated during authorization process.
    zoom_auth_code = fields.Char('Auth Code', help="")
    zoom_access_token = fields.Char('Access Token', help="The token that must be used to access the ZOOM API.")
    zoom_refresh_token = fields.Char('Refresh Token')

    # @api.multi
    def sanitize_data(self, field_to_sanitize):
        '''
            This method sanitizes the data to remove UPPERCASE and
            spaces between field chars
            @params : field_to_sanitize(char)
            @returns : field_to_sanitize(char)
        '''
        return field_to_sanitize.strip()

    # @api.multi
    def get_headers(self, type=False):
        headers = {}
        headers['Authorization'] = 'Bearer ' + str(self.zoom_access_token)
        headers['accept'] = 'application/json'
        if type:
            headers['Content-Type'] = 'application/json'
        else:
            headers['Content-Type'] = 'text/plain'
        return headers

    # @api.multi
    def refresh_token_from_access_token(self):
        '''
            This method gets access token from refresh token
            and grant type is refresh_token,
            This token will be long lived.
        '''
        if not self.zoom_refresh_token:
            raise Warning("Please authenticate first.")
        payload = {}
        headers = {
            'content-type': "application/x-www-form-urlencoded"
        }
        zoom_refresh_token = self.sanitize_data(self.zoom_refresh_token)
        zoom_client_id = self.sanitize_data(self.zoom_client_id)
        zoom_client_secret = self.sanitize_data(self.zoom_client_secret)
        zoom_access_token_url = self.sanitize_data(self.zoom_access_token_url)

        combine = zoom_client_id + ':' + zoom_client_secret
        userAndPass = base64.b64encode(combine.encode()).decode("ascii")
        #print('\n commfd ', userAndPass)

        headers = {'Authorization': 'Basic {}'.format(userAndPass)}

        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': zoom_refresh_token,
        }
        refresh_token_response = requests.request("POST", zoom_access_token_url, headers=headers, data=payload)
        #print(refresh_token_response.text.encode('utf8'))
        if refresh_token_response.status_code == 200:
            try:
                # try getting JSON repr of it
                parsed_response = refresh_token_response.json()
                if 'access_token' in parsed_response:
                    _logger.info("REFRESHING ACCESS TOKEN {}".format(parsed_response.get('access_token')))
                    self.zoom_access_token = parsed_response.get('access_token')
                    self.zoom_refresh_token = parsed_response.get('refresh_token')
            except Exception as ex:
                raise Warning("EXCEPTION : {}".format(ex))
        elif refresh_token_response.status_code == 401:
            _logger.error("Access token/refresh token is expired")
        else:
            raise Warning("We got a issue !!!! Desc : {}".format(refresh_token_response.text))

    @api.model
    def _scheduler_login_authentication(self):
        company_id = self.env['res.users'].search([('id', '=', self.env.user.id)], limit=1).company_id
        if self.env.user.company_id:
            self.env.user.company_id.refresh_token_from_access_token()

    # @api.multi
    def login(self):
        url = self.zoom_auth_base_url + '?&response_type=code&client_id=' + self.zoom_client_id + '&redirect_uri=' + self.zoom_request_token_url
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new"
        }
