# -*- coding: utf-8 -*-

import base64
import datetime
import hashlib
import pytz
import threading
import logging
import hmac
from email.utils import formataddr
from collections import defaultdict
from datetime import datetime, timedelta
import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.modules import get_module_resource
import pytz
import math  # noqa
import base64  # noqa
import io  # noqa
from xlwt import easyxf, Workbook  # noqa
from xlwt import Formula  # noqa
from PIL import Image  # noqa
_logger = logging.getLogger(__name__)

SELECTION_EQUIVALENCIA = {'-': u'-','a': u'A', 'j': u'J', 'f': u'F'}

class SituacionAlumno(models.Model):
	_name = 'situacion.alumno'

	name = fields.Char(string="Nivel")
	desde = fields.Float(string="Desde")
	hasta = fields.Float(string="Hasta")

class PesosEvaluaciones(models.Model):
	_name = 'peso.evaluacion'

	name = fields.Char(string="Nivel")
	peso = fields.Float(string="Pesos")
	tipo_evaluacion = fields.Selection([
		('diario', 'Diario'),
		('semanal', 'Semanal'),
		('simulacro', 'Simulacro')],
		string='Tipo de Prueba',
		help="Tipo de prueba", required=True)

	@api.onchange("tipo_evaluacion")
	def onchange_tipo_eva(self):
		for record in self:
			if record.tipo_evaluacion =='diario':
				record.name = 'diario'
			if record.tipo_evaluacion =='semanal':
				record.name = 'semanal'
			if record.tipo_evaluacion =='simulacro':
				record.name = 'simulacro'

class InheritCarrera(models.Model):
	_inherit="estudiante.carrera"

	minimo = fields.Float(string="Minimo",defaul=200)

