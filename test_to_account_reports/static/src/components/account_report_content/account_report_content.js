/** @odoo-module **/

import { Component } from "@odoo/owl";
import { AccountReportLine } from "../account_report_line/account_report_line";

export class AccountReportContent extends Component {}

AccountReportContent.template = "to_account_reports.AccountReportContent";
AccountReportContent.components = { AccountReportLine }
