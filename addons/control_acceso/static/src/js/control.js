odoo.define('control_acceso.hide_action_form_optn', function(require) {
  "use strict";
  console.log('hide_acceso')
  var FormController = require('web.FormController');
  var ListController = require('web.ListController');
  var BasicView = require('web.BasicView');
  var session = require('web.session');
  var core = require('web.core');
  var _t = core._t;

  BasicView.include({

     init: function(viewInfo, params) {
      var self = this;
      this._super.apply(this, arguments)
      session.user_has_group('elearning_aprentech.group_control_acceso_superadmin').then(function(has_group){
        if(has_group){
          console.log('group_control_acceso_superadmin')
          self.controllerParams.archiveEnabled = 'active' in viewInfo.fields
          self.controllerParams.importEnabled = 'active' in viewInfo.fields
          self.controllerParams.activeActions.edit = true
          self.controllerParams.activeActions.create = true
          self.controllerParams.activeActions.export_xlsx = true
          self.controllerParams.activeActions.delete = true
        }else{
          console.log('not has_group')
        }

      })

      session.user_has_group('elearning_aprentech.group_control_acceso_admin').then(function(has_group){
        if(has_group){
          console.log('group_control_acceso_admin')
          self.controllerParams.archiveEnabled = 'active' in viewInfo.fields
          self.controllerParams.importEnabled = 'active' in viewInfo.fields
          self.controllerParams.activeActions.edit = true
          self.controllerParams.activeActions.create = true
          self.controllerParams.activeActions.export_xlsx = false
          self.controllerParams.activeActions.delete = true
        }else{
          console.log('not has_group')
        }

      })

      session.user_has_group('elearning_aprentech.group_control_acceso_editor').then(function(has_group){
        if(has_group){
          let modelos = ["slide.channel","res.users","mail.channel"]
          console.log('group_control_acceso_editor')
          self.controllerParams.archiveEnabled = 'False' in viewInfo.fields
          self.controllerParams.importEnabled = 'active' in viewInfo.fields
          self.controllerParams.activeActions.edit = true
          self.controllerParams.activeActions.create = true
          self.controllerParams.activeActions.export_xlsx = false
          self.controllerParams.activeActions.delete = true
          if(modelos.indexOf(self.controllerParams.modelName) > -1){
             self.controllerParams.activeActions.delete = false
          }
        }else{
          console.log('not has_group observador')
        }

      })

      session.user_has_group('elearning_aprentech.group_control_acceso_observador').then(function(has_group){
        if(has_group){
          console.log('group_control_acceso_observador')
          self.controllerParams.archiveEnabled = 'False' in viewInfo.fields
          self.controllerParams.importEnabled = 'False' in viewInfo.fields
          self.controllerParams.activeActions.edit = false
          self.controllerParams.activeActions.create = false
          self.controllerParams.activeActions.export_xlsx = false
          self.controllerParams.activeActions.delete = false
          self.controllerParams.hasSidebar = false
          self.controllerParams.hasButtons = false
        }else{
          console.log('not has_group observador')
        }

      })

  }
})

})
