/** @odoo-module */

import { registry } from '@web/core/registry';
import { StateSelectionField } from '@web/views/fields/state_selection/state_selection_field';


export class FreightSelectionField extends StateSelectionField {
    setup() {
        super.setup();
        let colors = this.colors;
        colors['to_define'] = 'gray';
        colors['on_track'] = 'green';
        colors['at_risk'] = 'orange';
        colors['off_track'] = 'red';
        colors['on_hold'] = 'blue';
        this.colors = colors;
    }
}

registry.category('fields').add('freight_state_selection', FreightSelectionField);
