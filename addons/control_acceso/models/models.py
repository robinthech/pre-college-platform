import logging
import datetime
from datetime import datetime, date, time, timedelta

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.http import request
import pytz
_logger = logging.getLogger(__name__)


class Ciclo(models.Model):
	_name = 'ciclo'

	name = fields.Char(string="Ciclo")
	fecha_inicio = fields.Date(string='Fecha de Inicio', required=True)
	fecha_fin = fields.Date(string='Fecha de Fin', required=True)
	users_ids = fields.One2many('res.users.ciclo', 'ciclo_id', string='Alumnos',store=True)

	@api.onchange("fecha_inicio","fecha_fin")
	def cambio_fecha_inicio(self):
		for record in self:
			res = {}
			if record.fecha_inicio and record.fecha_fin:
				if record.fecha_inicio >= record.fecha_fin:
					record.fecha_inicio = record.feusuario.ciclo_eval_idscha_fin - timedelta(hours=1)
					res ={'warning':{
						'title':_('ALERTA'),
						'message':_('La Fecha de Inicio debe ser antes de la Fecha de Fin')
						}
					}
					return res

	def cron_archivar_ciclo(self):
		# cron para fecha fin mayor a fecha actual
		# archivar contactos y estudiantes pertenecientes al ciclo
		usuarios = self.env['res.users'].sudo().search([])
		fecha_actual = datetime.now().date()
		for usuario in usuarios:
			res_user_ciclos = self.env['res.users.ciclo'].sudo().search([('user_id', '=', usuario.id)])
			ciclos = self.env["ciclo"].sudo().search([('id', 'in', [(rec.ciclo_id.id) for rec in res_user_ciclos])],order='fecha_fin desc')
			if (len(ciclos)!=0):
				_logger.info('entra')
				if ciclos[0].fecha_fin < fecha_actual:
					_logger.info('menor')
					usuario.active = False
					usuario.partner_id.active = False
				else:
					_logger.info('mayor')
					usuario.active = True
					usuario.partner_id.active = True


class ResUserCicloLines(models.Model):
	_name = 'res.users.ciclo'

	name = fields.Char(string="Nombre",related="ciclo_id.name")
	ciclo_id = fields.Many2one('ciclo', string='Ciclo', index=True, required=True,store=True)
	user_id = fields.Many2one('res.users', string='Alumno', index=True, required=True,store=True)
	active = fields.Boolean(string="Active",related="user_id.active")
	

class ResUsersCiclo(models.Model):
	_inherit = 'res.users'

	ciclo_eval_ids = fields.One2many(
		'res.users.ciclo', 'user_id', string='Ciclo', index=True,store=True)
