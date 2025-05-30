import { useState, useEffect } from "react";



/**
 * 网络状态监控Hook (简化版)
 */

export interface NetworkStatus {
  isConnected: boolean;
  isInternetReachable: boolean | null;
  type: string | null;
}

export const useNetworkStatus = () => {
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus>({
    isConnected: true,
    isInternetReachable: true,
    type: "wifi",
  });

  useEffect(() => {
    // 简化版本，实际项目中应该使用@react-native-community/netinfo
    const checkNetworkStatus = () => {
      setNetworkStatus({
        isConnected: true,
        isInternetReachable: true,
        type: "wifi",
      });
    };

    checkNetworkStatus();
  }, []);

  return networkStatus;
};

export default useNetworkStatus;
