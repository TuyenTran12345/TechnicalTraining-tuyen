/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

export class AccountReportLine extends Component {
	setup() {
		this.action = useService("action");
		this.orm = useService("orm");
	}

	toggleFoldable() {
		if (this.props.line.unfoldable) {
			this.props.line.unfolded = !this.props.line.unfolded;
			if (!this.props.line.details_loaded) {
				this.loadLineDetails();
				this.props.line.details_loaded = true;
			}
	
			for (let line of this.props.lines) {
				if (this.props.line.unfolded) {
					if (line.parent_id === this.props.line.id) {
						line.visible = true;
					}
				}
				else {
					if (line.id != this.props.line.id && line.id.startsWith(this.props.line.id + '|')){
						line.visible = false;
						line.unfolded = false;
					}
				}
			}
		}
	}

	async loadLineDetails() {
		const lineDetails = await this.orm.call(
			"account.report.line",
			"get_expanded_lines",
			[this.props.line, this.props.filterOptions, this.props.reportData.columns]
		);

		if (lineDetails.length > 0)
			this.props.lines.splice(this.props.lineIndex, 0, ...lineDetails);
	}
	
	async clickAuditableColumn(line, columnKey) {
		const action = await this.orm.call(
			"account.report",
			"action_open_auditable",
			[line, columnKey, this.props.filterOptions]
		);
		
		if (action) return this.action.doAction(action);
	}
	
	async openLineAction(line) {
		const action = await this.orm.call(
			"account.report",
			"open_line_action",
			[line, this.props.filterOptions]
		);

		if (action) return this.action.doAction(action);
	}

}

AccountReportLine.template = "to_account_reports.AccountReportLine"
