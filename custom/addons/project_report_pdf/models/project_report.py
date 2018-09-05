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
from odoo import models, fields, api, _
import datetime, locale

class ProjectReportButton(models.TransientModel):
    _name = 'wizard.project.report'

    task_select = fields.Boolean(string="Task", default=True)
    binnacle_select = fields.Boolean(string="Bitacotas", default=True)
    issue_select = fields.Boolean(string="Issue", default=True)
    partner_select = fields.Many2many('res.users', string='Assigned to')
    stage_select = fields.Many2many('project.task.type', string="Stage")

    department_select = fields.Many2one('hr.department', string='Departamento')
    signed_up_start = fields.Datetime('Fecha inicio')
    signed_up_end = fields.Datetime('Fecha fin')
    career_select = fields.Many2one('hr.job', string='Carrera')


    @api.multi
    def print_project_report_resumen_pdf(self):
        record = self.env['project.task']
        return self.env['report'].get_action(record, "project_report_pdf.project_report_resumen_template")

    @api.multi
    def print_project_report_pdf(self):

        active_record = self._context['active_id']
        record = self.env['project.report.grade'].browse(active_record)
        #return self.env['report'].get_action(record, "project_report_pdf.project_report_template")
        return self.env['report'].get_action(record, "project_report_pdf.project_report_template")

    @api.multi
    def print_project_report_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'project.project'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return {'type': 'ir.actions.report.xml',
                'report_name': 'project_report_pdf.project_report_xls.xlsx',
                'datas': datas,
                'name': 'Project Report'
                }

class ProjectTaskReportGrade(models.Model):
    _name = 'project.report.grade'
    _description = 'Reportes'

    name = fields.Char(string='Nombre', required=True)
    name_end = fields.Char(string='Finalizacion de la defensa', required=True)
    project_task_id = fields.Many2one('project.task', string='Tema de grado')
    date_defending = fields.Datetime(index=True, string='Fecha de defensa',select=True, default=fields.Datetime.now())
    date_defending_end = fields.Datetime(index=True, string='Final de defensa',select=True)
    name_president = fields.Char(string='Presidente')
    name_secretary = fields.Char(string='Secretario')
    name_vocal = fields.Char(string='Vocal')

    @api.onchange('date_defending')
    def set_letters(self):
        conte_date = str(self.date_defending)
        locale.setlocale(locale.LC_ALL, 'es_SV.utf8')
        hour_letter = self.numero_to_letras(int(datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('%I')))
        minutes_letter = self.numero_to_letras(int(datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('%M')))
        day_letter = self.numero_to_letras(int(datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('%d')))
        month_letter = datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('%B')
        year_letter = self.numero_to_letras(int(datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('%Y')))
        self.name = datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('El dia es: %A, mes: %B, anio: %Y,  hora: %I, minutos: %M,    -->') + str(hour_letter) + ' minutos ' + str(minutes_letter)
        self.name = "a las " + str(hour_letter) + " con " + str(minutes_letter) + " minutos del " + str(day_letter) + " de " + str(month_letter) + " del año " + str(year_letter)
        #self.name = str()

    @api.onchange('date_defending_end')
    def set_letters_end(self):
        conte_date = str(self.date_defending_end)
        locale.setlocale(locale.LC_ALL, 'es_SV.utf8')
        hour_letter = self.numero_to_letras(int(datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('%I')))
        minutes_letter = self.numero_to_letras(int(datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('%M')))
        day_letter = self.numero_to_letras(int(datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('%d')))
        month_letter = datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('%B')
        year_letter = self.numero_to_letras(int(datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('%Y')))
        self.name_end = datetime.datetime.strptime(conte_date, '%Y-%m-%d %H:%M:%S').strftime('El dia es: %A, mes: %B, anio: %Y,  hora: %I, minutos: %M,    -->') + str(hour_letter) + ' minutos ' + str(minutes_letter)
        self.name_end = "a las " + str(hour_letter) + " con " + str(minutes_letter) + " minutos del " + str(day_letter) + " de " + str(month_letter) + " del año " + str(year_letter)
    
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = (record.name[:40] + '...') if len(record.name) > 40 else record.name
            res.append((record.id, name))
        return res

    def numero_to_letras_nota(self, numero):
        entero = int(numero)
        decimal = int(round((numero - entero)*100))            
        numero_letras = self.numero_to_letras(entero) + " punto " + self.numero_to_letras(decimal)
        if decimal == 0:
            numero_letras = self.numero_to_letras(entero) + " punto cero"
        return numero_letras

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

