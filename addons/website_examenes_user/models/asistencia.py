# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from datetime import datetime, date, time, timedelta

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class AsistenciaEstudiante(models.Model):
	_name = 'asistencia.estudiante'
	_order = "id desc"

	name = fields.Char(string='Nombre',compute="_compute_name")
	curso_general_id = fields.Many2one('curso.general',  related="horario_id.curso_general_id",string='Curso',store=True)
	grupo_alumnos = fields.Many2one('grupo.alumnos', related="horario_id.grupo_alumnos", string="Aula",store=True)
	profesor_id = fields.Many2one('res.users',related="horario_id.profesor_id", string='Profesor', index=True, )
	fecha = fields.Datetime(string='Fecha', index=True,store=True)
	fecha_date = fields.Char(string='Fecha',compute="_compute_name", index=True,store=True)
	tipo_sesion = fields.Selection([
		('normal', 'No Feriado'),
		('feriado', 'Feriado')],
		string='Normal/Feriado',default="normal",
		help="Normal/Feriado", related="sesion_id.tipo_sesion",store=True)
	registro_asistencia = fields.Selection([
		('a', 'Asistencia'),
		('j', 'Justificado'),('f', 'Falta')],
		string='Registro de Asistencia',
		default='a',
		help="Registro de Asistencia")
	horario_id = fields.Many2one('horario', string='HORARIO', index=True, required=True)
	sesion_id = fields.Many2one('reuniones.sesiones', string='Sesiones', index=True, required=True)
	user_id = fields.Many2one('res.users', string='Alumno', index=True, required=True)

	@api.depends("curso_general_id","fecha")
	def _compute_name(self):
		for record in self:
			if record.curso_general_id:
				record.name = record.curso_general_id.name
			if record.fecha:
				record.fecha_date =(record.fecha - timedelta(hours=5)).strftime("%Y-%m-%d")