class ReporteTransient(models.TransientModel):
	_name = 'reporte.notas.transient'

	def get_name_aulas(self,lines):
		aulas = ''
		contador_lines = 1
		for obj in lines:
			if contador_lines == 1:
				aulas += obj.grupo_alumnos_id.name
			else:
				aulas = aulas + ',' + obj.grupo_alumnos_id.name
			contador_lines += 1
		return aulas


	# reporte asistencia para alumno
	def funcion_matriz_asistencias(self,desde,hasta,aula):
		fecha_actual = datetime.now()
		matriz = []
		matriz_total = []
		aula_filtro = self.env["grupo.alumnos"].sudo().search([('id', '=', aula)]).id
		asistencias = self.env['asistencia.estudiante'].sudo().search([('user_id','=',self.env.user.id),('grupo_alumnos', '=', aula_filtro),('fecha','>=',desde),('fecha','<=',hasta)],order="fecha asc")
		matriz = []
		matriz_total = []
		for line in asistencias:
			matriz_line = []
			matriz_line.append((line.fecha - timedelta(hours=5)).strftime("%Y-%m-%d"))
			valor_asistencia_falta = "-"
			if line.tipo_sesion == 'normal':
				valor_asistencia_falta = line.registro_asistencia
			matriz_line.append(valor_asistencia_falta)
			matriz_total.append(matriz_line)

		matriz_agrupada = []
		fechas = []
		for elem in matriz_total:
			if len(matriz_agrupada)==0:
				matriz_line = []
				matriz_line.append(elem[0])
				fechas.append(elem[0])
				matriz_line.append(SELECTION_EQUIVALENCIA[elem[1]])
				matriz_agrupada.append(matriz_line)
			else:
				if  elem[0] in fechas:
					for line in matriz_agrupada:
						if elem[0] == line[0]:
							line.append(SELECTION_EQUIVALENCIA[elem[1]])
				else:
					matriz_line = []
					matriz_line.append(elem[0])
					fechas.append(elem[0])
					matriz_line.append(SELECTION_EQUIVALENCIA[elem[1]])
					matriz_agrupada.append(matriz_line)

		maximo = 0
		asistencias = []
		justificados = []
		faltas = []
		for line in  matriz_agrupada:
			if len(line) > maximo:
				maximo = len(line)

		for line in  matriz_agrupada:
			num_asistencia = 0
			num_falta = 0
			num_justificada = 0
			for sub_line in line:
				if sub_line == 'A':
					num_asistencia += 1
				elif sub_line == 'J':
					num_justificada += 1
				elif sub_line == 'F':
					num_falta += 1
			if len(line) < maximo:
				for max in range(maximo-len(line)):
					line.append("-")
			asistencias.append(num_asistencia)
			justificados.append(num_justificada)
			faltas.append(num_falta)
			line.append(num_asistencia)
			line.append(num_justificada)
			line.append(num_falta)

		header = ["FECHA"]
		footer = [""]
		for max in range(maximo-1):
			header.append(max+1)
			footer.append("")
		footer.append(sum(asistencias))
		footer.append(sum(justificados))
		footer.append(sum(faltas))
		header.append("ASISTENCIA")
		header.append("JUSTIFICADO")
		header.append("FALTA")
		matriz_agrupada.insert(0,header)
		matriz_agrupada.append(footer)

		return matriz_agrupada

	# reporte asistencia por alumno
	def funcion_matriz_asistencias_por_alumno(self,desde,hasta,aula,alumno):
		fecha_actual = datetime.now()
		matriz = []
		matriz_total = []
		user_id = self.env['res.users'].sudo().search([('id','=',alumno)],limit=1).id
		aula_filtro = self.env["grupo.alumnos"].sudo().search([('id', '=', aula)]).id
		if desde and not hasta:
			asistencias = self.env['asistencia.estudiante'].sudo().search([('user_id','=',user_id),('grupo_alumnos', '=', aula_filtro),('fecha','>=',desde)],order="fecha asc")
		elif not desde and not hasta:
			asistencias = self.env['asistencia.estudiante'].sudo().search([('user_id','=',user_id),('grupo_alumnos', '=', aula_filtro)],order="fecha asc")
		elif not desde and  hasta:
			asistencias = self.env['asistencia.estudiante'].sudo().search([('user_id','=',user_id),('grupo_alumnos', '=', aula_filtro),('fecha','<=',hasta)],order="fecha asc")
		elif desde and  hasta:
			asistencias = self.env['asistencia.estudiante'].sudo().search([('user_id','=',user_id),('grupo_alumnos', '=', aula_filtro),('fecha','>=',desde),('fecha','<=',hasta)],order="fecha asc")
		matriz = []
		matriz_total = []
		for line in asistencias:
			matriz_line = []
			matriz_line.append((line.fecha - timedelta(hours=5)).strftime("%Y-%m-%d"))
			valor_asistencia_falta = "-"
			if line.tipo_sesion == 'normal':
				valor_asistencia_falta = line.registro_asistencia
			matriz_line.append(valor_asistencia_falta)
			matriz_total.append(matriz_line)

		matriz_agrupada = []
		fechas = []
		for elem in matriz_total:
			if len(matriz_agrupada)==0:
				matriz_line = []
				matriz_line.append(elem[0])
				fechas.append(elem[0])
				matriz_line.append(SELECTION_EQUIVALENCIA[elem[1]])
				matriz_agrupada.append(matriz_line)
			else:
				if  elem[0] in fechas:
					for line in matriz_agrupada:
						if elem[0] == line[0]:
							line.append(SELECTION_EQUIVALENCIA[elem[1]])
				else:
					matriz_line = []
					matriz_line.append(elem[0])
					fechas.append(elem[0])
					matriz_line.append(SELECTION_EQUIVALENCIA[elem[1]])
					matriz_agrupada.append(matriz_line)
		maximo = 0
		asistencias = []
		justificados = []
		faltas = []
		for line in  matriz_agrupada:
			if len(line) > maximo:
				maximo = len(line)

		for line in  matriz_agrupada:
			num_asistencia = 0
			num_falta = 0
			num_justificada = 0
			for sub_line in line:
				if sub_line == 'A':
					num_asistencia = num_asistencia +1
				elif sub_line == 'J':
					num_justificada =num_justificada +1
				elif sub_line == 'F':
					num_falta = num_falta+1
			if len(line) < maximo:
				for max in range(maximo-len(line)):
					line.append("-")
			asistencias.append(num_asistencia)
			justificados.append(num_justificada)
			faltas.append(num_falta)
			line.append(num_asistencia)
			line.append(num_justificada)
			line.append(num_falta)

		header = ["FECHA"]
		footer = [""]
		for max in range(maximo-1):
			header.append(max+1)
			footer.append("")
		footer.append(sum(asistencias))
		footer.append(sum(justificados))
		footer.append(sum(faltas))
		header.append("ASISTENCIA")
		header.append("JUSTIFICADO")
		header.append("FALTA")
		matriz_agrupada.insert(0,header)
		matriz_agrupada.append(footer)

		return matriz_agrupada

	# REPORTE DE ASISTENCIA POR AULA
	def funcion_matriz_asistencias_por_aula(self,desde,hasta,aula):
		fecha_actual = datetime.now()
		matriz = []
		matriz_total = []
		aula_filtro = self.env["grupo.alumnos"].sudo().search([('id', '=', aula)]).id
		if desde and not hasta:
			asistencias = self.env['asistencia.estudiante'].sudo().search([('grupo_alumnos', '=', aula_filtro),('fecha','>=',desde)],order="fecha asc")
		elif not desde and not hasta:
			asistencias = self.env['asistencia.estudiante'].sudo().search([('grupo_alumnos', '=', aula_filtro)],order="fecha asc")
		elif not desde and  hasta:
			asistencias = self.env['asistencia.estudiante'].sudo().search([('grupo_alumnos', '=', aula_filtro),('fecha','<=',hasta)],order="fecha asc")
		elif desde and  hasta:
			asistencias = self.env['asistencia.estudiante'].sudo().search([('grupo_alumnos', '=', aula_filtro),('fecha','>=',desde),('fecha','<=',hasta)],order="fecha asc")

		matriz_usuarios = []
		ids_user = []
		ids_fechas = []
		enumerador = 1
		for elem in asistencias:
			if len(ids_user)==0:
				ids_user.append(elem.user_id.name)
			else:
				if elem.user_id.name not in ids_user:
					ids_user.append(elem.user_id.name)
			if len(ids_fechas)==0:
				ids_fechas.append((elem.fecha - timedelta(hours=5)).strftime("%Y-%m-%d"))
			else:
				if (elem.fecha - timedelta(hours=5)).strftime("%Y-%m-%d") not in ids_fechas:
					ids_fechas.append((elem.fecha - timedelta(hours=5)).strftime("%Y-%m-%d"))
		array_asistencias_suma = []
		for fecha in ids_fechas:
			matriz_line = [fecha]
			array_asistencias_suma.append(matriz_line)
		justificados_suma = []
		for fecha in ids_fechas:
			matriz_line = [fecha]
			justificados_suma.append(matriz_line)
		faltas_suma = []
		for fecha in ids_fechas:
			matriz_line = [fecha]
			faltas_suma.append(matriz_line)

		for id_line in ids_user:
			matriz_line = []
			matriz_line.append(enumerador)
			matriz_line.append(id_line)
			indice_fecha = 0
			for fecha_line in ids_fechas:
				asistencia_fechas = self.env['asistencia.estudiante'].sudo().search([('grupo_alumnos', '=', aula_filtro),('fecha_date','=',fecha_line),('user_id','=',id_line)],order="fecha asc")
				if len(asistencia_fechas) ==0:
					matriz_line.append("-")
				else:
					if (len(array_asistencias_suma[indice_fecha])-1) < len(asistencia_fechas) :
						for max in range(  len(asistencia_fechas)-(len(array_asistencias_suma[indice_fecha])- 1) ):
							array_asistencias_suma[indice_fecha].append(0)

					if (len(justificados_suma[indice_fecha])-1) < len(asistencia_fechas) :
						for max in range( len(asistencia_fechas)-(len(justificados_suma[indice_fecha])- 1)):
							justificados_suma[indice_fecha].append(0)

					if (len(faltas_suma[indice_fecha])-1) < len(asistencia_fechas) :
						for max in range( len(asistencia_fechas)-(len(faltas_suma[indice_fecha])- 1)):
							faltas_suma[indice_fecha].append(0)
					cadena = ''
					contador_cadena = 0

					for asis_line in asistencia_fechas:
						valor_asistencia_falta = "-"
						if asis_line.tipo_sesion == 'normal':
							valor_asistencia_falta = asis_line.registro_asistencia
						if contador_cadena == 0:
							cadena = cadena  + SELECTION_EQUIVALENCIA[valor_asistencia_falta]
						else:
							cadena =  cadena + '/' + SELECTION_EQUIVALENCIA[valor_asistencia_falta]
						if valor_asistencia_falta =='a':
							array_asistencias_suma[indice_fecha][contador_cadena + 1] = 1 + array_asistencias_suma[indice_fecha][contador_cadena+1]
						elif valor_asistencia_falta =='j':
							justificados_suma[indice_fecha][contador_cadena+1] = 1 + justificados_suma[indice_fecha][contador_cadena+1]
						elif valor_asistencia_falta =='f':
							faltas_suma[indice_fecha][contador_cadena+1] = 1 + faltas_suma[indice_fecha][contador_cadena+1]
						contador_cadena += 1
					matriz_line.append(cadena)
				indice_fecha += 1

			matriz_usuarios.append(matriz_line)
			enumerador += 1

		header = ["Nº","APELLIDO Y NOMBRES"]
		footer_1 = ["","ASISTENCIA"]
		footer_2 = ["","JUSTIFICADO"]
		footer_3 = ["","FALTA"]
		enumerador = 0
		for max in ids_fechas:
			header.append(max)
			sub_line = 0
			cadena = ''
			for line in array_asistencias_suma[enumerador]:
				if  0 <  sub_line:
					if sub_line == 1:
						cadena = cadena  + str(line)
					else:
						cadena =  cadena + '/' + str(line)
				sub_line += 1
			footer_1.append(cadena)

			sub_line = 0
			cadena = ''
			for line in justificados_suma[enumerador]:
				if  0 <  sub_line:
					if sub_line == 1:
						cadena = cadena  + str(line)
					else:
						cadena =  cadena + '/' + str(line)
				sub_line += 1
			footer_2.append(cadena)

			sub_line = 0
			cadena = ''
			for line in faltas_suma[enumerador]:
				if  0 <  sub_line:
					if sub_line == 1:
						cadena = cadena  + str(line)
					else:
						cadena =  cadena + '/' + str(line)
				sub_line += 1
			footer_3.append(cadena)
			enumerador += 1

		def get_salary(elem):
			return elem[1]
		matriz_usuarios.sort(key=get_salary)
		for line in range(len(matriz_usuarios)):
			matriz_usuarios[line][0] = line +1
		matriz_usuarios.insert(0,header)
		matriz_usuarios.append(footer_1)
		matriz_usuarios.append(footer_2)
		matriz_usuarios.append(footer_3)

		return matriz_usuarios

	# reporte diario por aula
	def funcion_matriz_notas_diario(self,desde,hasta,aula):
		fecha_actual = datetime.now()
		cursos = self.env['curso.general'].sudo().search([])
		aula_filtro = self.env["grupo.alumnos"].sudo().search([('id', '=', aula)]).id
		alumnos = self.env["grupo.alumnos"].sudo().search([('id', '=', aula)]).users_ids
		if desde and not hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', '=', aula_filtro), ('tipo_evaluacion',  '=',  'diario'),  ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '>=',  desde)])
		elif not desde and not hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', '=', aula_filtro), ('tipo_evaluacion',  '=',  'diario'), ('fecha_fin',  '<=',  fecha_actual)])
		elif not desde and  hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', '=',aula_filtro), ('tipo_evaluacion',  '=',  'diario'),  ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '<=',  hasta)])
		elif desde and  hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', '=', aula_filtro), ('tipo_evaluacion',  '=',  'diario'), ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '<=',  hasta), ('fecha_fin',  '>=',  desde)])

		matriz_diario_total = []
		matriz_diario = []
		matriz_diario_active = [1,1,"FECHA"]
		matriz_diario_idcursos = ["id cursos",0,0]
		matriz_diario_namecursos = ["active","Nº","ALUMNO"]
		for line in cursos:
			matriz_diario_active.append(0)
			matriz_diario_idcursos.append(line.id)
			matriz_diario_namecursos.append(line.name_corto)
		matriz_diario_active.append(10002)
		matriz_diario_idcursos.append(10001)
		matriz_diario_namecursos.append(10000)
		matriz_diario.append(matriz_diario_active)
		matriz_diario.append(matriz_diario_idcursos)
		matriz_diario.append(matriz_diario_namecursos)
		for alumno in alumnos:
			matriz_alumno = []
			matriz_alumno.append(0)
			matriz_alumno.append(alumno.user_id.id)
			matriz_alumno.append(alumno.user_id.name)
			matriz_alumno_diario_active = [0,0,0]
			matriz_alumno_diario_idcursos = [0,0,0]
			matriz_alumno_suma_cantidad = [0,0,0]
			matriz_alumno_suma_total = [0,0,0]
			contador_cursos_activos = 0
			suma_cursos_activos = 0
			for curso_line in cursos:
				matriz_alumno.append("-")
				matriz_alumno_diario_active.append(0)
				matriz_alumno_diario_idcursos.append(curso_line.id)
				matriz_alumno_suma_cantidad.append(0)
				matriz_alumno_suma_total.append(0)

			for x_j_z in range(len(evaluaciones)) :
				respuestas = self.env["respuesta"].sudo().search([('evaluacion_id', '=',evaluaciones[x_j_z].id),('user_id', '=',alumno.user_id.id)],order = 'nota_vigesimal desc',limit=1)
				if respuestas:
					matriz_alumno[0] = 1
					for nota_curso in respuestas.respuestas_slide_ids:
						if nota_curso.curso_general_id:
							indice = matriz_alumno_diario_idcursos.index(nota_curso.curso_general_id.id)
							matriz_diario[0][indice] = 1
							matriz_alumno_diario_active[indice] = 1
							matriz_alumno_suma_total[indice] = matriz_alumno_suma_total[indice] +  nota_curso.nota_vigesimal
							matriz_alumno_suma_cantidad[indice] = matriz_alumno_suma_cantidad[indice] + 1
			for guardar in range(len(matriz_alumno_diario_active)) :
				if matriz_alumno_diario_active[guardar] != 0:
					contador_cursos_activos = contador_cursos_activos + 1
					if matriz_alumno_suma_cantidad[guardar] ==0:
						matriz_alumno[guardar] = format( 0.0 , '.2f')
					else:
						matriz_alumno[guardar] = format( round(matriz_alumno_suma_total[guardar] / matriz_alumno_suma_cantidad[guardar],2) , '.2f')
					suma_cursos_activos = suma_cursos_activos +round(matriz_alumno_suma_total[guardar] / matriz_alumno_suma_cantidad[guardar],2)
			if contador_cursos_activos == 0:
				matriz_alumno.append(0)
			else:
				matriz_alumno.append(round(suma_cursos_activos/contador_cursos_activos,2))
			matriz_diario.append(matriz_alumno)
		matriz_diario_total = 	[s for s in matriz_diario if s[0] != 0]
		def get_salary(elem):
			return elem[len(cursos)+3]

		matriz_diario_total.sort(key=get_salary, reverse=True)
		puesto_diario = 1
		for buscar_id in range(len(matriz_diario_total)):
			if  2 < buscar_id:
				matriz_diario_total[buscar_id][1] = puesto_diario
				matriz_diario_total[buscar_id][len(cursos)+3] = format( matriz_diario_total[buscar_id][len(cursos)+3], '.2f')
				puesto_diario = puesto_diario + 1
		matriz_diario_total[2][len(cursos)+3] = "PROMEDIO"
		return matriz_diario_total

	# reporte semanal por aula
	def funcion_matriz_notas_semanal(self,desde,hasta,aula):
		fecha_actual = datetime.now()
		cursos = self.env['curso.general'].sudo().search([])
		aula_filtro = self.env["grupo.alumnos"].sudo().search([('id', '=', aula)]).id
		alumnos = self.env["grupo.alumnos"].sudo().search([('id', '=', aula)]).users_ids
		if desde and not hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', '=', aula_filtro), ('tipo_evaluacion',  '=',  'semanal'),  ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '>',  desde)])
		elif not desde and not hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', '=', aula_filtro), ('tipo_evaluacion',  '=',  'semanal'), ('fecha_fin',  '<',  fecha_actual)])
		elif not desde and  hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', '=',aula_filtro), ('tipo_evaluacion',  '=',  'semanal'),  ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta)])
		elif desde and  hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', '=', aula_filtro), ('tipo_evaluacion',  '=',  'semanal'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta), ('fecha_fin',  '>',  desde)])

		matriz_semanal_total = []
		matriz_semanal = []
		matriz_semanal_active = [1,1,"FECHA"]
		matriz_semanal_idcursos = ["id cursos",0,0]
		matriz_semanal_namecursos = ["active","Nº","ALUMNO"]
		for line in cursos:
			matriz_semanal_active.append(0)
			matriz_semanal_idcursos.append(line.id)
			matriz_semanal_namecursos.append(line.name_corto)
		matriz_semanal_active.append(10002)
		matriz_semanal_idcursos.append(10001)
		matriz_semanal_namecursos.append(10000)
		matriz_semanal.append(matriz_semanal_active)
		matriz_semanal.append(matriz_semanal_idcursos)
		matriz_semanal.append(matriz_semanal_namecursos)
		for alumno in alumnos:
			matriz_alumno = []
			matriz_alumno.append(0)
			matriz_alumno.append(alumno.user_id.id)
			matriz_alumno.append(alumno.user_id.name)
			matriz_alumno_semanal_active = [0,0,0]
			matriz_alumno_semanal_idcursos = [0,0,0]
			matriz_alumno_suma_cantidad = [0,0,0]
			matriz_alumno_suma_total = [0,0,0]
			contador_cursos_activos = 0
			suma_cursos_activos = 0
			for curso_line in cursos:
				matriz_alumno.append("-")
				matriz_alumno_semanal_active.append(0)
				matriz_alumno_semanal_idcursos.append(curso_line.id)
				matriz_alumno_suma_cantidad.append(0)
				matriz_alumno_suma_total.append(0)

			for x_j_z in range(len(evaluaciones)) :
				for bloque in evaluaciones[x_j_z].bloques_ids:
					respuestas = self.env["respuesta"].sudo().search([('evaluacion_id', '=',evaluaciones[x_j_z].id),('user_id', '=',alumno.user_id.id),('examen_id', '=',bloque.examen_id.id)],order = 'nota_vigesimal desc',limit=1)
					if respuestas:
						matriz_alumno[0] = 1
						for nota_curso in respuestas.respuestas_slide_ids:
							if nota_curso.curso_general_id:
								indice = matriz_alumno_semanal_idcursos.index(nota_curso.curso_general_id.id)
								matriz_semanal[0][indice] = 1
								matriz_alumno_semanal_active[indice] = 1
								matriz_alumno_suma_total[indice] = matriz_alumno_suma_total[indice] +  nota_curso.nota_vigesimal
								matriz_alumno_suma_cantidad[indice] = matriz_alumno_suma_cantidad[indice] + 1
			for guardar in range(len(matriz_alumno_semanal_active)) :
				if matriz_alumno_semanal_active[guardar] != 0:
					contador_cursos_activos = contador_cursos_activos + 1
					if matriz_alumno_suma_cantidad[guardar] ==0:
						matriz_alumno[guardar] = format( 0.0 , '.2f')
					else:
						matriz_alumno[guardar] = format( round(matriz_alumno_suma_total[guardar] / matriz_alumno_suma_cantidad[guardar],2) , '.2f')
					suma_cursos_activos = suma_cursos_activos +round(matriz_alumno_suma_total[guardar] / matriz_alumno_suma_cantidad[guardar],2)
			if contador_cursos_activos == 0:
				matriz_alumno.append(0)
			else:
				matriz_alumno.append(round(suma_cursos_activos/contador_cursos_activos,2))
			matriz_semanal.append(matriz_alumno)
		matriz_semanal_total = 	[s for s in matriz_semanal if s[0] != 0]
		def get_salary(elem):
			return elem[len(cursos)+3]

		matriz_semanal_total.sort(key=get_salary, reverse=True)
		puesto_diario = 1
		for buscar_id in range(len(matriz_semanal_total)):
			if  2 < buscar_id:
				matriz_semanal_total[buscar_id][1] = puesto_diario
				matriz_semanal_total[buscar_id][len(cursos)+3] = format( matriz_semanal_total[buscar_id][len(cursos)+3], '.2f')
				puesto_diario = puesto_diario + 1
		matriz_semanal_total[2][len(cursos)+3] = "PROMEDIO"
		return matriz_semanal_total


	# reporte simulacro por aula
	def funcion_matriz_notas_simulacro(self,desde,aula,grupo):
		fecha_actual = datetime.now(pytz.timezone('America/Lima'))
		if ((len(aula)==0) and (len(grupo)>0)) or ((len(aula)>0) and (len(grupo)==0)) :
			select_grupo = []
			for rec in range(len(aula)):
				select_grupo.append(int(aula[rec]))
			for rec in range(len(grupo)):
				select_grupo.append(int(grupo[rec]))
			select_grupo_dict = self.env['grupo.alumnos'].sudo().search([('id',  'in', [(rec) for rec in select_grupo])])
			alumno_ids = []
			for line in select_grupo_dict:
				for line_user in line.users_ids:
					alumno_ids.append(line_user.user_id.id)
			respuestas = self.env["respuesta"].sudo().search([('user_id','in',alumno_ids),('evaluacion_id.tipo_evaluacion','=','simulacro'), ('create_date','<',fecha_actual)],order = 'nota_vigesimal desc')
			evaluaciones_ids = []
			for line in respuestas:
				evaluaciones_ids.append(line.evaluacion_id.id)
			cursos = self.env['curso.general'].sudo().search([])
			carreras = self.env['estudiante.carrera'].sudo().search([])
			evaluaciones = self.env["evaluacion"].sudo().search([('id',  'in', evaluaciones_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('fecha_fin',  '<',  fecha_actual)])
			matriz_simulacro_total_eval = []
			matriz_simulacro_total_header = []
			matriz_simulacro_total_header.append("id")
			matriz_simulacro_total_header.append("CARRERA")
			matriz_simulacro_total_header.append("N°")
			matriz_simulacro_total_header.append("ALUMNO")
			matriz_simulacro_total_header.append("AULAS")
			matriz_simulacro_total_header.append("")
			matriz_simulacro_total_header.append("")
			matriz_simulacro_total_header.append("")
			matriz_simulacro_total_header.append("")
			matriz_simulacro_total_header.append("PUNTAJE")
			indice_face = 1
			cursos_activos = []
			matriz_simulacro = []
			matriz_simulacro_total = []
			indice_matriz = 1
			matriz_simulacro.append([])
			matriz_simulacro[0].append("id")
			matriz_simulacro[0].append("CARRERA")
			matriz_simulacro[0].append("N°")
			matriz_simulacro[0].append("ALUMNO")
			matriz_simulacro[0].append("AULAS")
			matriz_simulacro[0].append("FASE 1")
			matriz_simulacro[0].append("FASE 2")
			matriz_simulacro[0].append("FASE 3")
			matriz_simulacro[0].append("FASE 4")
			matriz_simulacro[0].append("PUNTAJE")

			for line in range(len(evaluaciones)):
				indice_face = 5
				puntaje_total = 0
				if evaluaciones[line].fecha_inicio.strftime("%Y-%m-%d") == desde:
					for bloque in evaluaciones[line].bloques_ids:
						matriz_simulacro_total_header[indice_face] = bloque.name
						bloque_respuesta = self.env["respuesta"].sudo().search([('user_id','in',alumno_ids),('evaluacion_id', '=', evaluaciones[line].id), ('examen_id',  '=',bloque.examen_id.id)],order = 'nota_vigesimal desc')
						for respuesta_alumno in range(len(bloque_respuesta)):
							crear_linea_tabla = True
							indice_linea_tabla = 0
							for buscar_id in range(len(matriz_simulacro)):
								if matriz_simulacro[buscar_id][2] ==bloque_respuesta[respuesta_alumno].user_id.id:
									crear_linea_tabla = False
									indice_linea_tabla = buscar_id
							if crear_linea_tabla:
								matriz_simulacro.append([])
								matriz_simulacro[indice_matriz].append(0)
								matriz_simulacro[indice_matriz].append(0)
								matriz_simulacro[indice_matriz].append(0)
								matriz_simulacro[indice_matriz].append("")
								matriz_simulacro[indice_matriz].append("")
								matriz_simulacro[indice_matriz].append("")
								matriz_simulacro[indice_matriz].append("")
								matriz_simulacro[indice_matriz].append("")
								matriz_simulacro[indice_matriz].append("")
								matriz_simulacro[indice_matriz].append(0)
								matriz_simulacro[indice_matriz][0] = bloque_respuesta[respuesta_alumno].user_id.carrera_id.name
								matriz_simulacro[indice_matriz][1] = bloque_respuesta[respuesta_alumno].user_id.carrera_id.id
								matriz_simulacro[indice_matriz][2] = bloque_respuesta[respuesta_alumno].user_id.id
								matriz_simulacro[indice_matriz][3] = bloque_respuesta[respuesta_alumno].user_id.name
								name_aulas = self.get_name_aulas(bloque_respuesta[respuesta_alumno].user_id.aula_eval_ids)
								matriz_simulacro[indice_matriz][4] = name_aulas[:40]
								matriz_simulacro[indice_matriz][indice_face] = format(round(bloque_respuesta[respuesta_alumno].puntaje,3), '.3f')
								matriz_simulacro[indice_matriz][9] = matriz_simulacro[indice_matriz][9] + (round(bloque_respuesta[respuesta_alumno].puntaje,3))

								if bloque_respuesta[respuesta_alumno].user_id.carrera_id.id not in cursos_activos:
									cursos_activos.append(bloque_respuesta[respuesta_alumno].user_id.carrera_id.id)
								indice_matriz = indice_matriz + 1
							else:
								matriz_simulacro[indice_linea_tabla][indice_face] = format(round(bloque_respuesta[respuesta_alumno].puntaje,3), '.3f')
								matriz_simulacro[indice_linea_tabla][9] = matriz_simulacro[indice_linea_tabla][9] + (round(bloque_respuesta[respuesta_alumno].puntaje,3))
						indice_face = indice_face + 1

			for curso_activo in range(len(cursos_activos)):
				matriz_simulacro_total.append([])
				carrera_name = self.env['estudiante.carrera'].sudo().search([('id', '=', cursos_activos[curso_activo])])
				matriz_simulacro_total[curso_activo].append(carrera_name.name)
				matriz_simulacro_total[curso_activo].append(carrera_name.minimo)
				matriz_simulacro_total[curso_activo].append([])
				for buscar_id in range(len(matriz_simulacro)):
					if matriz_simulacro[buscar_id][1] == cursos_activos[curso_activo]:
						matriz_simulacro_total[curso_activo][2].append(matriz_simulacro[buscar_id])
				if not cursos_activos[curso_activo]:
					matriz_simulacro_total[curso_activo][0]="SIN CARRERA"

			matriz_simulacro_total_ordenados = []
			for curso_activo in range(len(cursos_activos)):
				matriz_simulacro_total_ordenados.append([])
				matriz_simulacro_total_ordenados[curso_activo].append(matriz_simulacro_total[curso_activo][0])
				matriz_simulacro_total_ordenados[curso_activo].append(matriz_simulacro_total[curso_activo][1])

				def get_salary(elem):
					return elem[9]
				matriz_simulacro_total[curso_activo][2].sort(key=get_salary, reverse=True)
				puesto_diario = 1
				for buscar_id in matriz_simulacro_total[curso_activo][2]:
					for n_puesto_line in buscar_id:
						buscar_id[2] = puesto_diario
					buscar_id[9] = format(buscar_id[9], '.3f')
					puesto_diario += 1
				matriz_simulacro_total_ordenados[curso_activo].append(matriz_simulacro_total[curso_activo][2])
			matriz_unico = []
			matriz_unico.append(matriz_simulacro_total_ordenados)
			matriz_unico.append(matriz_simulacro_total_header)
			return matriz_unico
		else:
			select_grupo = []
			select_aula = []
			for rec in range(len(aula)):
				select_aula.append(int(aula[rec]))
			for rec in range(len(grupo)):
				select_grupo.append(int(grupo[rec]))
			select_grupo_dict = self.env['grupo.alumnos'].sudo().search([('id',  'in', [(rec) for rec in select_grupo])])
			alumno_ids = []
			for line in select_grupo_dict:
				for line_user in line.users_ids:
					for linea_user_aula in line_user.user_id.aula_eval_ids:
						if linea_user_aula.grupo_alumnos_id.id in select_aula:
							if not(line_user.user_id.id in alumno_ids):
								alumno_ids.append(line_user.user_id.id)
			respuestas = self.env["respuesta"].sudo().search([('user_id','in',alumno_ids),('evaluacion_id.tipo_evaluacion','=','simulacro'), ('create_date','<',fecha_actual)],order = 'nota_vigesimal desc')
			evaluaciones_ids = []
			for line in respuestas:
				evaluaciones_ids.append(line.evaluacion_id.id)
			cursos = self.env['curso.general'].sudo().search([])
			carreras = self.env['estudiante.carrera'].sudo().search([])
			evaluaciones = self.env["evaluacion"].sudo().search([('id',  'in', evaluaciones_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('fecha_fin',  '<',  fecha_actual)])
			matriz_simulacro_total_eval = []
			matriz_simulacro_total_header = []
			matriz_simulacro_total_header.append("id")
			matriz_simulacro_total_header.append("CARRERA")
			matriz_simulacro_total_header.append("N°")
			matriz_simulacro_total_header.append("ALUMNO")
			matriz_simulacro_total_header.append("AULAS")
			matriz_simulacro_total_header.append("")
			matriz_simulacro_total_header.append("")
			matriz_simulacro_total_header.append("")
			matriz_simulacro_total_header.append("")
			matriz_simulacro_total_header.append("PUNTAJE")
			indice_face = 1
			cursos_activos = []
			matriz_simulacro = []
			matriz_simulacro_total = []
			indice_matriz = 1
			matriz_simulacro.append([])
			matriz_simulacro[0].append("id")
			matriz_simulacro[0].append("CARRERA")
			matriz_simulacro[0].append("N°")
			matriz_simulacro[0].append("ALUMNO")
			matriz_simulacro[0].append("AULAS")
			matriz_simulacro[0].append("FASE 1")
			matriz_simulacro[0].append("FASE 2")
			matriz_simulacro[0].append("FASE 3")
			matriz_simulacro[0].append("FASE 4")
			matriz_simulacro[0].append("PUNTAJE")

			for line in range(len(evaluaciones)):
				indice_face = 5
				puntaje_total = 0
				if evaluaciones[line].fecha_inicio.strftime("%Y-%m-%d") == desde:
					for bloque in evaluaciones[line].bloques_ids:
						matriz_simulacro_total_header[indice_face] = bloque.name
						bloque_respuesta = self.env["respuesta"].sudo().search([('user_id','in',alumno_ids),('evaluacion_id', '=', evaluaciones[line].id), ('examen_id',  '=',bloque.examen_id.id)],order = 'nota_vigesimal desc')
						for respuesta_alumno in range(len(bloque_respuesta)):
							crear_linea_tabla = True
							indice_linea_tabla = 0
							for buscar_id in range(len(matriz_simulacro)):
								if matriz_simulacro[buscar_id][2] ==bloque_respuesta[respuesta_alumno].user_id.id:
									crear_linea_tabla = False
									indice_linea_tabla = buscar_id
							if crear_linea_tabla:
								matriz_simulacro.append([])
								matriz_simulacro[indice_matriz].append(0)
								matriz_simulacro[indice_matriz].append(0)
								matriz_simulacro[indice_matriz].append(0)
								matriz_simulacro[indice_matriz].append("")
								matriz_simulacro[indice_matriz].append("")
								matriz_simulacro[indice_matriz].append("")
								matriz_simulacro[indice_matriz].append("")
								matriz_simulacro[indice_matriz].append("")
								matriz_simulacro[indice_matriz].append("")
								matriz_simulacro[indice_matriz].append(0)
								matriz_simulacro[indice_matriz][0] = bloque_respuesta[respuesta_alumno].user_id.carrera_id.name
								matriz_simulacro[indice_matriz][1] = bloque_respuesta[respuesta_alumno].user_id.carrera_id.id
								matriz_simulacro[indice_matriz][2] = bloque_respuesta[respuesta_alumno].user_id.id
								matriz_simulacro[indice_matriz][3] = bloque_respuesta[respuesta_alumno].user_id.name
								name_aulas = self.get_name_aulas(bloque_respuesta[respuesta_alumno].user_id.aula_eval_ids)
								matriz_simulacro[indice_matriz][4] = name_aulas[:40]
								matriz_simulacro[indice_matriz][indice_face] = format(round(bloque_respuesta[respuesta_alumno].puntaje,3), '.3f')
								matriz_simulacro[indice_matriz][9] = matriz_simulacro[indice_matriz][9] + (round(bloque_respuesta[respuesta_alumno].puntaje,3))

								if bloque_respuesta[respuesta_alumno].user_id.carrera_id.id not in cursos_activos:
									cursos_activos.append(bloque_respuesta[respuesta_alumno].user_id.carrera_id.id)
								indice_matriz = indice_matriz + 1
							else:
								matriz_simulacro[indice_linea_tabla][indice_face] = format(round(bloque_respuesta[respuesta_alumno].puntaje,3), '.3f')
								matriz_simulacro[indice_linea_tabla][9] = matriz_simulacro[indice_linea_tabla][9] + (round(bloque_respuesta[respuesta_alumno].puntaje,3))
						indice_face = indice_face + 1

			for curso_activo in range(len(cursos_activos)):
				matriz_simulacro_total.append([])
				carrera_name = self.env['estudiante.carrera'].sudo().search([('id', '=', cursos_activos[curso_activo])])
				matriz_simulacro_total[curso_activo].append(carrera_name.name)
				matriz_simulacro_total[curso_activo].append(carrera_name.minimo)
				matriz_simulacro_total[curso_activo].append([])
				for buscar_id in range(len(matriz_simulacro)):
					if matriz_simulacro[buscar_id][1] == cursos_activos[curso_activo]:
						matriz_simulacro_total[curso_activo][2].append(matriz_simulacro[buscar_id])
				if not cursos_activos[curso_activo]:
					matriz_simulacro_total[curso_activo][0]="SIN CARRERA"

			matriz_simulacro_total_ordenados = []
			for curso_activo in range(len(cursos_activos)):
				matriz_simulacro_total_ordenados.append([])
				matriz_simulacro_total_ordenados[curso_activo].append(matriz_simulacro_total[curso_activo][0])
				matriz_simulacro_total_ordenados[curso_activo].append(matriz_simulacro_total[curso_activo][1])

				def get_salary(elem):
					return elem[9]
				matriz_simulacro_total[curso_activo][2].sort(key=get_salary, reverse=True)
				puesto_diario = 1
				for buscar_id in matriz_simulacro_total[curso_activo][2]:
					for n_puesto_line in buscar_id:
						buscar_id[2] = puesto_diario
					buscar_id[9] = format(buscar_id[9], '.3f')
					puesto_diario += 1
				matriz_simulacro_total_ordenados[curso_activo].append(matriz_simulacro_total[curso_activo][2])
			matriz_unico = []
			matriz_unico.append(matriz_simulacro_total_ordenados)
			matriz_unico.append(matriz_simulacro_total_header)
			return matriz_unico

	def funcion_matriz_notas_simulacro_promedios(self,desde,hasta,aula,grupo):
		fecha_actual = datetime.now()
		if ((len(aula)==0) and (len(grupo)>0)) or ((len(aula)>0) and (len(grupo)==0)) :
			select_grupo = []
			for rec in range(len(aula)):
				select_grupo.append(int(aula[rec]))
			for rec in range(len(grupo)):
				select_grupo.append(int(grupo[rec]))
			select_grupo_dict = self.env['grupo.alumnos'].sudo().search([('id',  'in', [(rec) for rec in select_grupo])])
			alumno_ids = []
			for line in select_grupo_dict:
				for line_user in line.users_ids:
					alumno_ids.append(line_user.user_id.id)
			respuestas = self.env["respuesta"].sudo().search([('user_id','in',alumno_ids),('evaluacion_id.tipo_evaluacion','=','simulacro'), ('create_date','<',fecha_actual)],order = 'nota_vigesimal desc')
			evaluaciones_ids = []
			for line in respuestas:
				evaluaciones_ids.append(line.evaluacion_id.id)
			cursos = self.env['curso.general'].sudo().search([])
			carreras = self.env['estudiante.carrera'].sudo().search([])
			if desde and not hasta:
				evaluaciones = self.env["evaluacion"].sudo().search([('id', '=',evaluaciones_ids), ('tipo_evaluacion',  '=',  'simulacro'),  ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '>=',  desde)],order = 'fecha_inicio asc')
			elif not desde and not hasta:
				evaluaciones = self.env["evaluacion"].sudo().search([('id', '=',evaluaciones_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('fecha_fin',  '<=',  fecha_actual)],order = 'fecha_inicio asc')
			elif not desde and  hasta:
				evaluaciones = self.env["evaluacion"].sudo().search([('id', '=',evaluaciones_ids), ('tipo_evaluacion',  '=',  'simulacro'),  ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '<=',  hasta)],order = 'fecha_inicio asc')
			elif desde and  hasta:
				evaluaciones = self.env["evaluacion"].sudo().search([('id', '=',evaluaciones_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '<=',  hasta), ('fecha_fin',  '>=',  desde)],order = 'fecha_inicio asc')

			fecha_data_evaluaciones  = []
			ids_data_evaluaciones  = []
			for line in range(len(evaluaciones)):
				date_fecha_fin = evaluaciones[line].fecha_inicio.date()
				if date_fecha_fin in fecha_data_evaluaciones:
					indice = fecha_data_evaluaciones.index(date_fecha_fin)
					ids_data_evaluaciones[indice].append(evaluaciones[line].id)
				else:
					fecha_data_evaluaciones.append(date_fecha_fin)
					ids_data_evaluaciones.append([evaluaciones[line].id])
			matriz_simulacro = []
			indice_matriz = 1
			cursos_activos = []
			matriz_simulacro.append([])
			matriz_simulacro[0].append("TOTAL")
			matriz_simulacro[0].append("CANTIDAD")
			matriz_simulacro[0].append("id")
			matriz_simulacro[0].append("N°")
			matriz_simulacro[0].append("ALUMNO")
			matriz_simulacro[0].append("AULAS")
			indice_matriz = 1
			for line in range(len(fecha_data_evaluaciones)):
				matriz_simulacro[0].append(fecha_data_evaluaciones[line])
				respuesta_eva = self.env["respuesta.simulacro"].sudo().search([('user_id','in',alumno_ids),('evaluacion_id', 'in', ids_data_evaluaciones[line])],order = 'puntaje desc')
				for respuesta_alumno in range(len(respuesta_eva)):
					crear_linea_tabla = True
					indice_linea_tabla = 0
					for buscar_id in range(len(matriz_simulacro)):
						if matriz_simulacro[buscar_id][2] ==respuesta_eva[respuesta_alumno].user_id.id:
							crear_linea_tabla = False
							indice_linea_tabla = buscar_id
					if crear_linea_tabla:
						matriz_simulacro.append([])
						matriz_simulacro[indice_matriz].append(0)
						matriz_simulacro[indice_matriz].append(0)
						matriz_simulacro[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.id)
						matriz_simulacro[indice_matriz].append("N°")
						matriz_simulacro[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.name)
						name_aulas =self.get_name_aulas( respuesta_eva[respuesta_alumno].user_id.aula_eval_ids)
						matriz_simulacro[indice_matriz].append(name_aulas[:40])
						for nueva_linea in range(len(fecha_data_evaluaciones)):
							matriz_simulacro[indice_matriz].append("-")
						matriz_simulacro[indice_matriz].append(0)
						matriz_simulacro[indice_matriz][line+6] = (round(respuesta_eva[respuesta_alumno].puntaje,3))
						matriz_simulacro[indice_matriz][0] = matriz_simulacro[indice_matriz][line+6] + matriz_simulacro[indice_matriz][0]
						matriz_simulacro[indice_matriz][1] = 1 + matriz_simulacro[indice_matriz][1]
						if matriz_simulacro[indice_matriz][1] == 0:
							matriz_simulacro[indice_matriz][len(fecha_data_evaluaciones) + 6] = 0
						else:
							matriz_simulacro[indice_matriz][len(fecha_data_evaluaciones) + 6] = round(matriz_simulacro[indice_matriz][0] / matriz_simulacro[indice_matriz][1] ,3)
						indice_matriz = indice_matriz + 1
					else:
						matriz_simulacro[indice_linea_tabla][line+6] = (round(respuesta_eva[respuesta_alumno].puntaje,3))
						matriz_simulacro[indice_linea_tabla][0] = matriz_simulacro[indice_linea_tabla][line+6] + matriz_simulacro[indice_linea_tabla][0]
						matriz_simulacro[indice_linea_tabla][1] = 1 + matriz_simulacro[indice_linea_tabla][1]
						if matriz_simulacro[indice_linea_tabla][1] == 0:
							matriz_simulacro[indice_linea_tabla][len(fecha_data_evaluaciones) + 6] = 0
						else:
							matriz_simulacro[indice_linea_tabla][len(fecha_data_evaluaciones) + 6] = round(matriz_simulacro[indice_linea_tabla][0] / matriz_simulacro[indice_linea_tabla][1] ,3)

			matriz_simulacro[0].append(10000)
			def get_salary(elem):
				return elem[len(fecha_data_evaluaciones) + 6]
			matriz_simulacro.sort(key=get_salary,reverse=True)
			puesto_diario = 1
			for buscar_id in range(len(matriz_simulacro)):
				if  0 < buscar_id:
					matriz_simulacro[buscar_id][3] = buscar_id
					matriz_simulacro[buscar_id][len(fecha_data_evaluaciones)+6] = format(matriz_simulacro[buscar_id][len(fecha_data_evaluaciones)+6], '.3f')
					for nueva_linea in range(len(matriz_simulacro[buscar_id])):
						if  5 < nueva_linea and nueva_linea < (len(fecha_data_evaluaciones)+6) and matriz_simulacro[buscar_id][nueva_linea] != "-":
							matriz_simulacro[buscar_id][nueva_linea] =  format(matriz_simulacro[buscar_id][nueva_linea], '.3f')

				puesto_diario += 1
			matriz_simulacro[0][len(fecha_data_evaluaciones)+6] = "PROMEDIO"

			return matriz_simulacro
		else:
			select_grupo = []
			select_aula = []
			for rec in range(len(aula)):
				select_aula.append(int(aula[rec]))
			for rec in range(len(grupo)):
				select_grupo.append(int(grupo[rec]))
			select_grupo_dict = self.env['grupo.alumnos'].sudo().search([('id',  'in', [(rec) for rec in select_grupo])])
			alumno_ids = []
			for line in select_grupo_dict:
				for line_user in line.users_ids:
					for linea_user_aula in line_user.user_id.aula_eval_ids:
						if linea_user_aula.grupo_alumnos_id.id in select_aula:
							if not(line_user.user_id.id in alumno_ids):
								alumno_ids.append(line_user.user_id.id)
			respuestas = self.env["respuesta"].sudo().search([('user_id','in',alumno_ids),('evaluacion_id.tipo_evaluacion','=','simulacro'), ('create_date','<',fecha_actual)],order = 'nota_vigesimal desc')
			evaluaciones_ids = []
			for line in respuestas:
				evaluaciones_ids.append(line.evaluacion_id.id)
			cursos = self.env['curso.general'].sudo().search([])
			carreras = self.env['estudiante.carrera'].sudo().search([])
			if desde and not hasta:
				evaluaciones = self.env["evaluacion"].sudo().search([('id', '=',evaluaciones_ids), ('tipo_evaluacion',  '=',  'simulacro'),  ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '>=',  desde)],order = 'fecha_inicio asc')
			elif not desde and not hasta:
				evaluaciones = self.env["evaluacion"].sudo().search([('id', '=',evaluaciones_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('fecha_fin',  '<=',  fecha_actual)],order = 'fecha_inicio asc')
			elif not desde and  hasta:
				evaluaciones = self.env["evaluacion"].sudo().search([('id', '=',evaluaciones_ids), ('tipo_evaluacion',  '=',  'simulacro'),  ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '<=',  hasta)],order = 'fecha_inicio asc')
			elif desde and  hasta:
				evaluaciones = self.env["evaluacion"].sudo().search([('id', '=',evaluaciones_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '<=',  hasta), ('fecha_fin',  '>=',  desde)],order = 'fecha_inicio asc')

			fecha_data_evaluaciones  = []
			ids_data_evaluaciones  = []
			for line in range(len(evaluaciones)):
				date_fecha_fin = evaluaciones[line].fecha_inicio.date()
				if date_fecha_fin in fecha_data_evaluaciones:
					indice = fecha_data_evaluaciones.index(date_fecha_fin)
					ids_data_evaluaciones[indice].append(evaluaciones[line].id)
				else:
					fecha_data_evaluaciones.append(date_fecha_fin)
					ids_data_evaluaciones.append([evaluaciones[line].id])
			matriz_simulacro = []
			indice_matriz = 1
			cursos_activos = []
			matriz_simulacro.append([])
			matriz_simulacro[0].append("TOTAL")
			matriz_simulacro[0].append("CANTIDAD")
			matriz_simulacro[0].append("id")
			matriz_simulacro[0].append("N°")
			matriz_simulacro[0].append("ALUMNO")
			matriz_simulacro[0].append("AULAS")
			indice_matriz = 1
			for line in range(len(fecha_data_evaluaciones)):
				matriz_simulacro[0].append(fecha_data_evaluaciones[line])
				respuesta_eva = self.env["respuesta.simulacro"].sudo().search([('user_id','in',alumno_ids),('evaluacion_id', 'in', ids_data_evaluaciones[line])],order = 'puntaje desc')
				for respuesta_alumno in range(len(respuesta_eva)):
					crear_linea_tabla = True
					indice_linea_tabla = 0
					for buscar_id in range(len(matriz_simulacro)):
						if matriz_simulacro[buscar_id][2] ==respuesta_eva[respuesta_alumno].user_id.id:
							crear_linea_tabla = False
							indice_linea_tabla = buscar_id
					if crear_linea_tabla:
						matriz_simulacro.append([])
						matriz_simulacro[indice_matriz].append(0)
						matriz_simulacro[indice_matriz].append(0)
						matriz_simulacro[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.id)
						matriz_simulacro[indice_matriz].append("N°")
						matriz_simulacro[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.name)
						name_aulas =self.get_name_aulas( respuesta_eva[respuesta_alumno].user_id.aula_eval_ids)
						matriz_simulacro[indice_matriz].append(name_aulas[:40])
						for nueva_linea in range(len(fecha_data_evaluaciones)):
							matriz_simulacro[indice_matriz].append("-")
						matriz_simulacro[indice_matriz].append(0)
						matriz_simulacro[indice_matriz][line+6] = (round(respuesta_eva[respuesta_alumno].puntaje,3))
						matriz_simulacro[indice_matriz][0] = matriz_simulacro[indice_matriz][line+6] + matriz_simulacro[indice_matriz][0]
						matriz_simulacro[indice_matriz][1] = 1 + matriz_simulacro[indice_matriz][1]
						if matriz_simulacro[indice_matriz][1] == 0:
							matriz_simulacro[indice_matriz][len(fecha_data_evaluaciones) + 6] = 0
						else:
							matriz_simulacro[indice_matriz][len(fecha_data_evaluaciones) + 6] = round(matriz_simulacro[indice_matriz][0] / matriz_simulacro[indice_matriz][1] ,3)
						indice_matriz = indice_matriz + 1
					else:
						matriz_simulacro[indice_linea_tabla][line+6] = (round(respuesta_eva[respuesta_alumno].puntaje,3))
						matriz_simulacro[indice_linea_tabla][0] = matriz_simulacro[indice_linea_tabla][line+6] + matriz_simulacro[indice_linea_tabla][0]
						matriz_simulacro[indice_linea_tabla][1] = 1 + matriz_simulacro[indice_linea_tabla][1]
						if matriz_simulacro[indice_linea_tabla][1] == 0:
							matriz_simulacro[indice_linea_tabla][len(fecha_data_evaluaciones) + 6] = 0
						else:
							matriz_simulacro[indice_linea_tabla][len(fecha_data_evaluaciones) + 6] = round(matriz_simulacro[indice_linea_tabla][0] / matriz_simulacro[indice_linea_tabla][1] ,3)

			matriz_simulacro[0].append(10000)
			def get_salary(elem):
				return elem[len(fecha_data_evaluaciones) + 6]
			matriz_simulacro.sort(key=get_salary,reverse=True)
			puesto_diario = 1
			for buscar_id in range(len(matriz_simulacro)):
				if  0 < buscar_id:
					matriz_simulacro[buscar_id][3] = buscar_id
					matriz_simulacro[buscar_id][len(fecha_data_evaluaciones)+6] = format(matriz_simulacro[buscar_id][len(fecha_data_evaluaciones)+6], '.3f')
					for nueva_linea in range(len(matriz_simulacro[buscar_id])):
						if  5 < nueva_linea and nueva_linea < (len(fecha_data_evaluaciones)+6) and matriz_simulacro[buscar_id][nueva_linea] != "-":
							matriz_simulacro[buscar_id][nueva_linea] =  format(matriz_simulacro[buscar_id][nueva_linea], '.3f')

				puesto_diario += 1
			matriz_simulacro[0][len(fecha_data_evaluaciones)+6] = "PROMEDIO"

			return matriz_simulacro


	def funcion_matriz_notas_simulacro_ponderados(self,desde,hasta,aula,grupo):
		fecha_actual = datetime.now()
		if ((len(aula)==0) and (len(grupo)>0)) or ((len(aula)>0) and (len(grupo)==0)) :
			select_grupo = []
			for rec in range(len(aula)):
				select_grupo.append(int(aula[rec]))
			for rec in range(len(grupo)):
				select_grupo.append(int(grupo[rec]))
			cursos = self.env['curso.general'].sudo().search([])
			carreras = self.env['estudiante.carrera'].sudo().search([])
			ids_filtro_estudiante = []
			ids_filtro_aulas = []
			for select_line in range(len(select_grupo)):
				aula_filtro = self.env["grupo.alumnos"].sudo().search([('id', '=', select_grupo[select_line])],limit=1)
				for linea_aula  in aula_filtro.users_ids:
					ids_filtro_estudiante.append(linea_aula.user_id.id)
					res_users_lineas = self.env["res.users.line"].sudo().search([('user_id', '=', linea_aula.user_id.id)])
					for linea_many_2 in res_users_lineas:
						ids_filtro_aulas.append(linea_many_2.grupo_alumnos_id.id)
			if desde and not hasta:
				evaluaciones_diarias = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', ids_filtro_aulas), ('tipo_evaluacion',  '=',  'diario'),  ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '>',  desde)])
				evaluaciones_semanales = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', ids_filtro_aulas), ('tipo_evaluacion',  '=',  'semanal'),  ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '>',  desde)])
				evaluaciones_simulacros = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', ids_filtro_aulas), ('tipo_evaluacion',  '=',  'simulacro'),  ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '>',  desde)])
			elif not desde and not hasta:
				evaluaciones_diarias = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', ids_filtro_aulas), ('tipo_evaluacion',  '=',  'diario'), ('fecha_fin',  '<',  fecha_actual)])
				evaluaciones_semanales = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', ids_filtro_aulas), ('tipo_evaluacion',  '=',  'semanal'), ('fecha_fin',  '<',  fecha_actual)])
				evaluaciones_simulacros = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', ids_filtro_aulas), ('tipo_evaluacion',  '=',  'simulacro'), ('fecha_fin',  '<',  fecha_actual)])
			elif not desde and  hasta:
				evaluaciones_diarias = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in',ids_filtro_aulas), ('tipo_evaluacion',  '=',  'diario'),  ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta)])
				evaluaciones_semanales = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in',ids_filtro_aulas), ('tipo_evaluacion',  '=',  'semanal'),  ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta)])
				evaluaciones_simulacros = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in',ids_filtro_aulas), ('tipo_evaluacion',  '=',  'simulacro'),  ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta)])
			elif desde and  hasta:
				evaluaciones_diarias = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', ids_filtro_aulas), ('tipo_evaluacion',  '=',  'diario'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta), ('fecha_fin',  '>',  desde)])
				evaluaciones_semanales = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', ids_filtro_aulas), ('tipo_evaluacion',  '=',  'semanal'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta), ('fecha_fin',  '>',  desde)])
				evaluaciones_simulacros = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', ids_filtro_aulas), ('tipo_evaluacion',  '=',  'simulacro'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta), ('fecha_fin',  '>',  desde)])

			matriz_ponderados = []
			indice_matriz = 1
			cursos_activos = []
			matriz_ponderados.append([])
			matriz_ponderados[0].append("TOTAL DIARIAS")
			matriz_ponderados[0].append("CANTIDAD DIARIAS")
			matriz_ponderados[0].append("TOTAL SEMANAL")
			matriz_ponderados[0].append("CANTIDAD SEMANAL")
			matriz_ponderados[0].append("TOTAL SIMULACRO")
			matriz_ponderados[0].append("CANTIDAD SIMULACRO")
			matriz_ponderados[0].append("id")
			matriz_ponderados[0].append("N°")
			matriz_ponderados[0].append("ALUMNO")
			matriz_ponderados[0].append("AULAS")
			matriz_ponderados[0].append("PD")
			matriz_ponderados[0].append("PS")
			matriz_ponderados[0].append("SIM")
			matriz_ponderados[0].append(10000)
			pesos_modelo_diario = self.env["peso.evaluacion"].sudo().search([('tipo_evaluacion', '=', 'diario')],order = 'peso desc',limit=1)
			if pesos_modelo_diario:
				pesos_modelo_diario_valor = pesos_modelo_diario.peso
			else:
				pesos_modelo_diario_valor = 1
			pesos_modelo_semanal = self.env["peso.evaluacion"].sudo().search([('tipo_evaluacion', '=', 'semanal')],order = 'peso desc',limit=1)
			if pesos_modelo_semanal:
				pesos_modelo_semanal_valor = pesos_modelo_semanal.peso
			else:
				pesos_modelo_semanal_valor = 1
			pesos_modelo_simulacro = self.env["peso.evaluacion"].sudo().search([('tipo_evaluacion', '=', 'simulacro')],order = 'peso desc',limit=1)
			if pesos_modelo_simulacro:
				pesos_modelo_simulacro_valor = pesos_modelo_simulacro.peso
			else:
				pesos_modelo_simulacro_valor = 1
			for ev_diarias in range(len(evaluaciones_diarias)):
				respuesta_eva = self.env["respuesta"].sudo().search([('evaluacion_id', '=', evaluaciones_diarias[ev_diarias].id)],order = 'puntaje desc')
				for respuesta_alumno in range(len(respuesta_eva)):
					if (respuesta_eva[respuesta_alumno].user_id.id in ids_filtro_estudiante):
						crear_linea_tabla = True
						indice_linea_tabla = 0
						for buscar_id in range(len(matriz_ponderados)):
							if matriz_ponderados[buscar_id][6] ==respuesta_eva[respuesta_alumno].user_id.id:
								crear_linea_tabla = False
								indice_linea_tabla = buscar_id
						if crear_linea_tabla:
							matriz_ponderados.append([])
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.id)
							matriz_ponderados[indice_matriz].append("N°")
							matriz_ponderados[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.name)
							name_aulas = self.get_name_aulas(respuesta_eva[respuesta_alumno].user_id.aula_eval_ids)
							matriz_ponderados[indice_matriz].append(name_aulas[:40])
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz][0] = round( respuesta_eva[respuesta_alumno].nota_vigesimal + matriz_ponderados[indice_matriz][0] , 2)
							matriz_ponderados[indice_matriz][1] = 1 + matriz_ponderados[indice_matriz][1]
							if matriz_ponderados[indice_matriz][1] == 0:
								matriz_ponderados[indice_matriz][10] = 0
							else:
								matriz_ponderados[indice_matriz][10] = round(matriz_ponderados[indice_matriz][0]/matriz_ponderados[indice_matriz][1] ,2)
								matriz_ponderados[indice_matriz][13] = round((matriz_ponderados[indice_matriz][10]*pesos_modelo_diario_valor + matriz_ponderados[indice_matriz][11]*pesos_modelo_semanal_valor + matriz_ponderados[indice_matriz][12]*pesos_modelo_simulacro_valor )/(pesos_modelo_diario_valor+pesos_modelo_semanal_valor+pesos_modelo_simulacro_valor),2)
							indice_matriz = indice_matriz + 1
						else:
							matriz_ponderados[indice_linea_tabla][0] = round( respuesta_eva[respuesta_alumno].nota_vigesimal + matriz_ponderados[indice_linea_tabla][0],2)
							matriz_ponderados[indice_linea_tabla][1] = 1 + matriz_ponderados[indice_linea_tabla][1]
							if matriz_ponderados[indice_linea_tabla][1] == 0:
								matriz_ponderados[indice_linea_tabla][10] = 0
							else:
								matriz_ponderados[indice_linea_tabla][10] = round(matriz_ponderados[indice_linea_tabla][0]/matriz_ponderados[indice_linea_tabla][1] ,2)
								matriz_ponderados[indice_linea_tabla][13] = round(  (matriz_ponderados[indice_linea_tabla][10]*pesos_modelo_diario_valor + matriz_ponderados[indice_linea_tabla][11]*pesos_modelo_semanal_valor + matriz_ponderados[indice_linea_tabla][12]*pesos_modelo_simulacro_valor)/(pesos_modelo_diario_valor+pesos_modelo_semanal_valor+pesos_modelo_simulacro_valor),2)

			for ev_semanal in range(len(evaluaciones_semanales)):
				respuesta_eva = self.env["respuesta.simulacro"].sudo().search([('evaluacion_id', '=', evaluaciones_semanales[ev_semanal].id)],order = 'puntaje desc')
				for respuesta_alumno in range(len(respuesta_eva)):
					if (respuesta_eva[respuesta_alumno].user_id.id in ids_filtro_estudiante):
						crear_linea_tabla = True
						indice_linea_tabla = 0
						for buscar_id in range(len(matriz_ponderados)):
							if matriz_ponderados[buscar_id][6] ==respuesta_eva[respuesta_alumno].user_id.id:
								crear_linea_tabla = False
								indice_linea_tabla = buscar_id
						if crear_linea_tabla:
							matriz_ponderados.append([])
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.id)
							matriz_ponderados[indice_matriz].append("N°")
							matriz_ponderados[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.name)
							name_aulas = self.get_name_aulas(respuesta_eva[respuesta_alumno].user_id.aula_eval_ids)
							matriz_ponderados[indice_matriz].append(name_aulas[:40])
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz][2] = round(respuesta_eva[respuesta_alumno].nota_vigesimal + matriz_ponderados[indice_matriz][2])
							matriz_ponderados[indice_matriz][3] = 1 + matriz_ponderados[indice_matriz][3]
							if matriz_ponderados[indice_matriz][1] == 0:
								matriz_ponderados[indice_matriz][11] = 0
							else:
								matriz_ponderados[indice_matriz][11] = round(matriz_ponderados[indice_matriz][2]/matriz_ponderados[indice_matriz][3] ,2)
								matriz_ponderados[indice_matriz][13] = round((matriz_ponderados[indice_matriz][10]*pesos_modelo_diario_valor + matriz_ponderados[indice_matriz][11]*pesos_modelo_semanal_valor + matriz_ponderados[indice_matriz][12]*pesos_modelo_simulacro_valor )/(pesos_modelo_diario_valor+pesos_modelo_semanal_valor+pesos_modelo_simulacro_valor),2)
							indice_matriz = indice_matriz + 1
						else:
							matriz_ponderados[indice_linea_tabla][2] = round( respuesta_eva[respuesta_alumno].nota_vigesimal + matriz_ponderados[indice_linea_tabla][2],2)
							matriz_ponderados[indice_linea_tabla][3] = 1 + matriz_ponderados[indice_linea_tabla][3]
							if matriz_ponderados[indice_linea_tabla][3] == 0:
								matriz_ponderados[indice_linea_tabla][11] = 0
							else:
								matriz_ponderados[indice_linea_tabla][11] = round(matriz_ponderados[indice_linea_tabla][2]/matriz_ponderados[indice_linea_tabla][3] ,2)
								matriz_ponderados[indice_linea_tabla][13] = round(  (matriz_ponderados[indice_linea_tabla][10]*pesos_modelo_diario_valor + matriz_ponderados[indice_linea_tabla][11]*pesos_modelo_semanal_valor + matriz_ponderados[indice_linea_tabla][12]*pesos_modelo_simulacro_valor)/(pesos_modelo_diario_valor+pesos_modelo_semanal_valor+pesos_modelo_simulacro_valor),2)

			for ev_simulacro in range(len(evaluaciones_simulacros)):
				respuesta_eva = self.env["respuesta.simulacro"].sudo().search([('evaluacion_id', '=', evaluaciones_simulacros[ev_simulacro].id)],order = 'puntaje desc')
				for respuesta_alumno in range(len(respuesta_eva)):
					if (respuesta_eva[respuesta_alumno].user_id.id in ids_filtro_estudiante):
						crear_linea_tabla = True
						indice_linea_tabla = 0
						for buscar_id in range(len(matriz_ponderados)):
							if matriz_ponderados[buscar_id][6] ==respuesta_eva[respuesta_alumno].user_id.id:
								crear_linea_tabla = False
								indice_linea_tabla = buscar_id
						if crear_linea_tabla:
							matriz_ponderados.append([])
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.id)
							matriz_ponderados[indice_matriz].append("N°")
							matriz_ponderados[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.name)
							name_aulas = self.get_name_aulas(respuesta_eva[respuesta_alumno].user_id.aula_eval_ids)
							matriz_ponderados[indice_matriz].append(name_aulas[:40])
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz][4] = round( respuesta_eva[respuesta_alumno].nota_vigesimal + matriz_ponderados[indice_matriz][4] ,2)
							matriz_ponderados[indice_matriz][5] = 1 + matriz_ponderados[indice_matriz][5]
							if matriz_ponderados[indice_matriz][1] == 0:
								matriz_ponderados[indice_matriz][11] = 0
							else:
								matriz_ponderados[indice_matriz][11] = round(matriz_ponderados[indice_matriz][4]/matriz_ponderados[indice_matriz][5] ,2)
								matriz_ponderados[indice_matriz][13] = round((matriz_ponderados[indice_matriz][10]*pesos_modelo_diario_valor + matriz_ponderados[indice_matriz][11]*pesos_modelo_semanal_valor + matriz_ponderados[indice_matriz][12]*pesos_modelo_simulacro_valor )/(pesos_modelo_diario_valor+pesos_modelo_semanal_valor+pesos_modelo_simulacro_valor),2)
							indice_matriz = indice_matriz + 1
						else:
							matriz_ponderados[indice_linea_tabla][4] = round(respuesta_eva[respuesta_alumno].nota_vigesimal + matriz_ponderados[indice_linea_tabla][4],2)
							matriz_ponderados[indice_linea_tabla][5] = 1 + matriz_ponderados[indice_linea_tabla][5]
							if matriz_ponderados[indice_linea_tabla][5] == 0:
								matriz_ponderados[indice_linea_tabla][12] = 0
							else:
								matriz_ponderados[indice_linea_tabla][12] = round(matriz_ponderados[indice_linea_tabla][4]/matriz_ponderados[indice_linea_tabla][5] ,2)
								matriz_ponderados[indice_linea_tabla][13] = round(  (matriz_ponderados[indice_linea_tabla][10]*pesos_modelo_diario_valor + matriz_ponderados[indice_linea_tabla][11]*pesos_modelo_semanal_valor + matriz_ponderados[indice_linea_tabla][12]*pesos_modelo_simulacro_valor)/(pesos_modelo_diario_valor+pesos_modelo_semanal_valor+pesos_modelo_simulacro_valor),2)

			def get_salary(elem):
				return elem[13]
			matriz_ponderados.sort(key=get_salary, reverse=True)
			for buscar_id in range(len(matriz_ponderados)):
				if  0 < buscar_id:
					matriz_ponderados[buscar_id][7] = buscar_id
					matriz_ponderados[buscar_id][10] = format(matriz_ponderados[buscar_id][10], '.2f')
					matriz_ponderados[buscar_id][11] = format(matriz_ponderados[buscar_id][11], '.2f')
					matriz_ponderados[buscar_id][12] = format(matriz_ponderados[buscar_id][12], '.2f')
					matriz_ponderados[buscar_id][13] = format(matriz_ponderados[buscar_id][13], '.2f')
			matriz_ponderados[0][13] = "PROMEDIO"

			return matriz_ponderados
		else:
			select_grupo = []
			select_aula = []
			for rec in range(len(aula)):
				select_aula.append(int(aula[rec]))
			for rec in range(len(grupo)):
				select_grupo.append(int(grupo[rec]))
			select_grupo_dict = self.env['grupo.alumnos'].sudo().search([('id',  'in', [(rec) for rec in select_grupo])])
			alumno_ids = []
			for line in select_grupo_dict:
				for line_user in line.users_ids:
					for linea_user_aula in line_user.user_id.aula_eval_ids:
						if linea_user_aula.grupo_alumnos_id.id in select_aula:
							if not(line_user.user_id.id in alumno_ids):
								alumno_ids.append(line_user.user_id.id)
			respuestas = self.env["respuesta"].sudo().search([('user_id','in',alumno_ids), ('create_date','<',fecha_actual)])
			evaluaciones_ids = []
			for line in respuestas:
				evaluaciones_ids.append(line.evaluacion_id.id)
			cursos = self.env['curso.general'].sudo().search([])
			carreras = self.env['estudiante.carrera'].sudo().search([])

			if desde and not hasta:
				evaluaciones_diarias = self.env["evaluacion"].sudo().search([('id', 'in', evaluaciones_ids), ('tipo_evaluacion',  '=',  'diario'),  ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '>',  desde)])
				evaluaciones_semanales = self.env["evaluacion"].sudo().search([('id', 'in', evaluaciones_ids), ('tipo_evaluacion',  '=',  'semanal'),  ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '>',  desde)])
				evaluaciones_simulacros = self.env["evaluacion"].sudo().search([('id', 'in', evaluaciones_ids), ('tipo_evaluacion',  '=',  'simulacro'),  ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '>',  desde)])
			elif not desde and not hasta:
				evaluaciones_diarias = self.env["evaluacion"].sudo().search([('id', 'in', evaluaciones_ids), ('tipo_evaluacion',  '=',  'diario'), ('fecha_fin',  '<',  fecha_actual)])
				evaluaciones_semanales = self.env["evaluacion"].sudo().search([('id', 'in', evaluaciones_ids), ('tipo_evaluacion',  '=',  'semanal'), ('fecha_fin',  '<',  fecha_actual)])
				evaluaciones_simulacros = self.env["evaluacion"].sudo().search([('id', 'in', evaluaciones_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('fecha_fin',  '<',  fecha_actual)])
			elif not desde and  hasta:
				evaluaciones_diarias = self.env["evaluacion"].sudo().search([('id', 'in',evaluaciones_ids), ('tipo_evaluacion',  '=',  'diario'),  ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta)])
				evaluaciones_semanales = self.env["evaluacion"].sudo().search([('id', 'in',evaluaciones_ids), ('tipo_evaluacion',  '=',  'semanal'),  ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta)])
				evaluaciones_simulacros = self.env["evaluacion"].sudo().search([('id', 'in',evaluaciones_ids), ('tipo_evaluacion',  '=',  'simulacro'),  ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta)])
			elif desde and  hasta:
				evaluaciones_diarias = self.env["evaluacion"].sudo().search([('id', 'in', evaluaciones_ids), ('tipo_evaluacion',  '=',  'diario'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta), ('fecha_fin',  '>',  desde)])
				evaluaciones_semanales = self.env["evaluacion"].sudo().search([('id', 'in', evaluaciones_ids), ('tipo_evaluacion',  '=',  'semanal'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta), ('fecha_fin',  '>',  desde)])
				evaluaciones_simulacros = self.env["evaluacion"].sudo().search([('id', 'in', evaluaciones_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta), ('fecha_fin',  '>',  desde)])

			matriz_ponderados = []
			indice_matriz = 1
			cursos_activos = []
			matriz_ponderados.append([])
			matriz_ponderados[0].append("TOTAL DIARIAS")
			matriz_ponderados[0].append("CANTIDAD DIARIAS")
			matriz_ponderados[0].append("TOTAL SEMANAL")
			matriz_ponderados[0].append("CANTIDAD SEMANAL")
			matriz_ponderados[0].append("TOTAL SIMULACRO")
			matriz_ponderados[0].append("CANTIDAD SIMULACRO")
			matriz_ponderados[0].append("id")
			matriz_ponderados[0].append("N°")
			matriz_ponderados[0].append("ALUMNO")
			matriz_ponderados[0].append("AULAS")
			matriz_ponderados[0].append("PD")
			matriz_ponderados[0].append("PS")
			matriz_ponderados[0].append("SIM")
			matriz_ponderados[0].append(10000)
			pesos_modelo_diario = self.env["peso.evaluacion"].sudo().search([('tipo_evaluacion', '=', 'diario')],order = 'peso desc',limit=1)
			if pesos_modelo_diario:
				pesos_modelo_diario_valor = pesos_modelo_diario.peso
			else:
				pesos_modelo_diario_valor = 1
			pesos_modelo_semanal = self.env["peso.evaluacion"].sudo().search([('tipo_evaluacion', '=', 'semanal')],order = 'peso desc',limit=1)
			if pesos_modelo_semanal:
				pesos_modelo_semanal_valor = pesos_modelo_semanal.peso
			else:
				pesos_modelo_semanal_valor = 1
			pesos_modelo_simulacro = self.env["peso.evaluacion"].sudo().search([('tipo_evaluacion', '=', 'simulacro')],order = 'peso desc',limit=1)
			if pesos_modelo_simulacro:
				pesos_modelo_simulacro_valor = pesos_modelo_simulacro.peso
			else:
				pesos_modelo_simulacro_valor = 1
			for ev_diarias in range(len(evaluaciones_diarias)):
				respuesta_eva = self.env["respuesta"].sudo().search([('user_id', 'in',alumno_ids),('evaluacion_id', '=', evaluaciones_diarias[ev_diarias].id)],order = 'puntaje desc')
				for respuesta_alumno in range(len(respuesta_eva)):
					if (respuesta_eva[respuesta_alumno].user_id.id in alumno_ids):
						crear_linea_tabla = True
						indice_linea_tabla = 0
						for buscar_id in range(len(matriz_ponderados)):
							if matriz_ponderados[buscar_id][6] ==respuesta_eva[respuesta_alumno].user_id.id:
								crear_linea_tabla = False
								indice_linea_tabla = buscar_id
						if crear_linea_tabla:
							matriz_ponderados.append([])
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.id)
							matriz_ponderados[indice_matriz].append("N°")
							matriz_ponderados[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.name)
							name_aulas = self.get_name_aulas(respuesta_eva[respuesta_alumno].user_id.aula_eval_ids)
							matriz_ponderados[indice_matriz].append(name_aulas[:40])
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz][0] = round( respuesta_eva[respuesta_alumno].nota_vigesimal + matriz_ponderados[indice_matriz][0] , 2)
							matriz_ponderados[indice_matriz][1] = 1 + matriz_ponderados[indice_matriz][1]
							if matriz_ponderados[indice_matriz][1] == 0:
								matriz_ponderados[indice_matriz][10] = 0
							else:
								matriz_ponderados[indice_matriz][10] = round(matriz_ponderados[indice_matriz][0]/matriz_ponderados[indice_matriz][1] ,2)
								matriz_ponderados[indice_matriz][13] = round((matriz_ponderados[indice_matriz][10]*pesos_modelo_diario_valor + matriz_ponderados[indice_matriz][11]*pesos_modelo_semanal_valor + matriz_ponderados[indice_matriz][12]*pesos_modelo_simulacro_valor )/(pesos_modelo_diario_valor+pesos_modelo_semanal_valor+pesos_modelo_simulacro_valor),2)
							indice_matriz = indice_matriz + 1
						else:
							matriz_ponderados[indice_linea_tabla][0] = round( respuesta_eva[respuesta_alumno].nota_vigesimal + matriz_ponderados[indice_linea_tabla][0],2)
							matriz_ponderados[indice_linea_tabla][1] = 1 + matriz_ponderados[indice_linea_tabla][1]
							if matriz_ponderados[indice_linea_tabla][1] == 0:
								matriz_ponderados[indice_linea_tabla][10] = 0
							else:
								matriz_ponderados[indice_linea_tabla][10] = round(matriz_ponderados[indice_linea_tabla][0]/matriz_ponderados[indice_linea_tabla][1] ,2)
								matriz_ponderados[indice_linea_tabla][13] = round(  (matriz_ponderados[indice_linea_tabla][10]*pesos_modelo_diario_valor + matriz_ponderados[indice_linea_tabla][11]*pesos_modelo_semanal_valor + matriz_ponderados[indice_linea_tabla][12]*pesos_modelo_simulacro_valor)/(pesos_modelo_diario_valor+pesos_modelo_semanal_valor+pesos_modelo_simulacro_valor),2)

			for ev_semanal in range(len(evaluaciones_semanales)):
				respuesta_eva = self.env["respuesta.simulacro"].sudo().search([('user_id', 'in',alumno_ids),('evaluacion_id', '=', evaluaciones_semanales[ev_semanal].id)],order = 'puntaje desc')
				for respuesta_alumno in range(len(respuesta_eva)):
					if (respuesta_eva[respuesta_alumno].user_id.id in alumno_ids):
						crear_linea_tabla = True
						indice_linea_tabla = 0
						for buscar_id in range(len(matriz_ponderados)):
							if matriz_ponderados[buscar_id][6] ==respuesta_eva[respuesta_alumno].user_id.id:
								crear_linea_tabla = False
								indice_linea_tabla = buscar_id
						if crear_linea_tabla:
							matriz_ponderados.append([])
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.id)
							matriz_ponderados[indice_matriz].append("N°")
							matriz_ponderados[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.name)
							name_aulas = self.get_name_aulas(respuesta_eva[respuesta_alumno].user_id.aula_eval_ids)
							matriz_ponderados[indice_matriz].append(name_aulas[:40])
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz][2] = round(respuesta_eva[respuesta_alumno].nota_vigesimal + matriz_ponderados[indice_matriz][2])
							matriz_ponderados[indice_matriz][3] = 1 + matriz_ponderados[indice_matriz][3]
							if matriz_ponderados[indice_matriz][1] == 0:
								matriz_ponderados[indice_matriz][11] = 0
							else:
								matriz_ponderados[indice_matriz][11] = round(matriz_ponderados[indice_matriz][2]/matriz_ponderados[indice_matriz][3] ,2)
								matriz_ponderados[indice_matriz][13] = round((matriz_ponderados[indice_matriz][10]*pesos_modelo_diario_valor + matriz_ponderados[indice_matriz][11]*pesos_modelo_semanal_valor + matriz_ponderados[indice_matriz][12]*pesos_modelo_simulacro_valor )/(pesos_modelo_diario_valor+pesos_modelo_semanal_valor+pesos_modelo_simulacro_valor),2)
							indice_matriz = indice_matriz + 1
						else:
							matriz_ponderados[indice_linea_tabla][2] = round( respuesta_eva[respuesta_alumno].nota_vigesimal + matriz_ponderados[indice_linea_tabla][2],2)
							matriz_ponderados[indice_linea_tabla][3] = 1 + matriz_ponderados[indice_linea_tabla][3]
							if matriz_ponderados[indice_linea_tabla][3] == 0:
								matriz_ponderados[indice_linea_tabla][11] = 0
							else:
								matriz_ponderados[indice_linea_tabla][11] = round(matriz_ponderados[indice_linea_tabla][2]/matriz_ponderados[indice_linea_tabla][3] ,2)
								matriz_ponderados[indice_linea_tabla][13] = round(  (matriz_ponderados[indice_linea_tabla][10]*pesos_modelo_diario_valor + matriz_ponderados[indice_linea_tabla][11]*pesos_modelo_semanal_valor + matriz_ponderados[indice_linea_tabla][12]*pesos_modelo_simulacro_valor)/(pesos_modelo_diario_valor+pesos_modelo_semanal_valor+pesos_modelo_simulacro_valor),2)

			for ev_simulacro in range(len(evaluaciones_simulacros)):
				respuesta_eva = self.env["respuesta.simulacro"].sudo().search([('user_id', 'in',alumno_ids),('evaluacion_id', '=', evaluaciones_simulacros[ev_simulacro].id)],order = 'puntaje desc')
				for respuesta_alumno in range(len(respuesta_eva)):
					if (respuesta_eva[respuesta_alumno].user_id.id in alumno_ids):
						crear_linea_tabla = True
						indice_linea_tabla = 0
						for buscar_id in range(len(matriz_ponderados)):
							if matriz_ponderados[buscar_id][6] ==respuesta_eva[respuesta_alumno].user_id.id:
								crear_linea_tabla = False
								indice_linea_tabla = buscar_id
						if crear_linea_tabla:
							matriz_ponderados.append([])
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.id)
							matriz_ponderados[indice_matriz].append("N°")
							matriz_ponderados[indice_matriz].append(respuesta_eva[respuesta_alumno].user_id.name)
							name_aulas = self.get_name_aulas(respuesta_eva[respuesta_alumno].user_id.aula_eval_ids)
							matriz_ponderados[indice_matriz].append(name_aulas[:40])
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz].append(0)
							matriz_ponderados[indice_matriz][4] = round( respuesta_eva[respuesta_alumno].nota_vigesimal + matriz_ponderados[indice_matriz][4] ,2)
							matriz_ponderados[indice_matriz][5] = 1 + matriz_ponderados[indice_matriz][5]
							if matriz_ponderados[indice_matriz][1] == 0:
								matriz_ponderados[indice_matriz][11] = 0
							else:
								matriz_ponderados[indice_matriz][11] = round(matriz_ponderados[indice_matriz][4]/matriz_ponderados[indice_matriz][5] ,2)
								matriz_ponderados[indice_matriz][13] = round((matriz_ponderados[indice_matriz][10]*pesos_modelo_diario_valor + matriz_ponderados[indice_matriz][11]*pesos_modelo_semanal_valor + matriz_ponderados[indice_matriz][12]*pesos_modelo_simulacro_valor )/(pesos_modelo_diario_valor+pesos_modelo_semanal_valor+pesos_modelo_simulacro_valor),2)
							indice_matriz = indice_matriz + 1
						else:
							matriz_ponderados[indice_linea_tabla][4] = round(respuesta_eva[respuesta_alumno].nota_vigesimal + matriz_ponderados[indice_linea_tabla][4],2)
							matriz_ponderados[indice_linea_tabla][5] = 1 + matriz_ponderados[indice_linea_tabla][5]
							if matriz_ponderados[indice_linea_tabla][5] == 0:
								matriz_ponderados[indice_linea_tabla][12] = 0
							else:
								matriz_ponderados[indice_linea_tabla][12] = round(matriz_ponderados[indice_linea_tabla][4]/matriz_ponderados[indice_linea_tabla][5] ,2)
								matriz_ponderados[indice_linea_tabla][13] = round(  (matriz_ponderados[indice_linea_tabla][10]*pesos_modelo_diario_valor + matriz_ponderados[indice_linea_tabla][11]*pesos_modelo_semanal_valor + matriz_ponderados[indice_linea_tabla][12]*pesos_modelo_simulacro_valor)/(pesos_modelo_diario_valor+pesos_modelo_semanal_valor+pesos_modelo_simulacro_valor),2)

			def get_salary(elem):
				return elem[13]
			matriz_ponderados.sort(key=get_salary, reverse=True)
			for buscar_id in range(len(matriz_ponderados)):
				if  0 < buscar_id:
					matriz_ponderados[buscar_id][7] = buscar_id
					matriz_ponderados[buscar_id][10] = format(matriz_ponderados[buscar_id][10], '.2f')
					matriz_ponderados[buscar_id][11] = format(matriz_ponderados[buscar_id][11], '.2f')
					matriz_ponderados[buscar_id][12] = format(matriz_ponderados[buscar_id][12], '.2f')
					matriz_ponderados[buscar_id][13] = format(matriz_ponderados[buscar_id][13], '.2f')
			matriz_ponderados[0][13] = "PROMEDIO"

			return matriz_ponderados

	def funcion_matriz_notas(self,desde,hasta,aula):
		fecha_actual = datetime.now()
		cursos = self.env['curso.general'].sudo().search([])
		user_id = self.env['res.users'].sudo().search([('id','=',self.env.user.id)],limit=1)
		fecha_ciclo = datetime.now().date()
		if len(user_id.ciclo_eval_ids)>0:
			for ciclo in user_id.ciclo_eval_ids:
				if ciclo.ciclo_id.fecha_inicio < fecha_ciclo:
					fecha_ciclo = ciclo.ciclo_id.fecha_inicio
			fecha_ciclo = datetime(fecha_ciclo.year, fecha_ciclo.month, fecha_ciclo.day)
		grupos_ids = []
		for rec in user_id.grupos_eval_ids:
			grupos_ids.append( rec.grupo_alumnos_id.id )
		for rec in user_id.aula_eval_ids:
			grupos_ids.append( rec.grupo_alumnos_id.id )

		if desde and not hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'diario'), ('state',  '=',  'publico'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '>',  desde)])
		elif not desde and not hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'diario'), ('state',  '=',  'publico'), ('fecha_fin',  '<',  fecha_actual), ('create_date',  '>=',  fecha_ciclo)])
		elif not desde and  hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'diario'), ('state',  '=',  'publico'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta), ('create_date',  '>=',  fecha_ciclo)])
		elif desde and  hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'diario'), ('state',  '=',  'publico'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta), ('fecha_fin',  '>',  desde)])


		respuestas = self.env["respuesta"].sudo().search([('evaluacion_id', 'in', [(rec.id) for rec in evaluaciones]), ('user_id',  '=', self.env.user.id)])


		matriz_diario = []
		matriz_diario_active = [0,"FECHA"]
		matriz_diario_idcursos = ["id cursos",0]
		matriz_diario_notavi = ["nota",0]
		matriz_diario_cantid = ["canti nota",0]
		matriz_diario_namecursos = ["name curso","FECHA"]
		matriz_diario_promedio = ["PROMEDIO","PROMEDIO"]
		for line in cursos:
			matriz_diario_active.append(0)
			matriz_diario_idcursos.append(line.id)
			matriz_diario_notavi.append(0.0)
			matriz_diario_cantid.append(0)
			matriz_diario_namecursos.append(line.name_corto)
			matriz_diario_promedio.append(0.0)
		matriz_diario.append(matriz_diario_active)
		matriz_diario.append(matriz_diario_idcursos)
		matriz_diario.append(matriz_diario_notavi)
		matriz_diario.append(matriz_diario_cantid)
		matriz_diario.append(matriz_diario_namecursos)

		for line in range(len(respuestas)):
			matriz_diario.append([])
			matriz_diario[line + 5].append(respuestas[line].id)
			matriz_diario[line + 5].append((respuestas[line].evaluacion_id.fecha_inicio - timedelta(hours=5)).date())
			for curso_line in cursos:
				matriz_diario[line + 5].append("-")
			for nota_curso in respuestas[line].respuestas_slide_ids:
				if nota_curso.curso_general_id:
					indice = matriz_diario[1].index(nota_curso.curso_general_id.id)
					matriz_diario[0][indice] = 1
					matriz_diario[2][indice] = matriz_diario[2][indice] + nota_curso.nota_vigesimal
					matriz_diario[3][indice] = matriz_diario[3][indice] + 1
					matriz_diario[line + 5][indice] =  nota_curso.nota_vigesimal
		for indice in range(len(cursos)):
			if matriz_diario[3][indice + 2] == 0:
				matriz_diario_promedio[indice + 2] = 0.0
			else:
				matriz_diario_promedio[indice + 2] = round(matriz_diario[2][indice + 2] / matriz_diario[3][indice + 2],2)
		matriz_diario.append(matriz_diario_promedio)

		if desde and not hasta:
			evaluaciones_semanal = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'semanal'), ('state',  '=',  'publico'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '>',  desde)])
		elif not desde and not hasta:
			evaluaciones_semanal = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'semanal'), ('state',  '=',  'publico'), ('fecha_fin',  '<',  fecha_actual), ('create_date',  '>=',  fecha_ciclo)])
		elif not desde and  hasta:
			evaluaciones_semanal = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'semanal'), ('state',  '=',  'publico'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta), ('create_date',  '>=',  fecha_ciclo)])
		elif desde and  hasta:
			evaluaciones_semanal = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'semanal'), ('state',  '=',  'publico'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta), ('fecha_fin',  '>',  desde)])
		respuestas_semanal = self.env["respuesta"].sudo().search([('evaluacion_id', 'in', [(rec.id) for rec in evaluaciones_semanal]), ('user_id',  '=', self.env.user.id)])


		matriz_semanal = []
		matriz_semanal_active = [0,"FECHA"]
		matriz_semanal_idcursos = ["id cursos",0]
		matriz_semanal_notavi = ["nota",0]
		matriz_semanal_cantid = ["canti nota",0]
		matriz_semanal_namecursos = ["name curso","FECHA"]
		matriz_semanal_promedio = ["PROMEDIO","PROMEDIO"]
		for line in cursos:
			matriz_semanal_active.append(0)
			matriz_semanal_idcursos.append(line.id)
			matriz_semanal_notavi.append(0.0)
			matriz_semanal_cantid.append(0)
			matriz_semanal_namecursos.append(line.name_corto)
			matriz_semanal_promedio.append(0.0)

		matriz_semanal.append(matriz_semanal_active)
		matriz_semanal.append(matriz_semanal_idcursos)
		matriz_semanal.append(matriz_semanal_notavi)
		matriz_semanal.append(matriz_semanal_cantid)
		matriz_semanal.append(matriz_semanal_namecursos)
		for line in range(len(evaluaciones_semanal)):
			matriz_semanal.append([])
			matriz_semanal[line + 5].append(evaluaciones_semanal[line].id)
			matriz_semanal[line + 5].append((evaluaciones_semanal[line].fecha_inicio - timedelta(hours=5)).date())
			for curso_line in cursos:
				matriz_semanal[line + 5].append("-")
			for respuesta_usuario in respuestas_semanal:
				if respuesta_usuario.evaluacion_id.id == evaluaciones_semanal[line].id:
					for nota_curso in respuesta_usuario.respuestas_slide_ids:
						if nota_curso.curso_general_id:
							indice = matriz_semanal[1].index(nota_curso.curso_general_id.id)
							matriz_semanal[0][indice] = 1
							matriz_semanal[2][indice] = matriz_semanal[2][indice] + nota_curso.nota_vigesimal
							matriz_semanal[3][indice] = matriz_semanal[3][indice] + 1
							matriz_semanal[line + 5][indice] =  nota_curso.nota_vigesimal

		for indice in range(len(cursos)):
			if matriz_semanal[3][indice + 2] == 0:
				matriz_semanal_promedio[indice + 2] = 0.0
			else:
				matriz_semanal_promedio[indice + 2] = round(matriz_semanal[2][indice + 2] / matriz_semanal[3][indice + 2],2)
		matriz_semanal.append(matriz_semanal_promedio)

		if desde and not hasta:
			evaluaciones_simulacro = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('state',  '=',  'publico'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '>',  desde)])
		elif not desde and not hasta:
			evaluaciones_simulacro = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('state',  '=',  'publico'), ('fecha_fin',  '<',  fecha_actual), ('create_date',  '>=',  fecha_ciclo)])
		elif not desde and  hasta:
			evaluaciones_simulacro = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('state',  '=',  'publico'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta), ('create_date',  '>=',  fecha_ciclo)])
		elif desde and  hasta:
			evaluaciones_simulacro = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('state',  '=',  'publico'), ('fecha_fin',  '<',  fecha_actual), ('fecha_fin',  '<',  hasta), ('fecha_fin',  '>',  desde)])
		respuestas_simulacro = self.env["respuesta"].sudo().search([('evaluacion_id', 'in', [(rec.id) for rec in evaluaciones_simulacro]), ('user_id',  '=', self.env.user.id)])
		respuestas_simulacro_unida = self.env["respuesta.simulacro"].sudo().search([('evaluacion_id', 'in', [(rec.id) for rec in evaluaciones_simulacro]), ('user_id',  '=', self.env.user.id)])


		matriz_simulacro = []
		indice_matriz = 0
		puntaje_total = 0

		labels = []
		fase_1 = []
		fase_2 = []
		fase_3 = []
		fase_4 = []
		total_bar = []
		indice_face = 1
		for line in range(len(evaluaciones_simulacro)):
			indice_face = 1
			matriz_simulacro.append([])
			matriz_simulacro.append([])
			matriz_simulacro.append([])
			matriz_simulacro[indice_matriz].append((evaluaciones_simulacro[line].fecha_inicio - timedelta(hours=5)).date())
			matriz_simulacro[indice_matriz + 1].append((evaluaciones_simulacro[line].fecha_inicio - timedelta(hours=5)).date())
			matriz_simulacro[indice_matriz + 2].append((evaluaciones_simulacro[line].fecha_inicio - timedelta(hours=5)).date())
			labels.append((evaluaciones_simulacro[line].fecha_inicio - timedelta(hours=5)).date())
			for bloque in evaluaciones_simulacro[line].bloques_ids:
				respuesta_simulacro = self.env["respuesta"].sudo().search([('evaluacion_id', 'in', [(rec.id) for rec in evaluaciones_simulacro]), ('user_id',  '=', self.env.user.id), ('examen_id',  '=',bloque.examen_id.id)],limit=1)
				if respuesta_simulacro:
					matriz_simulacro[indice_matriz].append(bloque.name)
					matriz_simulacro[indice_matriz].append("-")
					matriz_simulacro[indice_matriz].append("-")
					matriz_simulacro[indice_matriz].append("-")
					matriz_simulacro[indice_matriz + 1].append("B")
					matriz_simulacro[indice_matriz + 1].append("M")
					matriz_simulacro[indice_matriz + 1].append("BL")
					matriz_simulacro[indice_matriz + 1].append("PUNTAJE")
					matriz_simulacro[indice_matriz + 2].append(respuesta_simulacro.n_correcto)
					matriz_simulacro[indice_matriz + 2].append(respuesta_simulacro.n_incorrecto)
					matriz_simulacro[indice_matriz + 2].append(respuesta_simulacro.n_blanco)
					matriz_simulacro[indice_matriz + 2].append(round(respuesta_simulacro.puntaje,3) )
					puntaje_total = puntaje_total + respuesta_simulacro.puntaje

					if indice_face ==1:
						fase_1.append(round(respuesta_simulacro.puntaje,3) )
					if indice_face ==2:
						fase_2.append(round(respuesta_simulacro.puntaje,3) )
					if indice_face ==3:
						fase_3.append(round(respuesta_simulacro.puntaje,3) )
					if indice_face ==4:
						fase_4.append(round(respuesta_simulacro.puntaje,3) )
					indice_face = indice_face + 1
				else:
					matriz_simulacro[indice_matriz].append(bloque.name)
					matriz_simulacro[indice_matriz].append("-")
					matriz_simulacro[indice_matriz].append("-")
					matriz_simulacro[indice_matriz].append("-")
					matriz_simulacro[indice_matriz + 1].append("B")
					matriz_simulacro[indice_matriz + 1].append("M")
					matriz_simulacro[indice_matriz + 1].append("BL")
					matriz_simulacro[indice_matriz + 1].append("PUNTAJE")
					matriz_simulacro[indice_matriz + 2].append(0)
					matriz_simulacro[indice_matriz + 2].append(0)
					matriz_simulacro[indice_matriz + 2].append(0)
					matriz_simulacro[indice_matriz + 2].append(0)
					puntaje_total = puntaje_total + 0

					if indice_face ==1:
						fase_1.append(0)
					if indice_face ==2:
						fase_2.append(0)
					if indice_face ==3:
						fase_3.append(0)
					if indice_face ==4:
						fase_4.append(0)
					indice_face = indice_face + 1
			if len(evaluaciones_simulacro[line].bloques_ids) == 0:
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
			elif len(evaluaciones_simulacro[line].bloques_ids) == 1:
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
			elif len(evaluaciones_simulacro[line].bloques_ids) == 2:
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
			elif len(evaluaciones_simulacro[line].bloques_ids) == 3:
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")

			if indice_face == 1:
				fase_2.append(0)
				fase_3.append(0)
				fase_4.append(0)
			elif indice_face == 2:
				fase_3.append(0)
				fase_4.append(0)
			elif indice_face == 3:
				fase_4.append(0)


			matriz_simulacro[indice_matriz].append(round(puntaje_total,3))
			total_bar.append(round(puntaje_total,3))
			indice_matriz = indice_matriz + 3
			puntaje_total = 0
		puntaje_total_situ =  sum(item.puntaje for item in respuestas_simulacro_unida)
		cantida_total_situ = len(respuestas_simulacro_unida)

		prom_total_situ = 0 if cantida_total_situ ==0 else round(puntaje_total_situ/cantida_total_situ,3)

		situacion = self.env["situacion.alumno"].sudo().search([('desde', '<', prom_total_situ), ('hasta',  '>',prom_total_situ)],limit=1)


		matriz_general = []
		matriz_general.append(matriz_diario)
		matriz_general.append(matriz_semanal)
		matriz_general.append(matriz_simulacro)
		matriz_general.append(labels)
		matriz_general.append(fase_1)
		matriz_general.append(fase_2)
		matriz_general.append(fase_3)
		matriz_general.append(fase_4)
		matriz_general.append(total_bar)
		matriz_general.append(situacion.name)

		data = {}
		return matriz_general


	def funcion_matriz_notas_admin(self,desde,hasta,aula,alumno):
		fecha_actual = datetime.now()
		cursos = self.env['curso.general'].sudo().search([])
		user_id = self.env['res.users'].sudo().search([('id','=',alumno)],limit=1).id
		usuario = self.env['res.users'].sudo().search([('id','=',alumno)],limit=1)
		fecha_ciclo = datetime.now().date()
		if len(usuario.ciclo_eval_ids)>0:
			for ciclo in usuario.ciclo_eval_ids:
				if ciclo.ciclo_id.fecha_inicio < fecha_ciclo:
					fecha_ciclo = ciclo.ciclo_id.fecha_inicio
			fecha_ciclo = datetime(fecha_ciclo.year, fecha_ciclo.month, fecha_ciclo.day)

		grupos_ids = []
		for rec in usuario.grupos_eval_ids:
			grupos_ids.append( rec.grupo_alumnos_id.id )
		for rec in usuario.aula_eval_ids:
			grupos_ids.append( rec.grupo_alumnos_id.id )

		if desde and not hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'diario'), ('state',  '=',  'publico'), ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '>=',  desde)],order = 'fecha_inicio asc')
		elif not desde and not hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'diario'), ('state',  '=',  'publico'), ('fecha_fin',  '<=',  fecha_actual), ('create_date',  '>=',  fecha_ciclo)],order = 'fecha_inicio asc')
		elif not desde and  hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'diario'), ('state',  '=',  'publico'), ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '<=',  hasta), ('create_date',  '>=',  fecha_ciclo)],order = 'fecha_inicio asc')
		elif desde and  hasta:
			evaluaciones = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'diario'), ('state',  '=',  'publico'), ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '<=',  hasta), ('fecha_fin',  '>=',  desde)],order = 'fecha_inicio asc')


		respuestas = self.env["respuesta"].sudo().search([('evaluacion_id', 'in', [(rec.id) for rec in evaluaciones]), ('user_id',  '=', user_id)])


		matriz_diario = []
		matriz_diario_active = [0,"FECHA"]
		matriz_diario_idcursos = ["id cursos",0]
		matriz_diario_notavi = ["nota",0]
		matriz_diario_cantid = ["canti nota",0]
		matriz_diario_namecursos = ["name curso","FECHA"]
		matriz_diario_promedio = ["PROMEDIO","PROMEDIO"]
		for line in cursos:
			matriz_diario_active.append(0)
			matriz_diario_idcursos.append(line.id)
			matriz_diario_notavi.append(0.0)
			matriz_diario_cantid.append(0)
			matriz_diario_namecursos.append(line.name_corto)
			matriz_diario_promedio.append(0.0)
		matriz_diario.append(matriz_diario_active)
		matriz_diario.append(matriz_diario_idcursos)
		matriz_diario.append(matriz_diario_notavi)
		matriz_diario.append(matriz_diario_cantid)
		matriz_diario.append(matriz_diario_namecursos)

		for line in range(len(respuestas)):
			matriz_diario.append([])
			matriz_diario[line + 5].append(respuestas[line].id)
			matriz_diario[line + 5].append((respuestas[line].evaluacion_id.fecha_inicio - timedelta(hours=5)).date())
			for curso_line in cursos:
				matriz_diario[line + 5].append("-")
			for nota_curso in respuestas[line].respuestas_slide_ids:
				if nota_curso.curso_general_id:
					indice = matriz_diario[1].index(nota_curso.curso_general_id.id)
					matriz_diario[0][indice] = 1
					matriz_diario[2][indice] = matriz_diario[2][indice] + nota_curso.nota_vigesimal
					matriz_diario[3][indice] = matriz_diario[3][indice] + 1
					matriz_diario[line + 5][indice] =  nota_curso.nota_vigesimal
		for indice in range(len(cursos)):
			if matriz_diario[3][indice + 2] == 0:
				matriz_diario_promedio[indice + 2] = 0.0
			else:
				matriz_diario_promedio[indice + 2] = round(matriz_diario[2][indice + 2] / matriz_diario[3][indice + 2],2)
		matriz_diario.append(matriz_diario_promedio)

		if desde and not hasta:
			evaluaciones_semanal = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'semanal'), ('state',  '=',  'publico'), ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '>=',  desde)],order = 'fecha_inicio asc')
		elif not desde and not hasta:
			evaluaciones_semanal = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'semanal'), ('state',  '=',  'publico'), ('fecha_fin',  '<=',  fecha_actual), ('create_date',  '>=',  fecha_ciclo)],order = 'fecha_inicio asc')
		elif not desde and  hasta:
			evaluaciones_semanal = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'semanal'), ('state',  '=',  'publico'), ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '<=',  hasta), ('create_date',  '>=',  fecha_ciclo)],order = 'fecha_inicio asc')
		elif desde and  hasta:
			evaluaciones_semanal = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'semanal'), ('state',  '=',  'publico'), ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '<=',  hasta), ('fecha_fin',  '>=',  desde)],order = 'fecha_inicio asc')
		respuestas_semanal = self.env["respuesta"].sudo().search([('evaluacion_id', 'in', [(rec.id) for rec in evaluaciones_semanal]), ('user_id',  '=', user_id)])


		matriz_semanal = []
		matriz_semanal_active = [0,"FECHA"]
		matriz_semanal_idcursos = ["id cursos",0]
		matriz_semanal_notavi = ["nota",0]
		matriz_semanal_cantid = ["canti nota",0]
		matriz_semanal_namecursos = ["name curso","FECHA"]
		matriz_semanal_promedio = ["PROMEDIO","PROMEDIO"]
		for line in cursos:
			matriz_semanal_active.append(0)
			matriz_semanal_idcursos.append(line.id)
			matriz_semanal_notavi.append(0.0)
			matriz_semanal_cantid.append(0)
			matriz_semanal_namecursos.append(line.name_corto)
			matriz_semanal_promedio.append(0.0)

		matriz_semanal.append(matriz_semanal_active)
		matriz_semanal.append(matriz_semanal_idcursos)
		matriz_semanal.append(matriz_semanal_notavi)
		matriz_semanal.append(matriz_semanal_cantid)
		matriz_semanal.append(matriz_semanal_namecursos)
		for line in range(len(evaluaciones_semanal)):
			matriz_semanal.append([])
			matriz_semanal[line + 5].append(evaluaciones_semanal[line].id)
			matriz_semanal[line + 5].append((evaluaciones_semanal[line].fecha_inicio - timedelta(hours=5)).date())
			for curso_line in cursos:
				matriz_semanal[line + 5].append("-")
			for respuesta_usuario in respuestas_semanal:
				if respuesta_usuario.evaluacion_id.id == evaluaciones_semanal[line].id:
					for nota_curso in respuesta_usuario.respuestas_slide_ids:
						if nota_curso.curso_general_id:
							indice = matriz_semanal[1].index(nota_curso.curso_general_id.id)
							matriz_semanal[0][indice] = 1
							matriz_semanal[2][indice] = matriz_semanal[2][indice] + nota_curso.nota_vigesimal
							matriz_semanal[3][indice] = matriz_semanal[3][indice] + 1
							matriz_semanal[line + 5][indice] =  nota_curso.nota_vigesimal

		for indice in range(len(cursos)):
			if matriz_semanal[3][indice + 2] == 0:
				matriz_semanal_promedio[indice + 2] = 0.0
			else:
				matriz_semanal_promedio[indice + 2] = round(matriz_semanal[2][indice + 2] / matriz_semanal[3][indice + 2],2)
		matriz_semanal.append(matriz_semanal_promedio)

		if desde and not hasta:
			evaluaciones_simulacro = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('state',  '=',  'publico'), ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '>=',  desde)],order = 'fecha_inicio asc')
		elif not desde and not hasta:
			evaluaciones_simulacro = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('state',  '=',  'publico'), ('fecha_fin',  '<=',  fecha_actual), ('create_date',  '>=',  fecha_ciclo)],order = 'fecha_inicio asc')
		elif not desde and  hasta:
			evaluaciones_simulacro = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('state',  '=',  'publico'), ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '<=',  hasta), ('create_date',  '>=',  fecha_ciclo)],order = 'fecha_inicio asc')
		elif desde and  hasta:
			evaluaciones_simulacro = self.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', grupos_ids), ('tipo_evaluacion',  '=',  'simulacro'), ('state',  '=',  'publico'), ('fecha_fin',  '<=',  fecha_actual), ('fecha_fin',  '<=',  hasta), ('fecha_fin',  '>=',  desde)],order = 'fecha_inicio asc')
		respuestas_simulacro = self.env["respuesta"].sudo().search([('evaluacion_id', 'in', [(rec.id) for rec in evaluaciones_simulacro]), ('user_id',  '=',user_id)])
		respuestas_simulacro_unida = self.env["respuesta.simulacro"].sudo().search([('evaluacion_id', 'in', [(rec.id) for rec in evaluaciones_simulacro]), ('user_id',  '=',user_id)])


		matriz_simulacro = []
		indice_matriz = 0
		puntaje_total = 0

		labels = []
		fase_1 = []
		fase_2 = []
		fase_3 = []
		fase_4 = []
		total_bar = []
		indice_face = 1
		for line in range(len(evaluaciones_simulacro)):
			indice_face = 1
			matriz_simulacro.append([])
			matriz_simulacro.append([])
			matriz_simulacro.append([])
			matriz_simulacro[indice_matriz].append((evaluaciones_simulacro[line].fecha_inicio - timedelta(hours=5)).date())
			matriz_simulacro[indice_matriz + 1].append((evaluaciones_simulacro[line].fecha_inicio - timedelta(hours=5)).date())
			matriz_simulacro[indice_matriz + 2].append((evaluaciones_simulacro[line].fecha_inicio - timedelta(hours=5)).date())
			labels.append((evaluaciones_simulacro[line].fecha_inicio - timedelta(hours=5)).date())
			for bloque in evaluaciones_simulacro[line].bloques_ids:
				respuesta_simulacro = self.env["respuesta"].sudo().search([('evaluacion_id', 'in', [(rec.id) for rec in evaluaciones_simulacro]), ('user_id',  '=', user_id), ('examen_id',  '=',bloque.examen_id.id)],limit=1)
				if respuesta_simulacro:
					matriz_simulacro[indice_matriz].append(bloque.name)
					matriz_simulacro[indice_matriz].append("-")
					matriz_simulacro[indice_matriz].append("-")
					matriz_simulacro[indice_matriz].append("-")
					matriz_simulacro[indice_matriz + 1].append("B")
					matriz_simulacro[indice_matriz + 1].append("M")
					matriz_simulacro[indice_matriz + 1].append("BL")
					matriz_simulacro[indice_matriz + 1].append("PUNTAJE")
					matriz_simulacro[indice_matriz + 2].append(respuesta_simulacro.n_correcto)
					matriz_simulacro[indice_matriz + 2].append(respuesta_simulacro.n_incorrecto)
					matriz_simulacro[indice_matriz + 2].append(respuesta_simulacro.n_blanco)
					matriz_simulacro[indice_matriz + 2].append(round(respuesta_simulacro.puntaje,3) )
					puntaje_total = puntaje_total + respuesta_simulacro.puntaje

					if indice_face ==1:
						fase_1.append(round(respuesta_simulacro.puntaje,3) )
					if indice_face ==2:
						fase_2.append(round(respuesta_simulacro.puntaje,3) )
					if indice_face ==3:
						fase_3.append(round(respuesta_simulacro.puntaje,3) )
					if indice_face ==4:
						fase_4.append(round(respuesta_simulacro.puntaje,3) )
					indice_face = indice_face + 1
				else:
					matriz_simulacro[indice_matriz].append(bloque.name)
					matriz_simulacro[indice_matriz].append("-")
					matriz_simulacro[indice_matriz].append("-")
					matriz_simulacro[indice_matriz].append("-")
					matriz_simulacro[indice_matriz + 1].append("B")
					matriz_simulacro[indice_matriz + 1].append("M")
					matriz_simulacro[indice_matriz + 1].append("BL")
					matriz_simulacro[indice_matriz + 1].append("PUNTAJE")
					matriz_simulacro[indice_matriz + 2].append(0)
					matriz_simulacro[indice_matriz + 2].append(0)
					matriz_simulacro[indice_matriz + 2].append(0)
					matriz_simulacro[indice_matriz + 2].append(0)
					puntaje_total = puntaje_total + 0

					if indice_face ==1:
						fase_1.append(0)
					if indice_face ==2:
						fase_2.append(0)
					if indice_face ==3:
						fase_3.append(0)
					if indice_face ==4:
						fase_4.append(0)
					indice_face = indice_face + 1
			if len(evaluaciones_simulacro[line].bloques_ids) == 0:
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
			elif len(evaluaciones_simulacro[line].bloques_ids) == 1:
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
			elif len(evaluaciones_simulacro[line].bloques_ids) == 2:
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
			elif len(evaluaciones_simulacro[line].bloques_ids) == 3:
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 1].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")
				matriz_simulacro[indice_matriz + 2].append("")

			if indice_face == 1:
				fase_2.append(0)
				fase_3.append(0)
				fase_4.append(0)
			elif indice_face == 2:
				fase_3.append(0)
				fase_4.append(0)
			elif indice_face == 3:
				fase_4.append(0)


			matriz_simulacro[indice_matriz].append(round(puntaje_total,3))
			total_bar.append(round(puntaje_total,3))
			indice_matriz = indice_matriz + 3
			puntaje_total = 0
		puntaje_total_situ =  sum(item.puntaje for item in respuestas_simulacro_unida)
		cantida_total_situ = len(respuestas_simulacro_unida)

		prom_total_situ = 0 if cantida_total_situ ==0 else round(puntaje_total_situ/cantida_total_situ,3)

		situacion = self.env["situacion.alumno"].sudo().search([('desde', '<', prom_total_situ), ('hasta',  '>',prom_total_situ)],limit=1)


		matriz_general = []
		matriz_general.append(matriz_diario)
		matriz_general.append(matriz_semanal)
		matriz_general.append(matriz_simulacro)
		matriz_general.append(labels)
		matriz_general.append(fase_1)
		matriz_general.append(fase_2)
		matriz_general.append(fase_3)
		matriz_general.append(fase_4)
		matriz_general.append(total_bar)
		matriz_general.append(situacion.name)
		matriz_general.append(False if len(evaluaciones)==0 else True)
		matriz_general.append(False if len(evaluaciones_semanal)==0 else True)
		matriz_general.append(False if len(evaluaciones_simulacro)==0 else True)

		data = {}
		return matriz_general

	def get_areas_user(self,alumno):
		user_id = self.env['res.users'].sudo().search([('id','=',alumno)],limit=1).id
		grupos = self.env["res.users.line"].sudo().search([('user_id',  '=', user_id)])
		aulas = self.env["grupo.alumnos"].sudo().search([('id', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos])])
		html_output = ''
		for line in aulas:
				html_output += "<option value=\"" + str(line.id) + "\">" + line.name + "</option>\n"
		return html_output
