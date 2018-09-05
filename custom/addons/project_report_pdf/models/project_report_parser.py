# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Nilmar Shereef(<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from odoo.http import request
from odoo import models, api
import datetime, locale
import logging
_logger = logging.getLogger(__name__)

class ProjectReportParser(models.AbstractModel):
    _name = 'report.project_report_pdf.project_report_template'

    def set_letters(self, date_change):
        conte_date = str(date_change)
        locale.setlocale(locale.LC_ALL, 'es_SV.utf8')
        hour_letter = self.numero_to_letras(int(datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('%I')))
        minutes_letter = self.numero_to_letras(int(datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('%M')))
        day_letter = self.numero_to_letras(int(datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('%d')))
        month_letter = datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('%B')
        year_letter = self.numero_to_letras(int(datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('%Y')))
        name_data = datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('El dia es: %A, mes: %B, anio: %Y,  hora: %I, minutos: %M,    -->') + str(hour_letter) + ' minutos ' + str(minutes_letter)
        name_data = "a las " + str(hour_letter) + " con " + str(minutes_letter) + " minutos del " + str(day_letter) + " de " + str(month_letter) + " del año " + str(year_letter)
        name_data = str(day_letter) + " de " + str(month_letter) + " del año " + str(year_letter)

        return name_data

    def set_letters_formt(self, date_change):
        conte_date = str(date_change)
        locale.setlocale(locale.LC_ALL, 'es_SV.utf8')
        day_letter = self.numero_to_letras(int(datetime.datetime.strptime(conte_date, '%Y-%m-%d').strftime('%d')))
        month_letter = datetime.datetime.strptime(conte_date, '%Y-%m-%d').strftime('%B')
        year_letter = self.numero_to_letras(int(datetime.datetime.strptime(conte_date, '%Y-%m-%d').strftime('%Y')))
        name_data = str(day_letter) + " de " + str(month_letter) + " del año " + str(year_letter)

        return name_data

    def get_elemets_letters(self, name):
        report_obj = request.env['project.report.grade']
        current_topic = report_obj.search([('id', '=', name)], limit=1).project_task_id
        vals_elements = []
        vals = {
            'create_project': self.set_letters(current_topic.create_date),
            'date_deadline':  self.set_letters_formt(current_topic.date_deadline)
        }
        vals_elements.append(vals)

        return vals_elements


    def get_binnacle_model(self, name):
        report_obj = request.env['project.report.grade']
        binnacle_obj = request.env['calendar.event']
        topic_obj = request.env['project.task']
        note_resument_obj = request.env['project.evaluation.resumen']
        current_topic = report_obj.search([('id', '=', name)], limit=1).project_task_id
        current_resumen_student = note_resument_obj.search([('project_task_id', '=', current_topic.id)])
        sql_query = """SELECT DISTINCT calendar_event_id FROM calendar_event_res_partner_rel WHERE res_partner_id IN (SELECT DISTINCT student_id FROM project_evaluation_resumen WHERE project_task_id = %s)"""
        params = (current_topic.id,)
        self.env.cr.execute(sql_query, params)
        results = [a for (a,) in self.env.cr.fetchall()]
        current_event_binnacle = binnacle_obj.search([('id','in',results)])
        vals_binnacle = []
        for i in current_event_binnacle:
            vals = {
                'id': i.id,
                'name': i.name,
                'date': i.display_start,
                'duration': i.duration,
                'observation': i.observation,
                'description': i.description,
                'attendee_ids': i.attendee_ids,
            }
            vals_binnacle.append(vals)
        return vals_binnacle

    def get_note_model(self, name):
        report_obj = request.env['project.report.grade']
        topic_obj = request.env['project.task']
        note_resument_obj = request.env['project.evaluation.resumen']
        student_note_oral = []
        current_topic = report_obj.search([('id', '=', name)], limit=1).project_task_id
        current_resumen_student = note_resument_obj.search([('project_task_id', '=', current_topic.id)])
        for i in current_resumen_student:
            if i.stage_id.end_stage:
                vals = {
                    'name': i.student_id.name,
                    'card': i.student_id.student_card,
                    'average': i.average,
                    'average_letter': report_obj.search([('id', '=', name)], limit=1).numero_to_letras_nota(i.average),
                }
                student_note_oral.append(vals)
        return student_note_oral
    
    def get_note_list_total(self, name):
        report_obj = request.env['project.report.grade']
        topic_obj = request.env['project.task']
        note_resument_obj = request.env['project.evaluation.resumen']
        note_list_obj = request.env['project.record.notes']
        student_note_oral = []
        current_topic = report_obj.search([('id', '=', name)], limit=1).project_task_id
        current_resumen_student = note_resument_obj.search([('project_task_id', '=', current_topic.id)])
        current_note_list = note_list_obj.search([('project_task_id', '=', current_topic.id)])
        vals_ids = []
        vals_note = []
        for i_val in current_resumen_student:
            vals_ids.append(i_val.student_id.id)
        vals_ids = set(vals_ids)
        for data in vals_ids:
            for i in current_note_list:
                if data == i.student_id.id:
                    vals = {
                        'name': i.student_id.name,
                        'card': i.student_id.student_card,
                        'name_evaluation': i.stage_id.name,
                        'name_criterion': i.criterion_id.name,
                        'percentage_criterion': i.criterion_id.percentage,
                        'note': i.note,
                    }
                    vals_note.append(vals)
        return vals_note

    def get_note_resumen(self, name):
        report_obj = request.env['project.report.grade']
        topic_obj = request.env['project.task']
        note_resument_obj = request.env['project.evaluation.resumen']
        student_note_oral = []
        current_topic = report_obj.search([('id', '=', name)], limit=1).project_task_id
        current_resumen_student = note_resument_obj.search([('project_task_id', '=', current_topic.id)])
        vals_ids = []
        vals_note = []
        for i_val in current_resumen_student:
            vals_ids.append(i_val.student_id.id)
        vals_ids = set(vals_ids)
        for data in vals_ids:
            vals_note = []
            name = ""
            card = ""
            global_note = 0.0
            for i in current_resumen_student:
                if data == i.student_id.id:
                    name = i.student_id.name
                    card = i.student_id.student_card
                    global_note = i.evaluation_id.average_global 
                    vals = {
                        'id': i.evaluation_id.id,
                        'average': i.average,
                    }
                    vals_note.append(vals)
            vals = {
                'name': name,
                'card': card,
                'notes': vals_note,
                'global_not': global_note,
            }
            student_note_oral.append(vals)
        return student_note_oral

    def get_task_model(self, name):
        wizard_record = request.env['wizard.project.report'].search([])[-1]
        task_obj = request.env['project.task']
        users_selected = []
        stages_selected = []
        current_task_obj = []
        for elements in wizard_record.partner_select:
            users_selected.append(elements.id)
        for elements in wizard_record.stage_select:
            stages_selected.append(elements.id)
        if len(wizard_record.partner_select) == 0:
            if len(wizard_record.stage_select) == 0:
                current_task = task_obj.search([('project_id', '=', name)])
                for i in current_task:
                    vals = {
                        'name': i.name,
                        'user_id': i.user_id.name,
                        'stage_id': i.stage_id.name,
                    }
                    current_task_obj.append(vals)
                return current_task_obj
            else:
                current_task = task_obj.search([('project_id', '=', name), ('stage_id', 'in', stages_selected)])
                for i in current_task:
                    vals = {
                        'name': i.name,
                        'user_id': i.user_id.name,
                        'stage_id': i.stage_id.name,
                    }
                    current_task_obj.append(vals)
                return current_task_obj
        else:
            if len(wizard_record.stage_select) == 0:
                current_task = task_obj.search([('project_id', '=', name), ('user_id', 'in', users_selected)])
                for i in current_task:
                    vals = {
                        'name': i.name,
                        'user_id': i.user_id.name,
                        'stage_id': i.stage_id.name,
                    }
                    current_task_obj.append(vals)
                return current_task_obj
            else:
                current_task = task_obj.search(
                    [('project_id', '=', name), ('user_id', 'in', users_selected), ('stage_id', 'in', stages_selected)])
                for i in current_task:
                    vals = {
                        'name': i.name,
                        'user_id':  i.user_id.name,
                        'stage_id': i.stage_id.name,
                    }
                    current_task_obj.append(vals)
                return current_task_obj

    def get_issue_model(self, name):
        wizard_record = request.env['wizard.project.report'].search([])[-1]
        issue_obj = request.env['project.issue']
        task_obj = issue_obj
        users_selected = []
        stages_selected = []
        current_task_obj = []
        for elements in wizard_record.partner_select:
            users_selected.append(elements.id)
        for elements in wizard_record.stage_select:
            stages_selected.append(elements.id)
        if len(wizard_record.partner_select) == 0:
            if len(wizard_record.stage_select) == 0:
                current_task = task_obj.search([('project_id', '=', name)])
                for i in current_task:
                    vals = {
                        'name': i.name,
                        'user_id': i.user_id.name,
                        'stage_id': i.stage_id.name,
                    }
                    current_task_obj.append(vals)
                return current_task_obj
            else:
                current_task = task_obj.search([('project_id', '=', name), ('stage_id', 'in', stages_selected)])
                for i in current_task:
                    vals = {
                        'name': i.name,
                        'user_id': i.user_id.name,
                        'stage_id': i.stage_id.name,
                    }
                    current_task_obj.append(vals)
                return current_task_obj
        else:
            if len(wizard_record.stage_select) == 0:
                current_task = task_obj.search([('project_id', '=', name), ('user_id', 'in', users_selected)])
                for i in current_task:
                    vals = {
                        'name': i.name,
                        'user_id': i.user_id.name,
                        'stage_id': i.stage_id.name,
                    }
                    current_task_obj.append(vals)
                return current_task_obj
            else:
                current_task = task_obj.search(
                    [('project_id', '=', name), ('user_id', 'in', users_selected), ('stage_id', 'in', stages_selected)])
                for i in current_task:
                    vals = {
                        'name': i.name,
                        'user_id': i.user_id.name,
                        'stage_id': i.stage_id.name,
                    }
                    current_task_obj.append(vals)
                return current_task_obj

    def get_list_model_task(self, name):
        wizard_record = request.env['wizard.project.report'].search([])[-1]
        if wizard_record.task_select:
            return 2
        else:
            return 3

    def get_list_model_issue(self, name):
        wizard_record = request.env['wizard.project.report'].search([])[-1]
        if wizard_record.issue_select:
            return 2
        else:
            return 3

    def get_list_model_binnacle(self, name):
        wizard_record = request.env['wizard.project.report'].search([])[-1]
        if wizard_record.binnacle_select:
            return 2
        else:
            return 3

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        model = self.env['project.report.grade'].search([('id', '=', docids)])
        get_task_model = self.get_task_model(docids),
        get_note_model = self.get_note_model(docids),
        get_note_resumen_global_model = self.get_note_resumen(docids),
        get_note_list_total = self.get_note_list_total(docids),
        get_binnacle_model = self.get_binnacle_model(docids),
        get_issue_model = self.get_issue_model(docids),
        get_list_model_task = self.get_list_model_task(docids),
        get_list_model_binnacle = self.get_list_model_binnacle(docids),
        get_list_model_issue = self.get_list_model_issue(docids),
        get_elemets_letters_data = self.get_elemets_letters(docids),
        docargs = {
            'doc': model,
            'get_note': get_note_model,
            'get_note_resumen': get_note_resumen_global_model,
            'get_note_list': get_note_list_total,
            'get_binnacle_list': get_binnacle_model,
            'get_task_model': get_task_model,
            'get_issue_model': get_issue_model,
            'get_list_model_task': get_list_model_task[0],
            'get_list_model_issue': get_list_model_issue[0],
            'get_list_model_binnacle': get_list_model_binnacle[0],
            'get_elemets_letters': get_elemets_letters_data,
        }

        return self.env['report'].render('project_report_pdf.project_report_template', docargs)



    def numero_to_letras(self, numero):
        indicador = [("",""),("MIL","MIL"),("MILLON","MILLONES"),("MIL","MIL"),("BILLON","BILLONES")]
        entero = int(numero)
        decimal = int(round((numero - entero)*100))
        #print 'decimal : ',decimal 
        contador = 0
        numero_letras = ""
        while entero >0:
            a = entero % 1000
            if contador == 0:
                en_letras = self.convierte_cifra(a,1).strip()
            else :
                en_letras = self.convierte_cifra(a,0).strip()
            if a==0:
                numero_letras = en_letras+" "+numero_letras
            elif a==1:
                if contador in (1,3):
                    numero_letras = indicador[contador][0]+" "+numero_letras
                else:
                    numero_letras = en_letras+" "+indicador[contador][0]+" "+numero_letras
            else:
                numero_letras = en_letras+" "+indicador[contador][1]+" "+numero_letras
            numero_letras = numero_letras.strip()
            contador = contador + 1
            entero = int(entero / 1000)
        numero_letras = numero_letras.lower()
        #return 'numero: ',numero
        return numero_letras

    def convierte_cifra(self,numero,sw):
        lista_centana = ["",("CIEN","CIENTO"),"DOSCIENTOS","TRESCIENTOS","CUATROCIENTOS","QUINIENTOS","SEISCIENTOS","SETECIENTOS","OCHOCIENTOS","NOVECIENTOS"]
        lista_decena = ["",("DIEZ","ONCE","DOCE","TRECE","CATORCE","QUINCE","DIECISEIS","DIECISIETE","DIECIOCHO","DIECINUEVE"),
                        ("VEINTE","VEINTI"),("TREINTA","TREINTA Y "),("CUARENTA" , "CUARENTA Y "),
                        ("CINCUENTA" , "CINCUENTA Y "),("SESENTA" , "SESENTA Y "),
                        ("SETENTA" , "SETENTA Y "),("OCHENTA" , "OCHENTA Y "),
                        ("NOVENTA" , "NOVENTA Y ")
                    ]
        lista_unidad = ["",("UN" , "UNO"),"DOS","TRES","CUATRO","CINCO","SEIS","SIETE","OCHO","NUEVE"]
        centena = int (numero / 100)
        decena = int((numero -(centena * 100))/10)
        unidad = int(numero - (centena * 100 + decena * 10))
        #print "centena: ",centena, "decena: ",decena,'unidad: ',unidad
     
        texto_centena = ""
        texto_decena = ""
        texto_unidad = ""
     
        #Validad las centenas
        texto_centena = lista_centana[centena]
        if centena == 1:
            if (decena + unidad)!=0:
                texto_centena = texto_centena[1]
            else :
                texto_centena = texto_centena[0]
     
        #Valida las decenas
        texto_decena = lista_decena[decena]
        if decena == 1 :
             texto_decena = texto_decena[unidad]
        elif decena > 1 :
            if unidad != 0 :
                texto_decena = texto_decena[1]
            else:
                texto_decena = texto_decena[0]
        #Validar las unidades
        #print "texto_unidad: ",texto_unidad
        if decena != 1:
            texto_unidad = lista_unidad[unidad]
            if unidad == 1:
                texto_unidad = texto_unidad[sw]
     
        return "%s %s %s" %(texto_centena,texto_decena,texto_unidad)

