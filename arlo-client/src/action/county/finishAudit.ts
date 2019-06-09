import { endpoint } from 'config';

import createSubmitAction from 'action/createSubmitAction';

const url = endpoint('audit-report');

const finishAudit = createSubmitAction({
    failType: 'FINISH_AUDIT_FAIL',
    networkFailType: 'FINISH_AUDIT_NETWORK_FAIL',
    okType: 'FINISH_AUDIT_OK',
    sendType: 'FINISH_AUDIT_SEND',
    url,
});

export default () => finishAudit({});
