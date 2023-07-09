# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
import io,binascii,tempfile
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
import logging
_logger = logging.getLogger(__name__)

try:
	import csv
except ImportError:
	_logger.debug('Cannot `import csv`.')
try:
	import xlrd
except ImportError:
	_logger.debug('Cannot `import xlrd`.')
try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.')


class ImportUsers(models.TransientModel):

	_name = 'import.users'

	file = fields.Binary('File',required=True)

	def create_users(self,values):
		groups = []

		if not values['name']:
			raise Warning(_("Ingresa el nombre de los usuarios"))
		if not values['email']:
			raise Warning(_("Ingresa el email de los usuarios"))
		if not values['login']:
			raise Warning(_("Ingresa el usuario para el login de los usuarios"))
		if not values['dni']:
			raise Warning(_("Ingresa el dni de los usuarios"))
		if not values['mobile']:
			raise Warning(_("Ingresa el mobile de los usuarios"))


		rec = self.env['res.users'].search([('login','like',values['login'])],limit=1)
		if rec:
			raise Warning(_("usuario %s ya existe!" %values['name']))


		if values['type']:
			user_type = self.env['res.groups'].search([('name','ilike',values['type'])])
			groups.append([4,user_type.id,])
		else:
			user_type = self.env['res.groups'].search([('name','ilike','Internal')])
			groups.append([4,user_type.id,])

		if not user_type:
			raise Warning(_("Please Enter Proper User Type for %s." %values['name']))


		# verificar carrera del alumno
		carrera = self.env['estudiante.carrera'].search([('name','like',values['carrera'])],limit=1)
		if carrera:
			carrera_id = carrera.id
			_logger.info(carrera.id)
		else:
			carrera_id = False
		# aulas y grupos
		grupos_ids = []
		if values['grupos']:
			for group in values['grupos']:
				rec = self.env['grupo.alumnos'].search([('name','like',group)],limit=1)
				if rec:
					grupos_ids.append(rec.id)
					_logger.info(rec.id)
				else:
					raise Warning(_("Grupo %s no encontrado" %(group) ))
		aulas_ids = []
		if values['aulas']:
			for group in values['aulas']:
				rec = self.env['grupo.alumnos'].search([('name','like',group)],limit=1)
				if rec:
					aulas_ids.append(rec.id)
					_logger.info(rec.id)
				else:
					raise Warning(_("Aula %s no encontrado" %(group) ))

		ciclos_ids = []
		if values['ciclos']:
			for group in values['ciclos']:
				rec = self.env['ciclo'].search([('name','like',group)],limit=1)
				if rec:
					ciclos_ids.append(rec.id)
					_logger.info(rec.id)
				else:
					raise Warning(_("Ciclo %s no encontrado" %(group) ))

		user = self.env['res.users'].sudo().create({
			'name':values['name'],
			'email':values['email'],
			'dni':values['dni'],
			'mobile':values['mobile'],
			'login':values['login'],
			'groups_id': tuple(groups),
			'carrera_id': carrera_id,
			})

		for line in grupos_ids:
			user_id = user.id
			user.grupos_eval_ids.create({"user_id":user_id,"grupo_alumnos_id":line})

		for line in aulas_ids:
			user_id = user.id
			user.aula_eval_ids.create({"user_id":user_id,"grupo_alumnos_id":line})

		for line in ciclos_ids:
			user_id = user.id
			user.ciclo_eval_ids.create({"user_id":user_id,"ciclo_id":line})

		return user

	def import_button(self):
		try:
			xlsfile = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
			xlsfile.write(binascii.a2b_base64(self.file))
			xlsfile.seek(0)
			workbook = xlrd.open_workbook(xlsfile.name)
			sheet = workbook.sheet_by_index(0)
		except Exception:
			raise Warning(_("Ingresar archivo de excel."))

		for row_no in range(sheet.nrows):
			if row_no > 0:
				line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
				_logger.info("impooort")
				vals = {
					'name':line[0],
					'email':line[1],
					'dni':line[2],
					'mobile':line[3],
					'login':line[4],
					'type':line[5],
					'carrera':line[6],
					'grupos':line[7].split(',') if line[7] else False,
					'aulas':line[8].split(',') if line[8] else False,
					'ciclos':line[9].split(',') if line[9] else False,

				}
				rec = self.create_users(vals)
				if not rec:
					raise Warning(_("Usuario %s no creado!" %line[0]))
		return
