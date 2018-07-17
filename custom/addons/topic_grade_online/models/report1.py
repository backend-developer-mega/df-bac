# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Report1(models.Model):

    _name = "topic.grade.online.report1"
    _description = "PROCESO FORMATIVO 1 ( CORRESPONDE AL 10 % DE LA CALIFICACION FINAL )"

    name = fields.Char(string='Reporte', default='Proceso formativo 1 (10%)')
    sequence = fields.Integer(
        "Secuencia", default=10,
        help="Secuencia que permite ordenar la lista de evaluaciones que se han espesificado.")
    evaluation_id = fields.Many2one('topic.grade.online.evaluations', string='Evaluacion',
                             ondelete='cascade',
                             help='Espesifica la evaluacion del trabajo de grado al cual esta asociado la evaluación.')
    carrera_id = fields.Many2one('hr.department', string='Carrera')
    name_egresado_id = fields.Many2one('hr.employee', "Egresado", track_visibility='onchange')
    id_report_6 = fields.Many2one('topic.grade.online.report6', string='Consolidado de notas')
    
    #----------------------------------------------------------------------------------------------------
    #Reporte 1 Estado: report1
    note_asistence = fields.Float("Asistencia",digits=0)
    note_puntuality = fields.Float("Puntualidad",digits=0)
    note_responsability = fields.Float("Responsabilidad",digits=0)
    note_iniciativity = fields.Float("Iniciativa",digits=0)
    note_creativity = fields.Float("Creatividad",digits=0)
    note_promedio_1 = fields.Float("Nota",digits=0,compute='_compute_total')

    @api.depends('note_asistence', 'note_puntuality', 'note_responsability', 'note_iniciativity', 'note_creativity')
    @api.one
    def _compute_total(self):
        self.note_promedio_1 = (self.note_asistence + self.note_puntuality + self.note_responsability + self.note_iniciativity + self.note_creativity)/5
        self.env['topic.grade.online.report6'].browse(self.id_report_6.id).write({'note_promedio_1': self.note_promedio_1})

    """
    #---------------------------------------------------------------------------------------------------
    #Reporte 2 Estado: report2
    note_presentation_resumen = fields.Float("Presentación y Resumen Ejecutivo",digits=0)
    note_conteni_charter = fields.Float("Contenido Capitular",digits=0)
    note_analis_discute = fields.Float("Análisis y Discusión de Resultados",digits=0)
    note_promedio_2 = fields.Float("Nota Final",digits=0,compute='_compute_total_2')

    @api.depends('note_presentation_resumen', 'note_conteni_charter', 'note_analis_discute')
    @api.one
    def _compute_total_2(self):
        self.note_promedio_2 = (self.note_presentation_resumen + self.note_conteni_charter + self.note_analis_discute)/3

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

    #---------------------------------------------------------------------------------------------------
    #Reporte 4 Estado: report4
    note_asistence_4 = fields.Float("Asistencia",digits=0)
    note_puntuality_4 = fields.Float("Puntualidad",digits=0)
    note_responsability_4 = fields.Float("Responsabilidad",digits=0)
    note_iniciativity_4 = fields.Float("Iniciativa",digits=0)
    note_creativity_4 = fields.Float("Creatividad",digits=0)
    note_promedio_4 = fields.Float("Nota",digits=0,compute='_compute_total_4')

    @api.depends('note_asistence_4', 'note_puntuality_4', 'note_responsability_4', 'note_iniciativity_4', 'note_creativity_4')
    @api.one
    def _compute_total_4(self):
        self.note_promedio_4 = (self.note_asistence_4 + self.note_puntuality_4 + self.note_responsability_4 + self.note_iniciativity_4 + self.note_creativity_4)/5

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

    #---------------------------------------------------------------------------------------------------
    #Reporte 6 Estado: report6
    note_promedio_6 = fields.Float("Nota Final",digits=0,compute='_compute_total_6')

    @api.depends('note_promedio_1', 'note_promedio_2', 'note_promedio_3', 'note_promedio_4', 'note_promedio_5')
    @api.one
    def _compute_total_6(self):
        self.note_promedio_6 = (self.note_promedio_1 + self.note_promedio_2 + self.note_promedio_3 + self.note_promedio_4 + self.note_promedio_5)/5

"""



