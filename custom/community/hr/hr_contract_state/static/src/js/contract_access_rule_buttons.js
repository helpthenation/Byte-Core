/*
 * © 2016 Camptocamp SA
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
 */
odoo.define('hr_contract_state.main', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');

    var FormView = require('web.FormView');
    var ListView = require('web.ListView');

    FormView.include({

        load_record: function () {
            var self = this;
            return this._super.apply(this, arguments)
                .then(function () {
                    if (self.model == "hr.contract" && ["open", "pending", "close"].indexOf(self.datarecord.state) >= 0 && session.uid != 1){
                        self.contract_show_hide_edit_button(true)
                    } else {
                        self.contract_show_hide_edit_button(false)
                    }
                });
        },
        contract_show_hide_edit_button: function (hide) {
            if (this.$buttons) {
                var button = this.$buttons.find('.oe_form_button_edit');
                if (button) {
                    button.prop('disabled',hide);
                }
            }
        }

    });

});
