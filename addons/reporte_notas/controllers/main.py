from odoo import http
from odoo.http import request
import datetime
from datetime import datetime,  timedelta
import werkzeug
import random
import logging
_logger = logging.getLogger(__name__)


class Main(http.Controller):

	"""
	type:  http | json
	"""
	@http.route("/reporte/alumno", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def reporte_notas_alumnos(self):
		user_id = request.env['res.users'].sudo().search([('id','=',request.env.user.id)],limit=1)
		url = "/reporte/alumno/"+str(user_id.id)
		return werkzeug.utils.redirect(url)

	@http.route("/reporte/alumno/<model('res.users'):user>", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def reporte_notas_alumnos_form(self,user):
		fecha_actual = datetime.now().date()
		cursos = request.env['curso.general'].sudo().search([])
		user_id = request.env['res.users'].sudo().search([('id','=',request.env.user.id)],limit=1)
		grupos = request.env["res.users.line"].sudo().search([('user_id',  '=', request.env.user.id)])
		aulas = request.env["grupo.alumnos"].sudo().search([('id', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos]),('tipo_grupo',  '=', 'aula'),('estado',  '=', 'activo') ])
		fecha_fin = fecha_actual.strftime("%Y-%m-%d")
		fecha_ciclo = datetime.now().date()
		if len(user_id.ciclo_eval_ids)>0:
			for ciclo in user_id.ciclo_eval_ids:
				if ciclo.ciclo_id.fecha_inicio < fecha_ciclo:
					fecha_ciclo = ciclo.ciclo_id.fecha_inicio
			fecha_inicio = datetime(fecha_ciclo.year, fecha_ciclo.month, fecha_ciclo.day)
		else:
			fecha_inicio = (fecha_actual - timedelta(days=30)).strftime("%Y-%m-%d")

		return request.render("reporte_notas.reporte_notas_alumno_form", {"aulas": aulas,"user":user,"fecha_inicio":fecha_inicio,"fecha_fin":fecha_fin})

	@http.route("/reporte/alumno/asistencia", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def reporte_asistencia_alumnos(self):
		user_id = request.env['res.users'].sudo().search([('id','=',request.env.user.id)],limit=1)
		url = "/reporte/alumno/asistencia/"+str(user_id.id)
		return werkzeug.utils.redirect(url)

	@http.route("/reporte/alumno/asistencia/<model('res.users'):user>", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def reporte_asistencia_alumno_form(self,user):
		fecha_actual = datetime.now().date()
		user_id = request.env['res.users'].sudo().search([('id','=',request.env.user.id)],limit=1)
		aulas = request.env["grupo.alumnos"].sudo().search([('id', 'in', [(rec.grupo_alumnos_id.id) for rec in user_id.aula_eval_ids]),('tipo_grupo',  '=', 'aula'),('estado',  '=', 'activo')])
		fecha_inicio = (fecha_actual - timedelta(days=30)).strftime("%Y-%m-%d")
		fecha_fin = fecha_actual.strftime("%Y-%m-%d")

		return request.render("reporte_notas.reporte_asistencia_alumno_form", {"aulas": aulas,"user":user,"fecha_inicio":fecha_inicio,"fecha_fin":fecha_fin})


	@http.route("/reporte/administrador", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def reporte_notas_admin_form(self):
		fecha_actual = datetime.now()
		alumnos = request.env['res.users'].sudo().search([('share', '=', True)])
		aulas = request.env["grupo.alumnos"].sudo().search([('estado', '=', 'activo')])

		return request.render("reporte_notas.reporte_notas_admin_form", {"alumnos":alumnos,"aulas": aulas})

	@http.route("/reporte/administrador/diario", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def reporte_notas_admin_diario(self):
		fecha_actual = datetime.now()
		alumnos = request.env['res.users'].sudo().search([('share', '=', True)])
		aulas = request.env["grupo.alumnos"].sudo().search([('estado', '=', 'activo')])

		return request.render("reporte_notas.reporte_notas_admin_diario", {"alumnos":alumnos,"aulas": aulas})

	@http.route("/reporte/administrador/semanal", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def reporte_notas_admin_semanal(self):
		fecha_actual = datetime.now()
		alumnos = request.env['res.users'].sudo().search([('share', '=', True)])
		aulas = request.env["grupo.alumnos"].sudo().search([('estado', '=', 'activo')])

		return request.render("reporte_notas.reporte_notas_admin_semanal", {"alumnos":alumnos,"aulas": aulas})

	@http.route("/reporte/administrador/simulacro", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def reporte_notas_admin_simulacro(self):
		fecha_actual = datetime.now()
		alumnos = request.env['res.users'].sudo().search([('share', '=', True)])
		aulas = request.env["grupo.alumnos"].sudo().search([('estado', '=', 'activo'),('tipo_grupo', '=', 'aula')])
		grupos = request.env["grupo.alumnos"].sudo().search([('estado', '=', 'activo'),('tipo_grupo', '=', 'grupo')])

		return request.render("reporte_notas.reporte_notas_admin_simulacro", {"alumnos":alumnos,"aulas": aulas,"grupos": grupos})

	@http.route("/reporte/administrador/promedios", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def reporte_notas_admin_promedios_simulacro(self):
		fecha_actual = datetime.now()
		alumnos = request.env['res.users'].sudo().search([('share', '=', True)])
		aulas = request.env["grupo.alumnos"].sudo().search([('estado', '=', 'activo'),('tipo_grupo', '=', 'aula')])
		grupos = request.env["grupo.alumnos"].sudo().search([('estado', '=', 'activo'),('tipo_grupo', '=', 'grupo')])

		return request.render("reporte_notas.reporte_notas_admin_promedios_simulacro", {"alumnos":alumnos,"aulas": aulas,"grupos": grupos})

	@http.route("/reporte/administrador/ponderados", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def reporte_notas_admin_ponderados_simulacro(self):
		fecha_actual = datetime.now()
		alumnos = request.env['res.users'].sudo().search([('share', '=', True)])
		aulas = request.env["grupo.alumnos"].sudo().search([('estado', '=', 'activo'),('tipo_grupo', '=', 'aula')])
		grupos = request.env["grupo.alumnos"].sudo().search([('estado', '=', 'activo'),('tipo_grupo', '=', 'grupo')])

		return request.render("reporte_notas.reporte_notas_admin_ponderados_simulacro", {"alumnos":alumnos,"aulas": aulas,"grupos": grupos})

	@http.route("/reporte/administrador/asistencia", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def reporte_asistencia_por_alumno(self):
		fecha_actual = datetime.now()
		alumnos = request.env['res.users'].sudo().search([('share', '=', True),('active', '=', True)])
		aulas = request.env["grupo.alumnos"].sudo().search([('estado', '=', 'activo'),('tipo_grupo',  '=', 'aula')])

		return request.render("reporte_notas.reporte_asistencia_por_alumno", {"alumnos":alumnos,"aulas": aulas})

	@http.route("/reporte/administrador/asistencia_aula", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def reporte_asistencia_por_aula(self):
		fecha_actual = datetime.now()
		aulas = request.env["grupo.alumnos"].sudo().search([('estado', '=', 'activo'),('tipo_grupo',  '=', 'aula')])

		return request.render("reporte_notas.reporte_asistencia_por_aula", {"aulas": aulas})
