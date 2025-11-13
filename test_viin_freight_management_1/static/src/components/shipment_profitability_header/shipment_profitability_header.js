/** @odoo-module **/

import { Component } from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";

export class ShipmentProfitabilityHeader extends Component {
    setup() {
        this.openRecord = (resModel, resId) => {
            this.props.openRecord({
                resModel,
                resId,
            });
        };
    }
}

ShipmentProfitabilityHeader.template = 'viin_freight_management.ShipmentProfitabilityHeader';
ShipmentProfitabilityHeader.props = {
    data: { type: Object },
    openRecord: { type: Function },
    openSaleOrderLines: { type: Function, optional: true },
    openBookings: { type: Function, optional: true },
};
ShipmentProfitabilityHeader.components = { Dropdown, DropdownItem };
