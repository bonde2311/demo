from odoo import models, fields, api
from odoo.exceptions import UserError


class TransferInternalValidationSample(models.Model):
    _inherit = "stock.picking"

    receiver_id = fields.Many2one(
        'res.users', string="Receiver Responsible",
        help="User at destination warehouse responsible for confirming receipt",
    )

    receiver_confirmation_state = fields.Selection(
        [('pending', 'Pending'), ('confirmed', 'Confirmed')],
        default='pending',
        string="Receiver Confirmation",
        tracking=True
    )

    waiting_receiver = fields.Boolean(
        compute='_compute_waiting_receiver',
        store=True,
        string="Waiting Receiver Confirmation",
    )

    state = fields.Selection(
        selection_add=[('waiting_receiver', 'Waiting Receiver Confirmation')],
    )

    @api.depends('state', 'picking_type_code', 'receiver_id')
    def _compute_waiting_receiver(self):
        for pick in self:
            pick.waiting_receiver = (
                pick.picking_type_code == 'internal'
                and pick.state == 'waiting_receiver'
                and bool(pick.receiver_id)
            )

    @api.constrains('receiver_id')
    def _check_receiver_assignment(self):
        for picking in self:
            if picking.state in ('waiting_receiver', 'done') and self.env.user != picking.user_id:
                raise UserError("Only the source responsible user can assign/change the receiver after dispatch.")

    def action_wait_for_receiver(self):
        for pick in self:
            if pick.picking_type_code != 'internal':
                raise UserError("Only internal transfers can wait for receiver.")
            if not pick.receiver_id:
                raise UserError("Please assign a Receiver before sending.")
            if pick.state != 'assigned':
                raise UserError("You can only send transfers that are in the 'Ready' state.")
            pick.write({
                'state': 'waiting_receiver',
                'receiver_confirmation_state': 'pending'
            })
        return True

    def button_validate(self):
        for pick in self:
            if pick.picking_type_code == 'internal':
                if pick.state == 'assigned':
                    raise UserError(
                        "You must first send this transfer to the receiver using the 'Send to Receiver' button."
                    )
                elif pick.state == 'waiting_receiver':
                    if not pick.receiver_id or pick.receiver_id != self.env.user:
                        raise UserError("Only the assigned receiver can validate this transfer.")
                    if pick.receiver_confirmation_state == 'confirmed':
                        raise UserError("This transfer has already been confirmed.")

                    # Mark receiver confirmation
                    pick.receiver_confirmation_state = 'confirmed'

                    # Let Odoo's core logic handle stock moves, quantities, accounting, etc.
                    return super().button_validate()

        return super().button_validate()


