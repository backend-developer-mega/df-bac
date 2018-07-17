# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Report5(models.Model):

    _name = "topic.grade.online.report5"
    _description = "PRESENTACION ORAL FINAL (CORRESPONDIENTE AL 20 % DE LA CALIFICACION FINAL)"

    name = fields.Char(string='Hoja de evaluacion de proyecto', default='Presentación oral final')
    sequence = fields.Integer(
        "Secuencia", default=50,
        help="Secuencia que permite ordenar la lista de evaluaciones que se han espesificado.")
    evaluation_id = fields.Many2one('topic.grade.online.evaluations', string='Evaluacion',
                             ondelete='cascade',
                             help='Espesifica la evaluacion del trabajo de grado al cual esta asociado la evaluación.')
    carrera_id = fields.Many2one('hr.department', string='Carrera')
    name_egresado_id = fields.Many2one('hr.employee', "Egresado", track_visibility='onchange')
    id_report_6 = fields.Many2one('topic.grade.online.report6', string='Consolidado de notas')
    
    #---------------------------------------------------------------------------------------------------
    #Reporte 5 Estado: report5
    note_presentation = fields.Float("Presentación",digits=0)
    note_capacity_resume = fields.Float("Capacidad de Síntesis",digits=0)
    note_use_recurse_audiovisual = fields.Float("Uso de Recursos Audiovisuales",digits=0)
    note_dominio_topic = fields.Float("Dominio del Tema",digits=0)
    note_promedio_5 = fields.Float("Nota Final",digits=0,compute='_compute_total_5')

    @api.depends('note_presentation', 'note_capacity_resume', 'note_use_recurse_audiovisual', 'note_dominio_topic')
    @api.one
    def _compute_total_5(self):
        self.note_promedio_5 = (self.note_presentation + self.note_capacity_resume + self.note_use_recurse_audiovisual + self.note_dominio_topic)/4
        self.env['topic.grade.online.report6'].browse(self.id_report_6.id).write({'note_promedio_5': self.note_promedio_5})

