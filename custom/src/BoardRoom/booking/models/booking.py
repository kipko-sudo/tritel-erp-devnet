from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Booking(models.Model):
    _name = 'boardroom.booking'
    _description = 'Booking'

    boardroom_id = fields.Many2one('boardroom.booking.room', string="Boardroom", required=True)
    requester_id = fields.Many2one('res.users', string="Requester", default=lambda self: self.env.user)
    start_datetime = fields.Datetime(string="Start DateTime", required=True)
    end_datetime = fields.Datetime(string="End DateTime", required=True)
    purpose = fields.Text(string="Purpose")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('in_use', 'In Use'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='draft')
    approved_by_id = fields.Many2one('res.users', string="Approved By")
    is_emergency = fields.Boolean(string="Emergency Booking", default=False)

    @api.constrains('start_datetime', 'end_datetime')
    def _check_datetime(self):
        for rec in self:
            if rec.start_datetime >= rec.end_datetime:
                raise ValidationError(_("End date must be after start date."))

    @api.constrains('start_datetime', 'end_datetime', 'boardroom_id')
    def _check_overlap(self):
        for rec in self:
            if rec.state not in ['draft', 'cancelled']:
                overlapping = self.env['boardroom.booking'].search([
                    ('boardroom_id', '=', rec.boardroom_id.id),
                    ('id', '!=', rec.id),
                    ('state', 'in', ['approved', 'in_use']),
                    ('start_datetime', '<', rec.end_datetime),
                    ('end_datetime', '>', rec.start_datetime)
                ])
                if overlapping and not rec.is_emergency:
                    raise ValidationError(_("This time slot overlaps with an existing booking."))

    @api.onchange('start_datetime', 'end_datetime', 'boardroom_id')
    def _onchange_check_availability(self):
        if self.start_datetime and self.end_datetime and self.boardroom_id:
            self._check_overlap()

    def action_submit(self):
        self.state = 'requested'
        self.message_post(body=_("Booking request submitted for approval."))

    def action_approve(self):
        self.state = 'approved'
        self.approved_by_id = self.env.user
        self.message_post(body=_("Booking approved by %s.") % self.env.user.name)

    def action_cancel(self):
        self.state = 'cancelled'
        self.message_post(body=_("Booking cancelled."))

    @api.model
    def _cron_update_status(self):
        now = fields.Datetime.now()
        bookings = self.search([('state', 'in', ['approved', 'in_use']), ('end_datetime', '<', now)])
        for booking in bookings:
            booking.state = 'completed'