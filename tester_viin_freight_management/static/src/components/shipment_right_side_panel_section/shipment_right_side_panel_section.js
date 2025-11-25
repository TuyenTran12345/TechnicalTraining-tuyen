/** @odoo-module **/

import { Component } from "@odoo/owl";

export class ShipmentRightSidePanelSection extends Component {}

ShipmentRightSidePanelSection.template = "viin_freight_management.ShipmentRightSidePanelSection";
ShipmentRightSidePanelSection.props = {
    name: { type: String },
    show: { type: Boolean, optional: true },
    slots: {
        type: Object,
        shape: {
            default: true,
            title: { type: Object, optional: true },
        },
    },
};
ShipmentRightSidePanelSection.defaultProps = {
    show: true,
};
