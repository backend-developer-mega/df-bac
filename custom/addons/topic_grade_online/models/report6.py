# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Report6(models.Model):

    _name = "topic.grade.online.report6"
    _description = "Hoja de evaluacion de proyecto"

    name = fields.Char(string='Hoja de evaluacion de proyecto', default='Consolidado final')
    sequence = fields.Integer(
        "Secuencia", default=10,
        help="Secuencia que permite ordenar la lista de evaluaciones que se han espesificado.")
    evaluation_id = fields.Many2one('topic.grade.online.evaluations', string='Evaluacion',
                             ondelete='cascade',
                             help='Espesifica la evaluacion del trabajo de grado al cual esta asociado la evaluación.')
    carrera_id = fields.Many2one('hr.department', string='Carrera')
    name_egresado_id = fields.Many2one('hr.employee', "Egresado", track_visibility='onchange')
    
    #----------------------------------------------------------------------------------------------------
    #Reporte 1 Estado: report1
    note_promedio_1 = fields.Float("Proceso formativo 1",digits=0)
    note_procentaje_1 = fields.Float("Porcentaje (%)",digits=0)
    #---------------------------------------------------------------------------------------------------
    #Reporte 2 Estado: report2
    note_promedio_2 = fields.Float("Anteproyecto",digits=0)
    note_procentaje_2 = fields.Float("Porcentaje (%)",digits=0)
    #---------------------------------------------------------------------------------------------------
    #Reporte 3 Estado: report3
    note_promedio_3 = fields.Float("Proceso formativo 2",digits=0)
    note_procentaje_3 = fields.Float("Porcentaje (%)",digits=0)
    #---------------------------------------------------------------------------------------------------
    #Reporte 4 Estado: report4
    note_promedio_4 = fields.Float("Avance capitular",digits=0)
    note_procentaje_4 = fields.Float("Porcentaje (%)",digits=0)
    #---------------------------------------------------------------------------------------------------
    #Reporte 5 Estado: report5
    note_promedio_5 = fields.Float("Presentación oral final",digits=0)
    note_procentaje_5 = fields.Float("Porcentaje (%)",digits=0)
    #---------------------------------------------------------------------------------------------------
    #Reporte 6 Estado: report6
    note_promedio_6 = fields.Float("Nota Final",digits=0,compute='_compute_total_6')

    @api.depends('note_promedio_1', 'note_promedio_2', 'note_promedio_3', 'note_promedio_4', 'note_promedio_5','note_procentaje_1','note_procentaje_2','note_procentaje_3','note_procentaje_4','note_procentaje_5')
    @api.one
    def _compute_total_6(self):
        self.note_promedio_6 = (((self.note_promedio_1*self.note_procentaje_1)/100) + ((self.note_promedio_2*self.note_procentaje_2)/100) + ((self.note_promedio_3*self.note_procentaje_3)/100) + ((self.note_promedio_4*self.note_procentaje_4)/100) + ((self.note_promedio_5*self.note_procentaje_5)/100))

    @api.multi
    @api.depends('name')
    def name_get(self):
        '''Method to display name and code'''
        return [(rec.id, ' - ' + rec.name) for rec in self]





