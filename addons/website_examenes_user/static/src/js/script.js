odoo.define("website_examenes_user.evaluaciones",function(require){
    'use strict';

    var publicWidget = require("web.public.widget");
    var rpc = require("web.rpc");
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;


    publicWidget.registry.Appnend = publicWidget.Widget.extend({
        selector:".horario",
        init:function(){
            this._super.apply(this, arguments);
        },
        start:function(){
            rpc.query({
              model:'horario.render',
              method:'render',
              args:[1],
            }).then(function(output){
              $(".schedule").append(output);
            });

        },
    })


    publicWidget.registry.RegistrarAsistencia = publicWidget.Widget.extend({
        selector:".horario",
        events:{
            'click .registrar-asistencia':"crear_asistencia"
        },
        crear_asistencia:function(ev){
          var horario_id = $(ev.currentTarget).data("horario_id");
          rpc.query({
              route:"/asistencia_json",
              params:{
                horario:horario_id,
              }
          }).then(function(res){
          });
        },
    })
})
