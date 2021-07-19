from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from datetime import datetime


class Website(Website):

    @http.route(auth='public')
    def index(self, data={}, **kw):
        res = super(Website, self).index(**kw)

        if request.env.user == request.website.user_id:
            return request.redirect('/web/login')

        if request.env.user.is_parent:
            return request.redirect('/my/home')
        else:
            return res


class OpeneducatParentWebView(http.Controller):

    @http.route('/home', auth='user', csrf=True, website=True)
    def my_home(self, *args, **kw):
        if request.env.user.is_parent:
            parent = request.env['op.parent'].sudo().search(
                [('user_id', '=', request.env.user.id)])
            student_partners = [p.partner_id.id for p in parent.student_ids]

            inv_bal = sum(request.env['account.move'].sudo().search(
                [('partner_id', 'in', student_partners), ('type', 'in', ['out_invoice'])]).mapped('amount_residual'))

            credit_bal = sum(request.env['account.move'].sudo().search(
                [('partner_id', 'in', student_partners), ('type', 'in', ['out_refund'])]).mapped('amount_residual'))

            total_balance = inv_bal - abs(credit_bal)

            events = request.env['event.event'].sudo().search(
                [('is_published', '=', True), ('state', '=', 'confirm'), ('date_begin', '>=', datetime.now())], order='date_begin asc', limit=5)

            context = {
                'parent': parent,
                'total_balance': total_balance,
                'events': events,
            }
            return request.render('openeducat_parent_web.myhome', context)

    @http.route('/my/fee/balance', auth='user', website=True)
    def my_fee(self):
        if request.env.user.is_parent:
            parent = request.env['op.parent'].sudo().search(
                [('user_id', '=', request.env.user.id)])

            context = {
                'parent': parent
            }
            return request.render('openeducat_parent_web.myfee', context)

    @http.route('/my/child/exam', auth='user', website=True)
    def my_childs_exams(self):
        if request.env.user.is_parent:
            parent = request.env['op.parent'].sudo().search(
                [('user_id', '=', request.env.user.id)])

            context = {
                'parent': parent
            }
            return request.render('openeducat_parent_web.my_child_results', context)

    @http.route('/my/child/exam/<int:student_id>', auth='user', website=True)
    def my_singlechild_exams(self, student_id):
        if request.env.user.is_parent:
            student = request.env['op.student'].sudo().search(
                [('id', '=', int(student_id))])
            exams = request.env['op.marksheet.line'].sudo().search([('student_id', '=', student.id)]).mapped(
                'marksheet_reg_id.exam_session_id').sorted(lambda r: r.start_date)

            context = {
                'student': student,
                'exams': exams
            }
            return request.render('openeducat_parent_web.my_singlechild_results', context)

    @http.route('/my/child/exams/<int:student_id>/exam/<int:exam_id>', auth='user', website=True)
    def my_singlechild_exams_results(self, student_id, exam_id):
        if request.env.user.is_parent:
            marksheet = request.env['op.marksheet.line'].sudo().search(
                [('student_id', '=', int(student_id)), ('marksheet_reg_id.exam_session_id', '=', int(exam_id))])

            context = {
                'class_section': marksheet.marksheet_reg_id.exam_session_id.course_id.upper_or_lower,
                'student': marksheet.student_id,
                'marksheet': marksheet
            }
            return request.render('openeducat_parent_web.my_singlechild_results_exam', context)

    @http.route('/my/child', auth='user', website=True)
    def web_get_parents_children(self, *args, **kwargs):
        if request.env.user.is_parent:
            students = request.env['op.parent'].sudo().search(
                [('user_id', '=', request.env.user.id)]).mapped('student_ids')

            context = {
                'students': students
            }
            return request.render('openeducat_parent_web.mychild', context)

    @http.route('/my/child/<int:student_id>/profile', auth='user', website=True)
    def web_get_child_profile(self, student_id, *args, **kw):

        if request.env.user.is_parent:
            student = request.env['op.student'].sudo().search(
                [('id', '=', int(student_id))])
            parents = request.env['op.parent'].sudo().search(
                [('student_ids', 'in', int(student_id))])
            activity = request.env['op.activity'].sudo().search(
                [('student_id', '=', int(student_id))])

            exams = request.env['op.marksheet.line'].sudo().search(
                [('student_id', '=', int(student_id))])

            examss = request.env['op.marksheet.line'].sudo().search([('student_id', '=', student.id)]).mapped(
                'marksheet_reg_id.exam_session_id').sorted(lambda r: r.start_date)

            exam_lines = []
            total_lines = []
            avg_and_score = {}
            class_type = ''
            if student.course_detail_ids:
                class_type = student.course_detail_ids[0].course_id.upper_or_lower

            grades = {
                '1': 'Grade One',
                '2': 'Grade Two',
                '3': 'Grade Three',
                '4': 'Gade Four',
                '5': 'Class Five',
                '6': 'Class Six',
                '7': 'Class Seven',
                '8': 'Class Eight',
            }

            for exam in exams:
                # class_type = exam.marksheet_reg_id.exam_session_id.course_id.upper_or_lower if exam.marksheet_reg_id else ''
                total = 0
                score = 0

                for line in exam.result_line:
                    if exam.marksheet_reg_id.exam_session_id.course_id.upper_or_lower != 'lower':
                        total += line.exam_id.total_marks
                        val = {
                            'name': line.exam_id.session_id.exam_type.name,
                            'total_marks': line.exam_id.total_marks,
                            'passing_marks': line.exam_id.min_marks,
                            'marks_obtained': line.marks,
                            'subject': line.exam_id.subject_id.name,
                            'grade': line.grade,
                            'status': line.status.capitalize(),
                        }
                        exam_lines.append(val)
                    else:
                        if exam.percentage >= 98 and exam.percentage <= 100:
                            score = 4
                        elif exam.percentage >= 80 and exam.percentage <= 97:
                            score = 3
                        elif exam.percentage >= 50 and exam.percentage <= 79:
                            score = 2
                        elif exam.percentage >= 0 and exam.percentage <= 49:
                            score = 1
                        val = {
                            'marks_obtained': line.marks,
                            'subject': line.exam_id.subject_id.name,
                            'rubrics_grade': line.rubrics_grade,
                            'percentage': exam.percentage,
                            'score': score
                        }
                        exam_lines.append(val)

                avg_and_score.update({
                    'percentage': exam.percentage,
                    'score': score,
                    'exam_name': exam.marksheet_reg_id.exam_session_id.name,
                    'class_number': grades.get(exam.marksheet_reg_id.exam_session_id.course_id.class_number)
                })

                total_lines.append({
                    'date': exam.generated_date.strftime('%m/%Y'),
                    'total_marks': exam.total_marks,
                    'exam_marks': total,
                    'percentage': exam.percentage,
                    'status': exam.status,
                })

            context = {
                'student': student,
                'parents': parents,
                'activity': activity,
                'exams': examss,
                'class_type': class_type,
                'total_lines': total_lines,
                'avg_and_score': avg_and_score,
            }
            return request.render('openeducat_parent_web.my_child_profile', context)

    @http.route('/my/child/attendance', auth='user', website=True)
    def child_attendance(self):
        if request.env.user.is_parent:
            parent = request.env['op.parent'].sudo().search(
                [('user_id', '=', request.env.user.id)])

            context = {
                'parent': parent,
            }
            return request.render('openeducat_parent_web.my_child_attendance', context)

    @http.route('/my/child/attendance/<int:student_id>', auth='user', website=True)
    def singlechild_attendance(self, student_id):
        if request.env.user.is_parent:
            student = request.env['op.student'].sudo().search(
                [('id', '=', int(student_id))])
            attendance = request.env['op.attendance.line'].sudo().search(
                [('student_id', '=', int(student_id)), ('present', '=', False)])

            context = {
                'student': student,
                'attendance': attendance,
            }
            return request.render('openeducat_parent_web.my_singlechild_attendance', context)

    @http.route('/my/child/assignment', auth='user', website=True)
    def child_assignment(self):
        if request.env.user.is_parent:
            parent = request.env['op.parent'].sudo().search(
                [('user_id', '=', request.env.user.id)])

            context = {
                'parent': parent,
            }
            return request.render('openeducat_parent_web.my_child_assignment', context)

    @http.route('/my/child/assignment/<int:student_id>', auth='user', website=True)
    def singlechild_assignment(self, student_id):
        if request.env.user.is_parent:
            student = request.env['op.student'].sudo().search(
                [('id', '=', int(student_id))])
            assignments = request.env['op.assignment'].sudo().search(
                [('allocation_ids', '=', int(student_id))])
            context = {
                'student': student,
                'assignments': assignments,
            }
            return request.render('openeducat_parent_web.my_singlechild_assignment', context)
