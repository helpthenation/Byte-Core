# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo import api
from odoo import models
from odoo.addons.base.res.res_users import is_reified_group
from odoo.tools.translate import _
from odoo.tools import ustr

IR_CONFIG_NAME = 'access_restricted.fields_view_get_uid'


class ResUsers(models.Model):
    _inherit = 'res.users'

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        if view_type == 'form':
            last_uid = self.pool['ir.config_parameter'].get_param(IR_CONFIG_NAME)
            if int(last_uid) != self.env.user.id:
                self.pool['res.groups'].update_user_groups_view(SUPERUSER_ID)

        return super(ResUsers, self).fields_view_get(view_id, view_type, toolbar, submenu)

    @api.multi
    def write(self, vals):
        for key in vals:
            if is_reified_group(key):
                self.env['ir.config_parameter'].sudo().set_param(IR_CONFIG_NAME, '0')
                break
        return super(ResUsers, self).write(vals)


class ResGroups(models.Model):
    _inherit = 'res.groups'

    def update_user_groups_view(self):
        real_uid = self.env.user.id
        self.pool['ir.config_parameter'].set_param(SUPERUSER_ID, IR_CONFIG_NAME, real_uid)
        return super(ResGroups, self).update_user_groups_view(SUPERUSER_ID)

    def get_application_groups(self, domain=None):
        if domain is None:
            domain = []
        domain.append(('share', '=', False))
        real_uid = self.env.user.id or int(self.pool['ir.config_parameter'].get_param(IR_CONFIG_NAME, '0'))
        if real_uid and real_uid != SUPERUSER_ID:
            model_data_obj = self.pool.get('ir.model.data')
            _model, group_no_one_id = model_data_obj.get_object_reference('base', 'group_no_one')
            domain = domain + ['|', ('users', 'in', [real_uid]), ('id', '=', group_no_one_id)]
        return self.search(SUPERUSER_ID, domain)


class res_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _get_classified_fields(self):
        classified = super(res_config_settings, self)._get_classified_fields()
        if self.env.user.id == SUPERUSER_ID:
            return classified

        group = []
        for name, groups, implied_group in classified['group']:
            if self.pool['res.users'].search_count([('id', '=', self.env.user.id), ('groups_id', 'in', [implied_group.id])]):
                group.append((name, groups, implied_group))
        classified['group'] = group
        return classified

    def fields_get(self, fields=None, write_access=True, attributes=None):
        fields = super(res_config_settings, self).fields_get(
            fields, write_access, attributes)

        if self.env.user.id == SUPERUSER_ID:
            return fields

        for name in fields:
            if not name.startswith('group_'):
                continue
            f = self._columns[name]
            if self.pool['res.users'].has_group(f.implied_group):
                continue

            fields[name].update(
                readonly=True,
                help=ustr(fields[name].get('help', '')) +
                _('\n\nYou don\'t have access to change this settings, because you administration rights are restricted'))
        return fields
