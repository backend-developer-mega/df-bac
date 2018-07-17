# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Report4(models.Model):

    _name = "topic.grade.online.report4"
    _description = "AVANCE CAPITULAR (CORRESPONDIENTE AL 40 % DE LA CALIFICACION FINAL)"

    name = fields.Char(string='Reporte', default='Avance capitular (40%)')
    sequence = fields.Integer(
        "Secuencia", default=40,
        help="Secuencia que permite ordenar la lista de evaluaciones que se han espesificado.")
    evaluation_id = fields.Many2one('topic.grade.online.evaluations', string='Evaluacion',
                             ondelete='cascade',
                             help='Espesifica la evaluacion del trabajo de grado al cual esta asociado la evaluación.')
    carrera_id = fields.Many2one('hr.department', string='Carrera')
    name_egresado_id = fields.Many2one('hr.employee', "Egresado", track_visibility='onchange')
    id_report_6 = fields.Many2one('topic.grade.online.report6', string='Consolidado de notas')


    #---------------------------------------------------------------------------------------------------
    #Reporte 4 Estado: report4
    note_presentation_resumen = fields.Float("Presentación y Resumen Ejecutivo",digits=0)
    note_conteni_charter = fields.Float("Contenido Capitular",digits=0)
    note_analis_discute = fields.Float("Análisis y Discusión de Resultados",digits=0)
    note_promedio_4 = fields.Float("Nota Final",digits=0,compute='_compute_total_4')

    @api.depends('note_presentation_resumen', 'note_conteni_charter', 'note_analis_discute')
    @api.one
    def _compute_total_4(self):
        self.note_promedio_4 = (self.note_presentation_resumen + self.note_conteni_charter + self.note_analis_discute)/3
        self.env['topic.grade.online.report6'].browse(self.id_report_6.id).write({'note_promedio_4': self.note_promedio_4})

