import { endpoint } from 'config';

import createFetchAction from 'action/createFetchAction';

const url = endpoint('county-dashboard');

export default createFetchAction({
    failType: 'COUNTY_DASHBOARD_REFRESH_FAIL',
    networkFailType: 'COUNTY_DASHBOARD_REFRESH_NETWORK_FAIL',
    okType: 'COUNTY_DASHBOARD_REFRESH_OK',
    sendType: 'COUNTY_DASHBOARD_REFRESH_SEND',
    url,
});
