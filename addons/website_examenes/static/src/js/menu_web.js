odoo.define('website_examenes.menu_web', function (require) {
    "use strict";
    var localStorage = require('web.local_storage');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');

    var ActionMenuWeb = Widget.extend({
        template: 'link_pagina_web',
        events: {
            'click .pagina_web': 'onclick_gifticon',
        },

        start: function () {

        },

        onclick_gifticon: function () {
          var url = "http://integralclass.aprentech.tech/"
          window.open(url, '_blank');
        },
    });

    SystrayMenu.Items.push(ActionMenuWeb);
    return ActionMenuWeb;
});
