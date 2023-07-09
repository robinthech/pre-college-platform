# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from datetime import datetime, date, time, timedelta

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class Horario(models.Model):
	_name = 'horario'
	_order = "fecha_inicio desc, id desc"

	name = fields.Char(string='Nombre',compute="_compute_name")
	nombre_profesor = fields.Char(string='Nombre',compute="_compute_name", store=True)
	curso_id = fields.Many2one('slide.channel', string='Curso')
	curso_general_id = fields.Many2one('curso.general', string='Curso',store=True)
	profesor_id = fields.Many2one(
		'res.users', string='Profesor', index=True, required=True)
	grupo_alumnos = fields.Many2one(
		'grupo.alumnos', required=True, string="Aula")
	fecha_inicio = fields.Date(string='Fecha Inicio', store=True)
	fecha_fin = fields.Date(string='Fecha Fin', store=True)
	meet_url = fields.Text(string='URL')

	lunes_inicio = fields.Float(string='Lunes Inicio', store=True,default=8)
	lunes_fin = fields.Float(string='Lunes Fin', store=True,default=8)
	martes_inicio = fields.Float(string='MARTES Inicio', store=True,default=8)
	martes_fin = fields.Float(string='MARTES Fin', store=True,default=8)
	miercoles_inicio = fields.Float(string='MIERCOLES Inicio', store=True,default=8)
	miercoles_fin = fields.Float(string='MIERCOLES Fin', store=True,default=8)
	jueves_inicio = fields.Float(string='JUEVES Inicio', store=True,default=8)
	jueves_fin = fields.Float(string='JUEVES Fin', store=True,default=8)
	viernes_inicio = fields.Float(string='VIERNES Inicio', store=True,default=8)
	viernes_fin = fields.Float(string='VIERNES Fin', store=True,default=8)
	sabado_inicio = fields.Float(string='SABADO Inicio', store=True,default=8)
	sabado_fin = fields.Float(string='SABADO Fin', store=True,default=8)
	domingo_inicio = fields.Float(string='DOMINGO Inicio', store=True,default=8)
	domingo_fin = fields.Float(string='DOMINGO Fin', store=True,default=8)

	lunes = fields.Boolean("LUNES", default=False)
	martes = fields.Boolean("MARTES", default=False)
	miercoles = fields.Boolean("MIERCOLES", default=False)
	jueves = fields.Boolean("JUEVES", default=False)
	viernes = fields.Boolean("VIERNES", default=False)
	sabado = fields.Boolean("SABADO", default=False)
	domingo = fields.Boolean("DOMINGO", default=False)

	reuniones_repro_ids = fields.One2many('reuniones', 'horario_id', string='Reuniones')
	sesiones_ids = fields.One2many('reuniones.sesiones', 'horario_id', string='Asistencias')
	asistencia_ids = fields.One2many('asistencia.estudiante', 'horario_id', string='Asistencias')
	reuniones_repro = fields.Integer("Respuestas",compute="_compute_respuesta")

	@api.depends("reuniones_repro_ids")
	def _compute_respuesta(self):
		for record in self:
			record.reuniones_repro = len(record.reuniones_repro_ids)

	@api.depends("curso_general_id","profesor_id")
	def _compute_name(self):
		for record in self:
			if record.curso_general_id:
				record.name = record.curso_general_id.name
			else:
				record.name = 'Reunión'

			if record.profesor_id:
				record.nombre_profesor = record.profesor_id.name

	def action_reuniones_horario(self):
		return {
			"type": "ir.actions.act_window",
			"target": "current",
			"res_model": "reuniones",
			"views": [[False, "search"], [self.env.ref('website_examenes_user.group_reuniones_tree_1').id, "list"], [False, "form"]],
			"domain": [["horario_id", "=", self.id]],
			"context": {'default_horario_id':  self.id,'default_curso_general_id':  self.curso_general_id.id,'default_profesor_id':  self.profesor_id.id,'default_grupo_alumnos':  self.grupo_alumnos.id,'default_meet_url':  self.meet_url},
			"name": u"Reuniones"
		}

	def action_sesiones_horario(self):
		for record in self:
			if len(record.sesiones_ids)==0:
				diferencia = abs((record.fecha_fin-record.fecha_inicio).days)
				dias_adicionales = 1
				for line in range(diferencia):
					fecha_record = record.fecha_inicio + timedelta(days=dias_adicionales)
					if record.lunes and fecha_record.weekday() == 0:
						record.sesiones_ids.create({'name':'LU','fecha':fecha_record, 'horario_id':self.id})
					elif record.martes and fecha_record.weekday() == 1:
						record.sesiones_ids.create({'name':'MA','fecha':fecha_record, 'horario_id':self.id})
					elif record.miercoles and fecha_record.weekday() == 2:
						record.sesiones_ids.create({'name':'MI','fecha':fecha_record, 'horario_id':self.id})
					elif record.jueves and fecha_record.weekday() == 3:
						record.sesiones_ids.create({'name':'JU','fecha':fecha_record, 'horario_id':self.id})
					elif record.viernes and fecha_record.weekday() == 4:
						record.sesiones_ids.create({'name':'VI','fecha':fecha_record, 'horario_id':self.id})
					elif record.sabado and fecha_record.weekday() == 5:
						record.sesiones_ids.create({'name':'SA','fecha':fecha_record, 'horario_id':self.id})
					elif record.domingo and fecha_record.weekday() == 6:
						record.sesiones_ids.create({'name':'DO','fecha':fecha_record, 'horario_id':self.id})
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


			return {
				"type": "ir.actions.act_window",
				"target": "current",
				"res_model": "reuniones.sesiones",
				"views": [[self.env.ref('website_examenes_user.reuniones_sesiones_search').id, "search"], [self.env.ref('website_examenes_user.reuniones_sesiones_tree').id, "list"], [self.env.ref('website_examenes_user.reuniones_sesiones_form').id, "form"]],
				"domain": [["horario_id", "=", self.id]],
				"context": {'default_horario_id':  self.id},
				"name": u"Sesiones"
			}



