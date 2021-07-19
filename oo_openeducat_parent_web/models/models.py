from odoo import api, fields, models


class OpCourse(models.Model):
    _inherit = 'op.course'

    upper_or_lower = fields.Selection(string='Class Section', selection=[
                                      ('lower', 'Lower'), ('upper', 'Upper')], store=True)
    class_number = fields.Selection(string='Class Number',
                                    selection=[('0', 'Kindergatten'),
                                               ('1', 'Grade One'), ('2',
                                                                    'Grade Two'),
                                               ('3', 'Grade Three'), ('4',
                                                                      'Grade Four'),
                                               ('5', 'Class Five'), ('6',
                                                                     'Class Six'),
                                               ('7', 'Class Seven'), ('8', 'Class Eight')], store=True)


class OpResultLine(models.Model):
    _inherit = 'op.result.line'

    rubrics_grade = fields.Char(
        string='Rubric Grade', compute='compute_rubric_grade')
    total_marks = fields.Integer(
        string='Exam Total Marks', compute='compute_total_marks')

    @api.depends('exam_id', 'exam_id.total_marks')
    def compute_total_marks(self):
        for rec in self:
            rec.total_marks = rec.exam_id.total_marks

    def compute_rubric_grade(self):
        for rec in self:
            if rec.exam_id.total_marks == 100:
                if rec.marks >= 98 and rec.marks <= 100:
                    rec.rubrics_grade = 4
                elif rec.marks >= 80 and rec.marks <= 97:
                    rec.rubrics_grade = 3
                elif rec.marks >= 50 and rec.marks <= 79:
                    rec.rubrics_grade = 2
                elif rec.marks >= 0 and rec.marks <= 49:
                    rec.rubrics_grade = 1
            elif rec.exam_id.total_marks == 50:
                if rec.marks >= 48 and rec.marks <= 50:
                    rec.rubrics_grade = 4
                elif rec.marks >= 40 and rec.marks <= 47:
                    rec.rubrics_grade = 3
                elif rec.marks >= 30 and rec.marks <= 39:
                    rec.rubrics_grade = 2
                elif rec.marks >= 0 and rec.marks <= 29:
                    rec.rubrics_grade = 1
            else:
                rec.rubrics_grade = 1


# class OpParent(models.Model):
#     _inherit = 'op.parent'

#     @api.model
#     def mass_create_parent_users(self):
#         parents = self.env['op.parent'].search(
#             [('user_id', '=', False), ('name.email', '!=', False)])

#         for parent in parents:
#             try:
#                 parent.create_parent_user()
#             except Exception as e:
#                 pass


class ResCompany(models.Model):
    _inherit = 'res.company'

    vision = fields.Text(string='School Vision')
    motto = fields.Text(string='School Motto')
    mission = fields.Text(string='School Mission')
