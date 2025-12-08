/** @odoo-module **/

import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { formatMonetary } from "@web/views/fields/formatters";

export class ShipmentOnBehalf extends Component {
    get totalOnBehalf() {
        const { data } = this.props.data;
        return {
            billed: data.reduce((acc, line) => acc + line.billed_amount, 0),
            to_bill: data.reduce((acc, line) => acc + line.to_bill_amount, 0),
            expected: data.reduce((acc, line) => acc + line.amount, 0),
        };
    }

    format(amount) {
        return formatMonetary(amount, { currencyId: this.props.currencyId });
    }

    get remainingAmountTooltip() {
        return _t(
            "Positive (red): Amount still to be collected.\nNegative (blue): Amount over-collected.\nZero (green): Collection is complete."
        );
    }

    getRemainingAmountClass(line) {
        const remaining = line.to_bill_amount;
        const precision =
            this.props.currencyDecimalPlaces === undefined ? 2 : this.props.currencyDecimalPlaces;

        if (remaining > 10 ** -precision) {
            return "text-danger fw-bold";
        } else if (remaining < -(10 ** -precision)) {
            return "text-info fw-bold";
        } else {
            return "text-success fw-bold";
        }
    }
}

ShipmentOnBehalf.template = "viin_freight_management.ShipmentOnBehalf";
ShipmentOnBehalf.props = {
    data: { type: Object },
    currencyId: { type: Number },
    currencyDecimalPlaces: { type: Number, optional: true },
};
