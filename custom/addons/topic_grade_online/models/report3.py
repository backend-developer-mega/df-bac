# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Report3(models.Model):

    _name = "topic.grade.online.report3"
    _description = "PROCESO FORMATIVO 2 ( CORRESPONDE AL 10 % DE LA CALIFICACION FINAL )"

    name = fields.Char(string='Reporte', default='Proceso formativo 2 (10%)')
    sequence = fields.Integer(
        "Secuencia", default=10,
        help="Secuencia que permite ordenar la lista de evaluaciones que se han espesificado.")
    evaluation_id = fields.Many2one('topic.grade.online.evaluations', string='Evaluacion',
                             ondelete='cascade',
                             help='Espesifica la evaluacion del trabajo de grado al cual esta asociado la evaluación.')
    carrera_id = fields.Many2one('hr.department', string='Carrera')
    name_egresado_id = fields.Many2one('hr.employee', "Egresado", track_visibility='onchange')
    id_report_6 = fields.Many2one('topic.grade.online.report6', string='Consolidado de notas')

    #---------------------------------------------------------------------------------------------------
    #Reporte 3 Estado: report3
    note_asistence_3 = fields.Float("Asistencia",digits=0)
    note_puntuality_3 = fields.Float("Puntualidad",digits=0)
    note_responsability_3 = fields.Float("Responsabilidad",digits=0)
    note_iniciativity_3 = fields.Float("Iniciativa",digits=0)
    note_creativity_3 = fields.Float("Creatividad",digits=0)
    note_promedio_3 = fields.Float("Nota",digits=0,compute='_compute_total_3')

    @api.depends('note_asistence_3', 'note_puntuality_3', 'note_responsability_3', 'note_iniciativity_3', 'note_creativity_3')
    @api.one
    def _compute_total_3(self):
        self.note_promedio_3 = (self.note_asistence_3 + self.note_puntuality_3 + self.note_responsability_3 + self.note_iniciativity_3 + self.note_creativity_3)/5
        self.env['topic.grade.online.report6'].browse(self.id_report_6.id).write({'note_promedio_3': self.note_promedio_3})


    