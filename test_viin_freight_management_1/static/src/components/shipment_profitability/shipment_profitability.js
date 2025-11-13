/** @odoo-module **/

import { Component } from "@odoo/owl";
import { formatMonetary } from "@web/views/fields/formatters";

export class ShipmentProfitability extends Component {

    get totalRevenue() {
        const { data } = this.props.data.revenues;
        return {
            billed: data.reduce((acc, line) => acc + line.billed_amount, 0),
            to_bill: data.reduce((acc, line) => acc + line.to_bill_amount, 0),
            expected: data.reduce((acc, line) => acc + line.amount, 0),
        };
    }

    get totalCosts() {
        const { data } = this.props.data.costs;
        return {
            billed: data.reduce((acc, line) => acc + line.billed_amount, 0),
            to_bill: data.reduce((acc, line) => acc + line.to_bill_amount, 0),
            expected: data.reduce((acc, line) => acc + line.amount, 0),
        };
    }

    get profit() {
        return this.totalRevenue.expected - this.totalCosts.expected;
    }

    format(amount) {
        return formatMonetary(amount, { currencyId: this.props.currencyId });
    }

}

ShipmentProfitability.template = 'viin_freight_management.ShipmentProfitability';
ShipmentProfitability.props = {
    data: { type: Object },
    currencyId: { type: Number },
};
