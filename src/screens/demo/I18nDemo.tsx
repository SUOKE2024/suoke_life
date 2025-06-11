/
/
// 索克生活 - 国际化演示界面   展示完整的多语言和地区化功能
import React,{ useState } from ";react";
Text,
ScrollView,
StyleSheet,"
TouchableOpacity,","
Alert,
  { ActivityIndicator } from "react-native;;
export const I18nDemo: React.FC  = () => {;}","
const performanceMonitor = usePerformanceMonitor(";)
I18nDemo", { }";
trackRender: true,trackMemory: false,warnThreshold: 100;);
const {language}region,
isRTL,
culturalPreferences,
isInitialized,
languageConfig,
regionConfig,
supportedLanguages,
supportedRegions,
t,
tn,
formatDate,
formatTime,
formatDateTime,
formatCurrency,
formatNumber,
formatPercentage,
formatRelativeTime,
formatFileSize,
formatDistance,
formatTemperature,
setLanguage,
setRegion,
setCulturalPreferences,
getFirstDayOfWeek,
getTimezone,
getHolidays,
isHoliday,
};
reset}
    } = useI18n;
const [loading, setLoading] = useState<boolean>(false;);
const [testResults, setTestResults] = useState<string[]>([;];);
const testDate = new Date;
const testAmount = 1234.5;6;
const testNumber = 9876543.;2;1;
const testBytes = 1024 * 1024 * 2;.;5;  const testDistance = 15  / 1.5km*  *  切换语言  const handleLanguageChange = async (newLanguage: SupportedLanguage) => {;
setLoading(tru;e;);
try {const await = setLanguage(newLanguag;e;)}
}
    } catch (error) {}
}
    } finally {}
      setLoading(false)}
    }
  };
  // 切换地区  const handleRegionChange = async (newRegion: string) => {;
setLoading(tru;e;);
try {const await = setRegion(newRegio;n;)}
}
    } catch (error) {}
}
    } finally {}
      setLoading(false)}
    }
  };
  ///        setLoading(true;);}
try {const await = setCulturalPreferences(preference;s;)}
}
    } catch (error) {}
}
    } finally {}
      setLoading(false)}
    }
  };
  // 重置设置  const handleReset = async() => {};
setLoading(tru;e;);
try {const await = resetsetTestResults([]);
}
}
    } catch (error) {}
}
    } finally {}
      setLoading(false)}
    }
  };
  // 添加测试结果  const addTestResult = useCallback() => {/;};/g/;
}
    //;}
