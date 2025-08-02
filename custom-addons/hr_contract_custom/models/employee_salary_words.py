from odoo import models, fields, api
from num2words import num2words


class HrContract(models.Model):
    _inherit = 'hr.contract'

    wage_annual = fields.Float(string="Wage (Annual)")
    ctc_monthly = fields.Float(string="CTC (Monthly)")
    ctc_annual = fields.Float(string="CTC (Annual)")
    ctc_in_words = fields.Char(string="CTC in Words", compute='_compute_ctc_in_words', store=True)
    wage_in_words = fields.Char(string="Wage in Words", compute='_compute_wage_in_words', store=True)
    # today_date = fields.Date(string="Today's Date", default=fields.Date.context_today, readonly=True)

    @api.depends('wage_annual')
    def _compute_wage_in_words(self):
        for rec in self:
            if rec.wage_annual:
                try:
                    words = num2words(rec.wage_annual, to='currency', lang='en_IN')
                except NotImplementedError:
                    words = num2words(rec.wage_annual, to='currency')

                words = words.replace("euro", "Rupees").replace("-", " ")
                rec.wage_in_words = ' '.join(w.capitalize() for w in words.split())
            else:
                rec.wage_in_words = ''

    @api.depends('ctc_annual')
    def _compute_ctc_in_words(self):
        for rec in self:
            if rec.ctc_annual:
                try:
                    words = num2words(rec.ctc_annual, to='currency', lang='en_IN')
                except NotImplementedError:
                    words = num2words(rec.ctc_annual, to='currency')

                words = words.replace("euro", "Rupees").replace("-", " ")
                rec.ctc_in_words = ' '.join(w.capitalize() for w in words.split())
            else:
                rec.ctc_in_words = ''

    @api.onchange('wage')
    def _onchange_wage(self):
        for rec in self:
            if rec.wage:
                rec.wage_annual = rec.wage * 12

    @api.onchange('wage_annual')
    def _onchange_wage_annual(self):
        for rec in self:
            if rec.wage_annual:
                rec.wage = rec.wage_annual / 12

    @api.onchange('ctc_monthly')
    def _onchange_ctc_monthly(self):
        for rec in self:
            if rec.ctc_monthly:
                rec.ctc_annual = rec.ctc_monthly * 12

    @api.onchange('ctc_annual')
    def _onchange_ctc_annual(self):
        for rec in self:
            if rec.ctc_annual:
                rec.ctc_monthly = rec.ctc_annual / 12


