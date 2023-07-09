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


class Respuestas(models.Model):
	_name = 'respuesta'

	name = fields.Char(translate=True, string="Titulo")
	evaluacion_id = fields.Many2one('evaluacion', string="Evaluación")
	examen_id = fields.Many2one('examen', string="Examen")
	fecha_limite = fields.Datetime(string="Fecha Límite", related="evaluacion_id.fecha_fin")
	fecha_termino = fields.Datetime(string="Fecha Hora Término")
	duracion = fields.Integer(string="Duración (min)",default=0)
	user_id = fields.Many2one('res.users', string='Alumno', index=True, required=True)
	estado =  fields.Selection([
		('incompleto', 'Incompleto'),
		('entregado', 'Entregado')],
		string='Estado',
		default='incompleto')
	calificacion = fields.Float("Calificación (%)", digits=(3, 3))
	nota_vigesimal = fields.Float("Calificación", digits=(2, 2))
	puntaje = fields.Float("Puntaje", digits=(3, 3))
	n_correcto = fields.Integer(compute="_compute_conteo_pregunta",string="B",store=True)
	n_incorrecto = fields.Integer(compute="_compute_conteo_pregunta",string="M",store=True)
	n_blanco = fields.Integer(compute="_compute_conteo_pregunta",string="BL",store=True)

	respuestas_ids = fields.One2many('respuesta.line', 'respuesta_id', string='Bloques')
	respuestas_slide_ids = fields.One2many('respuesta.slide', 'respuesta_id', string='Cursos')
	grupo_alumnos = fields.Many2one('grupo.alumnos', string="Grupo de Alumnos",related="evaluacion_id.grupo_alumnos")
	tipo_evaluacion = fields.Selection([
		('diario', 'Diario'),
		('semanal', 'Semanal'),
		('simulacro', 'Simulacro')],
		string='Tipo de Prueba',related="evaluacion_id.tipo_evaluacion")


	@api.depends("fecha_termino")
	def _compute_duracion(self):
		for record in self:
			if record.create_date and record.fecha_termino:
				record.duracion = (record.create_date - record.fecha_termino)/timedelta(minutes=1)

	@api.depends("respuestas_ids")
	def _compute_conteo_pregunta(self):
		for record in self:
			cont_correcto = 0
			cont_incorrecto = 0
			cont_blanco = 0
			for line in record.respuestas_ids:
				if line.is_curso == False:
					if line.correcto:
						cont_correcto = cont_correcto + 1
					if line.incorrecto:
						cont_incorrecto = cont_incorrecto + 1
					if line.blanco:
						cont_blanco = cont_blanco + 1
			record.n_correcto = cont_correcto
			record.n_incorrecto = cont_incorrecto
			record.n_blanco = cont_blanco


class Respuestaline(models.Model):
	_name = 'respuesta.line'

	name = fields.Char(translate=True, string="Titulo")
	sequence = fields.Integer(string="N° Pregunta")
	curso_id = fields.Many2one('slide.channel', string='Curso')
	curso_general_id = fields.Many2one('curso.general', string='Curso',store=True)

	respuesta_id = fields.Many2one('respuesta', string='Respuesta')
	alternativa = fields.Char("Respuesta Ingresada")
	correcto = fields.Boolean("Correcto",default=False)
	incorrecto = fields.Boolean("Incorrecto",default=False)
	blanco = fields.Boolean("Blanco",default=True)
	puntaje = fields.Float("Puntaje", digits=(3, 3))
	is_curso = fields.Boolean('Is a category', default=False)
	respuesta_a = fields.Boolean("A")
	respuesta_b = fields.Boolean("B")
	respuesta_c = fields.Boolean("C")
	respuesta_d = fields.Boolean("D")
	respuesta_e = fields.Boolean("E")


class RespuestaSlide(models.Model):
	_name = 'respuesta.slide'

	name = fields.Char(translate=True, string="Titulo")
	curso_id = fields.Many2one('slide.channel', string='Curso')
	curso_general_id = fields.Many2one('curso.general', string='Curso',store=True)

	puntaje = fields.Float("Puntaje", digits=(3, 3))
	nota_vigesimal = fields.Float("Calificación", digits=(2, 2))
	respuesta_id = fields.Many2one('respuesta', string='Respuesta')
	n_correcto = fields.Integer(string="B",store=True)
	n_incorrecto = fields.Integer(string="M",store=True)
	n_blanco = fields.Integer(string="BL",store=True)

class RespuestaSimulacro(models.Model):
	_name = 'respuesta.simulacro'

	name = fields.Char(translate=True, string="Titulo")
	puntaje = fields.Float("Puntaje", digits=(3, 3))
	nota_vigesimal = fields.Float("Calificación", digits=(2, 2))
	evaluacion_id = fields.Many2one('evaluacion', string="Evaluación")
	user_id = fields.Many2one('res.users', string='Alumno', index=True, required=True)
	n_correcto = fields.Integer(string="B",store=True)
	n_incorrecto = fields.Integer(string="M",store=True)
	n_blanco = fields.Integer(string="BL",store=True)
	grupo_alumnos = fields.Many2one('grupo.alumnos', string="Grupo de Alumnos",related="evaluacion_id.grupo_alumnos")

	tipo_evaluacion = fields.Selection([
		('diario', 'Diario'),
		('semanal', 'Semanal'),
		('simulacro', 'Simulacro')],
		string='Tipo de Prueba',related="evaluacion_id.tipo_evaluacion")

