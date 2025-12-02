/** @odoo-module */

import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";

async function actionDownloadAccountReport({ env, action }) {
    env.services.ui.block();
    const url = "/to_account_reports";
    const data = action.data;
    const company_id = action.company_id;
    try {
      await download({ url, data, company_id});
    } finally {
      env.services.ui.unblock();
    }
}

registry
    .category("action_handlers")
    .add('ir_actions_af_report_dl', actionDownloadAccountReport);
