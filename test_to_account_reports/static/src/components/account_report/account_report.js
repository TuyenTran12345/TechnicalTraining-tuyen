/** @odoo-module **/

import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { session } from "@web/session";
import { useService } from "@web/core/utils/hooks";
import { WarningDialog } from "@web/core/errors/error_dialogs";
import { Component, useState, onWillStart  } from "@odoo/owl";
import { AccountReportControlPanel } from "../account_report_control_panel/account_report_control_panel"
import { AccountReportContent } from "../account_report_content/account_report_content";


export class AccountReportComponent extends Component {
	setup() {
		this.orm = useService("orm");
		this.dialog = useService("dialog");
		this.action = useService("action");

		this.reports = [];

		this.state = useState({
			filterOptions: {},
			currentReport: null,
			reportData: {},
		});

		onWillStart(async () => {
			await this.initReports();
			await this.initFilterOptions();
			await this.loadData();
		});
	}

	async initReports() {
		const reportID = this.props.action.context.report_id
		const custom_line_name_template = this.props.action.context.custom_line_name_template
		const results = await this.orm.call(
			"account.report",
			"init_report_data",
			[reportID, custom_line_name_template],
		);

		this.reports = results["reports"];
		this.state.currentReport = results["current_report"];
	}

	async initFilterOptions() {
		const filterOptionsParam = this.props.action.params.filterOptions;
		if (filterOptionsParam) {
			this.state.filterOptions = await this.orm.call(
				"account.report",
				"init_filter_options",
				[this.state.currentReport.id, filterOptionsParam],
			);
			this.props.action.params.filterOptions = null;
		}
		else {
			const filterOptionsSession = this.getFilterOptionsSession()
			if (JSON.stringify(filterOptionsSession) === "{}" || !filterOptionsSession) {
				this.state.filterOptions = await this.orm.call(
					"account.report",
					"init_filter_options",
					[this.state.currentReport.id],
				);
			}
			else this.state.filterOptions = this.getFilterOptionsSession();
		}
		
		this.updateFilterOptionsSession();
	}
	
	getFilterOptionsSessionID() {
		return `account.report:${ this.state.currentReport.id }:${ session.company_id }:${session.user_context.lang}`;
	}
	
	getFilterOptionsSession() {
		return JSON.parse(browser.sessionStorage.getItem(this.getFilterOptionsSessionID()));
	}
	
	updateFilterOptionsSession() {
		browser.sessionStorage.setItem(this.getFilterOptionsSessionID(), JSON.stringify(this.state.filterOptions));
	}

	async loadData() {
		const reportData = await this.orm.call(
			"account.report",
			"generate_report_data",
			[this.state.currentReport.id, this.state.filterOptions],
		);
		this.state.filterOptions = reportData.filter_options;
		this.state.reportData = reportData;
		this.updateFilterOptionsSession();
	}

	async onChangeReport(reportID) {
		if (this.state.currentReport.id != reportID) {
			this.state.currentReport = this.reports.find(r => r.id == reportID);
			this.state.filterOptions = await this.orm.call(
				"account.report",
				"init_filter_options",
				[this.state.currentReport.id],
			);
			await this.loadData();
		}
	}

	async onChangeAccountType(optionKey) {
        this.state.filterOptions.account_type[optionKey] = !this.state.filterOptions.account_type[optionKey];         
        await this.loadData();
    }

    async onSelectUnpostedEntry() {
        this.state.filterOptions.include_unposted_entry = !this.state.filterOptions.include_unposted_entry;
        await this.loadData();
    }

    async onSelectUnfoldAll() {
        this.state.filterOptions.unfold_all = !this.state.filterOptions.unfold_all;        
    }

    async onChangeDateFilter(dateFilter) {
        if (this.state.filterOptions.current_date.key != dateFilter) {
            this.state.filterOptions.current_date = this.state.filterOptions.date_range.find(d => d.key == dateFilter);
            await this.loadData();
        }
    }

    async onSelectComparison(comparisonFilter) {
		if (this.state.filterOptions.current_comparison.key != comparisonFilter) {
			this.state.filterOptions.current_comparison = this.state.filterOptions.comparisons.find(c => c.key == comparisonFilter);
			await this.loadData();
		}
	}

	async onUpdateMany2X() {
		await this.loadData();
	}

	async onChangeCustomStartDate(date) {
		this.state.filterOptions.date_range.find(d => d.key == 'custom').date_from = date;
	}

	async onChangeCustomEndDate(date) {
		this.state.filterOptions.date_range.find(d => d.key == 'custom').date_to = date;
	}

	async onApplyCustomDate() {
		const currentDate = this.state.filterOptions.date_range.find(d => d.key == 'custom');
		let warningMessage = '';
		if (this.state.filterOptions.use_filter_date_range){
			if (!currentDate.date_from)
					warningMessage = this.env._t("Start Date cannot be empty")
			else if (!currentDate.date_to)
				warningMessage = this.env._t("End Date cannot be empty")
		}
		else if (!currentDate.date_to)
			warningMessage = this.env._t("End Date cannot be empty");

		if (warningMessage) {
			this.dialog.add(WarningDialog, {
                title: this.env._t("Warning"),
                message: warningMessage,
            });
		}
		else {
			this.state.filterOptions.current_date = currentDate;
			await this.loadData();
		}
	}

	async onChangeComparisonStartDate(date) {
		this.state.filterOptions.comparisons.find(d => d.key == 'custom').date_from = date;
	}

	async onChangeComparisonEndDate(date) {
		this.state.filterOptions.comparisons.find(d => d.key == 'custom').date_to = date;
	}

	async onApplyComparisonDate() {
		const currentComparison = this.state.filterOptions.comparisons.find(d => d.key == 'custom');
		let warningMessage = '';
		if (this.state.filterOptions.use_filter_date_range){
			if (!currentComparison.date_from)
					warningMessage = this.env._t("Start Date cannot be empty")
			else if (!currentComparison.date_to)
				warningMessage = this.env._t("End Date cannot be empty")
		}
		else if (!currentComparison.date_to)
			warningMessage = this.env._t("End Date cannot be empty");

		if (warningMessage) {
			this.dialog.add(WarningDialog, {
                title: this.env._t("Warning"),
                message: warningMessage,
            });
		}
		else {
			this.state.filterOptions.current_comparison = currentComparison;
			await this.loadData();
		}
	}

	async onExport(fileType) {
		try {
			const reportBody = this.__owl__.bdom.el.querySelector('.account_report_body');
			const action = await this.orm.call(
				"account.report",
				'action_export_report',
				[this.state.currentReport.id, {
					...this.state.reportData,
					body_html: reportBody.innerHTML,
					report_width: reportBody.querySelector('.account_report_page').clientWidth,
				}, fileType],
			);
			this.action.doAction(action);
		} catch (error) {
			throw new Error(error);
		}
	}
}

AccountReportComponent.template = "to_account_reports.AccountReportComponent";
AccountReportComponent.components = { AccountReportControlPanel, AccountReportContent };

registry.category("actions").add("account_report", AccountReportComponent);
