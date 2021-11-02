from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning

class AccountLoan(models.Model):
    
    _inherit = 'account.loan'
     
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        state_obj = self.env['loan.stages'].search([('sequence','=', 1)], limit=1)
        if not state_obj:
            return False
        return state_obj.id
    
    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            if task.kanban_state == 'normal':
                task.kanban_state_label = task.legend_normal
            elif task.kanban_state == 'blocked':
                task.kanban_state_label = task.legend_blocked
            else:
                task.kanban_state_label = task.legend_done
    
    stage_id = fields.Many2one('loan.stages', string='Stage',  group_expand='_read_group_stage_ids', default=_get_default_stage_id,track_visibility='onchange', index=True,  copy=False)
    color = fields.Integer(string='Color Index')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ], default='0', index=True, string="Priority")
    
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True,
        help="A task's kanban state indicates special situations affecting it:\n"
             " * Grey is the default situation\n"
             " * Red indicates something is preventing the progress of this task\n"
             " * Green indicates the task is ready to be pulled to the next stage")
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Kanban State', track_visibility='onchange')
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True, related_sudo=False)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True, related_sudo=False)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True, related_sudo=False)
    
    @api.onchange('stage_id','state')
    def onchange_stage_id(self):
        if self._origin.id:
            record = self.env['account.loan'].browse(self._origin.id)
            if record.state != self.stage_id.state:
                raise Warning(_('Please Change To Appropriate State Before Moving To This Stage.'))
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['loan.stages'].search([])
            
    
#     stage_ids = fields.Many2many('loan.stages', 'loan_stages_rel', 'loan_id', 'stage_id', string='Stage',  default=_get_default_stage_id,track_visibility='onchange', index=True, copy=False)
