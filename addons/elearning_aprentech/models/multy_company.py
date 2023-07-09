# -*- coding: utf-8 -*-

import logging

from ast import literal_eval
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.misc import ustr

from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.addons.auth_signup.models.res_partner import SignupError, now

_logger = logging.getLogger(__name__)


class SlideChannel(models.Model):
    _inherit = "slide.channel"

    company_id = fields.Many2one('res.company', string='Company',  default=lambda self: self.env.company)

class SlideChannelTag(models.Model):
    _inherit = "slide.channel.tag"

    company_id = fields.Many2one('res.company', string='Company',  default=lambda self: self.env.company)

class SlideChannelTagGroup(models.Model):
    _inherit = "slide.channel.tag.group"

    company_id = fields.Many2one('res.company', string='Company',  default=lambda self: self.env.company)

class SlideTag(models.Model):
    _inherit = "slide.tag"

    company_id = fields.Many2one('res.company', string='Company',  default=lambda self: self.env.company)

class Forum(models.Model):
    _inherit = "forum.forum"

    company_id = fields.Many2one('res.company', string='Company',  default=lambda self: self.env.company)

class Post(models.Model):
    _inherit = "forum.post"

    company_id = fields.Many2one('res.company', string='Company',  default=lambda self: self.env.company)

class Slide(models.Model):
    _inherit = "slide.slide"

    company_id = fields.Many2one('res.company', string='Company',  default=lambda self: self.env.company)

class Rating(models.Model):
    _inherit = "rating.rating"

    company_id = fields.Many2one('res.company', string='Company',  default=lambda self: self.env.company)

class Survey(models.Model):
    _inherit = "survey.survey"

    company_id = fields.Many2one('res.company', string='Company',  default=lambda self: self.env.company)

class Question(models.Model):
    _inherit = "slide.question"

    company_id = fields.Many2one('res.company', string='Company',  default=lambda self: self.env.company)

class Question(models.Model):
    _inherit = "calendar.event"

    company_id = fields.Many2one('res.company', string='Company',  default=lambda self: self.env.company)

"""redefinicion de campos base """

class ResPartnerr(models.Model):
    _inherit = "res.partner"

    signup_token = fields.Char(groups="")
    signup_type = fields.Char(groups="")
    signup_expiration = fields.Datetime(groups="")

class SlideChannelInvite(models.TransientModel):
    _inherit = 'slide.channel.invite'

    company_id = fields.Many2one('res.company', string='Company',  default=lambda self: self.env.company)


class Users(models.Model):
	_inherit = 'res.users'

	dni = fields.Char(string='DNI')
