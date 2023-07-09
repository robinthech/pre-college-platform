# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from datetime import datetime, date, time, timedelta

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class EstudianteCarrera(models.Model):
	_name = 'estudiante.carrera'

	name = fields.Char(string='Carrera')
	estudiantes_ids = fields.One2many(
		"res.users", "carrera_id", string="estudiantes")


class Apoderado(models.Model):
	_name = 'apoderado'

	name = fields.Char(string='Nombre de Apoderado')
	email = fields.Char(string='Correo de Apoderado')


class Reuniones(models.Model):
	_name = 'reuniones'
	_order = "start_time desc, id desc"

	name = fields.Char(string='Nombre',compute="_compute_name")
	curso_id = fields.Many2one('slide.channel', string='Curso')
	curso_general_id = fields.Many2one('curso.general', string='Curso',store=True)

	profesor_id = fields.Many2one(
		'res.users', string='Profesor', index=True, required=True)
	grupo_alumnos = fields.Many2one(
		'grupo.alumnos', required=True, string="Aula")
	start_time = fields.Datetime(string='Fecha Inicio', index=True,store=True)
	fecha = fields.Date(compute="_compute_dia",
						string='Fecha Inicio', index=True,store=True)
	end_date_time = fields.Datetime(string='Fecha FIn', index=True,store=True)
	meet_url = fields.Text(string='URL')
	meet_id = fields.Text(string='ID')
	meet_pwd = fields.Text(string='Password')

	horario_id = fields.Many2one(
		'horario', string='HORARIO', index=True, required=True)

	@api.depends("start_time")
	def _compute_dia(self):
		for record in self:
			if record.start_time:
				record.fecha = datetime.date(record.start_time)
				record.end_date_time = record.start_time + timedelta(hours=1)

	@api.depends("curso_general_id")
	def _compute_name(self):
		for record in self:
			if record.curso_general_id:
				record.name = record.curso_general_id.name

	@api.onchange("end_date_time")
	def cambio_fecha_inicio(self):
		for record in self:
			res = {}
			if record.start_time and record.end_date_time:
				if record.start_time > record.end_date_time:
					res ={'warning':{
						'title':_('ALERTA'),
						'message':_('La Fecha Inicio debe ser antes de la Fecha Fin')
						}
					}
					return res

class ResUsers(models.Model):
	_inherit = 'res.users'

	carrera_id = fields.Many2one("estudiante.carrera", string='Carrera')
	apoderado_email = fields.Char(
		string="Correo de Apoderado", related="apoderado_id.email")
	apoderado_id = fields.Many2one("apoderado", string='Apoderado')
	grupos_eval_ids = fields.One2many(
		'res.users.line', 'user_id',domain=[('grupo_alumnos_id.tipo_grupo','=','grupo')], string='Grupo')
	aula_eval_ids = fields.One2many(
		'res.users.line', 'user_id',domain=[('grupo_alumnos_id.tipo_grupo','=','aula')], string='Aula')


class CarreraRespuesta(models.Model):
	_inherit = 'respuesta.simulacro'

	carrera_id = fields.Many2one(
		"estudiante.carrera", string='Carrera', related="user_id.carrera_id")

class InheritSLide(models.Model):
	_inherit = 'slide.channel'

	grupos_aula_id = fields.Many2one("grupo.alumnos", string='Aula')
	curso_general_id = fields.Many2one("curso.general", string='Curso')
	name = fields.Char(compute="onchange_curso_name", string='Name', translate=True, required=True)

	@api.depends("curso_general_id")
	def onchange_curso_name(self):
		for record in self:
			if record.curso_general_id:
				record.name = record.curso_general_id.name


class Inheritgrupo(models.Model):
	_inherit = 'grupo.alumnos'

	tipo_grupo = fields.Selection([('aula', 'Aula'),('grupo', 'Grupo')], string='Aula / Grupo', default='aula', help="Aula / Grupo")
	cursos_ids = fields.One2many('slide.channel', 'grupos_aula_id', string='Cursos')
	estado = fields.Selection([
			('activo', 'Activo'),
			('inactivo', 'Inactivo'),
			], default='activo', string='Estado')

	def activar_evaluacion(self):
		for record in self:
			record.estado = 'activo'

	def inactivar_evaluacion(self):
		for record in self:
			record.estado = 'inactivo'

	def action_cursos_aula(self):
		for record in self:
			crear_partner_slide = True
			for usuario in record.users_ids:
				for obj_curso in record.cursos_ids:
					crear_partner_slide = True
					for participante in obj_curso.channel_partner_ids:
						if usuario.user_id.partner_id.id == participante.partner_id.id:
							crear_partner_slide = False
					if crear_partner_slide:
						obj_curso.channel_partner_ids.create({'partner_id':usuario.user_id.partner_id.id,"channel_id":obj_curso.id})

		return {
			"type": "ir.actions.act_window",
			"target": "current",
			"res_model": "slide.channel",
			"views": [[False, "search"], [self.env.ref('website_examenes_user.cursos_aula_elearning_kanban').id, "kanban"], [self.env.ref('website_examenes_user.cursos_aula_elearning_tree').id, "list"], [self.env.ref('website_examenes_user.cursos_aula_elearning_form').id, "form"]],
			"domain": [["grupos_aula_id", "=", self.id]],
			"context": {'default_grupos_aula_id':  self.id},
			"name": u"Cursos"
		}

class InheritResUserLine(models.Model):
	_inherit = 'res.users.line'

	def create(self, values):
		record = super(InheritResUserLine, self).create(values)
		create_curso_partner = True
		_logger.info("create")
		_logger.info(values)

		for line_creacion in range(len(values)) :
			grupo_alumnos_id = self.env["grupo.alumnos"].sudo().search([('id',  '=',int(values[line_creacion]["grupo_alumnos_id"]))])
			usuario_id = self.env["res.users"].sudo().search([('id',  '=',int(values[line_creacion]["user_id"]))])
			for obj_curso in grupo_alumnos_id.cursos_ids:
				 crear_partner_slide = True
				 for participante in obj_curso.channel_partner_ids:
					 if usuario_id.partner_id.id == participante.partner_id.id:
						 crear_partner_slide = False
				 if crear_partner_slide:
					 obj_curso.channel_partner_ids.create({'partner_id':usuario_id.partner_id.id,"channel_id":obj_curso.id})

		return record

	def unlink(self):
		for record in self:
			slides_channel_partner_id = self.env["slide.channel.partner"].sudo().search([('channel_id.grupos_aula_id','=',record.grupo_alumnos_id.id),("partner_id","=",record.user_id.partner_id.id)])
			for line in slides_channel_partner_id:
				line.unlink()
		return super(InheritResUserLine, self).unlink()
