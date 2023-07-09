from odoo import http
from odoo.http import request
import datetime
from datetime import datetime,  timedelta


class Main(http.Controller):

	"""
	type:  http | json
	"""
	@http.route("/evaluaciones", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def evaluaciones(self):
		fecha_actual = datetime.now()
		grupos = request.env["res.users.line"].sudo().search([('user_id',  '=', request.env.user.id)])
		evaluaciones = request.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos]), ('state',  '=',  'publico'), ('fecha_inicio',  '<',  fecha_actual), ('fecha_fin',  '>',  fecha_actual)])
		eval_ids = []
		for evaluacion in evaluaciones:
			if evaluacion.tipo_evaluacion == 'diario':
				respuesta = request.env["respuesta"].search([["user_id", "=", request.env.uid], ["evaluacion_id", "=", evaluacion.id], ["estado", "=", 'entregado']],limit=1)
				if len(respuesta) == 0:
					eval_ids.append(1)
				else:
					eval_ids.append(0)
				adjuntos = evaluacion.examen_id.exam_file_ids
				for line in adjuntos:
					line.public = True
				solucionarios = evaluacion.examen_id.solve_file_ids
				for line in solucionarios:
					line.public = True
			elif evaluacion.tipo_evaluacion != 'diario':
				eval_ids.append(1)
				for bloque in evaluacion.bloques_ids:
					adjuntos = bloque.examen_id.exam_file_ids
					for line in adjuntos:
						line.public = True
					solucionarios = bloque.examen_id.solve_file_ids
					for line in solucionarios:
						line.public = True
		return request.render("website_examenes.evaluaciones", {"evaluaciones": evaluaciones,"eval_ids":eval_ids})

	@http.route(['/evaluaciones/content/<int:evaluacion>/<int:examen>'], type='http', auth="public")
	def evaluaciones_content_common(self, xmlid=None, model='ir.attachment', id=None, field='datas',
					   filename=None, filename_field='name', unique=None, mimetype=None,
					   download=None, data=None, token=None, access_token=None,evaluacion=None,examen=None, **kw):
		evaluacion = request.env["evaluacion"].sudo().search([('id',  '=',evaluacion)],limit=1)
		fecha_actual = datetime.now()
		if evaluacion.fecha_fin <= fecha_actual:
			if evaluacion.tipo_evaluacion == 'diario':
				solucionarios = evaluacion.examen_id.solve_file_ids
				for solve in solucionarios:
					solve.public = True
			elif evaluacion.tipo_evaluacion != 'diario':
				for bloque in evaluacion.bloques_ids:
					solucionarios = bloque.examen_id.solve_file_ids
					for solve in solucionarios:
						solve.public = True
		else:
			return "<h1>NO DISPONIBLE</h1>"

			status, headers, content = request.env['ir.http'].binary_content(
				xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
				filename_field=filename_field, download=download, mimetype=mimetype, access_token=access_token)

			if status != 200:
				return request.env['ir.http']._response_by_status(status, headers, content)
			else:
				content_base64 = base64.b64decode(content)
				headers.append(('Content-Length', len(content_base64)))
				response = request.make_response(content_base64, headers)
			if token:
				response.set_cookie('fileToken', token)
			return response

	@http.route("/evaluacionespro", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def evaluacionespro(self):
		fecha_actual = datetime.now()
		grupos = request.env["res.users.line"].sudo().search([('user_id', '=', request.env.user.id)])
		evaluaciones = request.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos]), ('state',  '=',  'publico'), ('fecha_inicio',  '>',  fecha_actual)])
		for evaluacion in evaluaciones:
			if evaluacion.tipo_evaluacion == 'diario':
				adjuntos = evaluacion.examen_id.exam_file_ids
				for line in adjuntos:
					line.public = True
				solucionarios = evaluacion.examen_id.solve_file_ids
				for line in solucionarios:
					line.public = True
			elif evaluacion.tipo_evaluacion != 'diario':
				for bloque in evaluacion.bloques_ids:
					adjuntos = bloque.examen_id.exam_file_ids
					for line in adjuntos:
						line.public = True
					solucionarios = bloque.examen_id.solve_file_ids
					for line in solucionarios:
						line.public = True
		return request.render("website_examenes.evaluaciones_programadas", {"evaluaciones": evaluaciones})

	@http.route("/evaluacionescer", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def evaluacionescer(self):
		fecha_actual = datetime.now()
		grupos = request.env["res.users.line"].sudo().search([('user_id',  '=',  request.env.user.id)])
		usuarios = request.env["res.users"].sudo().search([('id', '=', request.env.user.id)],limit=1)
		fecha_ciclo = datetime.now().date()
		if len(usuarios.ciclo_eval_ids)>0:
			for ciclo in usuarios.ciclo_eval_ids:
				if ciclo.ciclo_id.fecha_inicio < fecha_ciclo:
					fecha_ciclo = ciclo.ciclo_id.fecha_inicio
			fecha_ciclo = fecha_ciclo - timedelta(days=7)
			fecha_ciclo = datetime(fecha_ciclo.year, fecha_ciclo.month, fecha_ciclo.day)
			evaluaciones = request.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos]), ('state',  '=',  'publico'), ('fecha_inicio',  '<',  fecha_actual), ('create_date',  '>',  fecha_ciclo)])
		else:
			evaluaciones = request.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos]), ('state',  '=',  'publico'), ('fecha_inicio',  '<',  fecha_actual)])
		for evaluacion in evaluaciones:
			if evaluacion.tipo_evaluacion == 'diario':
				adjuntos = evaluacion.examen_id.exam_file_ids
				for line in adjuntos:
					line.public = True
				solucionarios = evaluacion.examen_id.solve_file_ids
				for line in solucionarios:
					line.public = True
			elif evaluacion.tipo_evaluacion != 'diario':
				for bloque in evaluacion.bloques_ids:
					adjuntos = bloque.examen_id.exam_file_ids
					for line in adjuntos:
						line.public = True
					solucionarios = bloque.examen_id.solve_file_ids
					for line in solucionarios:
						line.public = True
		return request.render("website_examenes.evaluaciones_cerradas", {"evaluaciones": evaluaciones})


	@http.route("/evaluaciones/examen/<model('evaluacion'):evaluacion>", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def examenes_1(self, evaluacion):
		# examen = request.env["examen"].browse(i1nt(id))
		ahora = datetime.now()
		user = request.env.user.id
		integrante = False
		for line in evaluacion.grupo_alumnos.users_ids:
			if user == line.user_id.id:
				integrante =  True
		if integrante:
			if evaluacion.state == 'publico':
				if(evaluacion.fecha_inicio <= ahora and evaluacion.fecha_fin >= ahora):
					examen = evaluacion.examen_id
					respuesta = request.env["respuesta"].search([["user_id", "=", request.env.uid], ["examen_id", "=", examen.id], ["evaluacion_id", "=", evaluacion.id]],limit=1)

					if len(respuesta) == 0:
						contador_preguntas = 0
						for exam_claves in examen.claves_ids:
							if not exam_claves.is_curso:
								contador_preguntas = contador_preguntas + 1
						request.env["respuesta"].sudo().create({"user_id": request.env.uid, "examen_id": examen.id, "evaluacion_id": evaluacion.id,"name":"Diario","fecha_termino":ahora,"nota_vigesimal":0.0,"puntaje":0.0,"n_blanco":contador_preguntas})
						respuesta = request.env["respuesta"].search([["user_id", "=", request.env.uid], ["examen_id", "=", examen.id], ["evaluacion_id", "=", evaluacion.id]],limit=1)
						lineas_respuestas = examen.claves_ids
						for line  in lineas_respuestas:
							request.env["respuesta.line"].sudo().create({"respuesta_id": respuesta.id, "is_curso": line.is_curso, "curso_general_id": line.curso_general_id.id, "sequence": line.sequence})
							if line.is_curso:
								request.env["respuesta.slide"].sudo().create({"respuesta_id": respuesta.id, "curso_general_id": line.curso_general_id.id})

					if respuesta.estado == "entregado" and (ahora - respuesta.create_date) < timedelta(minutes=evaluacion.duracion):
						return request.render("website_examenes.template_entregado")
					if respuesta.estado == "entregado" and (ahora - respuesta.create_date) > timedelta(minutes=evaluacion.duracion):
						return request.render("website_examenes.template_entregado")
					if respuesta.estado == "incompleto" and (ahora - respuesta.create_date) < timedelta(minutes=evaluacion.duracion):
						return request.render("website_examenes.examenes_layout", {"examen": examen, "respuesta": respuesta, "evaluacion": evaluacion})
					if respuesta.estado == "incompleto" and (ahora - respuesta.create_date) > timedelta(minutes=evaluacion.duracion):
						return request.render("website_examenes.template_tiempo_acabado")
				elif evaluacion.fecha_fin <= ahora:
					return request.render("website_examenes.template_examen_finalizado")
				elif evaluacion.fecha_inicio >= ahora:
					return request.render("website_examenes.template_examen_inicio")
			else:
				return request.render("website_examenes.template_examen_no_disponible")
		else:
			return request.render("website_examenes.template_no_inscrito")

	@http.route("/evaluaciones/list/<model('evaluacion'):evaluacion>", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def evaluaciones_list(self, evaluacion):
		user = request.env.user.id
		integrante = False
		ahora = datetime.now()

		for line in evaluacion.grupo_alumnos.users_ids:
			if user == line.user_id.id:
				integrante =  True
		if integrante:
			if evaluacion.state == 'publico':
				if(evaluacion.fecha_inicio <= ahora and evaluacion.fecha_fin >= ahora):
					return request.render("website_examenes.evaluacion_list_bloques", {"evaluacion": evaluacion})
				elif evaluacion.fecha_fin <= ahora:
					return request.render("website_examenes.template_examen_finalizado")
				elif evaluacion.fecha_inicio >= ahora:
					return request.render("website_examenes.template_examen_inicio")
			else:
				return request.render("website_examenes.template_examen_no_disponible")
		else:
			return request.render("website_examenes.template_no_inscrito")

	@http.route("/evaluaciones/list/examenes/<model('evaluacion.line'):bloque>", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def evaluaciones_list_examenes(self, bloque):
			ahora = datetime.now()
			evaluacion = bloque.evaluacion_id
			user = request.env.user.id

			respuesta_simulacro = request.env["respuesta.simulacro"].search([["user_id", "=", request.env.uid], ["evaluacion_id", "=", bloque.evaluacion_id.id]],limit=1)
			if len(respuesta_simulacro)==0:
				if bloque.evaluacion_id.tipo_evaluacion != 'diario':
					contador_preguntas = 0
					for bloque_line in evaluacion.bloques_ids:
						for exam_claves in bloque_line.examen_id.claves_ids:
							if not exam_claves.is_curso:
								contador_preguntas = contador_preguntas + 1
					request.env["respuesta.simulacro"].sudo().create({"user_id": request.env.uid, "evaluacion_id": bloque.evaluacion_id.id,"nota_vigesimal":0.0,"puntaje":0.0,"n_blanco":contador_preguntas})
			integrante = False
			for line in evaluacion.grupo_alumnos.users_ids:
				if user == line.user_id.id:
					integrante =  True
			if integrante:
				if bloque.evaluacion_id.state == 'publico':
					if(bloque.evaluacion_id.fecha_inicio <= ahora and bloque.evaluacion_id.fecha_fin >= ahora):
						examen = bloque.examen_id
						respuesta = request.env["respuesta"].search([["user_id", "=", request.env.uid], ["examen_id", "=", examen.id], ["evaluacion_id", "=", bloque.evaluacion_id.id]],limit=1)

						if len(respuesta) == 0:
							contador_preguntas = 0
							for exam_claves in examen.claves_ids:
								if not exam_claves.is_curso:
									contador_preguntas = contador_preguntas + 1
							request.env["respuesta"].sudo().create({"user_id": request.env.uid, "examen_id": examen.id, "evaluacion_id": bloque.evaluacion_id.id,"name":bloque.name,"fecha_termino":ahora,"nota_vigesimal":0.0,"puntaje":0.0,"n_blanco":contador_preguntas})
							respuesta = request.env["respuesta"].search([["user_id", "=", request.env.uid], ["examen_id", "=", examen.id], ["evaluacion_id", "=", bloque.evaluacion_id.id]],limit=1)
							lineas_respuestas = examen.claves_ids
							for line  in lineas_respuestas:
								request.env["respuesta.line"].sudo().create({"respuesta_id": respuesta.id, "is_curso": line.is_curso,  "curso_general_id": line.curso_general_id.id, "sequence": line.sequence})
								if line.is_curso:
									request.env["respuesta.slide"].sudo().create({"respuesta_id": respuesta.id, "curso_general_id": line.curso_general_id.id})

						if respuesta.estado == "entregado" and (ahora - respuesta.create_date) < timedelta(minutes=bloque.duracion):
							return request.render("website_examenes.template_entregado")
						if respuesta.estado == "entregado" and (ahora - respuesta.create_date) > timedelta(minutes=bloque.duracion):
							return request.render("website_examenes.template_entregado")
						if respuesta.estado == "incompleto" and (ahora - respuesta.create_date) < timedelta(minutes=bloque.duracion):
							return request.render("website_examenes.examenes_simulacro_layout", {"examen": examen, "respuesta": respuesta, "evaluacion": evaluacion, "bloque": bloque})
						if respuesta.estado == "incompleto" and (ahora - respuesta.create_date) > timedelta(minutes=bloque.duracion):
							return request.render("website_examenes.template_tiempo_acabado")
					elif bloque.evaluacion_id.fecha_fin <= ahora:
						return request.render("website_examenes.template_examen_finalizado")
					elif bloque.evaluacion_id.fecha_inicio >= ahora:
						return request.render("website_examenes.template_examen_inicio")
				else:
					return request.render("website_examenes.template_examen_no_disponible")
			else:
				return request.render("website_examenes.template_no_inscrito")

	# rutas de solucionario

	@http.route("/evaluaciones/solucionario/<model('evaluacion'):evaluacion>", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def evaluaciones_solucionario(self, evaluacion):
		examen = evaluacion.examen_id
		ahora = datetime.now()
		user = request.env.user.id
		integrante = False
		for line in evaluacion.grupo_alumnos.users_ids:
			if user == line.user_id.id:
				integrante =  True
		if integrante:
			if evaluacion.fecha_fin:
				if evaluacion.fecha_fin <= ahora:
					if evaluacion.state == 'publico':
						if evaluacion.tipo_evaluacion == 'diario':
							return request.render("website_examenes.examenes_solucionario", {"evaluacion": evaluacion, "examen": examen})
						else:
							return request.render("website_examenes.examenes_solucionario_simulacro", {"evaluacion": evaluacion})
					else:
						return request.render("website_examenes.template_solucionario_no_disponible")
				else:
					return request.render("website_examenes.template_solucionario_no_disponible")
			else:
				return request.render("website_examenes.template_solucionario_no_disponible")
		else:
			return request.render("website_examenes.template_solucionario_no_disponible")

	@http.route("/evaluaciones/solucionarios/<model('evaluacion.line'):evaluacion_line>", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def evaluaciones_solucionarios(self, evaluacion_line):
		ahora = datetime.now()
		user = request.env.user.id
		integrante = False
		for line in evaluacion_line.evaluacion_id.grupo_alumnos.users_ids:
			if user == line.user_id.id:
				integrante = True
		if integrante:
			if evaluacion_line.evaluacion_id.fecha_fin:
				if evaluacion_line.evaluacion_id.fecha_fin <= ahora:
					if evaluacion_line.evaluacion_id.state == 'publico':
						return request.render("website_examenes.examenes_solucionario", {"examen": evaluacion_line.examen_id})
					else:
						return request.render("website_examenes.template_solucionario_no_disponible")
				else:
					return request.render("website_examenes.template_solucionario_no_disponible")
			else:
				return request.render("website_examenes.template_solucionario_no_disponible")
		else:
			return request.render("website_examenes.template_solucionario_no_disponible")

	#claves

	@http.route("/evaluaciones/clave/<model('evaluacion'):evaluacion>", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def evaluaciones_clave(self, evaluacion):
		examen = evaluacion.examen_id
		ahora = datetime.now()
		user = request.env.user.id
		integrante = False
		for line in evaluacion.grupo_alumnos.users_ids:
			if user == line.user_id.id:
				integrante =  True
		if integrante:
			if evaluacion.fecha_fin:
				if evaluacion.fecha_fin <= ahora:
					if evaluacion.state == 'publico':
						if evaluacion.tipo_evaluacion == 'diario':
							return request.render("website_examenes.examenes_clave", {"evaluacion": evaluacion, "examen": examen})
						else:
							return request.render("website_examenes.examenes_clave_simulacro", {"evaluacion": evaluacion})
					else:
						return request.render("website_examenes.template_clave_no_disponible")
				else:
					return request.render("website_examenes.template_clave_no_disponible")
			else:
				return request.render("website_examenes.template_clave_no_disponible")
		else:
			return request.render("website_examenes.template_clave_no_disponible")


	@http.route("/evaluaciones/claves/<model('evaluacion.line'):evaluacion_line>", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def evaluaciones_claves(self, evaluacion_line):
		ahora = datetime.now()
		user = request.env.user.id
		integrante = False
		for line in evaluacion_line.evaluacion_id.grupo_alumnos.users_ids:
			if user == line.user_id.id:
				integrante = True
		if integrante:
			if evaluacion_line.evaluacion_id.fecha_fin:
				if evaluacion_line.evaluacion_id.fecha_fin <= ahora:
					if evaluacion_line.evaluacion_id.state == 'publico':
						return request.render("website_examenes.examenes_clave", {"examen": evaluacion_line.examen_id})
					else:
						return request.render("website_examenes.template_clave_no_disponible")
				else:
					return request.render("website_examenes.template_clave_no_disponible")
			else:
				return request.render("website_examenes.template_clave_no_disponible")
		else:
			return request.render("website_examenes.template_clave_no_disponible")


	#claves
	@http.route("/ranking", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def ranking(self):
		fecha_actual = datetime.now()
		grupos = request.env["res.users.line"].sudo().search([('user_id',  '=',  request.env.user.id)])
		usuarios = request.env["res.users"].sudo().search([('id', '=', request.env.user.id)],limit=1)
		fecha_ciclo = datetime.now().date()
		if len(usuarios.ciclo_eval_ids)>0:
			for ciclo in usuarios.ciclo_eval_ids:
				if ciclo.ciclo_id.fecha_inicio < fecha_ciclo:
					fecha_ciclo = ciclo.ciclo_id.fecha_inicio
			fecha_ciclo = fecha_ciclo - timedelta(days=10)
			fecha_ciclo = datetime(fecha_ciclo.year, fecha_ciclo.month, fecha_ciclo.day)
			evaluaciones = request.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos]), ('state',  '=',  'publico'), ('fecha_inicio',  '<',  fecha_actual), ('create_date',  '>',  fecha_ciclo)])
		else:
			evaluaciones = request.env["evaluacion"].sudo().search([('grupo_alumnos', 'in', [(rec.grupo_alumnos_id.id) for rec in grupos]), ('state',  '=',  'publico'), ('fecha_inicio',  '<',  fecha_actual)])
		return request.render("website_examenes.evaluaciones_ranking_list", {"evaluaciones": evaluaciones})


	# examen = request.env["examen"].browse(i1nt(id))
	@http.route("/ranking/<model('evaluacion'):evaluacion>", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def ranking_simulacro(self, evaluacion):
		ahora = datetime.now()
		user = request.env.user.id
		integrante = False
		record_respuestas = request.env["respuesta"].sudo().search([('evaluacion_id',  '=', evaluacion.id)])
		for respuesta_line in record_respuestas:
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
					line.puntaje = 0.0
				contador = contador + 1
			curso_activo = 0
			identificador = 0
			puntaje_curso = 0.0
			contador_curso = 0
			ultimo = len(lineas_respuestas)
			for line in lineas_respuestas:
				if line.is_curso:
					if identificador == 0:
						curso_activo = line.curso_general_id.id
						puntaje_curso = 0.0
						contador_curso = 0
					else:
						for obj in respuesta_line.respuestas_slide_ids:
							if obj.curso_general_id.id == curso_activo:
								if puntaje_curso <=0:
									obj.puntaje = puntaje_curso
									obj.nota_vigesimal = round((puntaje_curso/(contador_curso*pts_correcto))*20,2)
								else:
									obj.puntaje = puntaje_curso
									obj.nota_vigesimal = round((puntaje_curso/(contador_curso*pts_correcto))*20,2)
						curso_activo = line.curso_general_id.id
						puntaje_curso = 0.0
						contador_curso = 0
				else:
					puntaje_curso = puntaje_curso + line.puntaje
					contador_curso = contador_curso + 1

				if ultimo-1==identificador:
					for obj in respuesta_line.respuestas_slide_ids:
						if obj.curso_general_id.id == curso_activo:
							if puntaje_curso <=0:
								obj.puntaje = puntaje_curso
								obj.nota_vigesimal = round((puntaje_curso/(contador_curso*pts_correcto))*20,2)
							else:
								obj.puntaje = puntaje_curso
								obj.nota_vigesimal = round((puntaje_curso/(contador_curso*pts_correcto))*20,2)
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


		respuestas = request.env["respuesta"].sudo().search([('evaluacion_id',  '=', evaluacion.id)],order = 'nota_vigesimal desc')
		respuesta_usuario = request.env["respuesta"].search([["user_id", "=", request.env.uid], ["evaluacion_id", "=", evaluacion.id]])
		respuesta_usuario_unida = request.env["respuesta.simulacro"].search([["user_id", "=", request.env.uid], ["evaluacion_id", "=", evaluacion.id]])
		respuestas_unidas_simulacro = request.env["respuesta.simulacro"].sudo().search([('evaluacion_id',  '=', evaluacion.id),('carrera_id',  '=', request.env.user.carrera_id.id)],order = 'puntaje desc')
		respuestas_unidas_semanal = request.env["respuesta.simulacro"].sudo().search([('evaluacion_id',  '=', evaluacion.id)],order = 'nota_vigesimal desc')
		#para la prueba diaria
		puesto_diario = 0
		numero_diario= 1
		for respuesta in respuestas:
			if respuesta.user_id.id == user:
				puesto_diario = numero_diario
			numero_diario = numero_diario + 1
		#para la prueba semanal
		puesto_semanal = 0
		numero_semanal = 1
		for respuesta in respuestas_unidas_semanal:
			if respuesta.user_id.id == user:
				puesto_semanal = numero_semanal
			numero_semanal = numero_semanal + 1
		#para la prueba simulacro
		puesto_simulacro = 0
		numero_simulacro = 1
		for respuesta in respuestas_unidas_simulacro:
			if respuesta.user_id.id == user:
				puesto_simulacro = numero_simulacro
			numero_simulacro = numero_simulacro + 1


		for line in evaluacion.grupo_alumnos.users_ids:
			if user == line.user_id.id:
				integrante = True
		if integrante:
			if evaluacion.fecha_fin:
				if evaluacion.fecha_fin <= ahora:
					if evaluacion.state == 'publico':
						if  evaluacion.tipo_evaluacion =='diario':
							return request.render("website_examenes.evaluaciones_ranking_form", {"evaluacion": evaluacion,"respuesta_usuario":respuesta_usuario,"puntaje_alumno":respuesta_usuario.nota_vigesimal ,"nombre_alumno":respuesta_usuario.user_id.name,"numero_alumno":puesto_diario})
						elif evaluacion.tipo_evaluacion =='simulacro':
							return request.render("website_examenes.evaluaciones_simulacro_ranking_form", {"evaluacion": evaluacion,"respuesta_usuario_unida":respuesta_usuario_unida,"puntaje_total_simulacro":respuesta_usuario_unida.puntaje,"nombre_alumno":respuesta_usuario_unida.user_id.name,"carrera_alumno":respuesta_usuario_unida.user_id.carrera_id.name,"numero_alumno":puesto_simulacro})
						elif evaluacion.tipo_evaluacion =='semanal':
							if evaluacion.fecha_fin <= datetime(2020, 7, 14, 0, 0, 0):
								return request.render("website_examenes.evaluaciones_ranking_form", {"evaluacion": evaluacion,"respuesta_usuario":respuesta_usuario,"puntaje_alumno":respuesta_usuario.nota_vigesimal ,"nombre_alumno":respuesta_usuario.user_id.name,"numero_alumno":puesto_diario})
							else:
								return request.render("website_examenes.evaluaciones_semanal_ranking_form", {"evaluacion": evaluacion,"respuesta_usuario_unida":respuesta_usuario_unida,"puntaje_total_simulacro":respuesta_usuario_unida.nota_vigesimal,"nombre_alumno":respuesta_usuario_unida.user_id.name,"carrera_alumno":respuesta_usuario_unida.user_id.carrera_id.name,"numero_alumno":puesto_semanal})
					else:
						return request.render("website_examenes.template_ranking_no_disponible")
				else:
					return request.render("website_examenes.template_ranking_no_disponible")
			else:
				return request.render("website_examenes.template_ranking_no_disponible")
		else:
			return request.render("website_examenes.template_ranking_no_disponible")

	@http.route("/ranking/list/<model('evaluacion.line'):evaluacion>", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def ranking_list(self, evaluacion):
		ahora = datetime.now()
		user = request.env.user.id
		integrante = False
		record_respuestas = request.env["respuesta"].sudo().search([('evaluacion_id',  '=', evaluacion.evaluacion_id.id),('examen_id',  '=', evaluacion.examen_id.id)])

		for respuesta_line in record_respuestas:
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
					line.puntaje = 0.0
				contador = contador + 1
			curso_activo = 0
			identificador = 0
			puntaje_curso = 0.0
			contador_curso = 0
			ultimo = len(lineas_respuestas)
			for line in lineas_respuestas:
				if line.is_curso:
					if identificador == 0:
						curso_activo = line.curso_general_id.id
						puntaje_curso = 0.0
						contador_curso = 0
					else:
						for obj in respuesta_line.respuestas_slide_ids:
							if obj.curso_general_id.id == curso_activo:
								if puntaje_curso <=0:
									obj.puntaje = puntaje_curso
									obj.nota_vigesimal = round((puntaje_curso/(contador_curso*pts_correcto))*20,2)
								else:
									obj.puntaje = puntaje_curso
									obj.nota_vigesimal = round((puntaje_curso/(contador_curso*pts_correcto))*20,2)
						curso_activo = line.curso_general_id.id
						puntaje_curso = 0.0
						contador_curso = 0
				else:
					puntaje_curso = puntaje_curso + line.puntaje
					contador_curso = contador_curso + 1

				if ultimo-1==identificador:
					for obj in respuesta_line.respuestas_slide_ids:
						if obj.curso_general_id.id == curso_activo:
							if puntaje_curso <=0:
								obj.puntaje = puntaje_curso
								obj.nota_vigesimal = round((puntaje_curso/(contador_curso*pts_correcto))*20,2)
							else:
								obj.puntaje = puntaje_curso
								obj.nota_vigesimal = round((puntaje_curso/(contador_curso*pts_correcto))*20,2)
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


		respuestas = request.env["respuesta"].sudo().search([('evaluacion_id',  '=', evaluacion.evaluacion_id.id),('examen_id',  '=', evaluacion.examen_id.id)],order = 'nota_vigesimal desc')
		respuesta_usuario = request.env["respuesta"].search([["user_id", "=", request.env.uid], ["examen_id", "=",  evaluacion.examen_id.id], ["evaluacion_id", "=", evaluacion.evaluacion_id.id]],order = 'nota_vigesimal desc',limit=1)

		numeracion = []
		nombre = []
		puntaje = []
		nombre_alumno = ''
		puntaje_alumno = 0.0
		nota_vigesimal_alumno = 0.0
		numero_alumno = 0
		numero= 1
		for respuesta in respuestas:
			if respuesta.user_id.id == user:
				nombre_alumno = respuesta.user_id.name
				puntaje_alumno = respuesta.puntaje
				nota_vigesimal_alumno = respuesta.nota_vigesimal
				numero_alumno = numero
			nombre.append(respuesta.user_id.name)
			puntaje.append(respuesta.puntaje)
			numeracion.append(numero)
			numero = numero + 1

		for line in evaluacion.evaluacion_id.grupo_alumnos.users_ids:
			if user == line.user_id.id:
				integrante = True
		if integrante:
			if evaluacion.evaluacion_id.fecha_fin:
				if evaluacion.evaluacion_id.fecha_fin <= ahora:
					if evaluacion.evaluacion_id.state == 'publico':
						if evaluacion.evaluacion_id.tipo_evaluacion =='simulacro':
							return request.render("website_examenes.evaluaciones_ranking_form_2", {"evaluacion": evaluacion,"respuesta_usuario":respuesta_usuario,"puntaje_alumno":puntaje_alumno,"nota_vigesimal_alumno":nota_vigesimal_alumno,"nombre_alumno":nombre_alumno,"numero_alumno":numero_alumno})
						else:
							return request.render("website_examenes.evaluaciones_ranking_form_1", {"evaluacion": evaluacion,"respuesta_usuario":respuesta_usuario,"puntaje_alumno":puntaje_alumno,"nota_vigesimal_alumno":nota_vigesimal_alumno,"nombre_alumno":nombre_alumno,"numero_alumno":numero_alumno})
					else:
						return request.render("website_examenes.template_ranking_no_disponible")
				else:
					return request.render("website_examenes.template_ranking_no_disponible")
			else:
				return request.render("website_examenes.template_ranking_no_disponible")
		else:
			return request.render("website_examenes.template_ranking_no_disponible")


	@http.route("/evaluaciones/detalle/<model('evaluacion'):evaluacion>", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def evaluaciones_detalle(self, evaluacion):
		examen = evaluacion.examen_id
		ahora = datetime.now()
		user = request.env.user.id
		integrante = False
		for line in evaluacion.grupo_alumnos.users_ids:
			if user == line.user_id.id:
				integrante =  True
		if integrante:
			if evaluacion.state == 'publico':
				if evaluacion.tipo_evaluacion == 'diario':
					if evaluacion.fecha_fin >= ahora:
						respuesta = request.env["respuesta"].search([["estado", "=", 'entregado'],["user_id", "=", request.env.uid], ["examen_id", "=", examen.id], ["evaluacion_id", "=", evaluacion.id]],order = 'nota_vigesimal desc',limit=1)
					else:
						respuesta = request.env["respuesta"].search([["user_id", "=", request.env.uid], ["examen_id", "=", examen.id], ["evaluacion_id", "=", evaluacion.id]],order = 'nota_vigesimal desc',limit=1)
					if len(respuesta)==0:
						return request.render("website_examenes.template_detalle_no_disponible")
					else:
						return request.render("website_examenes.examenes_detalle", {"respuesta":respuesta})
				else:
					return request.render("website_examenes.examenes_detalle_list", {"evaluacion": evaluacion})
			else:
				return request.render("website_examenes.template_detalle_no_disponible")
		else:
			return request.render("website_examenes.template_detalle_no_disponible")

	@http.route("/evaluaciones/detalles/<model('evaluacion.line'):evaluacion_line>", type="http", method=["GET", "POST"], auth="user", csrf=False, website=True)
	def evaluaciones_detalles(self, evaluacion_line):
		ahora = datetime.now()
		user = request.env.user.id
		integrante = False
		for line in evaluacion_line.evaluacion_id.grupo_alumnos.users_ids:
			if user == line.user_id.id:
				integrante = True
		if integrante:
			if evaluacion_line.evaluacion_id.state == 'publico':
				if evaluacion_line.evaluacion_id.fecha_fin >= ahora:
					respuesta = request.env["respuesta"].search([["estado", "=", 'entregado'],["user_id", "=", request.env.uid], ["examen_id", "=", evaluacion_line.examen_id.id], ["evaluacion_id", "=", evaluacion_line.evaluacion_id.id]],order = 'nota_vigesimal desc',limit=1)
				else:
					respuesta = request.env["respuesta"].search([["user_id", "=", request.env.uid], ["examen_id", "=", evaluacion_line.examen_id.id], ["evaluacion_id", "=", evaluacion_line.evaluacion_id.id]],order = 'nota_vigesimal desc',limit=1)
				if len(respuesta)==0:
					return request.render("website_examenes.template_detalle_no_disponible")
				else:
					if evaluacion_line.evaluacion_id.tipo_evaluacion == 'semanal':
						return request.render("website_examenes.examenes_detalle_semanal", {"respuesta":respuesta})
					if evaluacion_line.evaluacion_id.tipo_evaluacion == 'simulacro':
						return request.render("website_examenes.examenes_detalle_simulacro", {"respuesta":respuesta})
			else:
				return request.render("website_examenes.template_detalle_no_disponible")
		else:
			return request.render("website_examenes.template_detalle_no_disponible")
