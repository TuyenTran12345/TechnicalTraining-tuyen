/** @odoo-module **/

import { Component } from "@odoo/owl";
import { DatePicker } from '@web/core/datepicker/datepicker';
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { Domain } from "@web/core/domain";
import { TagsList } from "@web/views/fields/many2many_tags/tags_list";
import { Many2XAutocomplete } from "@web/views/fields/relational_utils";
import { useService } from "@web/core/utils/hooks";

const { DateTime } = luxon;

export class AccountReportFilter extends Component {
	setup() {
		this.displayPartners = {};
		this.displayAnalyticAccounts = {};
		this.displayJournals = {};
        this.orm = useService('orm');
	}

	async updatePartner(records) {
        for (const record of records.filter((record) => record.name)) {
            this.displayPartners[record.id] = record.name;
            this.props.filterOptions.partner_ids.push(record.id);
        }
        let unnameRecordsIds = records.filter((record) => !record.name).map((record) => record.id);
        if (unnameRecordsIds.length) {
            let recordsData = await this.orm.call('res.partner', 'read', [unnameRecordsIds, ['name']]);
            for (const record of recordsData) {
                this.displayPartners[record.id] = record.name;
                this.props.filterOptions.partner_ids.push(record.id);
            }
        }
        this.props.updateMany2X();
    }

    async updateAnalyticAccount(records) {
        for (const record of records.filter((record) => record.name)) {
            this.displayAnalyticAccounts[record.id] = record.name;
            this.props.filterOptions.analytic_account_ids.push(record.id);
        }
        let unnameRecordsIds = records.filter((record) => !record.name).map((record) => record.id);
        if (unnameRecordsIds.length) {
            let recordsData = await this.orm.call('account.analytic.account', 'read', [unnameRecordsIds, ['name']]);
            for (const record of recordsData) {
                this.displayAnalyticAccounts[record.id] = record.name;
                this.props.filterOptions.analytic_account_ids.push(record.id);
            }
        }
        this.props.updateMany2X();
    }

    async updateJournal(records) {
        for (const record of records.filter((record) => record.id)) {
            let displayNames
            if (record.name) {
                displayNames = record.name;
            } else {
                const nameGet = await this.orm.nameGet('account.journal', [record.id]);
                displayNames = nameGet[0][1]
            }
            this.displayJournals[record.id] = displayNames;
            this.props.filterOptions.journal_ids.push(record.id);
        }
        this.props.updateMany2X();
    }

    searchPartnerDomain() {
        return Domain.not([["id", "in", this.props.filterOptions.partner_ids]]).toList();
    }

    searchAnalyticAccountDomain() {
        return Domain.not([["id", "in", this.props.filterOptions.analytic_account_ids]]).toList();
    }

    searchJournalDomain() {
        return Domain.not([["id", "in", this.props.filterOptions.journal_ids]]).toList();
    }

    removePartner(partnerId) {
        delete this.displayPartners[partnerId];
        this.props.filterOptions.partner_ids = this.props.filterOptions.partner_ids.filter((id) => id != partnerId);
        this.props.updateMany2X();
    }

    removeAnalyticAccount(accountId) {
        delete this.displayAnalyticAccounts[accountId];
        this.props.filterOptions.analytic_account_ids = this.props.filterOptions.analytic_account_ids.filter((id) => id != accountId);
        this.props.updateMany2X();
    }

    removeJournal(journalId) {
        delete this.displayJournals[journalId];
        this.props.filterOptions.journal_ids = this.props.filterOptions.journal_ids.filter((id) => id != journalId);
        this.props.updateMany2X();
    }

	//---- Getters ----

	get parnerTags() {		 
		return this.props.filterOptions.partner_ids.map((id) => ({
            text: this.displayPartners[id],
            onDelete: () => this.removePartner(id),
            displayBadge: true,
        }));
    }

    get analyticAccountTags() {		 
		return this.props.filterOptions.analytic_account_ids.map((id) => ({
            text: this.displayAnalyticAccounts[id],
            onDelete: () => this.removeAnalyticAccount(id),
            displayBadge: true,
        }));
    }

    get journalTags() {		 
		return this.props.filterOptions.journal_ids.map((id) => ({
            text: this.displayJournals[id],
            onDelete: () => this.removeJournal(id),
            displayBadge: true,
        }));
    }

	get displayableAccountType() {
		return Object.keys(this.props.filterOptions.display_account_type);
	}

	get currentAccountTypeNames() {
        return this.displayableAccountType.filter(key => 
        	this.props.filterOptions.account_type[key]).map(key => 
        		this.props.filterOptions.display_account_type[key]).join(", ");
    }

    get customStartDate() {
		if (this.props.filterOptions.date_range.find(d => d.key == 'custom').date_from)			
			return DateTime.fromISO(this.props.filterOptions.date_range.find(d => d.key == 'custom').date_from);
		return
	}

	get customEndDate() {
		if (this.props.filterOptions.date_range.find(d => d.key == 'custom').date_to)			
			return DateTime.fromISO(this.props.filterOptions.date_range.find(d => d.key == 'custom').date_to);
		return
	}

	get comparisonStartDate() {
		if (this.props.filterOptions.comparisons.find(d => d.key == 'custom').date_from)			
			return DateTime.fromISO(this.props.filterOptions.comparisons.find(d => d.key == 'custom').date_from);
		return
	}

	get comparisonEndDate() {
		if (this.props.filterOptions.comparisons.find(d => d.key == 'custom').date_to)			
			return DateTime.fromISO(this.props.filterOptions.comparisons.find(d => d.key == 'custom').date_to);
		return
	}

}

AccountReportFilter.template = "to_account_reports.AccountReportFilter";
AccountReportFilter.components = { Dropdown, DropdownItem, TagsList, Many2XAutocomplete, DatePicker };
