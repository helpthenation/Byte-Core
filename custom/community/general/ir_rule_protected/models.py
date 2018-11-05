# -*- coding: utf-8 -*-
from odoo import models, api, fields, exceptions, SUPERUSER_ID
from collections import defaultdict
from operator import attrgetter
import importlib
import logging
import os
import shutil
import tempfile
import urllib2
import urlparse
import zipfile

from docutils import nodes
from docutils.core import publish_string
from docutils.transforms import Transform, writer_aux
from docutils.writers.html4css1 import Writer
import lxml.html

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO   # NOQA

import odoo
from odoo import api, fields, models, modules, tools, _
from odoo.exceptions import AccessDenied, UserError
from odoo.tools.parse_version import parse_version
from odoo.tools.misc import topological_sort


MODULE_NAME = 'ir_rule_protected'
ACTION_DICT = {
    'view_type': 'form',
    'view_mode': 'form',
    'res_model': 'base.module.upgrade',
    'target': 'new',
    'type': 'ir.actions.act_window',
}


class IRRule(models.Model):
    _inherit = 'ir.rule'

    protected = fields.Boolean('Protected', help='Make rule editable only for superuser')

    @api.multi
    def check_restricted(self):
        if self.env.user.id == SUPERUSER_ID:
            return
        for r in self:
            if r.protected:
                raise exceptions.Warning("The Rule is protected. You don't have access for this operation")

    @api.multi
    def write(self, vals):
        self.check_restricted()
        return super(IRRule, self).write(vals)

    @api.multi
    def unlink(self):
        self.check_restricted()
        return super(IRRule, self).unlink()


class Module(models.Model):
    _inherit = "ir.module.module"


    @api.multi
    def button_uninstall(self):
        if 'base' in self.mapped('name'):
            raise UserError(_("The `base` module cannot be uninstalled"))
        deps = self.downstream_dependencies()
        (self + deps).write({'state': 'to remove'})
        return dict(ACTION_DICT, name=_('Uninstall'))