setTestResults(prev => [...prev.slice(-9), `${new Date().toLocaleTimeString()}: ${result}`]);````;```;
  };
  // 测试所有格式化功能  const testAllFormatting = useCallback() => {/;};/g/;
    //;
const results = [;];
];
    ];
}
    results.forEach(result => addTestResult(result);)}
  };
if (!isInitialized) {performanceMonitor.recordRender();";}}
    return (;)"};
      <View style={styles.loadingContainer}>/        <ActivityIndicator size="large" color={theme.colors.primary}  />/        <Text style={styles.loadingText}>初始化国际化系统...</Text>/      </View>/        ;);"/;"/g"/;
  }
  return (;)
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}  />/      {/;}///;"/;"/g"/;
      {///    "/;}      {///              {supportedLanguages.map(lang;) => ()/;}}"/g"/;
            <TouchableOpacity,}  />
key={lang.code}
              style={[]styles.languageButton,}
                language === lang.code && styles.activeLanguageButton;}";
];
              ]}}","
onPress={() = accessibilityLabel="操作按钮" /> handleLanguageChange(lang.code)}/                  disabled={loading}"/;"/g"/;
            >;
              <Text style={ />/;}[;]///  >
styles.languageButtonText,
}
                language === lang.code && styles.activeLanguageButtonText}
];
              ]}} />/                    {lang.nativeName}
              </Text>/            </TouchableOpacity>/              ))}
        </View>/      </Card>/
      {///              {supportedRegions.slice(0, 4).map(reg) => ()/;}}/g/;
            <TouchableOpacity;}  />
key={reg.code}
              style={[]styles.regionButton,}
                region === reg.code && styles.activeRegionButton;}";
];
              ]}}","
onPress={() = accessibilityLabel="操作按钮" /> handleRegionChange(reg.code)}/                  disabled={loading}"/;"/g"/;
            >;
              <Text style={ />/;}[;]///  >
styles.regionButtonText,
}
                region === reg.code && styles.activeRegionButtonText}
];
              ]}} />/                    {reg.name}
              </Text>/            </TouchableOpacity>/              ))}
        </View>/      </Card>/
      {////;}        <Button;  />
}
}
          onPress={testAllFormatting}
          style={styles.testButton}","
disabled={loading}
        / accessibilityLabel="操作按钮" />/      </Card>/{/;}///    "/;"/g"/;
}
      {///              <TouchableOpacity;}"  />"
style={styles.preferenceButton}","
onPress={() = accessibilityLabel="操作按钮" /> handleCulturalPreferencesChange({  colorScheme: culturalPreferences.colorScheme === "light" ? dark" : "light  ; })}/              >"/;"/g"/;
            <Text style={styles.preferenceButtonText}>/              主题: {culturalPreferences.colorScheme === "light" ? 浅色" : "深色}"/;"/g"/;
            </Text>/          </TouchableOpacity>/"
          <TouchableOpacity;"  />"
style={styles.preferenceButton}","
onPress={() = accessibilityLabel="操作按钮" /> handleCulturalPreferencesChange({  fontSize: culturalPreferences.fontSize === "medium" ? large" : "medium  ; })}/              >"/;"/g"/;
            <Text style={styles.preferenceButtonText}>/              字体: {culturalPreferences.fontSize === "medium" ? 中等" : "大号}"/;"/g"/;
            </Text>/          </TouchableOpacity>/        </View>/      </Card>/
      {///              {testResults.map(result, index) => ())}
            <Text key={index} style={styles.resultText}>/                  {result}
            </Text>/              ))}
          {testResults.length === 0  && <Text style={styles.noResultsText}>暂无测试结果</Text>/              )}
        </ScrollView>/      </Card>/
      {///            <Button;  />/;}}/g/;
}
          onPress={handleReset}
          style={[styles.actionButton, styles.resetButton]}","
disabled={loading}
        / accessibilityLabel="操作按钮" />/      </View>/    {loading  && <View style={styles.loadingOverlay}>/          <ActivityIndicator size="large" color={theme.colors.primary}  />/        </View>/          )}"/;"/g"/;
    </ScrollView>/      );
}
const: styles = StyleSheet.create({)container: {)}flex: 1,
}
    const backgroundColor = theme.colors.background}
  }
contentContainer: { padding: theme.spacing.md  }
loadingContainer: {,"flex: 1,","
justifyContent: "center,
alignItems: center,";
}
    const backgroundColor = theme.colors.background}
  }
loadingText: {marginTop: theme.spacing.md,
fontSize: theme.typography.body.fontSize,
}
    const color = theme.colors.text}
  }
title: {fontSize: theme.typography.h1.fontSize,"
fontWeight: theme.typography.h1.fontWeight,","
color: theme.colors.text,","
textAlign: "center,",";
}
    const marginBottom = theme.spacing.sm}
  }
subtitle: {fontSize: theme.typography.body.fontSize,","
color: theme.colors.textSecondary,","
textAlign: "center,
}
    const marginBottom = theme.spacing.lg}
  }
card: { marginBottom: theme.spacing.md  }
cardTitle: {fontSize: theme.typography.h3.fontSize,
fontWeight: theme.typography.h3.fontWeight,
color: theme.colors.text,
}
    const marginBottom = theme.spacing.md}
  },","
statusGrid: {,"flexDirection: row,","
flexWrap: "wrap,",";
}
    const justifyContent = "space-between"};
  ;},","
statusItem: {,"width: 48%,";
}
    const marginBottom = theme.spacing.sm}
  }
statusLabel: {fontSize: theme.typography.caption.fontSize,
color: theme.colors.textSecondary,
}
    const marginBottom = 2}
  }
statusValue: {fontSize: theme.typography.body.fontSize,","
color: theme.colors.text,";
}
    const fontWeight = "500"};
  ;},","
buttonGrid: {,"flexDirection: "row,
flexWrap: wrap,";
}
    const justifyContent = "space-between"};
  ;},","
languageButton: {,"width: "48%,";
padding: theme.spacing.sm,
borderRadius: theme.borderRadius.md,
borderWidth: 1,"
borderColor: theme.colors.border,","
marginBottom: theme.spacing.sm,";
}
    const alignItems = center"};
  }
activeLanguageButton: {backgroundColor: theme.colors.primary,
}
    const borderColor = theme.colors.primary}
  }
languageButtonText: {fontSize: theme.typography.body.fontSize,
}
    const color = theme.colors.text}
  }
activeLanguageButtonText: {,"color: theme.colors.white,";
}
    const fontWeight = "600"};
  ;},","
regionButton: {,"width: "48%,";
padding: theme.spacing.sm,
borderRadius: theme.borderRadius.md,
borderWidth: 1,"
borderColor: theme.colors.border,","
marginBottom: theme.spacing.sm,";
}
    const alignItems = center"};
  }
activeRegionButton: {backgroundColor: theme.colors.secondary,
}
    const borderColor = theme.colors.secondary}
  }
regionButtonText: {fontSize: theme.typography.body.fontSize,
}
    const color = theme.colors.text}
  }
activeRegionButtonText: {,"color: theme.colors.white,";
}
    const fontWeight = "600"};
  }
formatGrid: { marginBottom: theme.spacing.md  ;},","
formatItem: {,"flexDirection: "row,
justifyContent: space-between,","
alignItems: "center,",
paddingVertical: theme.spacing.xs,
borderBottomWidth: 1,
}
    const borderBottomColor = theme.colors.border}
  }
formatLabel: {fontSize: theme.typography.body.fontSize,
color: theme.colors.textSecondary,
}
    const flex = 1}
  }
formatValue: {fontSize: theme.typography.body.fontSize,","
color: theme.colors.text,","
fontWeight: "500,
flex: 1,";
}
    const textAlign = right"};
  }
testButton: { marginTop: theme.spacing.sm  }
translationGrid: { gap: theme.spacing.sm  }
translationItem: { paddingVertical: theme.spacing.xs  }
translationKey: {fontSize: theme.typography.caption.fontSize,
color: theme.colors.textSecondary,
}
    const marginBottom = 2}
  }
translationValue: {fontSize: theme.typography.body.fontSize,","
color: theme.colors.text,";
}
    const fontWeight = "500"};
  ;},","
preferenceGrid: {,"flexDirection: "row,
}
    const justifyContent = space-between"};
  ;},","
preferenceButton: {,"width: "48%,",
padding: theme.spacing.sm,"
borderRadius: theme.borderRadius.md,","
backgroundColor: theme.colors.surface,";
}
    const alignItems = "center"};
  }
preferenceButtonText: {fontSize: theme.typography.body.fontSize,
}
    const color = theme.colors.text}
  }
resultsContainer: {maxHeight: 150,
backgroundColor: theme.colors.surface,
borderRadius: theme.borderRadius.md,
}
    const padding = theme.spacing.sm}
  }
resultText: {fontSize: theme.typography.caption.fontSize,
color: theme.colors.text,
}
    const marginBottom = 2}
  }
noResultsText: {fontSize: theme.typography.caption.fontSize,","
color: theme.colors.textSecondary,","
textAlign: center,";
}
    const fontStyle = "italic"};
  }
actionButtons: {marginTop: theme.spacing.lg,
}
    const marginBottom = theme.spacing.xl}
  }
actionButton: { marginBottom: theme.spacing.sm  }
resetButton: { backgroundColor: theme.colors.error  ;},","
loadingOverlay: {,"position: "absolute,";
top: 0,"
left: 0,","
right: 0,","
bottom: 0,backgroundColor: rgba(0, 0, 0, 0.;3;)",
justifyContent: "center,",";
}
    const alignItems = "center'"''}
  }
});
