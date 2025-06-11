react-native;","
import DeviceInfo from "react-native-device-info"
import React from "react";
interface ApiResponse<T = any  /> {/data: T;/     , success: boolean;
}
  message?: string}
code?: number}
export interface DeviceCapabilities {camera: boolean}microphone: boolean,;
location: boolean,
biometrics: boolean,
nfc: boolean,
}
}
  const bluetooth = boolean}
}
export interface DeviceSpecs {deviceId: string}brand: string,;
model: string,
systemName: string,
systemVersion: string,buildNumber: string,bundleId: string,
totalMemory: number,
usedMemory: number,
totalDiskCapacity: number,
freeDiskStorage: number,
batteryLevel: number,
screenWidth: number,
screenHeight: number,
pixelRatio: number,
fontScale: number,
carrier: string,
ipAddress: string,
macAddress: string,
capabilities: DeviceCapabilities,
isEmulator: boolean,
isTablet: boolean,
hasNotch: boolean,
}
}
  const supportedAbis = string[]}
}
export interface PerformanceMetrics {;
appStartTime: number,
}
  memoryUsage: {used: number,total: number,percentage: number}
};
cpuUsage: number,
batteryDrain: number,
networkLatency: number,
const renderTime = number}
class DeviceInfoManager {private startTime: number = Date.now()private performanceMetrics: PerformanceMetrics[] = [];
  ///    > {"/;}}"/g"/;
}
    try {"}
const { width, height   } = Dimensions.get("window";);;
const: deviceSpecs: DeviceSpecs = {deviceId: await DeviceInfo.getUniqueId()}brand: await DeviceInfo.getBrand(),
model: await DeviceInfo.getModel(),
systemName: DeviceInfo.getSystemName(),
systemVersion: DeviceInfo.getSystemVersion(),
buildNumber: await DeviceInfo.getBuildNumber(),
bundleId: DeviceInfo.getBundleId(),
totalMemory: await DeviceInfo.getTotalMemory(),
usedMemory: await DeviceInfo.getUsedMemory(),
totalDiskCapacity: await DeviceInfo.getTotalDiskCapacity(),
freeDiskStorage: await DeviceInfo.getFreeDiskStorage(),
batteryLevel: await DeviceInfo.getBatteryLevel(),
screenWidth: width,
screenHeight: height,
pixelRatio: PixelRatio.get(),
fontScale: PixelRatio.getFontScale(),
carrier: await DeviceInfo.getCarrier(),
ipAddress: await DeviceInfo.getIpAddress(),
macAddress: await DeviceInfo.getMacAddress(),
capabilities: await this.getDeviceCapabilities(),
isEmulator: await DeviceInfo.isEmulator(),
isTablet: DeviceInfo.isTablet(),
}
        hasNotch: DeviceInfo.hasNotch(),}
        const supportedAbis = await DeviceInfo.supportedAbis();};
return deviceSpe;c;s;
    } catch (error) {}
      const throw = error}
    }
  }
  ///    > {/try {"return {camera: ";}          (await DeviceInfo.hasSystemFeature("android.hardware.came;r;a;";)) ||","/g"/;
Platform.OS === 'ios','
const microphone = 
          (await DeviceInfo.hasSystemFeature("android.hardware.microphone";);) ||","
Platform.OS === 'ios','
const location = 
          (await DeviceInfo.hasSystemFeature("android.hardware.location";);) ||","
Platform.OS === 'ios','';
const biometrics = await DeviceInfo.supportedAbis();
          .then(); => true);
          .catch() => false),'
const nfc = 
          (await DeviceInfo.hasSystemFeature("android.hardware.nfc;";)) || false,","
const bluetooth = 
          (await DeviceInfo.hasSystemFeature("android.hardware.bluetooth;";)) ||";
}
          Platform.OS === "ios"};
      }
    } catch (error) {";}  // 性能监控"/;"/g"/;
}
const: performanceMonitor = usePerformanceMonitor('deviceInfo', {trackRender: true,)'}'';
trackMemory: false,warnThreshold: 100, // ms ;};);
return {camera: false,microphone: false,location: false,biometrics: false,nfc: false,bluetooth: fals;e;
    }
  }
  ///    > {/try {const totalMemory = await DeviceInfo.getTotalMemo;r;yconst usedMemory = await DeviceInfo.getUsedMemo;r;y,/g/;
