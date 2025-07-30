from odoo import models, fields, api
from num2words import num2words
from datetime import date

class HrContract(models.Model):
    _inherit = 'hr.contract'

    salary_in_words = fields.Char(string="Salary in Words", compute='_compute_salary_in_words', store=True)
    today_date = fields.Date(string="Today's Date", default=fields.Date.context_today, readonly=True)


    @api.depends('wage')
    def _compute_salary_in_words(self):
        for rec in self:
            if rec.wage:
                # Convert to plain number in words
                words = num2words(rec.wage, lang='en_IN')
                # Capitalize every word and append “Rupees Only”
                rec.salary_in_words = words.title() + " Rupees Only"
            else:
                rec.salary_in_words = ''
