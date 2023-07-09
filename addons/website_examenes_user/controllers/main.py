from odoo import http
from odoo.http import request
from datetime import datetime, date, time, timedelta
from datetime import datetime,  timedelta
import logging
_logger = logging.getLogger(__name__)


class Main(http.Controller):

	"""
	type:  http | json
	"""
	@http.route("/reuniones", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def evaluaciones(self):
		fecha_actual = datetime.now().date()
		usuario = request.env.user
		grupos = request.env["res.users.line"].sudo().search([('user_id',  '=', request.env.user.id)])
		reuniones = request.env["reuniones"].sudo().search([('grupo_alumnos', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos]), ('fecha',  '>=', fecha_actual)])

		return request.render("website_examenes_user.reuniones", {"reuniones": reuniones,"usuario":usuario})


	@http.route("/schedule_template", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def schedule_template(self):
		usuario = request.env.user
		fecha_hoy = datetime.now().date()
		output = ''
		color = ["#b71c1c", "#004ba0", "#4a148c", "#006978", "#4b830d", "#c43e00", "#616161", "#c60055", "#3f1dcb", "#004d40", "#6a0080", "#c49000", "#5f4339", "#ff8a65", "#F7F408", "#B2F708", "#6AF708", "#0FAD11", "#0FAD68", "#00FFFB", "#06ACF5", "#BECAF4", "#F1DFFA", "#95A5A6", "#D5D8DC", "#2E8B57", "#FF6347", "#FFFF00", "#9ACD32"]
		indice_color = 0
		grupos = request.env["res.users.line"].search([('user_id',  '=', request.env.user.id)])
		horarios = request.env["horario"].search([('grupo_alumnos', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos]),('fecha_inicio', '<=', fecha_hoy),('fecha_fin', '>=', fecha_hoy)])
		lunes_data = []
		martes_data = []
		miercoles_data = []
		jueves_data = []
		viernes_data = []
		sabado_data =[]
		domingo_data = []
		for line in horarios:
			if line.lunes:
				lunes_line = {}
				desde_minuto =format(int((line.lunes_inicio -  int(line.lunes_inicio))*60) )
				hasta_minuto = format(int((line.lunes_fin -  int(line.lunes_fin))*60))
				lunes_line["hora"] = int(line.lunes_inicio if line.lunes_inicio else 0)
				lunes_line["minutos"] = int((line.lunes_inicio -  int(line.lunes_inicio))*60)
				lunes_line["start"] = '{}:{}'.format(int(line.lunes_inicio if line.lunes_inicio else ""),desde_minuto)
				lunes_line["end"] = '{}:{}'.format(int(line.lunes_fin if line.lunes_fin else ""),hasta_minuto)
				lunes_line["name"] = '{}'.format(line.curso_general_id.name if line.curso_general_id else "")
				lunes_line["aula"] = '{}'.format(line.grupo_alumnos.name if line.grupo_alumnos else "")
				lunes_line["curso"] = '{}'.format(line.curso_general_id.name if line.curso_general_id else "")
				lunes_line["docente"] = '{}'.format(line.nombre_profesor if line.profesor_id else "")
				lunes_line["link"] = '{}'.format(line.meet_url)
				lunes_line["id"] = '{}'.format(line.id)
				lunes_line["color"] =  color[indice_color]
				lunes_data.append(lunes_line)
			if line.martes:
				martes_line = {}
				desde_minuto =format(int((line.martes_inicio -  int(line.martes_inicio))*60))
				hasta_minuto =format( int((line.martes_fin -  int(line.martes_fin))*60))
				martes_line["hora"] = int(line.martes_inicio if line.martes_inicio else 0)
				martes_line["minutos"] = int((line.martes_inicio -  int(line.martes_inicio))*60)
				martes_line["start"] = '{}:{}'.format(int(line.martes_inicio if line.martes_inicio else ""),desde_minuto)
				martes_line["end"] = '{}:{}'.format(int(line.martes_fin if line.martes_fin else ""),hasta_minuto)
				martes_line["name"] = '{}'.format(line.curso_general_id.name if line.curso_general_id else "")
				martes_line["aula"] = '{}'.format(line.grupo_alumnos.name if line.grupo_alumnos else "")
				martes_line["curso"] = '{}'.format(line.curso_general_id.name if line.curso_general_id else "")
				martes_line["docente"] = '{}'.format(line.nombre_profesor if line.profesor_id else "")
				martes_line["link"] = '{}'.format(line.meet_url)
				martes_line["id"] = '{}'.format(line.id)
				martes_line["color"] =  color[indice_color]
				martes_data.append(martes_line)
			if line.miercoles:
				miercoles_line = {}
				desde_minuto =format( int((line.miercoles_inicio -  int(line.miercoles_inicio))*60))
				hasta_minuto =format(int((line.miercoles_fin -  int(line.miercoles_fin))*60) )
				miercoles_line["hora"] = int(line.miercoles_inicio if line.miercoles_inicio else 0)
				miercoles_line["minutos"] = int((line.miercoles_inicio -  int(line.miercoles_inicio))*60)
				miercoles_line["start"] = '{}:{}'.format(int(line.miercoles_inicio if line.miercoles_inicio else ""),desde_minuto)
				miercoles_line["end"] = '{}:{}'.format(int(line.miercoles_fin if line.miercoles_fin else ""),hasta_minuto)
				miercoles_line["name"] = '{}'.format(line.curso_general_id.name if line.curso_general_id else "")
				miercoles_line["aula"] = '{}'.format(line.grupo_alumnos.name if line.grupo_alumnos else "")
				miercoles_line["curso"] = '{}'.format(line.curso_general_id.name if line.curso_general_id else "")
				miercoles_line["docente"] = '{}'.format(line.nombre_profesor if line.profesor_id else "")
				miercoles_line["link"] = '{}'.format(line.meet_url)
				miercoles_line["id"] = '{}'.format(line.id)
				miercoles_line["color"] =  color[indice_color]
				miercoles_data.append(miercoles_line)
			if line.jueves:
				jueves_line = {}
				desde_minuto =format(int((line.jueves_inicio -  int(line.jueves_inicio))*60))
				hasta_minuto =format(int((line.jueves_fin -  int(line.jueves_fin))*60))
				jueves_line["hora"] = int(line.jueves_inicio if line.jueves_inicio else 0)
				jueves_line["minutos"] = int((line.jueves_inicio -  int(line.jueves_inicio))*60)
				jueves_line["start"] = '{}:{}'.format(int(line.jueves_inicio if line.jueves_inicio else ""),desde_minuto)
				jueves_line["end"] = '{}:{}'.format(int(line.jueves_fin if line.jueves_fin else ""),hasta_minuto)
				jueves_line["name"] = '{}'.format(line.curso_general_id.name if line.curso_general_id else "")
				jueves_line["aula"] = '{}'.format(line.grupo_alumnos.name if line.grupo_alumnos else "")
				jueves_line["curso"] = '{}'.format(line.curso_general_id.name if line.curso_general_id else "")
				jueves_line["docente"] = '{}'.format(line.nombre_profesor if line.profesor_id else "")
				jueves_line["link"] = '{}'.format(line.meet_url)
				jueves_line["id"] = '{}'.format(line.id)
				jueves_line["id"] = '{}'.format(line.id)
				jueves_line["color"] =  color[indice_color]
				jueves_data.append(jueves_line)
			if line.viernes:
				viernes_line = {}
				desde_minuto = format( int((line.viernes_inicio -  int(line.viernes_inicio))*60))
				hasta_minuto = format( int((line.viernes_fin -  int(line.viernes_fin))*60))
				viernes_line["hora"] = int(line.viernes_inicio if line.viernes_inicio else 0)
				viernes_line["minutos"] = int((line.viernes_inicio -  int(line.viernes_inicio))*60)
				viernes_line["start"] = '{}:{}'.format(int(line.viernes_inicio if line.viernes_inicio else ""),desde_minuto)
				viernes_line["end"] = '{}:{}'.format(int(line.viernes_fin if line.viernes_fin else ""),hasta_minuto)
				viernes_line["name"] = '{}'.format(line.curso_general_id.name if line.curso_general_id else "")
				viernes_line["aula"] = '{}'.format(line.grupo_alumnos.name if line.grupo_alumnos else "")
				viernes_line["curso"] = '{}'.format(line.curso_general_id.name if line.curso_general_id else "")
				viernes_line["docente"] = '{}'.format(line.nombre_profesor if line.profesor_id else "")
				viernes_line["link"] = '{}'.format(line.meet_url)
				viernes_line["id"] = '{}'.format(line.id)
				viernes_line["color"] =  color[indice_color]
				viernes_data.append(viernes_line)
			if line.sabado:
				sabado_line = {}
				desde_minuto = format( int((line.sabado_inicio -  int(line.sabado_inicio))*60))
				hasta_minuto = format( int((line.sabado_fin -  int(line.sabado_fin))*60))
				sabado_line["hora"] = int(line.sabado_inicio if line.sabado_inicio else 0)
				sabado_line["minutos"] = int((line.sabado_inicio -  int(line.sabado_inicio))*60)
				sabado_line["start"] = '{}:{}'.format(int(line.sabado_inicio if line.sabado_inicio else ""),desde_minuto)
				sabado_line["end"] = '{}:{}'.format(int(line.sabado_fin if line.sabado_fin else ""),hasta_minuto)
				sabado_line["name"] = '{}'.format(line.curso_general_id.name if line.curso_general_id else "")
				sabado_line["aula"] = '{}'.format(line.grupo_alumnos.name if line.grupo_alumnos else "")
				sabado_line["curso"] = '{}'.format(line.curso_general_id.name if line.curso_general_id else "")
				sabado_line["docente"] = '{}'.format(line.nombre_profesor if line.profesor_id else "")
				sabado_line["link"] = '{}'.format(line.meet_url)
				sabado_line["id"] = '{}'.format(line.id)
				sabado_line["color"] =  color[indice_color]
				sabado_data.append(sabado_line)
			if line.domingo:
				domingo_line = {}
				desde_minuto =format( int((line.domingo_inicio -  int(line.domingo_inicio))*60))
				hasta_minuto =format( int((line.domingo_fin -  int(line.domingo_fin))*60))
				domingo_line["hora"] = int(line.domingo_inicio if line.domingo_inicio else 0)
				domingo_line["minutos"] = int((line.domingo_inicio -  int(line.domingo_inicio))*60)
				domingo_line["start"] = '{}:{}'.format(int(line.domingo_inicio if line.domingo_inicio else ""),desde_minuto)
				domingo_line["end"] = '{}:{}'.format(int(line.domingo_fin if line.domingo_fin else ""),hasta_minuto)
				domingo_line["name"] = '{}'.format(line.curso_general_id.name if line.curso_general_id else "")
				domingo_line["aula"] = '{}'.format(line.grupo_alumnos.name if line.grupo_alumnos else "")
				domingo_line["curso"] = '{}'.format(line.curso_general_id.name if line.curso_general_id else "")
				domingo_line["docente"] = '{}'.format(line.nombre_profesor if line.profesor_id else "")
				domingo_line["link"] = '{}'.format(line.meet_url)
				domingo_line["id"] = '{}'.format(line.id)
				domingo_line["color"] =  color[indice_color]
				domingo_data.append(domingo_line)
			if indice_color <len(color)-1:
				indice_color = indice_color + 1
			else:
				indice_color = 0

		lunes_data = sorted(lunes_data, key = lambda i: (i['hora'], i['minutos']))
		martes_data = sorted(martes_data, key = lambda i: (i['hora'], i['minutos']))
		miercoles_data = sorted(miercoles_data, key = lambda i: (i['hora'], i['minutos']))
		jueves_data = sorted(jueves_data, key = lambda i: (i['hora'], i['minutos']))
		viernes_data = sorted(viernes_data, key = lambda i: (i['hora'], i['minutos']))
		sabado_data = sorted(sabado_data, key = lambda i: (i['hora'], i['minutos']))
		domingo_data = sorted(domingo_data, key = lambda i: (i['hora'], i['minutos']))
		horario_data = lunes_data + martes_data + miercoles_data + jueves_data + viernes_data + sabado_data + domingo_data


		return request.render("website_examenes_user.template_schedule",{"lunes_data": lunes_data,"martes_data": martes_data,"miercoles_data": miercoles_data,"jueves_data": jueves_data,"viernes_data": viernes_data,"sabado_data": sabado_data,"domingo_data": domingo_data,"usuario":usuario,"horarios":horario_data})

	@http.route("/reunionespro", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def evaluacionespro(self):
		fecha_actual = datetime.now().date()
		grupos = request.env["res.users.line"].sudo().search([('user_id',  '=', request.env.user.id)])
		reuniones = request.env["reuniones"].sudo().search([('grupo_alumnos', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos]), ('fecha',  '>', fecha_actual)])

		return request.render("website_examenes_user.reuniones_programadas", {"reuniones": reuniones})

	@http.route("/horario", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def horario(self):
		fecha_actual = datetime.now().date()
		usuario = request.env.user
		grupos = request.env["res.users.line"].sudo().search([('user_id',  '=', request.env.user.id)])
		lunes = request.env["horario"].sudo().search([('grupo_alumnos', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos]), ('lunes',  '=', True)])
		martes = request.env["horario"].sudo().search([('grupo_alumnos', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos]), ('martes',  '=', True)])

		return request.render("website_examenes_user.template_horario", {"lunes": lunes,"martes":martes,"usuario":usuario})

	@http.route("/aulavirtual", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def aula_virtual(self):
		fecha_actual = datetime.now().date()
		usuario = request.env.user
		grupos = request.env["res.users.line"].sudo().search([('user_id',  '=', request.env.user.id)])
		lunes = request.env["horario"].sudo().search([('grupo_alumnos', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos]), ('lunes',  '=', True)])
		martes = request.env["horario"].sudo().search([('grupo_alumnos', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos]), ('martes',  '=', True)])

		return request.render("website_examenes_user.template_aula_virtual", {"lunes": lunes,"martes":martes,"usuario":usuario})

	@http.route(["/asistencia_json"],type="json",auth="public",method=["GET", "POST"],website=True)
	def asistencia_json(self,horario):
		fecha_actual = datetime.now()
		fecha_actual_date =  (datetime.now()- timedelta(hours=5)).date()
		usuario = request.env.user
		horario_id = request.env["horario"].sudo().search([('id',  '=',horario)])
		area_id = horario_id.grupo_alumnos.id
		curso_general_id = horario_id.curso_general_id.id
		profesor_id = horario_id.profesor_id.id
		hora_actual = (datetime.now()- timedelta(hours=5)).time()
		float_hm =  float( "{}.{}".format((datetime.now()- timedelta(hours=5)).hour,(datetime.now()- timedelta(hours=5)).minute) )
		if horario_id.fecha_inicio < fecha_actual_date and horario_id.fecha_fin >fecha_actual_date :
			if  fecha_actual_date.weekday() == 0 and horario_id.lunes:
				fecha_lunes_ini = datetime(2020,12,12,int(horario_id.lunes_inicio),int((horario_id.lunes_inicio -  int(horario_id.lunes_inicio))*60),0)
				fecha_lunes_fin = datetime(2020,12,12,int(horario_id.lunes_fin),int((horario_id.lunes_fin -  int(horario_id.lunes_fin))*60),0)
				if (fecha_lunes_ini-timedelta(minutes=10)).time() <= hora_actual and hora_actual <= (fecha_lunes_fin.time()):
					horarios_ids = request.env["horario"].sudo().search([('grupo_alumnos','=',area_id),('curso_general_id', '=',curso_general_id),('profesor_id', '=',profesor_id),('lunes', '=',True)])
					for line_horario in horarios_ids:
						sesion_id = request.env["reuniones.sesiones"].search([("horario_id",'=',line_horario.id),("fecha",'=',fecha_actual_date)],limit=1)
						asistencia = request.env["asistencia.estudiante"].search([("user_id",'=',request.env.uid),("horario_id",'=',line_horario.id),("sesion_id",'=',sesion_id.id)],limit=1)
						asistencia.write({"registro_asistencia":'a',"fecha":fecha_actual})
			elif  fecha_actual_date.weekday() == 1 and horario_id.martes :
				fecha_lunes_ini = datetime(2020,12,12,int(horario_id.martes_inicio),int((horario_id.martes_inicio -  int(horario_id.martes_inicio))*60),0)
				fecha_lunes_fin = datetime(2020,12,12,int(horario_id.martes_fin),int((horario_id.martes_fin -  int(horario_id.martes_fin))*60),0)
				if (fecha_lunes_ini-timedelta(minutes=10)).time() <= hora_actual and hora_actual <= (fecha_lunes_fin.time()):
					horarios_ids = request.env["horario"].sudo().search([('grupo_alumnos','=',area_id),('curso_general_id', '=',curso_general_id),('profesor_id', '=',profesor_id),('martes', '=',True)])
					for line_horario in horarios_ids:
						sesion_id = request.env["reuniones.sesiones"].search([("horario_id",'=',line_horario.id),("fecha",'=',fecha_actual_date)],limit=1)
						asistencia = request.env["asistencia.estudiante"].search([("user_id",'=',request.env.uid),("horario_id",'=',line_horario.id),("sesion_id",'=',sesion_id.id)])
						asistencia.write({"registro_asistencia":'a',"fecha":fecha_actual})
			elif  fecha_actual_date.weekday() == 2 and horario_id.miercoles :
				fecha_lunes_ini = datetime(2020,12,12,int(horario_id.miercoles_inicio),int((horario_id.miercoles_inicio -  int(horario_id.miercoles_inicio))*60),0)
				fecha_lunes_fin = datetime(2020,12,12,int(horario_id.miercoles_fin),int((horario_id.miercoles_fin -  int(horario_id.miercoles_fin))*60),0)
				if (fecha_lunes_ini-timedelta(minutes=10)).time() <= hora_actual and hora_actual <= (fecha_lunes_fin.time()):
					horarios_ids = request.env["horario"].sudo().search([('grupo_alumnos','=',area_id),('curso_general_id', '=',curso_general_id),('profesor_id', '=',profesor_id),('miercoles', '=',True)])
					for line_horario in horarios_ids:
						sesion_id = request.env["reuniones.sesiones"].search([("horario_id",'=',line_horario.id),("fecha",'=',fecha_actual_date)],limit=1)
						asistencia = request.env["asistencia.estudiante"].search([("user_id",'=',request.env.uid),("horario_id",'=',line_horario.id),("sesion_id",'=',sesion_id.id)])
						asistencia.write({"registro_asistencia":'a',"fecha":fecha_actual})
			elif  fecha_actual_date.weekday() == 3 and horario_id.jueves:
				fecha_lunes_ini = datetime(2020,12,12,int(horario_id.jueves_inicio),int((horario_id.jueves_inicio -  int(horario_id.jueves_inicio))*60),0)
				fecha_lunes_fin = datetime(2020,12,12,int(horario_id.jueves_fin),int((horario_id.jueves_fin -  int(horario_id.jueves_fin))*60),0)
				if (fecha_lunes_ini-timedelta(minutes=10)).time() <= hora_actual and hora_actual <= (fecha_lunes_fin.time()):
					horarios_ids = request.env["horario"].sudo().search([('grupo_alumnos','=',area_id),('curso_general_id', '=',curso_general_id),('profesor_id', '=',profesor_id),('jueves', '=',True)])
					for line_horario in horarios_ids:
						sesion_id = request.env["reuniones.sesiones"].search([("horario_id",'=',line_horario.id),("fecha",'=',fecha_actual_date)],limit=1)
						asistencia = request.env["asistencia.estudiante"].search([("user_id",'=',request.env.uid),("horario_id",'=',line_horario.id),("sesion_id",'=',sesion_id.id)])
						asistencia.write({"registro_asistencia":'a',"fecha":fecha_actual})
			elif  fecha_actual_date.weekday() == 4 and horario_id.viernes:
				fecha_lunes_ini = datetime(2020,12,12,int(horario_id.viernes_inicio),int((horario_id.viernes_inicio -  int(horario_id.viernes_inicio))*60),0)
				fecha_lunes_fin = datetime(2020,12,12,int(horario_id.viernes_fin),int((horario_id.viernes_fin -  int(horario_id.viernes_fin))*60),0)
				if (fecha_lunes_ini-timedelta(minutes=10)).time() <= hora_actual and hora_actual <= (fecha_lunes_fin.time()):
					horarios_ids = request.env["horario"].sudo().search([('grupo_alumnos','=',area_id),('curso_general_id', '=',curso_general_id),('profesor_id', '=',profesor_id),('viernes', '=',True)])
					for line_horario in horarios_ids:
						sesion_id = request.env["reuniones.sesiones"].search([("horario_id",'=',line_horario.id),("fecha",'=',fecha_actual_date)],limit=1)
						asistencia = request.env["asistencia.estudiante"].search([("user_id",'=',request.env.uid),("horario_id",'=',line_horario.id),("sesion_id",'=',sesion_id.id)])
						asistencia.write({"registro_asistencia":'a',"fecha":fecha_actual})
			elif  fecha_actual_date.weekday() == 5 and horario_id.sabado:
				fecha_lunes_ini = datetime(2020,12,12,int(horario_id.sabado_inicio),int((horario_id.sabado_inicio -  int(horario_id.sabado_inicio))*60),0)
				fecha_lunes_fin = datetime(2020,12,12,int(horario_id.sabado_fin),int((horario_id.sabado_fin -  int(horario_id.sabado_fin))*60),0)
				if (fecha_lunes_ini-timedelta(minutes=10)).time() <= hora_actual and hora_actual <= (fecha_lunes_fin.time()):
					horarios_ids = request.env["horario"].sudo().search([('grupo_alumnos','=',area_id),('curso_general_id', '=',curso_general_id),('profesor_id', '=',profesor_id),('sabado', '=',True)])
					for line_horario in horarios_ids:
						sesion_id = request.env["reuniones.sesiones"].search([("horario_id",'=',line_horario.id),("fecha",'=',fecha_actual_date)],limit=1)
						asistencia = request.env["asistencia.estudiante"].search([("user_id",'=',request.env.uid),("horario_id",'=',line_horario.id),("sesion_id",'=',sesion_id.id)])
						asistencia.write({"registro_asistencia":'a',"fecha":fecha_actual})
			elif  fecha_actual_date.weekday() == 6 and horario_id.domingo:
				fecha_lunes_ini = datetime(2020,12,12,int(horario_id.domingo_inicio),int((horario_id.domingo_inicio -  int(horario_id.domingo_inicio))*60),0)
				fecha_lunes_fin = datetime(2020,12,12,int(horario_id.domingo_fin),int((horario_id.domingo_fin -  int(horario_id.domingo_fin))*60),0)
				if (fecha_lunes_ini-timedelta(minutes=10)).time() <= hora_actual and hora_actual <= (fecha_lunes_fin.time()):
					horarios_ids = request.env["horario"].sudo().search([('grupo_alumnos','=',area_id),('curso_general_id', '=',curso_general_id),('profesor_id', '=',profesor_id),('domingo', '=',True)])
					for line_horario in horarios_ids:
						sesion_id = request.env["reuniones.sesiones"].search([("horario_id",'=',line_horario.id),("fecha",'=',fecha_actual_date)],limit=1)
						asistencia = request.env["asistencia.estudiante"].search([("user_id",'=',request.env.uid),("horario_id",'=',line_horario.id),("sesion_id",'=',sesion_id.id)])
						asistencia.write({"registro_asistencia":'a',"fecha":fecha_actual})
		return True
