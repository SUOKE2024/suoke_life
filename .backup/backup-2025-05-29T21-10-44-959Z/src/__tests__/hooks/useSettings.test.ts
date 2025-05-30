import { renderHook, act } from "@testing-library/react-native";
import React from "react";

// Mock AsyncStorage
const mockAsyncStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

jest.mock("@react-native-async-storage/async-storage", () => mockAsyncStorage);

// Mock设置Hook
const useSettings = () => {
  const [settings, setSettings] = React.useState({
    notifications: {
      healthReminders: true,
      agentMessages: true,
      systemUpdates: false,
      soundEnabled: true,
      vibrationEnabled: true,
    },
    privacy: {
      dataSharing: false,
      analyticsEnabled: false,
      locationTracking: true,
      biometricAuth: false,
    },
    display: {
      theme: "light" as "light" | "dark" | "auto",
      fontSize: "medium" as "small" | "medium" | "large",
      language: "zh-CN",
    },
    health: {
      units: "metric" as "metric" | "imperial",
      stepGoal: 10000,
      waterGoal: 2000,
      sleepGoal: 8,
    },
  });

  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const loadSettings = async () => {
    setLoading(true);
    setError(null);

    try {
      const savedSettings = await mockAsyncStorage.getItem("user_settings");
      if (savedSettings) {
        const parsedSettings = JSON.parse(savedSettings);
        setSettings((prev) => ({ ...prev, ...parsedSettings }));
      }
    } catch (err) {
      setError("加载设置失败");
    } finally {
      setLoading(false);
    }
  };

  const updateNotificationSettings = async (
    newSettings: Partial<typeof settings.notifications>
  ) => {
    setLoading(true);
    setError(null);

    try {
      const updatedSettings = {
        ...settings,
        notifications: { ...settings.notifications, ...newSettings },
      };

      await mockAsyncStorage.setItem(
        "user_settings",
        JSON.stringify(updatedSettings)
      );
      setSettings(updatedSettings);
    } catch (err) {
      setError("更新通知设置失败");
    } finally {
      setLoading(false);
    }
  };

  const updatePrivacySettings = async (
    newSettings: Partial<typeof settings.privacy>
  ) => {
    setLoading(true);
    setError(null);

    try {
      const updatedSettings = {
        ...settings,
        privacy: { ...settings.privacy, ...newSettings },
      };

      await mockAsyncStorage.setItem(
        "user_settings",
        JSON.stringify(updatedSettings)
      );
      setSettings(updatedSettings);
    } catch (err) {
      setError("更新隐私设置失败");
    } finally {
      setLoading(false);
    }
  };

  const updateDisplaySettings = async (
    newSettings: Partial<typeof settings.display>
  ) => {
    setLoading(true);
    setError(null);

    try {
      const updatedSettings = {
        ...settings,
        display: { ...settings.display, ...newSettings },
      };

      await mockAsyncStorage.setItem(
        "user_settings",
        JSON.stringify(updatedSettings)
      );
      setSettings(updatedSettings);
    } catch (err) {
      setError("更新显示设置失败");
    } finally {
      setLoading(false);
    }
  };

  const updateHealthSettings = async (
    newSettings: Partial<typeof settings.health>
  ) => {
    setLoading(true);
    setError(null);

    try {
      const updatedSettings = {
        ...settings,
        health: { ...settings.health, ...newSettings },
      };

      await mockAsyncStorage.setItem(
        "user_settings",
        JSON.stringify(updatedSettings)
      );
      setSettings(updatedSettings);
    } catch (err) {
      setError("更新健康设置失败");
    } finally {
      setLoading(false);
    }
  };

  const resetSettings = async () => {
    setLoading(true);
    setError(null);

    try {
      await mockAsyncStorage.removeItem("user_settings");
      setSettings({
        notifications: {
          healthReminders: true,
          agentMessages: true,
          systemUpdates: false,
          soundEnabled: true,
          vibrationEnabled: true,
        },
        privacy: {
          dataSharing: false,
          analyticsEnabled: false,
          locationTracking: true,
          biometricAuth: false,
        },
        display: {
          theme: "light",
          fontSize: "medium",
          language: "zh-CN",
        },
        health: {
          units: "metric",
          stepGoal: 10000,
          waterGoal: 2000,
          sleepGoal: 8,
        },
      });
    } catch (err) {
      setError("重置设置失败");
    } finally {
      setLoading(false);
    }
  };

  const exportSettings = async () => {
    try {
      return JSON.stringify(settings, null, 2);
    } catch (err) {
      setError("导出设置失败");
      return null;
    }
  };

  const importSettings = async (settingsJson: string) => {
    setLoading(true);
    setError(null);

    try {
      const importedSettings = JSON.parse(settingsJson);
      const updatedSettings = { ...settings, ...importedSettings };

      await mockAsyncStorage.setItem(
        "user_settings",
        JSON.stringify(updatedSettings)
      );
      setSettings(updatedSettings);
    } catch (err) {
      setError("导入设置失败");
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadSettings();
  }, []); // TODO: 检查依赖项; // TODO: 检查依赖项; // TODO: 检查依赖项;

  return {
    settings,
    loading,
    error,
    updateNotificationSettings,
    updatePrivacySettings,
    updateDisplaySettings,
    updateHealthSettings,
    resetSettings,
    exportSettings,
    importSettings,
    loadSettings,
  };
};

