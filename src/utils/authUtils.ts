import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';
import DeviceInfo from 'react-native-device-info';
// 存储键常量
const STORAGE_KEYS = {
      AUTH_TOKEN: "@suoke_life:auth_token",
      REFRESH_TOKEN: '@suoke_life:refresh_token',USER_ID: '@suoke_life:user_id',DEVICE_ID: '@suoke_life:device_id';
};
/**
* 存储认证令牌
*/
export const storeAuthTokens = async (;)
  accessToken: string,
  refreshToken: string;
): Promise<void> => {
  try {
    await AsyncStorage.multiSet([)
      [STORAGE_KEYS.AUTH_TOKEN, accessToken],
      [STORAGE_KEYS.REFRESH_TOKEN, refreshToken]
    ]);
  } catch (error) {
    console.error('存储认证令牌失败:', error);
    throw new Error('存储认证令牌失败');
  }
};
/**
* 获取访问令牌
*/
export const getAuthToken = async (): Promise<string | null> => {try {return await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
  } catch (error) {
    console.error('获取访问令牌失败:', error);
    return null;
  }
};
/**
* 获取刷新令牌
*/
export const getRefreshToken = async (): Promise<string | null> => {try {return await AsyncStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
  } catch (error) {
    console.error('获取刷新令牌失败:', error);
    return null;
  }
};
/**
* 清除所有认证信息
*/
export const clearAuthTokens = async (): Promise<void> => {try {await AsyncStorage.multiRemove([;)
      STORAGE_KEYS.AUTH_TOKEN,STORAGE_KEYS.REFRESH_TOKEN,STORAGE_KEYS.USER_ID;
    ]);
  } catch (error) {
    console.error('清除认证信息失败:', error);
    throw new Error('清除认证信息失败');
  }
};
/**
* 存储用户ID;
*/
export const storeUserId = async (userId: string): Promise<void> => {try {await AsyncStorage.setItem(STORAGE_KEYS.USER_ID, userId);
  } catch (error) {
    console.error('存储用户ID失败:', error);
    throw new Error('存储用户ID失败');
  }
};
/**
* 获取用户ID;
*/
export const getUserId = async (): Promise<string | null> => {try {return await AsyncStorage.getItem(STORAGE_KEYS.USER_ID);
  } catch (error) {
    console.error('获取用户ID失败:', error);
    return null;
  }
};
/**
* 获取或生成设备ID;
*/
export const getDeviceId = async (): Promise<string> => {try {// 先尝试从存储中获取;
    let deviceId = await AsyncStorage.getItem(STORAGE_KEYS.DEVICE_ID);
    if (!deviceId) {
      // 如果没有存储的设备ID，则生成一个新的
      try {
        // 尝试获取设备的唯一标识符
        deviceId = await DeviceInfo.getUniqueId();
      } catch (error) {
        // 如果获取设备ID失败，生成一个随机ID;
        deviceId = generateRandomDeviceId();
      }
      // 存储设备ID;
      await AsyncStorage.setItem(STORAGE_KEYS.DEVICE_ID, deviceId);
    }
    return deviceId;
  } catch (error) {
    console.error('获取设备ID失败:', error);
    // 返回一个临时的设备ID;
    return generateRandomDeviceId();
  }
};
/**
* 生成随机设备ID;
*/
const generateRandomDeviceId = (): string => {const timestamp = Date.now().toString();
  const random = Math.random().toString(36).substring(2);
  const platform = Platform.OS;
  return `${platform}_${timestamp}_${random}`;
};
/**
* 检查是否已登录
*/
export const isLoggedIn = async (): Promise<boolean> => {try {const token = await getAuthToken();
    return !!token;
  } catch (error) {
    return false;
  }
};
/**
* 获取认证头
*/
export const getAuthHeader = async (): Promise<{ Authorization: string } | {}> => {try {const token = await getAuthToken();
    if (token) {
      return { Authorization: `Bearer ${token}` };
    }
    return {};
  } catch (error) {
    return {};
  }
};
/**
* 验证令牌是否过期（简单检查）
*/
export const isTokenExpired = (token: string): boolean => {try {// 解析JWT令牌的payload部分;
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    // 检查是否过期
    return payload.exp < currentTime;
  } catch (error) {
    // 如果解析失败，认为令牌无效
    return true;
  }
};
/**
* 从令牌中提取用户信息
*/
export const getUserInfoFromToken = (token: string): any => {try {const payload = JSON.parse(atob(token.split('.')[1]));
    return {userId: payload.sub,username: payload.username,email: payload.email,exp: payload.exp,iat: payload.iat;
    };
  } catch (error) {
    console.error('解析令牌失败:', error);
    return null;
  }
};