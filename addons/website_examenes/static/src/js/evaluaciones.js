odoo.define("website_examenes.evaluaciones",function(require){
    'use strict';

    var publicWidget = require("web.public.widget");
    var rpc = require("web.rpc");
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    publicWidget.registry.Respuestas = publicWidget.Widget.extend({
        selector:".botton-click",
        events:{
            'click .botton-click':"action_mas_respuestas"
        },
        action_mas_info:function(ev){
            var partner_id = $(ev.currentTarget).data("partner_id")
            rpc.query({
                model:"res.partner",
                method:"read",
                args:[[partner_id],['id','name','email']]
            }).then(function(res){
            })
        },
        render_template:function(ev){
          tabla = QWeb.render("evaluaciones_programadas")
          $('div.evahoy').replaceWith("<b>Paragraph. </b>");
        },
        action_mas_respuestas:function(ev){
                var accordionitem = $(this).attr("data-tab");
              $("#"+accordionitem).slideToggle().parent().siblings().find(".accordion-content").slideUp();

              $(this).toggleClass("active-title");
              $("#"+accordionitem).parent().siblings().find(".accordion-title").removeClass("active-title");

              $("i.fa-chevron-down",this).toggleClass("chevron-top");
              $("#"+accordionitem).parent().siblings().find(".accordion-title i.fa-chevron-down").removeClass("chevron-top");
              },
    })


    publicWidget.registry.RowAlternativas = publicWidget.Widget.extend({
        selector:".row-alternativas",
        jsLibs: [
          '/website_permiso/static/src/lib/notify.js',
        ],
        events:{
            'click input':'click_alternativa'
        },
        click_alternativa:function(ev){
            var alternativa = $(ev.target).data("alternativa");
            var pregunta_id = $(this.$el).data("pregunta_id");
            var respuesta_id = $(".seccion-preguntas").data("respuesta_id");
            var sequence = $(this.$el).data("sequence");
            var duracion = $(".temporizador_container").data("duracion");
            rpc.query({
    					model:'respuesta.create.line',
    					method:'crear_respuestas_lines',
    					args:[1,respuesta_id,pregunta_id,alternativa,sequence,duracion],
    				}).then(function (output) {
              if (output == 1) {
                   alert("Usted ya ha entregado su examen");
                   location.reload();
                } else if (output == 2) {
                   alert("Usted ya ha entregado su examen");
                   location.reload();
                }else if (output == 3) {
                 alert("Usted ya no cuenta con tiempo");
                 location.reload();
                }else if (output == 4) {
                  $.notify.addStyle('happyblue', {
                    html: '<div class="toast" role="alert" aria-live="assertive" aria-atomic="true"><div class="toast-header"><button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close"><span aria-hidden="true"></span></button></div><div class="toast-body"><span data-notify-text/></div></div>',
                    classes: {
                      base: {
                        "white-space": "nowrap",
                        "padding": "2px"
                      },
                      superblue: {
                        "background-color": "#54a6dd",
                        "background":"lighten(#54a6dd, 30%)",
                        "border-color":"lighten(#54a6dd, 20%)",
                        "border-left-color":"#54a6dd",
                        "color":"darken(#54a6dd, 20%)",
                         "float": "right",
                      }
                    }
                  });
                    $.notify("RESPUESTA GUARDADA", {
                      style: 'happyblue',
                      className: 'superblue'
                    });

                }


            });



        }
    })

    publicWidget.registry.BtnEntrega = publicWidget.Widget.extend({
        selector:".btn-entrega",
        events:{
            'click a':'click_alternativa'
        },
        click_alternativa:function(ev){
            var respuesta_id = $(".btn-entrega").data("respuesta_id");
            rpc.query({
              model:'respuesta.create.line',
              method:'entredar_examen_button',
              args:[1,respuesta_id],
            }).then(function (output) {


            });



        },
    })


    publicWidget.registry.TemporizadorContainer = publicWidget.Widget.extend({
        selector:".temporizador_container",
        init:function(){
            this._super.apply(this, arguments);
        },
        start:function(){
            var self = this
            var duracion = $(".temporizador_container").data("duracion");
            var fecha_inicio = $(".temporizador_container").data("create_date");
            //Dividimos la fecha primero utilizando el espacio para obtener solo la fecha y el tiempo por separado
            var splitDate= fecha_inicio.split(" ");
            var date=splitDate[0].split("-");
            var time=splitDate[1].split(":");

            // Obtenemos los campos individuales para todas las partes de la fecha
            var dd=date[2];
            var mm=date[1]-1;
            var yyyy =date[0];
            var hh=time[0];
            var min=time[1];
            var ss=time[2];

            // Creamos la fecha con Javascript
            var fecha = new Date(yyyy,mm,dd,hh,min,ss);
            var init = (new Date(yyyy,mm,dd,hh,min,ss)).getTime() - 5*60*60*1000;

            var ahora = (new Date()).getTime()

            var tiempo_restante = duracion*60*1000 - (ahora - init)
            if(init && tiempo_restante>0){
                var format10 = function(val){
                    return val<10?`0${val}`:`${val}`
                }
                var tempo = function(){
                    ahora = (new Date()).getTime()
                    tiempo_restante = duracion*60*1000 - (ahora - init)
                    if( tiempo_restante < 0) self.start()
                    this.tiempo_restante = tiempo_restante
                    var dias = format10(parseInt(tiempo_restante/(24*60*60*1000)))
                    var tiempo_restante = tiempo_restante%(24*60*60*1000)

                    var horas = parseInt(tiempo_restante/(60*60*1000))
                    var tiempo_restante = tiempo_restante%(60*60*1000)

                    var minutos = parseInt(tiempo_restante/(60*1000))
                    var tiempo_restante = tiempo_restante%(60*1000)

                    var segundos = format10(parseInt(tiempo_restante/(1000)))
                    var segundos_int = parseInt(tiempo_restante/(1000))
                    if(minutos<=5 && horas == 0){
                        $(self.$el).find(".msg-tempo").text("¡ESTÁ POR TERMINAR!")
                    }
                    if (horas<= 0 && minutos <= 0  && segundos_int <= 0 ){
                      $(self.$el).find(".msg-tempo").text("¡HA TERMINADO!")
                      $(self.$el).find(".tiempo-restante-minutos").text('0')
                      $(self.$el).find(".tempo-segundos").text('0')
                      $(self.$el).find(".tempo-minutos").text('0')
                      $(self.$el).find(".tempo-horas").text('0')
                      $(self.$el).find(".tempo-segundos").text('0')

                    }else{
                      $(self.$el).find(".tiempo-restante-minutos").text(format10(minutos))
                      $(self.$el).find(".tiempo-restante-horas").text(format10(horas))
                      $(self.$el).find(".tempo-segundos").text(segundos)
                      $(self.$el).find(".tempo-minutos").text(format10(minutos))
                      $(self.$el).find(".tempo-horas").text(format10(horas))
                      $(self.$el).find(".tempo-segundos").text(segundos)
                    }


                }
                setInterval(tempo, 1000)
            }
        }


    })

})