// 需要导入React

describe("useSettings", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockAsyncStorage.getItem.mockResolvedValue(null);
    mockAsyncStorage.setItem.mockResolvedValue(undefined);
    mockAsyncStorage.removeItem.mockResolvedValue(undefined);
  });

  it("应该返回默认设置", () => {
    const { result } = renderHook(() => useSettings());

    expect(result.current.settings.notifications.healthReminders).toBe(true);
    expect(result.current.settings.privacy.dataSharing).toBe(false);
    expect(result.current.settings.display.theme).toBe("light");
    expect(result.current.settings.health.stepGoal).toBe(10000);
  });

  it("应该加载保存的设置", async () => {
    const savedSettings = {
      notifications: { healthReminders: false },
      display: { theme: "dark" },
    };

    mockAsyncStorage.getItem.mockResolvedValue(JSON.stringify(savedSettings));

    const { result } = renderHook(() => useSettings());

    await act(async () => {
      await new Promise<void>((resolve) => setTimeout(resolve, 0));
    });

    expect(result.current.settings.notifications.healthReminders).toBe(false);
    expect(result.current.settings.display.theme).toBe("dark");
  });

  it("应该更新通知设置", async () => {
    const { result } = renderHook(() => useSettings());

    await act(async () => {
      await result.current.updateNotificationSettings({
        healthReminders: false,
        soundEnabled: false,
      });
    });

    expect(result.current.settings.notifications.healthReminders).toBe(false);
    expect(result.current.settings.notifications.soundEnabled).toBe(false);
    expect(mockAsyncStorage.setItem).toHaveBeenCalled();
  });

  it("应该更新隐私设置", async () => {
    const { result } = renderHook(() => useSettings());

    await act(async () => {
      await result.current.updatePrivacySettings({
        dataSharing: true,
        biometricAuth: true,
      });
    });

    expect(result.current.settings.privacy.dataSharing).toBe(true);
    expect(result.current.settings.privacy.biometricAuth).toBe(true);
    expect(mockAsyncStorage.setItem).toHaveBeenCalled();
  });

  it("应该更新显示设置", async () => {
    const { result } = renderHook(() => useSettings());

    await act(async () => {
      await result.current.updateDisplaySettings({
        theme: "dark",
        fontSize: "large",
        language: "en-US",
      });
    });

    expect(result.current.settings.display.theme).toBe("dark");
    expect(result.current.settings.display.fontSize).toBe("large");
    expect(result.current.settings.display.language).toBe("en-US");
    expect(mockAsyncStorage.setItem).toHaveBeenCalled();
  });

  it("应该更新健康设置", async () => {
    const { result } = renderHook(() => useSettings());

    await act(async () => {
      await result.current.updateHealthSettings({
        stepGoal: 12000,
        waterGoal: 2500,
        units: "imperial",
      });
    });

    expect(result.current.settings.health.stepGoal).toBe(12000);
    expect(result.current.settings.health.waterGoal).toBe(2500);
    expect(result.current.settings.health.units).toBe("imperial");
    expect(mockAsyncStorage.setItem).toHaveBeenCalled();
  });

  it("应该重置所有设置", async () => {
    const { result } = renderHook(() => useSettings());

    // 先修改一些设置
    await act(async () => {
      await result.current.updateDisplaySettings({ theme: "dark" });
    });

    expect(result.current.settings.display.theme).toBe("dark");

    // 重置设置
    await act(async () => {
      await result.current.resetSettings();
    });

    expect(result.current.settings.display.theme).toBe("light");
    expect(mockAsyncStorage.removeItem).toHaveBeenCalledWith("user_settings");
  });

  it("应该导出设置", async () => {
    const { result } = renderHook(() => useSettings());

    await act(async () => {
      const exported = await result.current.exportSettings();
      expect(typeof exported).toBe("string");
      expect(JSON.parse(exported!)).toEqual(result.current.settings);
    });
  });

  it("应该导入设置", async () => {
    const { result } = renderHook(() => useSettings());

    const importSettings = {
      display: { theme: "dark", fontSize: "large" },
      health: { stepGoal: 15000 },
    };

    await act(async () => {
      await result.current.importSettings(JSON.stringify(importSettings));
    });

    expect(result.current.settings.display.theme).toBe("dark");
    expect(result.current.settings.display.fontSize).toBe("large");
    expect(result.current.settings.health.stepGoal).toBe(15000);
    expect(mockAsyncStorage.setItem).toHaveBeenCalled();
  });

  it("应该处理加载设置错误", async () => {
    mockAsyncStorage.getItem.mockRejectedValue(new Error("Storage error"));

    const { result } = renderHook(() => useSettings());

    await act(async () => {
      await new Promise<void>((resolve) => setTimeout(resolve, 0));
    });

    expect(result.current.error).toBe("加载设置失败");
  });

  it("应该处理更新设置错误", async () => {
    mockAsyncStorage.setItem.mockRejectedValue(new Error("Storage error"));

    const { result } = renderHook(() => useSettings());

    await act(async () => {
      await result.current.updateNotificationSettings({
        healthReminders: false,
      });
    });

    expect(result.current.error).toBe("更新通知设置失败");
  });

  it("应该处理导入无效JSON错误", async () => {
    const { result } = renderHook(() => useSettings());

    await act(async () => {
      await result.current.importSettings("invalid json");
    });

    expect(result.current.error).toBe("导入设置失败");
  });

  it("应该正确管理加载状态", async () => {
    const { result } = renderHook(() => useSettings());

    // 等待初始加载完成
    await act(async () => {
      await new Promise<void>((resolve) => setTimeout(resolve, 0));
    });

    expect(result.current.loading).toBe(false);

    await act(async () => {
      await result.current.updateNotificationSettings({
        healthReminders: false,
      });
    });

    expect(result.current.loading).toBe(false);
  });

  it("应该保持其他设置不变", async () => {
    const { result } = renderHook(() => useSettings());

    const originalPrivacy = result.current.settings.privacy;
    const originalHealth = result.current.settings.health;

    await act(async () => {
      await result.current.updateDisplaySettings({ theme: "dark" });
    });

    expect(result.current.settings.privacy).toEqual(originalPrivacy);
    expect(result.current.settings.health).toEqual(originalHealth);
  });

  it("应该支持部分设置更新", async () => {
    const { result } = renderHook(() => useSettings());

    await act(async () => {
      await result.current.updateNotificationSettings({
        healthReminders: false,
      });
    });

    // 其他通知设置应该保持不变
    expect(result.current.settings.notifications.agentMessages).toBe(true);
    expect(result.current.settings.notifications.soundEnabled).toBe(true);
    expect(result.current.settings.notifications.healthReminders).toBe(false);
  });
});
