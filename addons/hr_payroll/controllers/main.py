# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import werkzeug

from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.http import request

_logger = logging.getLogger(__name__)

class AuthSignupHome(Home):

    @http.route('/web/approval', type='http', auth='public', website=True)
    def get_run_approval(self, *args, **kw):
        qcontext = self.get_approval_qcontext()

        if not qcontext.get('token'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_approval(qcontext)
                    return request.render('hr_payroll.payroll_approved', qcontext)
                else:
                    login = qcontext.get('login')
                    assert login, "No login provided."
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        login, request.env.user.login, request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(login)
                    qcontext['message'] = _("An email has been sent with credentials to reset your password")
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception, e:
                qcontext['error'] = e.message or e.name

        return request.render('hr_payroll.approve_approve', qcontext)

    def get_approval_qcontext(self):
        """ Shared helper returning the rendering context for signup and reset password """
        qcontext = request.params.copy()
        if qcontext.get('token'):
            try:
                token_infos = request.env['hr.payslip.run'].sudo().approval_retrieve_info(qcontext.get('token'))
                for k in token_infos.items():
                    qcontext.setdefault(k)
            except:
                qcontext['error'] = _("Invalid approval token")
                qcontext['invalid_token'] = True
        return qcontext

    def do_approval(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        note = qcontext['approval_note']
        self._approve(qcontext.get('token'), note)
        request.env.cr.commit()

    def _approve(self, token, note):
        request.env['hr.payslip.run'].sudo().approve(note, token)