class ReunionesSesiones(models.Model):
	_name = 'reuniones.sesiones'
	_order = "fecha desc, id desc"

	name = fields.Char(string='Nombre',default="SESION")
	fecha = fields.Date(string='Fecha', index=True,store=True)
	fecha_disponible = fields.Date(string='Fecha',related="horario_id.fecha_inicio", index=True,store=True)
	horario_id = fields.Many2one('horario', string='HORARIO', index=True, required=True)
	asistencia_ids = fields.One2many('asistencia.estudiante', 'sesion_id', string='Asistencias')
	estado = fields.Selection([
		('menor', 'Menor'),
		('mayor', 'Mayor')],
		string='Estado',compute="_compute_name",
		help="Registro de Asistencia")
	tipo_sesion = fields.Selection([
		('normal', 'No Feriado'),
		('feriado', 'Feriado')],
		string='Normal/Feriado',default="normal",
		help="Normal/Feriado")
	active = fields.Boolean("active",default=True)

	def marcar_como_feriado(self):
		for record in self:
			record.tipo_sesion = 'feriado'

	def marcar_como_normal(self):
		for record in self:
			record.tipo_sesion = 'normal'

	@api.depends("fecha_disponible","fecha")
	def _compute_name(self):
		for record in self:
			if record.fecha and record.fecha_disponible:
				if record.fecha > record.fecha_disponible:
					record.estado = 'mayor'
				else:
					record.estado = 'menor'

	def cron_crear_usuario_sesion(self):
		# cron para crear asistencia
		# archivar contactos y estudiantes pertenecientes al ciclo
		fecha_actual = datetime.now()
		fecha_actual_date = datetime.now().date()
		horarios = self.env['horario'].sudo().search([])
		for horario in horarios:
			if horario.fecha_inicio <= fecha_actual_date and fecha_actual_date<= horario.fecha_fin:
				for record in horario:
					if len(record.sesiones_ids)==0:
						diferencia = abs((record.fecha_fin-record.fecha_inicio).days)
						dias_adicionales = 1
						for line in range(diferencia):
							fecha_record = record.fecha_inicio + timedelta(days=dias_adicionales)
							if record.lunes and fecha_record.weekday() == 0:
								record.sesiones_ids.create({'name':'LU','fecha':fecha_record, 'horario_id':record.id})
							elif record.martes and fecha_record.weekday() == 1:
								record.sesiones_ids.create({'name':'MA','fecha':fecha_record, 'horario_id':record.id})
							elif record.miercoles and fecha_record.weekday() == 2:
								record.sesiones_ids.create({'name':'MI','fecha':fecha_record, 'horario_id':record.id})
							elif record.jueves and fecha_record.weekday() == 3:
								record.sesiones_ids.create({'name':'JU','fecha':fecha_record, 'horario_id':record.id})
							elif record.viernes and fecha_record.weekday() == 4:
								record.sesiones_ids.create({'name':'VI','fecha':fecha_record, 'horario_id':record.id})
							elif record.sabado and fecha_record.weekday() == 5:
								record.sesiones_ids.create({'name':'SA','fecha':fecha_record, 'horario_id':record.id})
							elif record.domingo and fecha_record.weekday() == 6:
								record.sesiones_ids.create({'name':'DO','fecha':fecha_record, 'horario_id':record.id})
							dias_adicionales += 1
					else:
						diferencia = abs((record.fecha_fin-record.fecha_inicio).days)
						fechas = []
						dias_adicionales = 1
						for line in range(diferencia):
							fecha_record = record.fecha_inicio + timedelta(days=dias_adicionales)
							if record.lunes and fecha_record.weekday() == 0:
								fechas.append(fecha_record)
							elif record.martes and fecha_record.weekday() == 1:
								fechas.append(fecha_record)
							elif record.miercoles and fecha_record.weekday() == 2:
								fechas.append(fecha_record)
							elif record.jueves and fecha_record.weekday() == 3:
								fechas.append(fecha_record)
							elif record.viernes and fecha_record.weekday() == 4:
								fechas.append(fecha_record)
							elif record.sabado and fecha_record.weekday() == 5:
								fechas.append(fecha_record)
							elif record.domingo and fecha_record.weekday() == 6:
								fechas.append(fecha_record)
							dias_adicionales += 1
						for sesion in record.sesiones_ids:
							if  sesion.fecha not in fechas:
								sesion.active = False
							elif sesion.fecha in fechas:
								sesion.active = True

		fecha_actual = datetime.now()
		fecha_actual_date = datetime.now().date()
		sesiones = self.env['reuniones.sesiones'].sudo().search([("fecha",'=',fecha_actual_date)])

		for sesion in sesiones:
			year = sesion.fecha.year
			month = sesion.fecha.month
			day = sesion.fecha.day
			if sesion.fecha.weekday() == 0:
				hour=  datetime(2020,12,12,int( sesion.horario_id.lunes_inicio),int(( sesion.horario_id.lunes_inicio -  int( sesion.horario_id.lunes_inicio))*60),0).hour
				minute =  datetime(2020,12,12,int( sesion.horario_id.lunes_inicio),int(( sesion.horario_id.lunes_inicio -  int( sesion.horario_id.lunes_inicio))*60),0).minute
			elif sesion.fecha.weekday() == 1:
				hour =  datetime(2020,12,12,int( sesion.horario_id.martes_inicio),int(( sesion.horario_id.martes_inicio -  int( sesion.horario_id.martes_inicio))*60),0).hour
				minute =  datetime(2020,12,12,int( sesion.horario_id.martes_inicio),int(( sesion.horario_id.martes_inicio -  int (sesion.horario_id.martes_inicio))*60),0).minute
			elif sesion.fecha.weekday() == 2:
				hour = datetime(2020,12,12,int( sesion.horario_id.miercoles_inicio),int(( sesion.horario_id.miercoles_inicio -  int( sesion.horario_id.miercoles_inicio))*60),0).hour
				minute = datetime(2020,12,12,int( sesion.horario_id.miercoles_inicio),int(( sesion.horario_id.miercoles_inicio -  int( sesion.horario_id.miercoles_inicio))*60),0).minute
			elif sesion.fecha.weekday() == 3:
				hour= datetime(2020,12,12,int( sesion.horario_id.jueves_inicio),int(( sesion.horario_id.jueves_inicio -  int( sesion.horario_id.jueves_inicio))*60),0).hour
				minute =  datetime(2020,12,12,int( sesion.horario_id.jueves_inicio),int(( sesion.horario_id.jueves_inicio -  int( sesion.horario_id.jueves_inicio))*60),0).minute
			elif sesion.fecha.weekday() == 4:
				hour = datetime(2020,12,12,int( sesion.horario_id.viernes_inicio),int(( sesion.horario_id.viernes_inicio -  int( sesion.horario_id.viernes_inicio))*60),0).hour
				minute =datetime(2020,12,12,int( sesion.horario_id.viernes_inicio),int(( sesion.horario_id.viernes_inicio -  int( sesion.horario_id.viernes_inicio))*60),0).minute
			elif sesion.fecha.weekday() == 5:
				hour =  datetime(2020,12,12,int( sesion.horario_id.sabado_inicio),int(( sesion.horario_id.sabado_inicio -  int( sesion.horario_id.sabado_inicio))*60),0).hour
				minute =  datetime(2020,12,12,int( sesion.horario_id.sabado_inicio),int(( sesion.horario_id.sabado_inicio -  int( sesion.horario_id.sabado_inicio))*60),0).minute
			elif sesion.fecha.weekday() == 6:
				hour = datetime(2020,12,12,int( sesion.horario_id.domingo_inicio),int(( sesion.horario_id.domingo_inicio -  int( sesion.horario_id.domingo_inicio))*60),0).hour
				minute = datetime(2020,12,12,int( sesion.horario_id.domingo_inicio),int(( sesion.horario_id.domingo_inicio -  int( sesion.horario_id.domingo_inicio))*60),0).minute
			fecha_sesion_hora_curso = datetime(year,month,day,hour,minute)+ timedelta(hours=5)
			id_usuarios = []
			for line_sesion in sesion.asistencia_ids:
				id_usuarios.append(line_sesion.user_id.id)
			for usuario in sesion.horario_id.grupo_alumnos.users_ids:
				if usuario.user_id.id not in id_usuarios:
					sesion.asistencia_ids.create({"user_id":usuario.user_id.id,"sesion_id":sesion.id,"horario_id":sesion.horario_id.id,"registro_asistencia":'f',"fecha":fecha_sesion_hora_curso})
