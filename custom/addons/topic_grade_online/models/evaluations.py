# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError

class Evaluations(models.Model):
    _name = "topic.grade.online.evaluations"
    _description = "Evaluaciones de los temas de trabajo de grado"
    _order = 'sequence'

    name = fields.Char("Titulo de la evaluación", required=True, translate=True)
    sequence = fields.Integer(
        "Secuencia", default=10,
        help="Secuencia que permite ordenar la lista de evaluaciones que se han espesificado.")
    topic_id = fields.Many2one('topic.grade.online.topic', string='Tema de grado',
                             ondelete='cascade',
                             help='Espesifica el tema del trabajo de grado al cual esta asociado la evaluación.')
    description = fields.Text("Descripción general de la evaluación")
    activity_ids = fields.One2many('topic.grade.online.activity', 'evaluations_id')
    note_procentaje_1 = fields.Float("Porcentaje (%)",digits=0,readonly=False)
    note_procentaje_2 = fields.Float("Porcentaje (%)",digits=0,readonly=False)
    note_procentaje_3 = fields.Float("Porcentaje (%)",digits=0,readonly=False)
    note_procentaje_4 = fields.Float("Porcentaje (%)",digits=0,readonly=False)
    note_procentaje_5 = fields.Float("Porcentaje (%)",digits=0,readonly=False)
    
    state = fields.Selection([
        ('report1', 'Reporte 1'),
        ('report2', 'Reporte 2'),
        ('report3', 'Reporte 3'),
        ('report4', 'Reporte 4'),
        ('report5', 'Reporte 5'),
        ('report6', 'Reporte 6')
    ], string='Estado', copy=False, default='report1')
    #-------------------------------------------------------------------------
    date_report = fields.Datetime('Fecha')
    docente_director_id = fields.Many2one('res.users', "Docente director", track_visibility='onchange')
    observations = fields.Char(string='Observaciones')
    description_note_final = fields.Char(string='Reglamento')

    #-------------------------------------------------------------------------
    #Relacion con los reportes
    report1_id = fields.One2many('topic.grade.online.report1', 'evaluation_id')
    report2_id = fields.One2many('topic.grade.online.report2', 'evaluation_id')
    report3_id = fields.One2many('topic.grade.online.report3', 'evaluation_id')
    report4_id = fields.One2many('topic.grade.online.report4', 'evaluation_id')
    report5_id = fields.One2many('topic.grade.online.report5', 'evaluation_id')
    report6_id = fields.One2many('topic.grade.online.report6', 'evaluation_id')

    #@api.depends('note_procentaje_1','note_procentaje_2','note_procentaje_3','note_procentaje_4','note_procentaje_5')
    @api.onchange('note_procentaje_1','note_procentaje_2','note_procentaje_3','note_procentaje_4','note_procentaje_5')
    @api.multi
    def _compute_total(self):
        list_data = self.env['topic.grade.online.evaluations'].search([('topic_id', '=', self.topic_id.id)])
        for datas in list_data:
            if datas.report6_id:
                for data in datas.report6_id:
                    if self.state == "report1":
                        self.env['topic.grade.online.report6'].browse(data.id).write({'note_procentaje_1': self.note_procentaje_1})
                    if self.state == "report2":
                        self.env['topic.grade.online.report6'].browse(data.id).write({'note_procentaje_2': self.note_procentaje_2})
                    if self.state == "report3":
                        self.env['topic.grade.online.report6'].browse(data.id).write({'note_procentaje_3': self.note_procentaje_3})
                    if self.state == "report4":
                        self.env['topic.grade.online.report6'].browse(data.id).write({'note_procentaje_4': self.note_procentaje_4})
                    if self.state == "report5":
                        self.env['topic.grade.online.report6'].browse(data.id).write({'note_procentaje_5': self.note_procentaje_5})
                    

