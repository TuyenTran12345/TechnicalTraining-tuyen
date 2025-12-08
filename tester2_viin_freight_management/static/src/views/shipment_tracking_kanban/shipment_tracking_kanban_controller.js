/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { ShipmentTrackingRightSidePanel } from "@viin_freight_management/components/shipment_tracking_right_side_panel/shipment_tracking_right_side_panel";

export class ShipmentTrackingKanbanController extends KanbanController {
    get className() {
        return super.className + " o_controller_with_rightpanel";
    }
}

ShipmentTrackingKanbanController.components = {
    ...KanbanController.components,
    ShipmentTrackingRightSidePanel,
};
ShipmentTrackingKanbanController.template = "viin_freight_management.ShipmentTrackingKanbanView";
