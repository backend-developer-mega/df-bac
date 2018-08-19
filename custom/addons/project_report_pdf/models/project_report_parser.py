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
import logging
_logger = logging.getLogger(__name__)

class ProjectReportParser(models.AbstractModel):
    _name = 'report.project_report_pdf.project_report_template'

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
        }

        return self.env['report'].render('project_report_pdf.project_report_template', docargs)

