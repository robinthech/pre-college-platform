odoo.define("reporte_notas.reporte_notas_alumno",function(require){
    'use strict';

    var publicWidget = require("web.public.widget");
    var rpc = require("web.rpc");
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    publicWidget.registry.HideSidebar = publicWidget.Widget.extend({
      selector: ".wrapper",
      events: {
        'click #sidebarCollapse': 'click_excel',
      },
      click_excel: function(ev) {
        $('#sidebar').toggleClass('active');


      },
    })

    publicWidget.registry.TablaReporteNotasAlumno = publicWidget.Widget.extend({
        selector:".search-section-reporte",
        xmlDependencies:["/reporte_notas/static/src/xml/reporte_class_ponde_700.xml"],
        events:{
            'click .wrn-btn-reporte':'click_render_reporte',
        },
        jsLibs: [
          '/web/static/lib/Chart/Chart.js',
        ],
        init:function(){
            this._super.apply(this, arguments);
        },
        start:function(){
          var desde = $(this.$el).find("input[name='fecha_desde']").val()
          var hasta = $(this.$el).find("input[name='fecha_hasta']").val()
            var aula = $(this.$el).find("select[name='aula']").val()
             rpc.query({
               model:'reporte.notas.transient',
               method:'funcion_matriz_notas',
               args:[1,desde,hasta,aula],
             }).then(function(matriz_general){
                var diario = qweb.render("reporte_notas.reporte_notas_diario_class",{matriz:  matriz_general[0]});
                $("#template-reporte-diario-render").html(diario);
                var semanal = qweb.render("reporte_notas.reporte_notas_semanal_class",{matriz_semanal:  matriz_general[1]});
                $("#template-reporte-semanal-render").html(semanal);
                var simulacro = qweb.render("reporte_notas.reporte_notas_simulacro_class",{matriz_simulacro:  matriz_general[2]});
                $("#template-reporte-simulacro-render").html(simulacro);
                var situacion = qweb.render("reporte_notas.reporte_notas_situacion_class",{desde:desde,hasta:hasta,situacion:  matriz_general[9]});
                $("#template-reporte-situacion-render").html(situacion);
                $('#bar-chart').replaceWith($('<canvas id="bar-chart" width="800" height="450"></canvas>'));
                new Chart(document.getElementById("bar-chart"), {
                  type: 'bar',
                  data: {
                    labels:   matriz_general[3],
                    datasets: [{
                      label: "FASE 1",
                       backgroundColor: "#F7DA0D",
                      data: matriz_general[4],
                    },
                    {
                      label: "FASE 2",
                       backgroundColor: "#9B59B6",
                      data: matriz_general[5],
                    },
                    {
                      label: "FASE 3",
                       backgroundColor: "#F83C1B",
                      data: matriz_general[6],
                    },
                    {
                      label: "FASE 4",
                       backgroundColor: "#077EFC",
                      data: matriz_general[7],
                    },
                    {
                      label: "TOTAL",
                       backgroundColor: "#46C40B",
                      data: matriz_general[8],
                    },
                  ]
                  },
                  options: {
                    legend: {
                        position: "top"
                      },
                    title: {
                      display: true,
                      text: 'PUNTAJE SIMULACRO'
                    }
                  }
                });

             });

        },
        click_render_reporte:function(){
          var desde = $(this.$el).find("input[name='fecha_desde']").val()
          var hasta = $(this.$el).find("input[name='fecha_hasta']").val()
            var aula = $(this.$el).find("select[name='aula']").val()
             rpc.query({
               model:'reporte.notas.transient',
               method:'funcion_matriz_notas',
               args:[1,desde,hasta,aula],
             }).then(function(matriz_general){
                var diario = qweb.render("reporte_notas.reporte_notas_diario_class",{matriz:  matriz_general[0]});
                $("#template-reporte-diario-render").html(diario);
                var semanal = qweb.render("reporte_notas.reporte_notas_semanal_class",{matriz_semanal:  matriz_general[1]});
                $("#template-reporte-semanal-render").html(semanal);
                var simulacro = qweb.render("reporte_notas.reporte_notas_simulacro_class",{matriz_simulacro:  matriz_general[2]});
                $("#template-reporte-simulacro-render").html(simulacro);
                var situacion = qweb.render("reporte_notas.reporte_notas_situacion_class",{desde:desde,hasta:hasta,situacion:  matriz_general[9]});
                $("#template-reporte-situacion-render").html(situacion);
                $('#bar-chart').replaceWith($('<canvas id="bar-chart" width="800" height="450"></canvas>'));
                new Chart(document.getElementById("bar-chart"), {
                  type: 'bar',
                  data: {
                    labels:   matriz_general[3],
                    datasets: [{
                      label: "FASE 1",
                       backgroundColor: "#F7DA0D",
                      data: matriz_general[4],
                    },
                    {
                      label: "FASE 2",
                       backgroundColor: "#9B59B6",
                      data: matriz_general[5],
                    },
                    {
                      label: "FASE 3",
                       backgroundColor: "#F83C1B",
                      data: matriz_general[6],
                    },
                    {
                      label: "FASE 4",
                       backgroundColor: "#077EFC",
                      data: matriz_general[7],
                    },
                    {
                      label: "TOTAL",
                       backgroundColor: "#46C40B",
                      data: matriz_general[8],
                    },
                  ]
                  },
                  options: {
                    legend: {
                        position: "top"
                      },
                    title: {
                      display: true,
                      text: 'PUNTAJE SIMULACRO'
                    }
                  }
                });

             });

        },
      });

    publicWidget.registry.TablaReporteAsistenciasAlumno = publicWidget.Widget.extend({
        selector:".search-section-reporte-asistencia",
        xmlDependencies:["/reporte_notas/static/src/xml/reporte_asistencia_20.xml"],
        events:{
            'click .wrn-btn-reporte':'click_render_reporte',
        },
        jsLibs: [
          '/web/static/lib/Chart/Chart.js',
        ],
        init:function(){
            this._super.apply(this, arguments);
        },
        start:function(){
          $( ".loading-learning ").show( "slow" );
          var desde = $(this.$el).find("input[name='fecha_desde']").val()
          var hasta = $(this.$el).find("input[name='fecha_hasta']").val()
          var aula = $(this.$el).find("select[name='aula']").val()
            rpc.query({
              model:'reporte.notas.transient',
              method:'funcion_matriz_asistencias',
              args:[1,desde,hasta,aula],
            }).then(function(output){
              var asistencia = qweb.render("reporte_notas.reporte_asistencia_alumno",{matriz:output});
              $("#template-reporte-asistencia-render").html(asistencia);
              $( ".loading-learning ").hide( "slow" );

            });
        },

        click_render_reporte:function(){
          $( ".loading-learning ").show( "slow" );
          var desde = $(this.$el).find("input[name='fecha_desde']").val()
          var hasta = $(this.$el).find("input[name='fecha_hasta']").val()
          var aula = $(this.$el).find("select[name='aula']").val()
          rpc.query({
            model:'reporte.notas.transient',
            method:'funcion_matriz_asistencias',
            args:[1,desde,hasta,aula],
          }).then(function(output){
            var asistencia = qweb.render("reporte_notas.reporte_asistencia_alumno",{matriz:output});
            $("#template-reporte-asistencia-render").html(asistencia);
            $( ".loading-learning ").hide( "slow" );

        });


        },
    });

    publicWidget.registry.TablaReporteAsistenciasPorAlumno = publicWidget.Widget.extend({
        selector:".search-section-reporte-asistencia-alumno",
        xmlDependencies:["/reporte_notas/static/src/xml/reporte_asistencia_20.xml"],
        events:{
            'click .wrn-btn-reporte':'click_render_reporte',
            'change #browser':'click_validate_form',
        },
        jsLibs: [
          '/web/static/lib/Chart/Chart.js',
        ],
        init:function(){
            this._super.apply(this, arguments);
        },
        start:function(){
          $(".wrn-btn-reporte").attr("disabled",true);
          $('#sidebar').toggleClass('active');
        },
        click_validate_form:function(){
            var val =  $("input[name='browser']").val();
            var alumno =  $('#browsers [value="' + val + '"]').data('customvalue')
            rpc.query({
              model:'reporte.notas.transient',
              method:'get_areas_user',
              args:[1,alumno],
            }).then(function(html_output){
              $("select[name='aula']").empty().append(html_output);
                $(".wrn-btn-reporte").attr("disabled",false)

          });

        },

        click_render_reporte:function(){
          $( ".loading-learning ").show( "slow" );
          var desde = $(this.$el).find("input[name='fecha_desde']").val()
          var hasta = $(this.$el).find("input[name='fecha_hasta']").val()
          var aula = $(this.$el).find("select[name='aula']").val()
          var val =  $("input[name='browser']").val();
          var alumno =  $('#browsers [value="' + val + '"]').data('customvalue')
          rpc.query({
            model:'reporte.notas.transient',
            method:'funcion_matriz_asistencias_por_alumno',
            args:[1,desde,hasta,aula,alumno],
          }).then(function(output){
            var asistencia = qweb.render("reporte_notas.reporte_asistencia_por_alumno_10",{matriz:output});
            $("#template-reporte-asistencia-render").html(asistencia);
            $( ".loading-learning ").hide( "slow" );

        });


        },
    });

    publicWidget.registry.TablaReporteAsistenciasPorAula = publicWidget.Widget.extend({
        selector:".search-section-reporte-asistencia-aula",
        xmlDependencies:["/reporte_notas/static/src/xml/reporte_asistencia_20.xml"],
        events:{
            'click .wrn-btn-reporte':'click_render_reporte',
        },
        jsLibs: [
          '/web/static/lib/Chart/Chart.js',
        ],
        init:function(){
            this._super.apply(this, arguments);
        },
        start:function(){
          $('#sidebar').toggleClass('active');
        },

        click_render_reporte:function(){
          $( ".loading-learning ").show( "slow" );
          var desde = $(this.$el).find("input[name='fecha_desde']").val()
          var hasta = $(this.$el).find("input[name='fecha_hasta']").val()
          var aula = $(this.$el).find("select[name='aula']").val()
          rpc.query({
            model:'reporte.notas.transient',
            method:'funcion_matriz_asistencias_por_aula',
            args:[1,desde,hasta,aula],
          }).then(function(output){
            var asistencia = qweb.render("reporte_notas.reporte_asistencia_por_aula_20",{matriz:output});
            $("#template-reporte-asistencia-render").html(asistencia);
            $( ".loading-learning ").hide( "slow" );

        });


        },
    });

    publicWidget.registry.TablaReporteNotasAdministrador = publicWidget.Widget.extend({
        selector:".search-section-reporte-admin",
        xmlDependencies:["/reporte_notas/static/src/xml/reporte_class_ponde_700.xml"],
        events:{
            'click .wrn-btn-reporte':'click_render_reporte',
            'change #browser':'click_validate_form',
        },
        jsLibs: [
          '/web/static/lib/Chart/Chart.js',
        ],
        init:function(){
            this._super.apply(this, arguments);
        },
        start:function(){
            $(".wrn-btn-reporte").attr("disabled",true);
            $('#sidebar').toggleClass('active');
        },
        click_validate_form:function(){
            var val =  $("input[name='browser']").val();
            var alumno =  $('#browsers [value="' + val + '"]').data('customvalue')
            rpc.query({
              model:'reporte.notas.transient',
              method:'get_areas_user',
              args:[1,alumno],
            }).then(function(html_output){
              $("select[name='aula']").empty().append(html_output);
                $(".wrn-btn-reporte").attr("disabled",false)

          });

        },
        click_render_reporte:function(){
          var desde = $(this.$el).find("input[name='fecha_desde']").val()
          var hasta = $(this.$el).find("input[name='fecha_hasta']").val()
          var val =  $("input[name='browser']").val();
          var alumno =  $('#browsers [value="' + val + '"]').data('customvalue')
            var aula = $(this.$el).find("select[name='aula']").val()
             rpc.query({
               model:'reporte.notas.transient',
               method:'funcion_matriz_notas_admin',
               args:[1,desde,hasta,aula,alumno],
             }).then(function(matriz_general){
                var diario = qweb.render("reporte_notas.reporte_notas_diario_class",{matriz:  matriz_general[0]});
                if (matriz_general[10]){
                  $("#template-reporte-diario-render").html(diario);
                  $(".template-reporte-diario-render-text").html("<h3>PRUEBAS DIARIAS</h3>");
                  $(".template-reporte-diario-render-text").show( "slow" );
                }
                else {
                  $("#template-reporte-diario-render").html("");
                  $(".template-reporte-diario-render-text").hide( "slow" );

                };

                var semanal = qweb.render("reporte_notas.reporte_notas_semanal_class",{matriz_semanal:  matriz_general[1]});
                if (matriz_general[11]){
                  $("#template-reporte-semanal-render").html(semanal);
                  $(".template-reporte-semanal-render-text").html("<h3>PRUEBAS SEMANAL</h3>");
                }else {
                  $("#template-reporte-semanal-render").html("");
                  $(".template-reporte-semanal-render-text").html("");

                };

                var simulacro = qweb.render("reporte_notas.reporte_notas_simulacro_class",{matriz_simulacro:  matriz_general[2]});
                var situacion = qweb.render("reporte_notas.reporte_notas_situacion_class",{desde:desde,hasta:hasta,situacion:  matriz_general[9]});
                if (matriz_general[12]){
                  $("#template-reporte-simulacro-render").html(simulacro);
                  $(".template-reporte-simulacro-render-text").html("<h3>PRUEBAS SIMULACRO</h3>");
                  $("#template-reporte-situacion-render").html(situacion);
                $('#bar-chart').replaceWith($('<canvas id="bar-chart" width="800" height="450"></canvas>'));
                new Chart(document.getElementById("bar-chart"), {
                  type: 'bar',
                  data: {
                    labels:   matriz_general[3],
                    datasets: [{
                      label: "FASE 1",
                       backgroundColor: "#F7DA0D",
                      data: matriz_general[4],
                    },
                    {
                      label: "FASE 2",
                       backgroundColor: "#9B59B6",
                      data: matriz_general[5],
                    },
                    {
                      label: "FASE 3",
                       backgroundColor: "#F83C1B",
                      data: matriz_general[6],
                    },
                    {
                      label: "FASE 4",
                       backgroundColor: "#077EFC",
                      data: matriz_general[7],
                    },
                    {
                      label: "TOTAL",
                       backgroundColor: "#46C40B",
                      data: matriz_general[8],
                    },
                  ]
                  },
                  options: {
                    legend: {
                        position: "top"
                      },
                    title: {
                      display: true,
                      text: 'PUNTAJE SIMULACRO'
                    }
                  }
                });
              }else {
                  $("#template-reporte-simulacro-render").html("");
                  $(".template-reporte-simulacro-render-text").html("");
                  $("#template-reporte-situacion-render").html("");
                  $('#bar-chart').replaceWith($('<canvas id="bar-chart" width="800" height="450"></canvas>'));

                };
             });

        },
    });

    publicWidget.registry.TablaReporteNotasDiario = publicWidget.Widget.extend({
        selector:".search-section-reporte-diario",
        xmlDependencies:["/reporte_notas/static/src/xml/reporte_class_ponde_700.xml"],
        events:{
            'click .wrn-btn-reporte':'click_render_reporte',
            'click #fecha_desde':'click_validate_form',
            'click #fecha_hasta':'click_validate_form',
            'click #aula':'click_validate_form',

        },
        jsLibs: [
          '/web/static/lib/Chart/Chart.js',
        ],
        init:function(){
            this._super.apply(this, arguments);
        },
        start: function(){
          $('#sidebar').toggleClass('active');
        },
        click_validate_form:function(){
                $(".wrn-btn-reporte").attr("disabled",false)
        },
        click_render_reporte:function(){
          $( ".loading-learning ").show( "slow" );
          var desde = $(this.$el).find("input[name='fecha_desde']").val()
          var hasta = $(this.$el).find("input[name='fecha_hasta']").val()
            var aula = $(this.$el).find("select[name='aula']").val()
              $(".wrn-btn-reporte").attr("disabled",true)
             rpc.query({
               model:'reporte.notas.transient',
               method:'funcion_matriz_notas_diario',
               args:[1,desde,hasta,aula],
             }).then(function(matriz_general){
                var diario = qweb.render("reporte_notas.reporte_notas_diario_req_200",{matriz: matriz_general});
                $("#template-reporte-diario-render").html(diario);
                $(".wrn-btn-reporte").attr("disabled",false)
                $( ".loading-learning ").hide( "slow" );

             });

        },
    });

    publicWidget.registry.TablaReporteNotasSemanal = publicWidget.Widget.extend({
        selector:".search-section-reporte-semanal",
        xmlDependencies:["/reporte_notas/static/src/xml/reporte_class_ponde_700.xml"],
        events:{
            'click .wrn-btn-reporte':'click_render_reporte',
            'click #fecha_desde':'click_validate_form',
            'click #fecha_hasta':'click_validate_form',
            'click #aula':'click_validate_form',

        },
        jsLibs: [
          '/web/static/lib/Chart/Chart.js',
        ],
        init:function(){
            this._super.apply(this, arguments);
        },
        start: function(){
          $('#sidebar').toggleClass('active');
        },
        click_validate_form:function(){
                $(".wrn-btn-reporte").attr("disabled",false)
        },
        click_render_reporte:function(){
          $( ".loading-learning ").show( "slow" );
          var desde = $(this.$el).find("input[name='fecha_desde']").val()
          var hasta = $(this.$el).find("input[name='fecha_hasta']").val()
            var aula = $(this.$el).find("select[name='aula']").val()
              $(".wrn-btn-reporte").attr("disabled",true)
             rpc.query({
               model:'reporte.notas.transient',
               method:'funcion_matriz_notas_semanal',
               args:[1,desde,hasta,aula],
             }).then(function(matriz_general){
                var diario = qweb.render("reporte_notas.reporte_notas_semanal_integral_300",{matriz: matriz_general});
                $("#template-reporte-semanal-render").html(diario);
                $(".wrn-btn-reporte").attr("disabled",false)
                $( ".loading-learning ").hide( "slow" );

             });

        },
    });

    publicWidget.registry.TablaReporteNotasSimulacro = publicWidget.Widget.extend({
        selector:".search-section-reporte-simulacro",
        xmlDependencies:["/reporte_notas/static/src/xml/reporte_class_ponde_700.xml"],
        events:{
            'click .wrn-btn-reporte':'click_render_reporte',
            'click #fecha_desde':'click_validate_form',
            'click #fecha_hasta':'click_validate_form',
            'click #aula':'click_validate_form',

        },
        jsLibs: [
          '/web/static/lib/Chart/Chart.js',
          '/reporte_notas/static/src/lib/dist/js/BsMultiSelect.js',
        ],
        init:function(){
            this._super.apply(this, arguments);
        },
        start: function(){
          $('#sidebar').toggleClass('active');
          $('#aula').bsMultiSelect();
          $('#grupo').bsMultiSelect();
        },
        click_validate_form:function(){
                $(".wrn-btn-reporte").attr("disabled",false);
        },
        click_render_reporte:function(){
          $( ".loading-learning ").show( "slow" );
          var fecha = $(this.$el).find("input[name='fecha_desde']").val()
          var aula = $(this.$el).find("select[name='aula']").val()
            var grupo = $(this.$el).find("select[name='grupo']").val()
              $(".wrn-btn-reporte").attr("disabled",true)
             rpc.query({
               model:'reporte.notas.transient',
               method:'funcion_matriz_notas_simulacro',
               args:[1,fecha,aula,grupo],
             }).then(function(matriz_general){
                var diario = qweb.render("reporte_notas.reporte_notas_simulacro_aul_400",{matriz_total_eval: matriz_general[0],matriz_header: matriz_general[1]});
                $("#template-reporte-simulacro-render").html(diario);
                $(".wrn-btn-reporte").attr("disabled",false)
                $( ".loading-learning ").hide( "slow" );

             });

        },
    });


    publicWidget.registry.TablaReporteNotasSimulacroPromedio = publicWidget.Widget.extend({
        selector:".search-section-reporte-simulacro-promedios",
        xmlDependencies:["/reporte_notas/static/src/xml/reporte_class_ponde_700.xml"],
        events:{
            'click .wrn-btn-reporte':'click_render_reporte',
            'click #fecha_desde':'click_validate_form',
            'click #fecha_hasta':'click_validate_form',
            'click #aula':'click_validate_form',

        },
        jsLibs: [
          '/web/static/lib/Chart/Chart.js',
          '/reporte_notas/static/src/lib/dist/js/BsMultiSelect.js',
        ],
        init:function(){
            this._super.apply(this, arguments);
        },
        start: function(){
          $('#sidebar').toggleClass('active');
          $('#aula').bsMultiSelect();
          $('#grupo').bsMultiSelect();

        },
        click_validate_form:function(){
                $(".wrn-btn-reporte").attr("disabled",false)
        },
        click_render_reporte:function(){
          $( ".loading-learning ").show( "slow" );
          var desde = $(this.$el).find("input[name='fecha_desde']").val()
          var hasta = $(this.$el).find("input[name='fecha_hasta']").val()
          var aula = $(this.$el).find("select[name='aula']").val()
            var grupo = $(this.$el).find("select[name='grupo']").val()
              $(".wrn-btn-reporte").attr("disabled",true)
             rpc.query({
               model:'reporte.notas.transient',
               method:'funcion_matriz_notas_simulacro_promedios',
               args:[1,desde,hasta,aula,grupo],
             }).then(function(matriz_general){
                var diario = qweb.render("reporte_notas.reporte_notas_simulacro_prom_500",{matriz_total: matriz_general});
                $("#template-reporte-simulacro-render").html(diario);
                $(".wrn-btn-reporte").attr("disabled",false)
                $( ".loading-learning ").hide( "slow" );

             });

        },
    });

    publicWidget.registry.TablaReporteNotasSimulacroPonderado = publicWidget.Widget.extend({
        selector:".search-section-reporte-simulacro-ponderados",
        xmlDependencies:["/reporte_notas/static/src/xml/reporte_class_ponde_700.xml"],
        events:{
            'click .wrn-btn-reporte':'click_render_reporte',
            'click #fecha_desde':'click_validate_form',
            'click #fecha_hasta':'click_validate_form',
            'click #aula':'click_validate_form',

        },
        jsLibs: [
          '/web/static/lib/Chart/Chart.js',
            '/reporte_notas/static/src/lib/dist/js/BsMultiSelect.js',
        ],
        init:function(){
            this._super.apply(this, arguments);
        },
        start: function(){
          $('#sidebar').toggleClass('active');
          $('#aula').bsMultiSelect();
          $('#grupo').bsMultiSelect();
        },
        click_validate_form:function(){
                $(".wrn-btn-reporte").attr("disabled",false)
        },
        click_render_reporte:function(){
          var desde = $(this.$el).find("input[name='fecha_desde']").val()
          var hasta = $(this.$el).find("input[name='fecha_hasta']").val()
          var aula = $(this.$el).find("select[name='aula']").val()
            var grupo = $(this.$el).find("select[name='grupo']").val()
              $(".wrn-btn-reporte").attr("disabled",true);
              $( ".loading-learning ").show( "slow" );
             rpc.query({
               model:'reporte.notas.transient',
               method:'funcion_matriz_notas_simulacro_ponderados',
               args:[1,desde,hasta,aula,grupo],
             }).then(function(matriz_general){
                var diario = qweb.render("reporte_notas.reporte_notas_simulacro_ponde_600",{matriz_total: matriz_general, desde:desde,hasta:hasta,aula:aula});
                $("#template-reporte-simulacro-render").html(diario);
                $(".wrn-btn-reporte").attr("disabled",false)
                $( ".loading-learning ").hide( "slow" );
             });

        },
    });


})
