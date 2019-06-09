import { endpoint } from 'config';

import createFetchAction from 'action/createFetchAction';

const url = endpoint('dos-dashboard');

export default createFetchAction({
    failType: 'DOS_DASHBOARD_REFRESH_FAIL',
    networkFailType: 'DOS_DASHBOARD_REFRESH_NETWORK_FAIL',
    okType: 'DOS_DASHBOARD_REFRESH_OK',
    sendType: 'DOS_DASHBOARD_REFRESH_SEND',
    url,
});
