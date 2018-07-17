# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Topic(models.Model):

    _name = "topic.grade.online.topic"
    _description = "Temas trabajo de grado"

    #name = fields.Char(string='Tema de grado', required=True, index=True, translate=True)
    #eraise_topic_ids = fields.Char(string='Referencia')
    #description = fields.Text(string='Descripcion')
    #carrera_id = fields.Many2one('hr.department', string='Carrera')
    #department_id = fields.Many2one('hr.job', string='Departamento')

    activity_ids = fields.One2many('topic.grade.online.activity', 'topic_id', "Actividades")
    activity_count = fields.Integer(compute='_compute_activity_count', string="Actividades")

    #jefe_department_id = fields.Many2one('res.users', "Jefe de Departamento", track_visibility='onchange')
    #coordinador_department_id = fields.Many2one('res.users', "Coordinador de Departamento", track_visibility='onchange')
    #docente_director_id = fields.Many2one('res.users', "Docente director", track_visibility='onchange')
    
    evaluations_ids = fields.One2many('topic.grade.online.evaluations', 'topic_id', string="Evaluaciones") 
    total = fields.Float(string="Total", readonly=True, compute='calulate_total', store=True)
    project_topic_id = fields.Many2one('project.task', string='Tema inscripcion')
    #student_ids = fields.Many2many('res.partner', 'students_lead_tag_rel_res', 'students_lead_id_res', 'students_tag_id_res')

    @api.multi
    def filter_kanban_topic(self):
        domain = []
        if self.env.uid != 1:
            domain = ['|',('docente_director_id.id','=',self.env.uid),'|',
            ('jefe_department_id.id','=',self.env.uid),
            ('student_ids.id', '=', self.env['res.users'].search([('id', '=', self.env.uid)],limit=1).emp_id)]

        return {
            'name': _('Trabajo Grado'),
            'view_type': 'form',
            'view_mode': 'kanban,form',
            'res_model': 'topic.grade.online.topic',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': domain, 
#           'domain': [('student_ids.id', '=', 53)] or [('docente_director_id.id','=',1)] and [],
#           'domain': [('create_uid', 'in', [x.id for x in self.student_ids])],
        }
    

    #document_ids = fields.One2many('ir.attachment', string="Documentos")
    state = fields.Selection([
        ('process', 'Desarrollo de tema de grado'),
        ('open', 'Cerrado')
    ], string='Estado', readonly=True, required=True, track_visibility='always', copy=False, default='process', help="Muestra en que estado se encuentra un tema de grado.")

    @api.multi
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}


    @api.multi
    def show_evaluations_topic(self):
        '''
        Este metodo muestra las evaluaciones que estan asociadas al tema de trbajo de grado
        '''
        action = self.env.ref('topic_grade_online.open_view_topic_grade_online_list')
        result = action.read()[0]
        result['domain'] = [('topic_id', '=', self.id)]
        return result


    @api.one
    @api.depends('evaluations_ids.note_procentaje_1')
    @api.onchange('evaluations_ids.note_procentaje_1')
    def calulate_total(self):
        divide = sum(1 for line in self.evaluations_ids)
        if divide != 0:
            self.total = sum(line.note_procentaje_1 for line in self.evaluations_ids) / sum(1 for line in self.evaluations_ids)
        elif divide == 0:
            self.total = 0.0


    @api.one
    @api.depends('project_topic_id','student_ids')
    def _onchange_id_values(self):
        self.student_ids = self.project_topic_id.student_ids
        for project_topic_id in self.project_topic_id:
            if (project_topic_id.id and (self.env["project.task"].search([['id', '=', self.project_topic_id.id]]).active == True)):
                obj = self.env["project.task"].search([['id', '=', self.project_topic_id.id]])[0]
                self.student_ids = obj.student_ids
                evaluations_for_topic_1 = self.env['topic.grade.online.evaluations'].create({
                                            'name': 'Proceso formativo 1 (10%)',
                                            'sequence': 10,
                                            'topic_id': self.id,
                                            'state': 'report1',
                                            'note_procentaje_1': 10.0,
                                            'docente_director_id': self.docente_director_id.id,
                                            'description_note_final': 'POR MEDIO DE LA PRESENTE SE HACE CONSTAR LA NOTA PONDERADA DE CADA ALUMNO AL FINAL DE LA COLUMNA RESPECTIVA'
                                        })
                evaluations_for_topic_2 = self.env['topic.grade.online.evaluations'].create({
                                            'name': 'Anteproyecto (20%)',
                                            'sequence': 20,
                                            'topic_id': self.id,
                                            'state': 'report2',
                                            'note_procentaje_2': 20.0,
                                            'docente_director_id': self.docente_director_id.id,
                                            'description_note_final': 'POR MEDIO DE LA PRESENTE SE HACE CONSTAR LA NOTA PONDERADA DE CADA ALUMNO AL FINAL DE LA COLUMNA RESPECTIVA'
                                        })
                evaluations_for_topic_3 = self.env['topic.grade.online.evaluations'].create({
                                            'name': 'Proceso formativo 2 (10%)',
                                            'sequence': 30,
                                            'topic_id': self.id,
                                            'state': 'report3',
                                            'note_procentaje_3': 10.0,
                                            'docente_director_id': self.docente_director_id.id,
                                            'description_note_final': 'POR MEDIO DE LA PRESENTE SE HACE CONSTAR LA NOTA PONDERADA DE CADA ALUMNO AL FINAL DE LA COLUMNA RESPECTIVA'
                                        })
                evaluations_for_topic_4 = self.env['topic.grade.online.evaluations'].create({
                                            'name': 'Avance capitular (40%)',
                                            'sequence': 40,
                                            'topic_id': self.id,
                                            'state': 'report4',
                                            'note_procentaje_4': 40.0,
                                            'docente_director_id': self.docente_director_id.id,
                                            'description_note_final': 'POR MEDIO DE LA PRESENTE SE HACE CONSTAR LA NOTA PONDERADA DE CADA ALUMNO AL FINAL DE LA COLUMNA RESPECTIVA'
                                        })
                evaluations_for_topic_5 = self.env['topic.grade.online.evaluations'].create({
                                            'name': 'Presentación oral final (20%)',
                                            'sequence': 50,
                                            'topic_id': self.id,
                                            'state': 'report5',
                                            'note_procentaje_5': 20.0,
                                            'docente_director_id': self.docente_director_id.id,
                                            'description_note_final': 'POR MEDIO DE LA PRESENTE SE HACE CONSTAR LA NOTA PONDERADA DE CADA ALUMNO AL FINAL DE LA COLUMNA RESPECTIVA'
                                        })
                evaluations_for_topic_6 = self.env['topic.grade.online.evaluations'].create({
                                            'name': 'Consolidado final (100%)',
                                            'sequence': 60,
                                            'topic_id': self.id,
                                            'state': 'report6',
                                            'docente_director_id': self.docente_director_id.id,
                                            'description_note_final': 'POR MEDIO DE LA PRESENTE SE HACE CONSTAR LA NOTA PONDERADA DE CADA ALUMNO AL FINAL DE LA COLUMNA RESPECTIVA'
                                        })

                for student_id_uni in obj.student_ids:
                    report_6 = self.env['topic.grade.online.report6'].create({
                                            'evaluation_id': evaluations_for_topic_6.id,
                                            'carrera_id': self.carrera_id.id,
                                            'name_egresado_id': student_id_uni.id,
                                            'note_procentaje_1': 10.0,
                                            'note_procentaje_2': 20.0,
                                            'note_procentaje_3': 10.0,
                                            'note_procentaje_4': 40.0,
                                            'note_procentaje_5': 20.0
                               })

                    report_1 = self.env['topic.grade.online.report1'].create({
                                            'evaluation_id': evaluations_for_topic_1.id,
                                            'carrera_id': self.carrera_id.id,
                                            'name_egresado_id': student_id_uni.id,
                                            'id_report_6': report_6.id,
                                            'name': str(report_6.id) + ' '
                               })
                    report_2 = self.env['topic.grade.online.report2'].create({
                                            'evaluation_id': evaluations_for_topic_2.id,
                                            'carrera_id': self.carrera_id.id,
                                            'name_egresado_id': student_id_uni.id,
                                            'id_report_6': report_6.id,
                                            'name': str(report_6.id) + ' '
                               })
                    report_3 = self.env['topic.grade.online.report3'].create({
                                            'evaluation_id': evaluations_for_topic_3.id,
                                            'carrera_id': self.carrera_id.id,
                                            'name_egresado_id': student_id_uni.id,
                                            'id_report_6': report_6.id,
                                            'name': str(report_6.id) + ' '
                               })
                    report_4 = self.env['topic.grade.online.report4'].create({
                                            'evaluation_id': evaluations_for_topic_4.id,
                                            'carrera_id': self.carrera_id.id,
                                            'name_egresado_id': student_id_uni.id,
                                            'id_report_6': report_6.id,
                                            'name': str(report_6.id) + ' '
                               })
                    report_5 = self.env['topic.grade.online.report5'].create({
                                            'evaluation_id': evaluations_for_topic_5.id,
                                            'carrera_id': self.carrera_id.id,
                                            'name_egresado_id': student_id_uni.id,
                                            'id_report_6': report_6.id,
                                            'name': str(report_6.id) + ' '
                               })

