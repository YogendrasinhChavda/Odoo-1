odoo.define('skit_freeze_header.header', function (require) {
"use strict";

	var ListRenderers = require('web.ListRenderer');
	
	var config = require('web.config');
	var core = require('web.core');
	var Dialog = require('web.Dialog');
	var dom = require('web.dom');
	var field_utils = require('web.field_utils');
	var Pager = require('web.Pager');
	var utils = require('web.utils');

	var _t = core._t;
	
	var web_client = require('web.web_client');
	
	
	ListRenderers.include({
		
		/*******Start code for _renderHeader********/
		_renderHeader: function (isGrouped) {
			var $thead = this._super.call(this,isGrouped);
			var $tr = $thead.find("tr");
			if(this.addTrashIcon){
				$tr.append("<th class='o_list_record_delete'>"  + "</th>");
			}
			return $thead;
	    },
	    /*******End code for _renderHeader********/
	    
	    
	    /*********Start code for _renderFooter********/
	    _renderFooter: function (isGrouped) {
	    	var $tfoot = this._super.call(this,isGrouped);
	 		var $tr = $tfoot.find("tr");
	 		if(this.addTrashIcon){
	 			$tr.append('<td></td>');
	 		}
	 		return $tfoot;
  		},
	    /*********End code for _renderFooter********/
  		

	    /*********Start code for _renderBody********/
	  	 _renderBody: function () {
	     	this._super(); 
	  		var self = this;
	     	var $rows = this._renderRows();
	        while ($rows.length < 9) {
	            $rows.push(this._renderEmptyRow());
	        }
	        var $body = $('<tbody>').append($rows);
	     	if (this.hasHandle) {
	            $body.sortable({
	                axis: 'y',
	                items: '> tr.o_data_row',
	                helper: 'clone',
	                handle: '.o_row_handle',
	                stop: this._resequence.bind(this),
	            });
	        }
	        return $body
	     },
	    /*********End code for _renderBody********/


	});
});