const batteryLevel = await DeviceInfo.getBatteryLev;e;l;
const metrics: PerformanceMetrics = {appStartTime: Date.now(); - this.startTime}memoryUsage: {used: usedMemory,
}
          total: totalMemory,}
          percentage: (usedMemory / totalMemory) * 100,/            ;},/,/g,/;
  cpuUsage: await this.getCpuUsage(),
batteryDrain: await this.getBatteryDrain(),
networkLatency: await this.getNetworkLatency(),
const renderTime = await this.getRenderTime(;);};
this.performanceMetrics.push(metrics);
return metri;c;s;
    } catch (error) {}
      const throw = error}
    }
  }
  // 获取CPU使用率 (模拟实现)  private async getCpuUsage(): Promise<number> {}
    / 这里提供一个模拟实现* ///     };
  // 获取电池消耗率  private async getBatteryDrain(): Promise<number> {/try {const currentLevel = await DeviceInfo.getBatteryLev;e;l;}}/g/;
      return Math.max(0, 1 - currentLevel;)}
    } catch (error) {}
      return 0}
    }
  }
  // 测试网络延迟  private async getNetworkLatency(): Promise<number> {/try {'const startTime = Date.now;(;);/g'/;
}
      const await = fetch("https: return Date.now - startTime;)"
    } catch (error) {}
      return -;1;  }
  }
  // 获取渲染时间 (模拟实现)  private async getRenderTime(): Promise<number> {/return Math.random * 16  / 模拟16ms以内的渲染时间* ///;
}
  // 检查设备兼容性  async checkCompatibility(): Promise<{ compatible: boolean,issues: string[],recommendations: string[];}
    }> {const deviceSpecs = await this.getDeviceSpe;c;sconst issues: string[] = [];","
const recommendations: string[] = [];","
if (Platform.OS === "ios") {"const iosVersion = parseFloat(deviceSpecs.systemVersion;),"";
if (iosVersion < 12.0) {}
}
      }
    } else if (Platform.OS === "android") {"const androidVersion = parseInt(deviceSpecs.systemVersio;n;),"";
if (androidVersion < 21) {issues.push()}
        )}
      }
    }
    const memoryGB = deviceSpecs.totalMemory  / (1024  1024  1024;)/     if (memoryGB < 2) {/;}}/g/;
}
    }
    const freeStorageGB = deviceSpecs.freeDiskStorage  / (1024  1024  1024;)/     if (freeStorageGB < 1) {/;}}/g/;
}
    }
    if (!deviceSpecs.capabilities.camera) {}
}
    }
    if (!deviceSpecs.capabilities.microphone) {}
}
    }
    return {compatible: issues.length === 0,issues,recommendation;s;};
  }
  // 生成设备报告  async generateDeviceReport(): Promise<string> {/const deviceSpecs = await this.getDeviceSpe;c;s,/g/;
const compatibility = await this.checkCompatibili;t;y;
const performance = await this.getCurrentPerformanceMetri;c;s;(;);
const report = `;`````;```;
}
}
- 内存: ${(deviceSpecs.totalMemory / (1024 * 1024 * 1024)).toFixed(2)}GB/- 存储: ${/;}(deviceSpecs.freeDiskStorage / (1024 * 1024 * 1024)).toFixed(/          2;)
}
      deviceSpecs.pixelRatio}
    }x);
,"
${compatibility.issues.map(issu;e;) => `- ${issue}`).join("\n")}"`;```;
","
${compatibility.recommendations.map(rec) => `- ${rec}`).join("\n")}"`;```;
    `;`````,```;
return report.trim;
  }
  // 获取性能历史数据  getPerformanceHistory(): PerformanceMetrics[] {/;}}/g/;
    return [...this.performanceMetric;s;]}
  }
  // 清除性能历史数据  clearPerformanceHistory(): void {/;}}/g/;
    this.performanceMetrics = []}
  }
}
export const deviceInfoManager = new DeviceInfoManager;","
export default deviceInfoManager;""
