# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class CursoGeneral(models.Model):
	_name = 'curso.general'

	name = fields.Char(string="Nombre")
	name_corto = fields.Char(string="Nombre Corto")