class HorarioRender(models.TransientModel):
	_name = 'horario.render'

	def render(self):
		fecha_hoy = datetime.now().date()
		output = ''
		color = ["#FCE7E3", "#F1DFA9", "#EFF454", "#C1F454", "#73DEA2", "#72ECD2", "#3AC9E8", "#85B4EA", "#9085EA", "#C285EA", "#EA85A8", "#C5B6BB", "#FD8C87", "#FDBB87", "#F7F408", "#B2F708", "#6AF708", "#0FAD11", "#0FAD68", "#00FFFB", "#06ACF5", "#BECAF4", "#F1DFFA", "#95A5A6", "#D5D8DC", "#2E8B57", "#FF6347", "#FFFF00", "#9ACD32"]
		indice_color = 0
		grupos = self.env["res.users.line"].search([('user_id',  '=', self.env.user.id)])
		horarios_lunes = self.env["horario"].search([('grupo_alumnos', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos]),('fecha_inicio', '<=', fecha_hoy),('fecha_fin', '>=', fecha_hoy)])
		for line in horarios_lunes:
			if line.lunes:
				desde_minuto =  int((line.lunes_inicio -  int(line.lunes_inicio))*60)
				hasta_minuto =  int((line.lunes_fin -  int(line.lunes_fin))*60)
				output = output + '<div class="schedule-item schedule-lunes time-from-{} time-to-{} nt" style="background-color: {};">{}   <button type="button" style="float: right;" class="btn btn-dark derecha" data-toggle="modal" data-target="#trabajador-lunes-{}">  <i class="fa fa-pencil-square-o" style="font-size:20px"></i></button><div class="modal fade" id="trabajador-lunes-{}" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true"><div class="modal-dialog" role="document"><div class="modal-content"><div class="modal-header"><h3 class="modal-title" id="exampleModalLabel" style="color:blue;"><strong>MI CLASE</strong></h3></div><div class="modal-body"> <div><div class="row text-left"><div class="col-6" data-><h6  style="color:blue;">AULA</h6></div><div class="col-6" data-aula_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-6"><h6 style="color:blue;">CURSO</h6></div><div class="col-6" data-curso_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-6"><h6 style="color:blue;">DOCENTE</h6></div><div class="col-6" data-profesor_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-3 text-left"><h6 style="color:blue;">DESDE</h6></div><div class="col-3"><span>{}:{}</span></div><div class="col-3 text-left"><h6 style="color:blue;">HASTA</h6></div><div class="col-3"><span>{}:{}</span></div></div></div></div><div class="modal-footer div-asistencia"><a class="btn btn-primary registrar-asistencia" role="button"  data-horario_id="{}" href="{}" ><span/>INGRESAR</a><button type="button" class="btn btn-secondary" data-dismiss="modal">CERRAR</button></div></div></div></div></div>'.format(int(line.lunes_inicio if line.lunes_inicio else ""), int(line.lunes_fin if line.lunes_fin else ""), color[indice_color],line.curso_general_id.name if line.curso_general_id else "", line.id, line.id,line.grupo_alumnos.id if line.grupo_alumnos else "",line.grupo_alumnos.name if line.grupo_alumnos else "",line.curso_general_id.id if line.curso_general_id else "",line.curso_general_id.name if line.curso_general_id else "",line.profesor_id.id if line.profesor_id else "",line.nombre_profesor,int(line.lunes_inicio if line.lunes_inicio else ""),desde_minuto,int(line.lunes_fin if line.lunes_fin else ""),hasta_minuto,line.id,line.meet_url)
			if line.martes:
				desde_minuto =  int((line.martes_inicio -  int(line.martes_inicio))*60)
				hasta_minuto =  int((line.martes_fin -  int(line.martes_fin))*60)
				output = output + '<div class="schedule-item schedule-martes time-from-{} time-to-{} nt" style="background-color: {};">{}   <button type="button" style="float: right;" class="btn btn-dark derecha" data-toggle="modal" data-target="#trabajador-martes-{}">  <i class="fa fa-pencil-square-o" style="font-size:20px"></i></button><div class="modal fade" id="trabajador-martes-{}" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true"><div class="modal-dialog" role="document"><div class="modal-content"><div class="modal-header"><h3 class="modal-title" id="exampleModalLabel" style="color:blue;"><strong>MI CLASE</strong></h3></div><div class="modal-body"> <div><div class="row text-left"><div class="col-6"><h6 style="color:blue;">AULA</h6></div><div class="col-6" data-aula_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-6"><h6 style="color:blue;">CURSO</h6></div><div class="col-6" data-curso_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-6"><h6 style="color:blue;">DOCENTE</h6></div><div class="col-6" data-profesor_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-3 text-left"><h6 style="color:blue;">DESDE</h6></div><div class="col-3"><span>{}:{}</span></div><div class="col-3 text-left"><h6 style="color:blue;">HASTA</h6></div><div class="col-3"><span>{}:{}</span></div></div></div></div><div class="modal-footer"><a data-horario_id="{}" href="{}" class="btn btn-primary registrar-asistencia"  role="button"><span/>INGRESAR</a><button type="button" class="btn btn-secondary" data-dismiss="modal">CERRAR</button></div></div></div></div></div>'.format(int(line.martes_inicio if line.martes_inicio else ""), int(line.martes_fin if line.martes_fin else ""), color[indice_color],line.curso_general_id.name if line.curso_general_id else "", line.id, line.id,line.grupo_alumnos.id if line.grupo_alumnos else "",line.grupo_alumnos.name if line.grupo_alumnos else "",line.curso_general_id.id if line.curso_general_id else "",line.curso_general_id.name if line.curso_general_id else "",line.profesor_id.id if line.profesor_id else "",line.nombre_profesor,int(line.martes_inicio if line.martes_inicio else ""),desde_minuto,int(line.martes_fin if line.martes_fin else ""),hasta_minuto,line.id,line.meet_url)
			if line.miercoles:
				desde_minuto =  int((line.miercoles_inicio -  int(line.miercoles_inicio))*60)
				hasta_minuto =  int((line.miercoles_fin -  int(line.miercoles_fin))*60)
				output = output + '<div class="schedule-item schedule-miercoles time-from-{} time-to-{} nt" style="background-color: {};">{}   <button type="button" style="float: right;" class="btn btn-dark derecha" data-toggle="modal" data-target="#trabajador-miercoles-{}">  <i class="fa fa-pencil-square-o" style="font-size:20px"></i></button><div class="modal fade" id="trabajador-miercoles-{}" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true"><div class="modal-dialog" role="document"><div class="modal-content"><div class="modal-header"><h3 class="modal-title" id="exampleModalLabel" style="color:blue;"><strong>MI CLASE</strong></h3></div><div class="modal-body"> <div><div class="row text-left"><div class="col-6"><h6 style="color:blue;">AULA</h6></div><div class="col-6" data-aula_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-6"><h6 style="color:blue;">CURSO</h6></div><div class="col-6" data-curso_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-6"><h6 style="color:blue;">DOCENTE</h6></div><div class="col-6" data-profesor_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-3 text-left"><h6 style="color:blue;">DESDE</h6></div><div class="col-3"><span>{}:{}</span></div><div class="col-3 text-left"><h6 style="color:blue;">HASTA</h6></div><div class="col-3"><span>{}:{}</span></div></div></div></div><div class="modal-footer"><a class="btn btn-primary registrar-asistencia" role="button" data-horario_id="{}" href="{}"><span/>INGRESAR</a><button type="button" class="btn btn-secondary" data-dismiss="modal">CERRAR</button></div></div></div></div></div>'.format(int(line.miercoles_inicio if line.miercoles_inicio else ""), int(line.miercoles_fin if line.miercoles_fin else ""), color[indice_color],line.curso_general_id.name if line.curso_general_id else "", line.id, line.id,line.grupo_alumnos.id if line.grupo_alumnos else "",line.grupo_alumnos.name if line.grupo_alumnos else "",line.curso_general_id.id if line.curso_general_id else "",line.curso_general_id.name if line.curso_general_id else "",line.profesor_id.id if line.profesor_id else "",line.nombre_profesor,int(line.miercoles_inicio if line.miercoles_inicio else ""),desde_minuto,int(line.miercoles_fin if line.miercoles_fin else ""),hasta_minuto,line.id,line.meet_url)
			if line.jueves:
				desde_minuto =  int((line.jueves_inicio -  int(line.jueves_inicio))*60)
				hasta_minuto =  int((line.jueves_fin -  int(line.jueves_fin))*60)
				output = output + '<div class="schedule-item schedule-jueves time-from-{} time-to-{} nt" style="background-color: {};">{}   <button type="button" style="float: right;" class="btn btn-dark derecha" data-toggle="modal" data-target="#trabajador-jueves-{}">  <i class="fa fa-pencil-square-o" style="font-size:20px"></i></button><div class="modal fade" id="trabajador-jueves-{}" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true"><div class="modal-dialog" role="document"><div class="modal-content"><div class="modal-header"><h3 class="modal-title" id="exampleModalLabel" style="color:blue;"><strong>MI CLASE</strong></h3></div><div class="modal-body"> <div><div class="row text-left"><div class="col-6"><h6 style="color:blue;">AULA</h6></div><div class="col-6" data-aula_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-6"><h6 style="color:blue;">CURSO</h6></div><div class="col-6" data-curso_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-6"><h6 style="color:blue;">DOCENTE</h6></div><div class="col-6" data-profesor_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-3 text-left"><h6 style="color:blue;">DESDE</h6></div><div class="col-3"><span>{}:{}</span></div><div class="col-3 text-left"><h6 style="color:blue;">HASTA</h6></div><div class="col-3"><span>{}:{}</span></div></div></div></div><div class="modal-footer"><a data-horario_id="{}" href="{}" class="btn btn-primary registrar-asistencia" role="button"><span/>INGRESAR</a><button type="button" class="btn btn-secondary" data-dismiss="modal">CERRAR</button></div></div></div></div></div>'.format(int(line.jueves_inicio if line.jueves_inicio else ""), int(line.jueves_fin if line.jueves_fin else ""), color[indice_color],line.curso_general_id.name if line.curso_general_id else "", line.id, line.id,line.grupo_alumnos.id if line.grupo_alumnos else "",line.grupo_alumnos.name if line.grupo_alumnos else "",line.curso_general_id.id if line.curso_general_id else "",line.curso_general_id.name if line.curso_general_id else "",line.profesor_id.id if line.profesor_id else "",line.nombre_profesor,int(line.jueves_inicio if line.jueves_inicio else ""),desde_minuto,int(line.jueves_fin if line.jueves_fin else ""),hasta_minuto,line.id,line.meet_url)
			if line.viernes:
				desde_minuto =  int((line.viernes_inicio -  int(line.viernes_inicio))*60)
				hasta_minuto =  int((line.viernes_fin -  int(line.viernes_fin))*60)
				output = output + '<div class="schedule-item schedule-viernes time-from-{} time-to-{} nt" style="background-color: {};">{}   <button type="button" style="float: right;" class="btn btn-dark derecha" data-toggle="modal" data-target="#trabajador-viernes-{}">  <i class="fa fa-pencil-square-o" style="font-size:20px"></i></button><div class="modal fade" id="trabajador-viernes-{}" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true"><div class="modal-dialog" role="document"><div class="modal-content"><div class="modal-header"><h3 class="modal-title" id="exampleModalLabel" style="color:blue;"><strong>MI CLASE</strong></h3></div><div class="modal-body"> <div><div class="row text-left"><div class="col-6"><h6 style="color:blue;">AULA</h6></div><div class="col-6" data-aula_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-6"><h6 style="color:blue;">CURSO</h6></div><div class="col-6" data-curso_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-6"><h6 style="color:blue;">DOCENTE</h6></div><div class="col-6" data-profesor_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-3 text-left"><h6 style="color:blue;">DESDE</h6></div><div class="col-3"><span>{}:{}</span></div><div class="col-3 text-left"><h6 style="color:blue;">HASTA</h6></div><div class="col-3"><span>{}:{}</span></div></div></div></div><div class="modal-footer"><a data-horario_id="{}" href="{}" class="btn btn-primary registrar-asistencia" role="button"><span/>INGRESAR</a><button type="button" class="btn btn-secondary" data-dismiss="modal">CERRAR</button></div></div></div></div></div>'.format(int(line.viernes_inicio if line.viernes_inicio else ""), int(line.viernes_fin if line.viernes_fin else ""), color[indice_color],line.curso_general_id.name if line.curso_general_id else "", line.id, line.id,line.grupo_alumnos.id if line.grupo_alumnos else "",line.grupo_alumnos.name if line.grupo_alumnos else "",line.curso_general_id.id if line.curso_general_id else "",line.curso_general_id.name if line.curso_general_id else "",line.profesor_id.id if line.profesor_id else "",line.nombre_profesor,int(line.viernes_inicio if line.viernes_inicio else ""),desde_minuto,int(line.viernes_fin if line.viernes_fin else ""),hasta_minuto,line.id,line.meet_url)
			if line.sabado:
				desde_minuto =  int((line.sabado_inicio -  int(line.sabado_inicio))*60)
				hasta_minuto =  int((line.sabado_fin -  int(line.sabado_fin))*60)
				output = output + '<div class="schedule-item schedule-sabado time-from-{} time-to-{} nt" style="background-color: {};">{}   <button type="button" style="float: right;" class="btn btn-dark derecha" data-toggle="modal" data-target="#trabajador-sabado-{}">  <i class="fa fa-pencil-square-o" style="font-size:20px"></i></button><div class="modal fade" id="trabajador-sabado-{}" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true"><div class="modal-dialog" role="document"><div class="modal-content"><div class="modal-header"><h3 class="modal-title" id="exampleModalLabel" style="color:blue;"><strong>MI CLASE</strong></h3></div><div class="modal-body"> <div><div class="row text-left"><div class="col-6"><h style="color:blue;"6>AULA</h6></div><div class="col-6" data-aula_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-6"><h6 style="color:blue;">CURSO</h6></div><div class="col-6" data-curso_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-6"><h6 style="color:blue;">DOCENTE</h6></div><div class="col-6" data-profesor_id="{}"><span>{}</span></div></div><hr/><div class="row text-left "><div class="col-3 text-left"><h6 style="color:blue;">DESDE</h6></div><div class="col-3"><span>{}:{}</span></div><div class="col-3 text-left"><h6 style="color:blue;">HASTA</h6></div><div class="col-3"><span>{}:{}</span></div></div></div></div><div class="modal-footer"><a data-horario_id="{}" href="{}" class="btn btn-primary registrar-asistencia" role="button"><span/>INGRESAR</a><button type="button" class="btn btn-secondary" data-dismiss="modal">CERRAR</button></div></div></div></div></div>'.format(int(line.sabado_inicio if line.sabado_inicio else ""), int(line.sabado_fin if line.sabado_fin else ""), color[indice_color],line.curso_general_id.name if line.curso_general_id else "", line.id, line.id,line.grupo_alumnos.id if line.grupo_alumnos else "",line.grupo_alumnos.name if line.grupo_alumnos else "",line.curso_general_id.id if line.curso_general_id else "",line.curso_general_id.name if line.curso_general_id else "",line.profesor_id.id if line.profesor_id else "",line.nombre_profesor,int(line.sabado_inicio if line.sabado_inicio else ""),desde_minuto,int(line.sabado_fin if line.sabado_fin else ""),hasta_minuto,line.id,line.meet_url)
			if line.domingo:
				desde_minuto =  int((line.domingo_inicio -  int(line.domingo_inicio))*60)
				hasta_minuto =  int((line.domingo_fin -  int(line.domingo_fin))*60)
				output = output + '<div class="schedule-item schedule-domingo time-from-{} time-to-{} nt" style="background-color: {};">{}   <button type="button" style="float: right;" class="btn btn-dark derecha" data-toggle="modal" data-target="#trabajador-domingo-{}">  <i class="fa fa-pencil-square-o" style="font-size:20px"></i></button><div class="modal fade" id="trabajador-domingo-{}" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true"><div class="modal-dialog" role="document"><div class="modal-content" ><div class="modal-header"><h3 class="modal-title" id="exampleModalLabel" style="color:blue;"><strong>MI CLASE</strong></h3></div><div class="modal-body"> <div><div class="row text-left"><div class="col-6"><h6 style="color:blue;">AULA</h6></div><div class="col-6" data-aula_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-6"><h6 style="color:blue;">CURSO</h6></div><div class="col-6" data-curso_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-6"><h6 style="color:blue;">DOCENTE</h6></div><div class="col-6" data-profesor_id="{}"><span>{}</span></div></div><hr/><div class="row text-left"><div class="col-3 text-left"><h6 style="color:blue;">DESDE</h6></div><div class="col-3"><span>{}:{}</span></div><div class="col-3 text-left"><h6 style="color:blue;">HASTA</h6></div><div class="col-3"><span>{}:{}</span></div></div></div> </div><div class="modal-footer"><a data-horario_id="{}" href="{}" class="btn btn-primary registrar-asistencia" role="button"><span/>INGRESAR</a><button type="button" class="btn btn-secondary" data-dismiss="modal">CERRAR</button></div></div></div></div></div>'.format(int(line.domingo_inicio if line.domingo_inicio else ""), int(line.domingo_fin if line.domingo_fin else ""), color[indice_color],line.curso_general_id.name if line.curso_general_id else "", line.id, line.id,line.grupo_alumnos.id if line.grupo_alumnos else "",line.grupo_alumnos.name if line.grupo_alumnos else "",line.curso_general_id.id if line.curso_general_id else "",line.curso_general_id.name if line.curso_general_id else "",line.profesor_id.id if line.profesor_id else "",line.nombre_profesor,int(line.domingo_inicio if line.domingo_inicio else ""),desde_minuto,int(line.domingo_fin if line.domingo_fin else ""),hasta_minuto,line.id,line.meet_url)
			if indice_color <len(color)-1:
				indice_color = indice_color + 1
			else:
				indice_color = 0
		return output
