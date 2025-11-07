from odoo import models, fields, api

class Boardroom(models.Model):
    _name = 'boardroom.booking.room'
    _description = 'Boardroom'

    name = fields.Char(string="Room Name", required=True)
    capacity = fields.Integer(string="Capacity", default=10)
    status = fields.Selection([
        ('available', 'Available'),
        ('in_use', 'In Use')
    ], string="Status", compute='_compute_status', store=True)
    booking_ids = fields.One2many('boardroom.booking', 'boardroom_id', string="Bookings")

    @api.depends('booking_ids.start_datetime', 'booking_ids.end_datetime', 'booking_ids.state')
    def _compute_status(self):
        for room in self:
            now = fields.Datetime.now()
            active_bookings = self.env['boardroom.booking'].search([
                ('boardroom_id', '=', room.id),
                ('state', 'in', ['approved', 'in_use']),
                ('start_datetime', '<=', now),
                ('end_datetime', '>', now)
            ])
            room.status = 'in_use' if active_bookings else 'available'