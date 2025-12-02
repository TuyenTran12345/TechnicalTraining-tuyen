/** @odoo-module **/

import { ControlPanel } from "@web/search/control_panel/control_panel";
import { Component } from "@odoo/owl";
import { AccountReportFilter } from "../account_report_filter/account_report_filter";

export class AccountReportControlPanel extends Component {
	setup() {
		this.controlPanelDisplay = {
			"top-right": false,
		};
		this.env.config.viewSwitcherEntries = [];
	}
}

AccountReportControlPanel.template = "to_account_reports.AccountReportControlPanel";
AccountReportControlPanel.components = { ControlPanel, AccountReportFilter };
