# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Report2(models.Model):

    _name = "topic.grade.online.report2"
    _description = "ANTEPROYECTO ( CORRESPONDIENTE AL 20 % DE LA CALIFICACION FINAL )"

    name = fields.Char(string='Hoja de evaluacion de proyecto', default='Anteproyecto (20%)')
    sequence = fields.Integer(
        "Secuencia", default=20,
        help="Secuencia que permite ordenar la lista de evaluaciones que se han espesificado.")
    evaluation_id = fields.Many2one('topic.grade.online.evaluations', string='Evaluacion',
                             ondelete='cascade',
                             help='Espesifica la evaluacion del trabajo de grado al cual esta asociado la evaluación.')
    carrera_id = fields.Many2one('hr.department', string='Carrera')
    name_egresado_id = fields.Many2one('hr.employee', "Egresado", track_visibility='onchange')
    id_report_6 = fields.Many2one('topic.grade.online.report6', string='Consolidado de notas')

    #---------------------------------------------------------------------------------------------------
    #Reporte 2 Estado: report2
    note_asistence_2 = fields.Float("Asistencia",digits=0)
    note_puntuality_2 = fields.Float("Puntualidad",digits=0)
    note_responsability_2 = fields.Float("Responsabilidad",digits=0)
    note_iniciativity_2 = fields.Float("Iniciativa",digits=0)
    note_creativity_2 = fields.Float("Creatividad",digits=0)
    note_promedio_2 = fields.Float("Nota",digits=0,compute='_compute_total_2')

    @api.depends('note_asistence_2', 'note_puntuality_2', 'note_responsability_2', 'note_iniciativity_2', 'note_creativity_2')
    @api.one
    def _compute_total_2(self):
        self.note_promedio_2 = (self.note_asistence_2 + self.note_puntuality_2 + self.note_responsability_2 + self.note_iniciativity_2 + self.note_creativity_2)/5
        self.env['topic.grade.online.report6'].browse(self.id_report_6.id).write({'note_promedio_2': self.note_promedio_2})


