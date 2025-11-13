/** @odoo-module **/

import { registry } from "@web/core/registry";
import { kanbanView } from '@web/views/kanban/kanban_view';
import { ShipmentTrackingKanbanController } from './shipment_tracking_kanban_controller';

export const shipmentTrackingKanbanView = {
    ...kanbanView,
    Controller: ShipmentTrackingKanbanController,
};

registry.category("views").add("shipment_tracking_kanban_with_sidebar", shipmentTrackingKanbanView);