class ProjectReportParserResumen(models.AbstractModel):
    _name = 'report.project_report_pdf.project_report_resumen_template'

    def get_project_list_model(self, name):
        wizard_record = request.env['wizard.project.report'].search([])[-1]
        topic_obj = request.env['project.task'].search([('create_date', '>=', wizard_record.signed_up_start),('create_date', '<=', wizard_record.signed_up_end)])
        vals_topic_task = []
        for i in topic_obj:
            for a in i.student_ids:
                vals = {
                    'id': i.id,
                    'name_topic': i.name,
                    'career': i.career_id.name,
                    'teacher': i.user_id.name,
                    'student_name': a.name,
                    'student_card': a.student_card,
                }
                vals_topic_task.append(vals)
        return vals_topic_task

    def get_project_topic_list(self, name):
        report_obj = request.env['project.report.grade']
        binnacle_obj = request.env['calendar.event']
        topic_obj = request.env['project.task']
        note_resument_obj = request.env['project.evaluation.resumen']
        current_topic = report_obj.search([('id', '=', name)], limit=1).project_task_id
        current_resumen_student = note_resument_obj.search([('project_task_id', '=', current_topic.id)])
        sql_query = """SELECT DISTINCT calendar_event_id FROM calendar_event_res_partner_rel WHERE res_partner_id IN (SELECT DISTINCT student_id FROM project_evaluation_resumen WHERE project_task_id = %s)"""
        params = (current_topic.id,)
        self.env.cr.execute(sql_query, params)
        results = [a for (a,) in self.env.cr.fetchall()]
        current_event_binnacle = binnacle_obj.search([('id','in',results)])
        vals_binnacle = []
        for i in current_event_binnacle:
            vals = {
                'id': i.id,
                'name': i.name,
                'date': i.display_start,
                'duration': i.duration,
                'observation': i.observation,
                'description': i.description,
                'attendee_ids': i.attendee_ids,
            }
            vals_binnacle.append(vals)
        return vals_binnacle


    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        model = self.env['project.task'].search([('id', '=', 75)])
        get_project_list_model = self.get_project_list_model(docids),
        docargs = {
            'doc': model,
            'get_project_list_task': get_project_list_model,
        }

        return self.env['report'].render('project_report_pdf.project_report_resumen_template', docargs)

        