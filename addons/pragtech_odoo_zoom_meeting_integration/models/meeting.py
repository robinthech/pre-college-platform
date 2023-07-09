from odoo import fields, models, api
import datetime
import calendar
# from datetime import timedelta
# from datetime import datetime
import requests

from odoo.exceptions import UserError

class CustomZoomMeet(models.Model):
    _inherit = 'calendar.event'
    _description = 'Zoom Meet Details'

    topic_name = fields.Char(string='Meet Topic')
    start_time = fields.Datetime(string='Start Date', index=True)
    password= fields.Char(string='Meet Password')
    agenda = fields.Text(string='Meeting Agenda')
    end_date_time=fields.Datetime(string='End Date', index=True)
    create_flag= fields.Boolean('Flag' ,default=False)
    meet_flag= fields.Boolean('Add Zoom Meet' ,default=False)

    meet_url= fields.Text(string='Meet URL')
    meet_id = fields.Text(string='Meet ID')
    meet_pwd= fields.Text(string='Meet Password')
    meet_data= fields.Text(string='Meet DATA',readonly=True)



    def post_request_meet(self):
        #print("post_request_meet ",self)
        #print("\n self.meet_url ",self.meet_url)
        url = self.meet_url
        return {
            'type': 'ir.actions.act_url',
            'url': url,
        }


    @api.model
    def create(self, vals_list):
        #print("\n\n\n Self ",self)
        #print("\n\n val -- ",vals_list)
        if vals_list.get('meet_flag'):
            vals_list=self.post_request_meet1(vals_list)
        return super(CustomZoomMeet, self).create(vals_list)


    def post_request_meet1(self,vals_list):
        #print("post_request_meet ",self)
        company_id = self.env['res.users'].search([('id', '=', self._context.get('uid'))]).company_id
        if self.env.user.company_id:
            self.env.user.company_id.refresh_token_from_access_token()

        if company_id.zoom_access_token and company_id.zoom_refresh_token:
            #print("HJJJJJJJJJJJJJJJJJJJJJJJJ ")

            zoom_access_token = company_id.sanitize_data(company_id.zoom_access_token)


            bearer = 'Bearer '+zoom_access_token
            payload = {}
            headers = {
                'Content-Type': "application/json",
                'Authorization':bearer
            }
            # start_time = datetime.strptime(str(self.start_time), '%Y-%m-%d %H:%M:%S')
            # end_date_time = datetime.strptime(str(self.end_date_time), '%Y-%m-%d %H:%M:%S')

            #print("\n\n DATE !!! ",self.start_time)
            #print("\n\n DATE 333 !!! ",str(self.start_time))


            data = {
                      "topic":str(vals_list.get('name')),
                      "type": "2",
                      "start_time": str(vals_list.get('start_datetime')),
                      "duration": "4",
                      "timezone": "NA",
                      "password": str(vals_list.get('password')),
                      "agenda": str(vals_list.get('description')),
                      "recurrence": {
                        "type": "2",
                        "repeat_interval": "3",
                        "end_times": "5",
                        "end_date_time": str(vals_list.get('end_date_time'))
                      },
                      "settings": {
                        "host_video": True,
                        "participant_video":True,
                        "registrants_email_notification": True

                    }
                }
            #print("\n\n yyyyy \n\n",data,"\n\n\n")

            meet_response = requests.request("POST", "https://api.zoom.us/v2/users/me/meetings", headers=headers, json=data)
            #print("\n\n meet_response ",meet_response)

            #print("\n\n meet_response ",meet_response.text.encode('utf8'))
            if meet_response.status_code == 200 or meet_response.status_code == 201:

                data_rec=meet_response.json()

                #print("\n\n data_rec ", data_rec)

                #print("\n join_url join_url ",data_rec.get('join_url'))
                vals_list['meet_url']=data_rec.get('join_url')
                vals_list['meet_id']=data_rec.get('id')
                vals_list['meet_pwd']=data_rec.get('password')

                vals_list['create_flag']=True
                vals_list['meet_data']=data_rec
                return vals_list

            elif meet_response.status_code == 401:
                raise UserError("Please Authenticate with Zoom Meet.")


