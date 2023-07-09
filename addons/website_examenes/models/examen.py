# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class PlantillaSlide(models.Model):
	_name = 'plantilla.slide'

	curso_id = fields.Many2one('slide.channel', string='Curso')
	curso_general_id = fields.Many2one('curso.general', string='Curso',store=True)

	preguntas = fields.Integer(string='Cantidad de preguntas')
	plantilla_id = fields.Many2one('plantilla', string='Plantilla')


class Plantilla(models.Model):
	_name = 'plantilla'

	name = fields.Char(translate=True, required=True,string="Nombre de Plantilla")
	pts_correcto = fields.Float(string='Puntaje por pregunta Correcta', default=4, digits=(3, 3))
	pts_incorrecto = fields.Float(string='Puntaje por pregunta Incorrecta', default=-1, digits=(3, 3))
	pts_blanco = fields.Float(string='Puntaje por pregunta Blanco', default=0, digits=(3, 3))
	numeracion = fields.Selection([
		('normal', 'Normal'),
		('curso', 'Por Curso')],
		string='Numeración',
		default='normal',
		help="Numeración de las preguntas.")

	cursos_ids = fields.One2many('plantilla.slide', 'plantilla_id', string='Cursos')


class Examen(models.Model):
	_name = 'examen'
	_order = "create_date desc, id desc"

	name = fields.Char(translate=True, required=True, string="Titulo")
	plantilla_id = fields.Many2one('plantilla', string="Plantilla")

	exam_file_ids = fields.Many2many("ir.attachment", "exam_exam_attach_rel", "exam_file_id", "attachment_id", string="Examen")
	solve_file_ids = fields.Many2many("ir.attachment", "exam_solve_attach_rel", 'solve_file_id', "attachment_id", string="Solucionario")

	claves_ids = fields.One2many("claves","examen_id", string="Claves")

	pts_correcto = fields.Float(string='Puntaje por pregunta Correcta', default=4, digits=(3, 3))
	pts_incorrecto = fields.Float(string='Puntaje por pregunta Incorrecta', default=-1, digits=(3, 3))
	pts_blanco = fields.Float(string='Puntaje por pregunta Blanco', default=0, digits=(3, 3))
	numeracion = fields.Selection([
		('normal', 'Normal'),
		('curso', 'Por Curso')],
		string='Numeración',
		default='normal',
		help="Numeración de las preguntas.")

	@api.onchange("plantilla_id")
	def claves_plantilla(self):
		for record in self:
			record.pts_correcto = record.plantilla_id.pts_correcto
			record.pts_incorrecto = record.plantilla_id.pts_incorrecto
			record.pts_blanco = record.plantilla_id.pts_blanco
			record.numeracion = record.plantilla_id.numeracion
			sequence = 1
			for line in record.plantilla_id.cursos_ids:
				record.claves_ids.create({"curso_general_id":line.curso_general_id.id,"is_curso":True,'examen_id':self.id})
				if record.numeracion =='curso':
					sequence = 1
				for x in range(line.preguntas):
					record.claves_ids.create({'sequence':sequence,'clave_a':True, "is_curso":False, 'examen_id':self.id})
					sequence = sequence  + 1


class Claves(models.Model):
	_name = 'claves'

	examen_id = fields.Many2one('examen', string="Examen")
	curso_id = fields.Many2one('slide.channel', string="Curso")
	curso_general_id = fields.Many2one('curso.general', string='Curso',store=True)
	
	clave_a = fields.Boolean("A")
	clave_b = fields.Boolean("B")
	clave_c = fields.Boolean("C")
	clave_d = fields.Boolean("D")
	clave_e = fields.Boolean("E")
	sequence = fields.Integer(string="N° Pregunta")
	is_curso = fields.Boolean('Is a category', default=False)

	@api.onchange("clave_a")
	def clave_unica_a(self):
		for record in self:
			if record.clave_a:
				record.clave_b = False
				record.clave_c = False
				record.clave_d = False
				record.clave_e = False


	@api.onchange("clave_b")
	def clave_unica_b(self):
		for record in self:
			if record.clave_b:
				record.clave_a = False
				record.clave_c = False
				record.clave_d = False
				record.clave_e = False

	@api.onchange("clave_c")
	def clave_unica_c(self):
		for record in self:
			if record.clave_c:
				record.clave_b = False
				record.clave_a = False
				record.clave_d = False
				record.clave_e = False

	@api.onchange("clave_d")
	def clave_unica_d(self):
		for record in self:
			if record.clave_d:
				record.clave_b = False
				record.clave_c = False
				record.clave_a = False
				record.clave_e = False

	@api.onchange("clave_e")
	def clave_unica_e(self):
		for record in self:
			if record.clave_e:
				record.clave_b = False
				record.clave_c = False
				record.clave_d = False
				record.clave_a = False
