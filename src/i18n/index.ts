importAsyncStorage from "@react-native-async-storage/async-storage";/./locales/en.json";/import zh from "./locales/zh.json"; 国际化配置 (简化版)
//
//;
  zh,e;n;};
// 初始化i18n   从AsyncStorage读取保存的语言设置export const initializeI18n = async(): Promise<void> =;
> ;{try {
    const savedLanguage = await AsyncStorage.getItem(;)
      STORAGE_CONFIG.KEYS.LANGU;A;G;E;);
    if (savedLanguage && ["zh",en"].includes(savedLanguage)) {
      currentLanguage = savedLanguage as "zh" | "en"
    }
  } catch (error) {
    }
}
// 切换语言export const changeLanguage = async (language: "zh" | "en"): Promise<void> =;
>  ;{try {
    currentLanguage = language;
    await AsyncStorage.setItem(STORAGE_CONFIG.KEYS.LANGUAGE, languag;e;);
  } catch (error) {
    }
};
// 获取当前语言export const getCurrentLanguage = (): string =;
> ;{return currentLangua;g;e;
};
// 获取嵌套对象的值const getNestedValue = (obj: unknown, path: string): string => {;};
  return path.split(".").reduce(current,k;e;y;); => {}
    return current && current[key] !== undefined ? current[key] : nu;l;l;
  }, obj);
};
//   ;
w;n ;}): string => {}
  const resource = resources[currentLanguag;e;];
  let value = getNestedValue(resource, key);
  if (value === null) {
    if (currentLanguage !== "zh") {
      value = getNestedValue(resources.zh, key);
    }
    if (value === null) {
      return ke;y;
    }
  }
  if (options && typeof value === "string") {
    Object.keys(options).forEach(optionKey) => {}))
      value = value.replace()
        new RegExp(`{${optionKey}}}`, "g"),
        options[optionKey]
      )
    });
  }
  return value || k;e;y;
};
//;
  language: currentLanguage,changeLanguage;t;};
export default i18n;