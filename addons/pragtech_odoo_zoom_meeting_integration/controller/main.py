from odoo import http
from odoo.http import request
import requests
import base64
import json
import xmlrpc.client as xmlrpc

import json
import logging

import requests
from odoo import http

_logger = logging.getLogger(__name__)


class Custom_Zoom_controller(http.Controller):

    # @api.model
    # def stringToBase64(s):
    #     return base64.b64encode(bytes(s)).decode('utf-8')


    @http.route('/get_auth_code', type="http", auth="public", website=True)
    def get_auth_code(self, **kwarg):
        #print("kwrg         = ",kwarg)
        if kwarg.get('code'):
            '''Get access Token and store in object'''
            zoom_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)], limit=1).company_id
            if zoom_id:

                zoom_id.write({'zoom_auth_code': kwarg.get('code')})

                client_id = zoom_id.zoom_client_id
                client_secret = zoom_id.zoom_client_secret

                combine = client_id + ':' + client_secret
                userAndPass = base64.b64encode(combine.encode()).decode("ascii")
                #print('\n commfd ',userAndPass)

                if zoom_id.zoom_request_token_url:
                    redirect_uri = zoom_id.zoom_request_token_url
                else:
                    redirect_uri = None
                url = "https://zoom.us/oauth/token"
                headers = {'Authorization': 'Basic {}'.format(userAndPass)}

                #print('\n\n ',headers)
                payload = {'grant_type': 'authorization_code',
                           'code': kwarg.get('code'),
                           'redirect_uri':redirect_uri,
                           }

                # print("\n\n PAYLOAD   ",payload)
                response = requests.request("POST", zoom_id.zoom_access_token_url, headers=headers, data=payload)
                #print(response.text.encode('utf8'))
                if response:
                    parsed_token_response = json.loads(response.text.encode('utf8'))
                    #print("\n\n\n OOOOOOOOOoo 0 ",parsed_token_response)

                    zoom_id.write({"zoom_access_token":parsed_token_response.get('access_token'),
                                   "zoom_refresh_token":parsed_token_response.get('refresh_token')})
        return "You can Close this window now"
