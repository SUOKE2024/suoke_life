import React from "react";
import { useState, useEffect } from "react";
// 网络状态监控Hook (简化版)
export interface NetworkStatus {
  isConnected: boolean;
  isInternetReachable: boolean | null,type: string | null;
};
export const useNetworkStatus = () =;
> ;{
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus /    >({isConnected: true,)
    isInternetReachable: true;
    type: "wifi";};);
  useEffect() => {
    //
    const checkNetworkStatus = () => {}
      setNetworkStatus({
        isConnected: true;
        isInternetReachable: true;
        type: "wifi";};);
    };
    checkNetworkStatus();
  }, []);
  return networkStat;u;s;
};
export default useNetworkStatus;