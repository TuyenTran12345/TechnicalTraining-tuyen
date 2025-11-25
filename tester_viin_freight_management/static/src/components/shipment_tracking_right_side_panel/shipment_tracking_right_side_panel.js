/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { ShipmentProfitabilityHeader } from "@viin_freight_management/components/shipment_profitability_header/shipment_profitability_header";
import { ShipmentProfitability } from "@viin_freight_management/components/shipment_profitability/shipment_profitability";
import { ShipmentRightSidePanelSection } from "@viin_freight_management/components/shipment_right_side_panel_section/shipment_right_side_panel_section";
import { ShipmentOnBehalf } from "@viin_freight_management/components/shipment_on_behalf/shipment_on_behalf";
import { Component, onWillStart, useState } from "@odoo/owl";

export class ShipmentTrackingRightSidePanel extends Component {
    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.state = useState({
            panelData: {},
            isLoading: true,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    get shipmentId() {
        return this.props.context.active_id;
    }

    async loadData() {
        if (!this.shipmentId) {
            this.state.isLoading = false;
            return;
        }
        this.state.isLoading = true;
        const data = await this.orm.call("freight.shipment", "get_panel_data", [this.shipmentId]);
        if (data) {
            this.state.panelData = data;
        }
        this.state.isLoading = false;
    }

    openRecord(params) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: params.resModel,
            res_id: params.resId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openSaleOrderLines() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Sale Order Items",
            res_model: "sale.order.line",
            domain: [["id", "in", this.state.panelData.sale_order_line_ids]],
            views: [
                [false, "list"],
                [false, "form"],
            ],
            target: "current",
        });
    }

    openBookings() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Bookings",
            res_model: "freight.booking",
            domain: [["id", "in", this.state.panelData.booking_ids]],
            views: [
                [false, "list"],
                [false, "form"],
            ],
            target: "current",
        });
    }
}

ShipmentTrackingRightSidePanel.template = "viin_freight_management.ShipmentTrackingRightSidePanel";
ShipmentTrackingRightSidePanel.components = {
    ShipmentProfitabilityHeader,
    ShipmentProfitability,
    ShipmentRightSidePanelSection,
    ShipmentOnBehalf,
};
ShipmentTrackingRightSidePanel.props = {
    context: Object,
    domain: Object,
};
