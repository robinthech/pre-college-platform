# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import datetime
from datetime import datetime, date, time, timedelta

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.http import request
import pytz
_logger = logging.getLogger(__name__)


class Evaluacion(models.Model):
	_name = 'evaluacion'
	_order = "fecha_inicio desc, id desc"

	name = fields.Char(translate=True, required=True, string="Titulo")
	grupo_alumnos = fields.Many2one('grupo.alumnos', required=True, string="Grupo de Alumnos")
	fecha_inicio = fields.Datetime('Fecha de Inicio', required=True, store=True)
	fecha_fin = fields.Datetime('Fecha de Fin', required=True, store=True)
	duracion = fields.Integer('Duración (min)', store=True)
	examen_id = fields.Many2one('examen', string="Examen", store=True)
	bloques_ids = fields.One2many('evaluacion.line', 'evaluacion_id', string='Bloques')
	respuestas_ids = fields.One2many('respuesta', 'evaluacion_id', string='Respuestas')
	respuestas_unidas_ids = fields.One2many('respuesta.simulacro', 'evaluacion_id', string='Respuestas')
	answer_done_count = fields.Integer("Respuestas",compute="_compute_respuesta")
	answer_done_count_simulacro = fields.Integer("Respuestas",compute="_compute_respuesta")
	state = fields.Selection([
			('borrador', 'Borrador'),
			('publico', 'Publico'),
			('cerrado', 'Cerrado'),
			], default='borrador', string='Estado',)

	tipo_evaluacion = fields.Selection([
		('diario', 'Diario'),
		('semanal', 'Semanal'),
		('simulacro', 'Simulacro')],
		string='Tipo de Prueba',
		help="Numeración de las preguntas.", required=True)

	@api.onchange("tipo_evaluacion")
	def tipo_evaluacion_function(self):
		for record in self:
			if record.tipo_evaluacion == 'diario':
				record.duracion = 60
				fecha_actual = datetime.now()
				record.fecha_inicio = fecha_actual.replace(hour=17, minute=0, second=0)
				record.fecha_fin = fecha_actual.replace(hour=22, minute=0, second=0)+ timedelta(hours=5)
			elif record.tipo_evaluacion == 'semanal':
				record.duracion = 70
				fecha_actual = datetime.now()
				record.fecha_inicio = fecha_actual.replace(hour=17, minute=0, second=0)
				record.fecha_fin = fecha_actual.replace(hour=22, minute=0, second=0)+ timedelta(hours=5)
				if len(record.bloques_ids)==0:
					record.bloques_ids.create({'name':'APTITUD ACADEMICA', 'duracion':50, 'evaluacion_id':self.id})
					record.bloques_ids.create({'name':'MATEMATICA', 'duracion':20, 'evaluacion_id':self.id})
					record.bloques_ids.create({'name':'HUMANIDADES', 'duracion':30, 'evaluacion_id':self.id})
					record.bloques_ids.create({'name':'CIENCIAS NATURALES', 'duracion':60, 'evaluacion_id':self.id})

				suma = 0
				for line in record.bloques_ids:
					suma = suma + line.duracion
				record.duracion = suma
			elif record.tipo_evaluacion == 'simulacro':
				record.duracion = 60
				fecha_actual = datetime.now()
				dia_semana = datetime.weekday(fecha_actual)

				if dia_semana==0:
					record.fecha_inicio = fecha_actual.replace(hour=17, minute=0, second=0)
					record.fecha_fin = fecha_actual.replace(hour=22, minute=0, second=0) + timedelta(days=4, hours=5)
				elif dia_semana==1:
					record.fecha_inicio = fecha_actual.replace(hour=17, minute=0, second=0) + timedelta(days=6)
					record.fecha_fin = fecha_actual.replace(hour=22, minute=0, second=0) + timedelta(days=10, hours=5)
				elif dia_semana==2:
					record.fecha_inicio = fecha_actual.replace(hour=17, minute=0, second=0) + timedelta(days=5)
					record.fecha_fin = fecha_actual.replace(hour=22, minute=0, second=0) + timedelta(days=9, hours=5)
				elif dia_semana==3:
					record.fecha_inicio = fecha_actual.replace(hour=17, minute=0, second=0) + timedelta(days=4)
					record.fecha_fin = fecha_actual.replace(hour=22, minute=0, second=0) + timedelta(days=8, hours=5)
				elif dia_semana==4:
					record.fecha_inicio = fecha_actual.replace(hour=17, minute=0, second=0) + timedelta(days=3)
					record.fecha_fin = fecha_actual.replace(hour=22, minute=0, second=0) + timedelta(days=7, hours=5)
				elif dia_semana==5:
					record.fecha_inicio = fecha_actual.replace(hour=17, minute=0, second=0) + timedelta(days=2)
					record.fecha_fin = fecha_actual.replace(hour=22, minute=0, second=0) + timedelta(days=6, hours=5)
				elif dia_semana==6:
					record.fecha_inicio = fecha_actual.replace(hour=17, minute=0, second=0) + timedelta(days=1)
					record.fecha_fin = fecha_actual.replace(hour=22, minute=0, second=0) + timedelta(days=5, hours=5)

				if len(record.bloques_ids)==0:
					record.bloques_ids.create({'name':'APTITUD ACADEMICA', 'duracion':50, 'evaluacion_id':self.id})
					record.bloques_ids.create({'name':'MATEMATICA', 'duracion':20, 'evaluacion_id':self.id})
					record.bloques_ids.create({'name':'HUMANIDADES', 'duracion':30, 'evaluacion_id':self.id})
					record.bloques_ids.create({'name':'CIENCIAS NATURALES', 'duracion':60, 'evaluacion_id':self.id})

				suma = 0
				for line in record.bloques_ids:
					suma = suma + line.duracion
				record.duracion = suma

	def publicar_evaluacion(self):
		for record in self:
			record.state = 'publico'
			suma = 0
			if record.tipo_evaluacion == 'diario':
				adjuntos = record.examen_id.exam_file_ids
				for line in adjuntos:
					line.public = True
				solucionarios = record.examen_id.solve_file_ids
				for line in solucionarios:
					line.public = True
			elif record.tipo_evaluacion != 'diario':
				for bloque in record.bloques_ids:
					suma = suma + bloque.duracion
					adjuntos = bloque.examen_id.exam_file_ids
					for line in adjuntos:
						line.public = True
					solucionarios = bloque.examen_id.solve_file_ids
					for line in solucionarios:
						line.public = True
				record.duracion = suma

	def corregir_notas(self):
		for record in self:
			res = {}
			for respuesta_line in record.respuestas_ids:
				lineas_respuestas = respuesta_line.respuestas_ids
				pts_correcto = respuesta_line.examen_id.plantilla_id.pts_correcto
				pts_incorrecto = respuesta_line.examen_id.plantilla_id.pts_incorrecto
				pts_blanco = respuesta_line.examen_id.plantilla_id.pts_blanco
				respuesta = []
				cont = 0
				contador = 0
				for clave in respuesta_line.examen_id.claves_ids:
					if clave.is_curso == False:
						if clave.clave_a == True:
							respuesta.append('A')
						elif clave.clave_b == True:
							respuesta.append('B')
						elif clave.clave_c == True:
							respuesta.append('C')
						elif clave.clave_d == True:
							respuesta.append('D')
						elif clave.clave_e == True:
							respuesta.append('E')
					else:
						respuesta.append('0')

				for line in lineas_respuestas:
					if line.is_curso == False:
						cont = cont + 1
						if line.respuesta_a == True:
							if respuesta[contador] == 'A':
								line.puntaje = pts_correcto
								line.correcto = True
								line.incorrecto = False
								line.blanco = False
							else:
								line.puntaje = pts_incorrecto
								line.correcto = False
								line.incorrecto = True
								line.blanco = False
						elif line.respuesta_b == True:
							if respuesta[contador] == 'B':
								line.puntaje = pts_correcto
								line.correcto = True
								line.incorrecto = False
								line.blanco = False
							else:
								line.puntaje = pts_incorrecto
								line.correcto = False
								line.incorrecto = True
								line.blanco = False
						elif line.respuesta_c == True:
							if respuesta[contador] == 'C':
								line.puntaje = pts_correcto
								line.correcto = True
								line.incorrecto = False
								line.blanco = False
							else:
								line.puntaje = pts_incorrecto
								line.correcto = False
								line.incorrecto = True
								line.blanco = False
						elif line.respuesta_d == True:
							if respuesta[contador] == 'D':
								line.puntaje = pts_correcto
								line.correcto = True
								line.incorrecto = False
								line.blanco = False
							else:
								line.puntaje = pts_incorrecto
								line.correcto = False
								line.incorrecto = True
								line.blanco = False
						elif line.respuesta_e == True:
							if respuesta[contador] == 'E':
								line.puntaje = pts_correcto
								line.correcto = True
								line.incorrecto = False
								line.blanco = False
							else:
								line.puntaje = pts_incorrecto
								line.correcto = False
								line.incorrecto = True
								line.blanco = False
						else:
							line.puntaje = pts_blanco
							line.correcto = False
							line.incorrecto = False
							line.blanco = True
					else:
						line.puntaje = 0
					contador = contador + 1
				curso_activo = 0
				identificador = 0
				puntaje_curso = 0.0
				contador_curso = 0
				n_cont_correcto_curso = 0
				n_cont_incorrecto_curso = 0
				n_cont_blanco_curso = 0
				ultimo = len(lineas_respuestas)
				for line in lineas_respuestas:
					if line.is_curso:
						if identificador == 0:
							curso_activo = line.curso_general_id.id
							puntaje_curso = 0.0
							contador_curso = 0
							n_cont_correcto_curso = 0
							n_cont_incorrecto_curso = 0
							n_cont_blanco_curso = 0
						else:
							for obj in respuesta_line.respuestas_slide_ids:
								if obj.curso_general_id.id == curso_activo:
									if puntaje_curso <=0:
										obj.puntaje = puntaje_curso
										obj.nota_vigesimal = round((puntaje_curso/(contador_curso*pts_correcto))*20,2)
										obj.n_correcto = n_cont_correcto_curso
										obj.n_incorrecto = n_cont_incorrecto_curso
										obj.n_blanco = n_cont_blanco_curso
									else:
										obj.puntaje = puntaje_curso
										obj.nota_vigesimal = round((puntaje_curso/(contador_curso*pts_correcto))*20,2)
										obj.n_correcto = n_cont_correcto_curso
										obj.n_incorrecto = n_cont_incorrecto_curso
										obj.n_blanco = n_cont_blanco_curso
							curso_activo = line.curso_general_id.id
							puntaje_curso = 0.0
							contador_curso = 0
							n_cont_correcto_curso = 0
							n_cont_incorrecto_curso = 0
							n_cont_blanco_curso = 0
					else:
						puntaje_curso = puntaje_curso + line.puntaje
						contador_curso = contador_curso + 1
						if line.correcto:
							n_cont_correcto_curso = n_cont_correcto_curso + 1
						elif line.incorrecto:
							n_cont_incorrecto_curso = n_cont_incorrecto_curso + 1
						elif line.blanco:
							n_cont_blanco_curso = n_cont_blanco_curso + 1

					if ultimo-1==identificador:
						for obj in respuesta_line.respuestas_slide_ids:
							if obj.curso_general_id.id == curso_activo:
								if puntaje_curso <=0:
									obj.puntaje = puntaje_curso
									obj.nota_vigesimal = round((puntaje_curso/(contador_curso*pts_correcto))*20,2)
									obj.n_correcto = n_cont_correcto_curso
									obj.n_incorrecto = n_cont_incorrecto_curso
									obj.n_blanco = n_cont_blanco_curso
								else:
									obj.puntaje = puntaje_curso
									obj.nota_vigesimal = round((puntaje_curso/(contador_curso*pts_correcto))*20,2)
									obj.n_correcto = n_cont_correcto_curso
									obj.n_incorrecto = n_cont_incorrecto_curso
									obj.n_blanco = n_cont_blanco_curso
					identificador = identificador + 1
				puntaje_total = 0.0
				n_cont_correcto = 0
				n_cont_incorrecto = 0
				n_cont_blanco = 0
				for i in lineas_respuestas:
					if i.is_curso==False:
						puntaje_total = puntaje_total + i.puntaje
						if i.correcto:
							n_cont_correcto = n_cont_correcto + 1
						if i.incorrecto:
							n_cont_incorrecto = n_cont_incorrecto + 1
						if i.blanco:
							n_cont_blanco = n_cont_blanco + 1
				respuesta_line.n_correcto = n_cont_correcto
				respuesta_line.n_incorrecto = n_cont_incorrecto
				respuesta_line.n_blanco = n_cont_blanco
				if puntaje_total <=0:
					respuesta_line.puntaje = puntaje_total
					respuesta_line.calificacion = 0
					respuesta_line.nota_vigesimal = round((puntaje_total/(cont*pts_correcto))*20,2)
				else:
					respuesta_line.puntaje = puntaje_total
					respuesta_line.calificacion = (puntaje_total/(cont*pts_correcto))*100
					respuesta_line.nota_vigesimal = round((puntaje_total/(cont*pts_correcto))*20,2)

			for corregir_unido in record.respuestas_unidas_ids:
				puntaje_simulacro = 0.0
				nota_vigesimal_simulacro = 0.0
				usuario_activo = corregir_unido.user_id.id
				contador_respuestas = 0
				n_acumulado_cont_correcto = 0
				n_acumulado_cont_incorrecto = 0
				n_acumulado_cont_blanco = 0
				for corregir_listas in record.respuestas_ids:
					if usuario_activo == corregir_listas.user_id.id:
						puntaje_simulacro = corregir_listas.puntaje + puntaje_simulacro
						nota_vigesimal_simulacro = corregir_listas.nota_vigesimal + nota_vigesimal_simulacro
						contador_respuestas = 1 + contador_respuestas
						n_acumulado_cont_correcto = corregir_listas.n_correcto + n_acumulado_cont_correcto
						n_acumulado_cont_incorrecto = corregir_listas.n_incorrecto + n_acumulado_cont_incorrecto
						n_acumulado_cont_blanco = corregir_listas.n_blanco + n_acumulado_cont_blanco
				corregir_unido.n_correcto = n_acumulado_cont_correcto
				corregir_unido.n_incorrecto = n_acumulado_cont_incorrecto
				corregir_unido.n_blanco = n_acumulado_cont_blanco
				if puntaje_simulacro <= 0 :
					corregir_unido.puntaje = 0.0
					corregir_unido.nota_vigesimal =  round((puntaje_simulacro/((n_acumulado_cont_blanco + n_acumulado_cont_correcto + n_acumulado_cont_incorrecto)*pts_correcto))*20,2)
				else:
					corregir_unido.puntaje = puntaje_simulacro
					corregir_unido.nota_vigesimal = round((puntaje_simulacro/((n_acumulado_cont_blanco + n_acumulado_cont_correcto + n_acumulado_cont_incorrecto)*pts_correcto))*20,2)

			if record.tipo_evaluacion != 'diario':
				for respuesta_line in record.respuestas_ids:
					for bloque in record.bloques_ids:
						if bloque.examen_id.id == respuesta_line.examen_id.id:
							respuesta_line.name = bloque.name


	def cerrar_evaluacion(self):
		for record in self:
			record.state = 'cerrado'

	@api.onchange("fecha_inicio","fecha_fin")
	def cambio_fecha_inicio(self):
		for record in self:
			res = {}
			if record.fecha_inicio and record.fecha_fin:
				if record.fecha_inicio >= record.fecha_fin:
					record.fecha_inicio = record.fecha_fin - timedelta(hours=1)
					res ={'warning':{
						'title':_('ALERTA'),
						'message':_('La Fecha de Inicio debe ser antes de la Fecha de Fin')
						}
					}
					return res

	def action_survey_user_input_completed(self):
		return {
			"type": "ir.actions.act_window",
			"target": "current",
			"res_model": "respuesta",
			"views": [[False, "search"], [self.env.ref('website_examenes.respuesta_tree').id, "list"], [self.env.ref('website_examenes.respuesta_form').id, "form"]],
			"domain": [["evaluacion_id", "=", self.id]],
			"context": [["evaluacion_id", "=", self.id]],
			"name": u"Respuestas"
		}

	def action_respuestas_semanal(self):
		return {
			"type": "ir.actions.act_window",
			"target": "current",
			"res_model": "respuesta",
			"views": [[False, "search"], [self.env.ref('website_examenes.respuesta_tree_semanal').id, "list"], [self.env.ref('website_examenes.respuesta_form').id, "form"]],
			"domain": [["evaluacion_id", "=", self.id]],
			"context": [["evaluacion_id", "=", self.id]],
			"name": u"Respuestas"
		}


	def action_survey_user_input_completed_1(self):
		return {
			"type": "ir.actions.act_window",
			"target": "current",
			"res_model": "respuesta",
			"views": [[False, "search"], [self.env.ref('website_examenes.respuesta_tree_1').id, "list"], [self.env.ref('website_examenes.respuesta_form_simulacro').id, "form"]],
			"domain": [["evaluacion_id", "=", self.id]],
			"context": [["evaluacion_id", "=", self.id]],
			"name": u"Respuestas"
		}

	def action_survey_user_input(self):
		return {
			"type": "ir.actions.act_window",
			"target": "current",
			"res_model": "respuesta.simulacro",
			"views": [[False, "search"], [self.env.ref('website_examenes.respuesta_simulacro_tree').id, "list"], [self.env.ref('website_examenes.respuesta_simulacro_form').id, "form"]],
			"domain": [["evaluacion_id", "=", self.id]],
			"context": [["evaluacion_id", "=", self.id]],
			"name": u"Respuestas"
		}

	def action_survey_user_input_1(self):
		return {
			"type": "ir.actions.act_window",
			"target": "current",
			"res_model": "respuesta.simulacro",
			"views": [[False, "search"], [self.env.ref('website_examenes.respuesta_simulacro_tree_1').id, "list"], [self.env.ref('website_examenes.respuesta_simulacro_form_1').id, "form"]],
			"domain": [["evaluacion_id", "=", self.id]],
			"context": [["evaluacion_id", "=", self.id]],
			"name": u"Respuestas"
		}


	@api.depends("respuestas_ids", "respuestas_unidas_ids")
	def _compute_respuesta(self):
		for record in self:
			record.answer_done_count = len(record.respuestas_ids)
			record.answer_done_count_simulacro = len(record.respuestas_unidas_ids)


class Evaluacionline(models.Model):
	_name = 'evaluacion.line'

	name = fields.Char(translate=True, required=True, string="FASE")
	examen_id = fields.Many2one('examen', string="Examen")
	duracion = fields.Integer('Duración (min)', required=True)

	evaluacion_id = fields.Many2one('evaluacion', string="Evaluación")


class GrupoAlumnos(models.Model):
	_name = 'grupo.alumnos'

	name = fields.Char(translate=True, required=True, string="Nombre")
	users_ids = fields.One2many('res.users.line', 'grupo_alumnos_id', string='Alumnos')

class UsersLines(models.Model):
	_name = 'res.users.line'

	name = fields.Char(string="Nombre",related="grupo_alumnos_id.name")
	grupo_alumnos_id = fields.Many2one('grupo.alumnos', string='Grupo', index=True, required=True)
	user_id = fields.Many2one('res.users', string='Alumno', index=True, required=True)
	active = fields.Boolean(string="Active",related="user_id.active")
