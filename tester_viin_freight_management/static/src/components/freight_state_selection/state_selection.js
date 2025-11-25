/** @odoo-module */

import { registry } from "@web/core/registry";
import {
    StateSelectionField,
    stateSelectionField,
} from "@web/views/fields/state_selection/state_selection_field";

export class FreightSelectionField extends StateSelectionField {
    setup() {
        super.setup();
        const colors = this.colors;
        colors["to_define"] = "gray";
        colors["on_track"] = "green";
        colors["at_risk"] = "orange";
        colors["off_track"] = "red";
        colors["on_hold"] = "blue";
        this.colors = colors;
    }
}

export const freightStateSelectionField = {
    ...stateSelectionField,
    component: FreightSelectionField,
};
registry.category("fields").add("freight_state_selection", freightStateSelectionField);