class RespuestaCreateLine(models.TransientModel):
	_name = 'respuesta.create.line'

	def crear_respuestas_lines(self, respuesta_id, pregunta_id, alternativa, sequence, duracion):

		prueba = False

		respuesta_line = self.env["respuesta"].search([('id', '=', respuesta_id)],limit=1)
		lineas_respuestas = respuesta_line.respuestas_ids
		pts_correcto = respuesta_line.examen_id.plantilla_id.pts_correcto
		pts_incorrecto = respuesta_line.examen_id.plantilla_id.pts_incorrecto
		pts_blanco = respuesta_line.examen_id.plantilla_id.pts_blanco
		respuesta_correcta = ''
		cont = 0
		contador_respuesta_correcta = 0
		contador_respuesta_ingresada = 0
		entregado_1 = 0
		ahora = datetime.now()
		if ahora > respuesta_line.evaluacion_id.fecha_fin:
			entregado_1 = 3
			return entregado_1
		else:
			if respuesta_line.estado == "entregado" and (ahora - respuesta_line.create_date) < timedelta(minutes=duracion):
				entregado_1 = 1
			if respuesta_line.estado == "entregado" and (ahora - respuesta_line.create_date) > timedelta(minutes=duracion):
				entregado_1 = 2
			if respuesta_line.estado == "incompleto" and (ahora - respuesta_line.create_date) > timedelta(minutes=duracion):
				entregado_1 = 3
			if respuesta_line.estado == "incompleto" and (ahora - respuesta_line.create_date) < timedelta(minutes=duracion):
				entregado_1 = 4

				for clave in respuesta_line.examen_id.claves_ids:
					if clave.is_curso == False:
						contador_respuesta_correcta = contador_respuesta_correcta + 1
					if contador_respuesta_correcta == sequence:
						if clave.clave_a == True:
							respuesta_correcta = 'A'
						elif clave.clave_b == True:
							respuesta_correcta = 'B'
						elif clave.clave_c == True:
							respuesta_correcta = 'C'
						elif clave.clave_d == True:
							respuesta_correcta = 'D'
						elif clave.clave_e == True:
							respuesta_correcta = 'E'

				for line in lineas_respuestas:
					if line.is_curso == False:
						cont = cont + 1
						contador_respuesta_ingresada = contador_respuesta_ingresada + 1

					if contador_respuesta_ingresada == sequence:
						if alternativa == 'A':
							line.respuesta_a = True
							line.respuesta_b = False
							line.respuesta_c = False
							line.respuesta_d = False
							line.respuesta_e = False
						elif alternativa == 'B':
							line.respuesta_b = True
							line.respuesta_a = False
							line.respuesta_c = False
							line.respuesta_d = False
							line.respuesta_e = False
						elif alternativa == 'C':
							line.respuesta_c = True
							line.respuesta_b = False
							line.respuesta_a = False
							line.respuesta_d = False
							line.respuesta_e = False
						elif alternativa == 'D':
							line.respuesta_d = True
							line.respuesta_b = False
							line.respuesta_c = False
							line.respuesta_a = False
							line.respuesta_e = False
						elif alternativa == 'E':
							line.respuesta_e = True
							line.respuesta_b = False
							line.respuesta_c = False
							line.respuesta_d = False
							line.respuesta_a = False

						if alternativa == respuesta_correcta:
							line.puntaje = pts_correcto
							line.correcto = True
							line.incorrecto = False
							line.blanco = False
						else:
							line.puntaje = pts_incorrecto
							line.correcto = False
							line.incorrecto = True
							line.blanco = False

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
							puntaje_curso = 0
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
							puntaje_curso = 0
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

				respuesta_simulacro = request.env["respuesta.simulacro"].search([["user_id", "=", request.env.uid], ["evaluacion_id", "=", respuesta_line.evaluacion_id.id]])
				respuesta_usuario = request.env["respuesta"].search([["user_id", "=", request.env.uid], ["evaluacion_id", "=", respuesta_line.evaluacion_id.id]])
				puntaje_simulacro = 0.0
				nota_vigesimal_simulacro = 0.0
				n_acumulado_cont_correcto = 0
				n_acumulado_cont_incorrecto = 0
				n_acumulado_cont_blanco = 0
				for line in respuesta_usuario:
					puntaje_simulacro = line.puntaje + puntaje_simulacro
					nota_vigesimal_simulacro = line.nota_vigesimal + nota_vigesimal_simulacro
					n_acumulado_cont_correcto = line.n_correcto + n_acumulado_cont_correcto
					n_acumulado_cont_incorrecto = line.n_incorrecto + n_acumulado_cont_incorrecto
					n_acumulado_cont_blanco = line.n_blanco + n_acumulado_cont_blanco
				respuesta_simulacro.puntaje = puntaje_simulacro
				respuesta_simulacro.n_correcto = n_acumulado_cont_correcto
				respuesta_simulacro.n_incorrecto = n_acumulado_cont_incorrecto
				respuesta_simulacro.n_blanco = n_acumulado_cont_blanco
				respuesta_line.fecha_termino = datetime.now()
				respuesta_line.duracion = (respuesta_line.fecha_termino - respuesta_line.create_date)/timedelta(minutes=1)
				if len(respuesta_usuario)<=0:
					respuesta_simulacro.nota_vigesimal = 0
				else:
					respuesta_simulacro.nota_vigesimal = round((puntaje_simulacro/((n_acumulado_cont_blanco + n_acumulado_cont_correcto + n_acumulado_cont_incorrecto)*pts_correcto))*20,2)
			return entregado_1


	def entredar_examen_button(self, respuesta_id):

		prueba = False

		respuesta_line = self.env["respuesta"].search([('id', '=', respuesta_id)],limit=1)
		respuesta_line.estado = 'entregado'

		return prueba
