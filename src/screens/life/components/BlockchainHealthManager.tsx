
const importIcon = from "../../../components/common/Icon/; 区块链健康数据管理组件   提供安全的健康数据存储和管理功能""/;,"/g"/;
import React,{ useState, useEffect } from react";";";
Text,;
StyleSheet,;
ScrollView,;
TouchableOpacity,;
Modal,;
Alert,";,"";
Switch,";"";
  { ActivityIndicator } from ";react-native";";
interface HealthDataRecord {";,}id: string,";,"";
type: diagnosis" | "medication | "test_result" | vital_signs" | "lifestyle;",";
title: string,;
description: string,;
timestamp: Date,;
hash: string,;
verified: boolean,;
encrypted: boolean,;
shared: boolean,;
}
}
  const size = string;}
};
interface DataPermission {id: string,";,}entity: string,";,"";
type: "hospital" | doctor" | "researcher | "insurance" | family";",";,"";
permissions: string[],;
expiryDate: Date,;
}
}
  const active = boolean;}
};
interface BlockchainHealthManagerProps {visible: boolean,;}}
}
  onClose: () => void;}
};";,"";
const: SAMPLE_RECORDS: HealthDataRecord[] = [;]{,";,}id: "1,",";,"";
type: "diagnosis";","";"";
";"";
";,"";
timestamp: new Date("2024-01-15");",";
hash: 0x1a2b3c4d5e6f...";",";,"";
verified: true,;
encrypted: true,";,"";
shared: false,";"";
}
    const size = "2.3 MB"}"";"";
  ;},";"";
  {";,}id: "2";",";
type: vital_signs";","";"";
";"";
";,"";
timestamp: new Date(2024-01-20"),";
hash: "0x2b3c4d5e6f7a...,",";,"";
verified: true,;
encrypted: true,";,"";
shared: true,";"";
}
    const size = "1.8 MB"}"";"";
  ;},";"";
  {";,}id: 3";",";,"";
type: "medication,",";"";
";"";
";,"";
timestamp: new Date("2024-01-25),";
hash: "0x3c4d5e6f7a8b...";",";
verified: true,;
encrypted: true,";,"";
shared: false,";"";
}
    const size = 0.5 MB"}"";"";
  ;}
];
];";,"";
const: SAMPLE_PERMISSIONS: DataPermission[] = [;]{,";,}id: "1,",";"";
";,"";
type: hospital";",";"";
";,"";
expiryDate: new Date(2024-12-31"),"";"";
}
    const active = true;}
  },";"";
  {";,}id: "2,",";"";
";,"";
type: doctor";",";"";
";,"";
expiryDate: new Date(2024-06-30"),"";"";
}
    const active = true;}
  },";"";
  {";,}id: "3,",";"";
";,"";
type: researcher";",";"";
";,"";
expiryDate: new Date("2024-03-31");","";"";
}
    const active = false;}
  }";"";
];
]";,"";
export const BlockchainHealthManager: React.FC<BlockchainHealthManagerProps  /> = ({/;)/   const performanceMonitor = usePerformanceMonitor(BlockchainHealthManager";))""/;}{//;,}trackRender: true,;"/g"/;
}
    trackMemory: true,}
    const warnThreshold = 50;});
visible,;
onClose;";"";
}) => {};";,"";
const [activeTab, setActiveTab] = useState<"records | "permissions" | security">("records);";
const [records, setRecords] = useState<HealthDataRecord[]  />(SAMPLE_RECORD;S;);/  const [permissions, setPermissions] = useState<DataPermission[]  />(SAMPLE_PERMISSION;S;);/  const [selectedRecord, setSelectedRecord] = useState<HealthDataRecord | null  />(nul;l;);/      const [isLoading, setIsLoading] = useState<boolean>(fals;e;);/;,/g/;
const  getTypeIcon = useCallback => {}
    try {}}
      await: new Promise<void>(resolve => setTimeout() => resolve(), 1000));}
      setRecords(prev => prev.map(record => {}));
record.id === recordId;
          ? { ...record, shared: !record.shared;}
          : record;
      ););

    } catch (error) {}}
}
    } finally {}}
      setIsLoading(false);}
    }
  };
const togglePermission = useMemo() => async (permissionId: string) => {;});
setIsLoading(true), []);
try {}}
      await: new Promise<void>(resolve => setTimeout(); => resolve(), 1000));}
      setPermissions(prev => prev.map(permission => {}));
permission.id === permissionId;
          ? { ...permission, active: !permission.active;}
          : permission;
      ););

    } catch (error) {}}
}
    } finally {}}
      setIsLoading(false);}
    }
  };
  //"/;"/g"/;
    <View style={styles.tabBar}>/          <TouchableOpacity;"  />/;,"/g"/;
style={[styles.tab, activeTab === "records && styles.activeTab]}";
onPress={() = accessibilityLabel="操作按钮" /> setActiveTab("records")}/          >"/;"/g"/;
        <Icon;"  />/;,"/g"/;
name="database";
size={20}";,"";
color={activeTab === records" ? colors.primary: colors.textSecondary;} />/        <Text style={[styles.tabText, activeTab === "records && styles.activeTabText]}  />/              数据记录"/;"/g"/;
        </Text>/      </TouchableOpacity>/"/;"/g"/;
      <TouchableOpacity;"  />/;,"/g"/;
style={[styles.tab, activeTab === "permissions" && styles.activeTab]}";,"";
onPress={() = accessibilityLabel="操作按钮" /> setActiveTab(permissions")}/          >""/;"/g"/;
        <Icon;"  />/;,"/g"/;
name="key";
size={20}";,"";
color={activeTab === "permissions ? colors.primary: colors.textSecondary;} />/        <Text style={[styles.tabText, activeTab === "permissions" && styles.activeTabText]}  />/              访问权限""/;"/g"/;
        </Text>/      </TouchableOpacity>/"/;"/g"/;
      <TouchableOpacity;"  />/;,"/g"/;
style={[styles.tab, activeTab === security" && styles.activeTab]}";
onPress={() = accessibilityLabel="操作按钮" /> setActiveTab("security)}/          >""/;"/g"/;
        <Icon;"  />/;,"/g"/;
name="shield-check";
size={20}";,"";
color={activeTab === "security" ? colors.primary: colors.textSecondary;} />/        <Text style={[styles.tabText, activeTab === security" && styles.activeTabText]}  />/              安全设置""/;"/g"/;
        </Text>/      </TouchableOpacity>/    </View>/      ), []);/;,/g/;
const renderRecordCard = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => (record: HealthDataRecord) => (;);
    <TouchableOpacity;  />/;,/g/;
key={record.id}";,"";
style={styles.recordCard}";,"";
onPress={() = accessibilityLabel="操作按钮" /> setSelectedRecord(record)}/        >"/;"/g"/;
      <View style={styles.recordHeader}>/        <View style={[styles.recordIcon, { backgroundColor: getTypeColor(record.type) + "20   ;}}]}  />/          <Icon name={getTypeIcon(record.type)} size={24} color={getTypeColor(record.type)}  />/        </View>/    ""/;"/g"/;
        <View style={styles.recordInfo}>/          <Text style={styles.recordTitle}>{record.title}</Text>/          <Text style={styles.recordDescription}>{record.description}</Text>/          <Text style={styles.recordTimestamp}>/                {record.timestamp.toLocaleDateString("zh-CN")}"/;"/g"/;
          </Text>/        </View>/"/;"/g"/;
        <View style={styles.recordStatus}>/              {record.verified   && <View style={styles.statusBadge}>/              <Icon name="check-circle" size={16} color={colors.success}  />/              <Text style={styles.statusText}>已验证</Text>/            </View>/              )}"/;"/g"/;
          {record.encrypted   && <View style={styles.statusBadge}>/              <Icon name="lock" size={16} color={colors.primary}  />/              <Text style={styles.statusText}>已加密</Text>/            </View>/              )}"/;"/g"/;
        </View>/      </View>//;/g/;
      <View style={styles.recordFooter}>/        <Text style={styles.recordHash}>哈希: {record.hash}</Text>/        <View style={styles.recordActions}>/          <Text style={styles.recordSize}>{record.size}</Text>/              <Switch;"  />/;,"/g"/;
value={record.shared}";,"";
onValueChange={() = /> toggleRecordSharing(record.id)}/            trackColor={ false: colors.gray300, true: colors.primary + 50";}}""/;,"/g"/;
thumbColor={record.shared ? colors.primary: colors.gray400;} />/          <Text style={styles.shareLabel}>共享</Text>/        </View>/      </View>/    </TouchableOpacity>/      ), []);/;,/g/;
const renderPermissionCard = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => (permission: DataPermission) => (;)";"";
    <View key={permission.id} style={styles.permissionCard}>/      <View style={styles.permissionHeader}>/        <View style={styles.permissionIcon}>/          <Icon name={getEntityIcon(permission.type)} size={24} color={colors.primary}  />/        </View>/"/;"/g"/;
        <View style={styles.permissionInfo}>/          <Text style={styles.permissionEntity}>{permission.entity}</Text>/          <Text style={styles.permissionType}>/            {/;,}permission.type === "hospital ? "医院" : "";"/g"/;
";"";
}
"}"";"";
          </Text>/          <Text style={styles.permissionExpiry}>/                到期时间: {permission.expiryDate.toLocaleDateString("zh-CN)}""/;"/g"/;
          </Text>/        </View>//;/g/;
        <Switch;"  />/;,"/g"/;
value={permission.active}";,"";
onValueChange={() = /> togglePermission(permission.id)}/          trackColor={ false: colors.gray300, true: colors.primary + "50";}}"/;,"/g"/;
thumbColor={permission.active ? colors.primary: colors.gray400;} />/      </View>//;/g/;
      <View style={styles.permissionsList}>/        <Text style={styles.permissionsTitle}>授权范围:</Text>/            {permission.permissions.map(perm, index); => ()}/;/g/;
          <Text key={index} style={styles.permissionItem}>• {perm}</Text>/            ))}/;/g/;
      </View>/    </View>/      ), []);"/;"/g"/;
  //"/;"/g"/;
    <View style={styles.securityContainer}>/      <View style={styles.securityCard}>/        <View style={styles.securityHeader}>/          <Icon name="fingerprint" size={32} color={colors.primary}  />/          <Text style={styles.securityTitle}>生物识别认证</Text>/        </View>/        <Text style={styles.securityDescription}>/              使用指纹或面部识别来保护您的健康数据访问"/;"/g"/;
        </Text>/            <Switch;"  />/;,"/g"/;
value={true}";,"";
trackColor={ false: colors.gray300, true: colors.primary + 50";}}";
thumbColor={colors.primary} />/      </View>/"/;"/g"/;
      <View style={styles.securityCard}>/        <View style={styles.securityHeader}>/          <Icon name="key-variant" size={32} color={colors.primary}  />/          <Text style={styles.securityTitle}>私钥管理</Text>/        </View>/        <Text style={styles.securityDescription}>/              您的私钥安全存储在设备中，用于数据加密和身份验证"/;"/g"/;
        </Text>/        <TouchableOpacity style={styles.securityButton} accessibilityLabel="备份私钥"  />/          <Text style={styles.securityButtonText}>备份私钥</Text>/        </TouchableOpacity>/      </View>/"/;"/g"/;
      <View style={styles.securityCard}>/        <View style={styles.securityHeader}>/          <Icon name="shield-lock" size={32} color={colors.primary}  />/          <Text style={styles.securityTitle}>零知识证明</Text>/        </View>/        <Text style={styles.securityDescription}>/              在不泄露具体数据的情况下，证明您的健康状态符合特定条件"/;"/g"/;
        </Text>/            <Switch;"  />/;,"/g"/;
value={true}";,"";
trackColor={ false: colors.gray300, true: colors.primary + "50;}}";
thumbColor={colors.primary} />/      </View>/    </View>/      ), []);/;,/g/;
const  renderContent = useCallback() => {";,}switch (activeTab) {";,}case "records": ";,"";
performanceMonitor.recordRender();
}
        return (;)}
          <ScrollView style={styles.content} showsVerticalScrollIndicator={false}  />/            <View style={styles.section}>/              <Text style={styles.sectionTitle}>健康数据记录</Text>/              <Text style={styles.sectionDescription}>/                    您的所有健康数据都经过加密存储在区块链上，确保数据的安全性和不可篡改性。;/;/g/;
              </Text>/                  {records.map(renderRecordCard)};"/;"/g"/;
            </View>/          </ScrollView>/            ;)"/;,"/g"/;
const case = permissions": ";
return (;);
          <ScrollView style={styles.content} showsVerticalScrollIndicator={false}  />/            <View style={styles.section}>/              <Text style={styles.sectionTitle}>数据访问权限</Text>/              <Text style={styles.sectionDescription}>/                    管理谁可以访问您的健康数据，您可以随时撤销或修改权限。;/;/g/;
              </Text>/                  {permissions.map(renderPermissionCard)};"/;"/g"/;
            </View>/          </ScrollView>/            ;)"/;,"/g"/;
case "security: ";
return (;);
          <ScrollView style={styles.content} showsVerticalScrollIndicator={false}  />/            <View style={styles.section}>/              <Text style={styles.sectionTitle}>安全设置</Text>/              <Text style={styles.sectionDescription}>/                    配置您的数据安全选项，确保只有您本人可以访问和管理健康数据。;/;/g/;
              </Text>/                  {renderSecuritySettings()};/;/g/;
            </View>/          </ScrollView>/            ;);/;,/g,/;
  default: ;
return nu;l;l;
    }
  }
  return (;);
    <Modal;"  />/;,"/g"/;
visible={visible}";,"";
animationType="slide";
presentationStyle="fullScreen";
onRequestClose={onClose} />/      <View style={styles.container}>/        <View style={styles.header}>/          <TouchableOpacity onPress={onClose} style={styles.closeButton} accessibilityLabel="关闭"  />/            <Icon name="close" size={24} color={colors.textPrimary}  />/          </TouchableOpacity>/          <Text style={styles.title}>区块链健康数据</Text>/          <TouchableOpacity style={styles.helpButton} accessibilityLabel="关闭"  />/            <Icon name="help-circle" size={24} color={colors.textPrimary}  />/          </TouchableOpacity>/        </View>/"/;"/g"/;
        {renderTabBar()}";"";
        {renderContent()}";"";
        {isLoading   && <View style={styles.loadingOverlay}>/            <ActivityIndicator size="large" color={colors.primary}  />/            <Text style={styles.loadingText}>处理中...</Text>/          </View>/            )};"/;"/g"/;
      </View>/    </Modal>/      ;);/;/g/;
};
styles: useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => StyleSheet.create({)container: {)}flex: 1,;
}
    const backgroundColor = colors.background;}
  },";,"";
header: {,";,}flexDirection: "row";",";
alignItems: center";",";,"";
justifyContent: "space-between,",";,"";
paddingHorizontal: spacing.lg,;
paddingVertical: spacing.md,;
borderBottomWidth: 1,;
}
    const borderBottomColor = colors.border;}
  }
closeButton: { padding: spacing.sm  ;}
title: {,";,}fontSize: 18,";,"";
fontWeight: "600";","";"";
}
    const color = colors.textPrimary;}
  }
helpButton: { padding: spacing.sm  ;},";,"";
tabBar: {,";,}flexDirection: row";",";,"";
backgroundColor: colors.surface,;
borderBottomWidth: 1,;
}
    const borderBottomColor = colors.border;}
  }
tab: {,";,}flex: 1,";,"";
flexDirection: "row,",";,"";
alignItems: "center";",";
justifyContent: center";",";
paddingVertical: spacing.md,;
}
    const paddingHorizontal = spacing.sm;}
  }
activeTab: {borderBottomWidth: 2,;
}
    const borderBottomColor = colors.primary;}
  }
tabText: {,";,}fontSize: 14,";,"";
fontWeight: "500,",";,"";
color: colors.textSecondary,;
}
    const marginLeft = spacing.xs;}
  }
activeTabText: { color: colors.primary  ;}
content: {flex: 1,;
}
    const paddingHorizontal = spacing.lg;}
  }
section: { paddingVertical: spacing.lg  ;}
sectionTitle: {,";,}fontSize: 20,";,"";
fontWeight: "bold";",";
color: colors.textPrimary,;
}
    const marginBottom = spacing.sm;}
  }
sectionDescription: {fontSize: 14,;
color: colors.textSecondary,;
lineHeight: 20,;
}
    const marginBottom = spacing.lg;}
  }
recordCard: {backgroundColor: colors.surface,;
borderRadius: 12,;
padding: spacing.md,;
marginBottom: spacing.md,;
borderWidth: 1,;
}
    const borderColor = colors.border;}
  },";,"";
recordHeader: {,";,}flexDirection: row";",";,"";
alignItems: "flex-start,",";"";
}
    const marginBottom = spacing.md;}
  }
recordIcon: {width: 48,;
height: 48,";,"";
borderRadius: 24,";,"";
justifyContent: "center";",";
alignItems: center";",";"";
}
    const marginRight = spacing.md;}
  }
recordInfo: { flex: 1  ;}
recordTitle: {,";,}fontSize: 16,";,"";
fontWeight: "600,",";,"";
color: colors.textPrimary,;
}
    const marginBottom = spacing.xs;}
  }
recordDescription: {fontSize: 14,;
color: colors.textSecondary,;
lineHeight: 20,;
}
    const marginBottom = spacing.xs;}
  }
recordTimestamp: {fontSize: 12,;
}
    const color = colors.textTertiary;}";"";
  },";,"";
recordStatus: { alignItems: "flex-end"  ;},";,"";
statusBadge: {,";,}flexDirection: row";",";,"";
alignItems: "center,",";,"";
backgroundColor: colors.gray100,;
paddingHorizontal: spacing.sm,;
paddingVertical: spacing.xs,;
borderRadius: 8,;
}
    const marginBottom = spacing.xs;}
  }
statusText: {fontSize: 12,;
color: colors.textSecondary,;
}
    const marginLeft = spacing.xs;}
  },";,"";
recordFooter: {,";,}flexDirection: "row";",";
justifyContent: space-between";",";,"";
alignItems: "center,",";,"";
paddingTop: spacing.md,;
borderTopWidth: 1,;
}
    const borderTopColor = colors.border;}
  }
recordHash: {fontSize: 12,";,"";
color: colors.textTertiary,";,"";
fontFamily: "monospace";","";"";
}
    const flex = 1;}
  },";,"";
recordActions: {,";,}flexDirection: row";",";"";
}
    const alignItems = "center"}"";"";
  ;}
recordSize: {fontSize: 12,;
color: colors.textSecondary,;
}
    const marginRight = spacing.md;}
  }
shareLabel: {fontSize: 12,;
color: colors.textSecondary,;
}
    const marginLeft = spacing.sm;}
  }
permissionCard: {backgroundColor: colors.surface,;
borderRadius: 12,;
padding: spacing.md,;
marginBottom: spacing.md,;
borderWidth: 1,;
}
    const borderColor = colors.border;}
  },";,"";
permissionHeader: {,";,}flexDirection: "row";",";
alignItems: center";","";"";
}
    const marginBottom = spacing.md;}
  }
permissionIcon: {width: 48,;
height: 48,";,"";
borderRadius: 24,";,"";
backgroundColor: colors.primary + "20,";
justifyContent: "center";",";
alignItems: center";","";"";
}
    const marginRight = spacing.md;}
  }
permissionInfo: { flex: 1  ;}
permissionEntity: {,";,}fontSize: 16,";,"";
fontWeight: "600,",";,"";
color: colors.textPrimary,;
}
    const marginBottom = spacing.xs;}
  }
permissionType: {fontSize: 14,;
color: colors.textSecondary,;
}
    const marginBottom = spacing.xs;}
  }
permissionExpiry: {fontSize: 12,;
}
    const color = colors.textTertiary;}
  }
permissionsList: {paddingTop: spacing.md,;
borderTopWidth: 1,;
}
    const borderTopColor = colors.border;}
  }
permissionsTitle: {,";,}fontSize: 14,";,"";
fontWeight: "600";",";
color: colors.textPrimary,;
}
    const marginBottom = spacing.sm;}
  }
permissionItem: {fontSize: 14,;
color: colors.textSecondary,;
marginBottom: spacing.xs,;
}
    const lineHeight = 20;}
  }
securityContainer: { gap: spacing.md  ;}
securityCard: {backgroundColor: colors.surface,;
borderRadius: 12,;
padding: spacing.lg,;
borderWidth: 1,;
}
    const borderColor = colors.border;}
  },";,"";
securityHeader: {,";,}flexDirection: row";",";,"";
alignItems: "center,",";"";
}
    const marginBottom = spacing.md;}
  }
securityTitle: {,";,}fontSize: 16,";,"";
fontWeight: "600";",";
color: colors.textPrimary,;
marginLeft: spacing.md,;
}
    const flex = 1;}
  }
securityDescription: {fontSize: 14,;
color: colors.textSecondary,;
lineHeight: 20,;
}
    const marginBottom = spacing.md;}
  }
securityButton: {backgroundColor: colors.primary,;
paddingVertical: spacing.sm,;
paddingHorizontal: spacing.md,";,"";
borderRadius: 8,";"";
}
    const alignSelf = flex-start"}"";"";
  ;}
securityButtonText: {,";,}fontSize: 14,";,"";
fontWeight: "600,",";"";
}
    const color = "white"}"";"";
  ;},";,"";
loadingOverlay: {,";,}position: absolute";",";,"";
top: 0,;
left: 0,;
right: 0,";,"";
bottom: 0,";,"";
backgroundColor: "rgba(0, 0, 0, 0.5),",";,"";
justifyContent: "center";","";"";
}
    const alignItems = center"}"";"";
  ;}
loadingText: {,";,}fontSize: 16,";,"";
color: 'white';','';'';
}
    const marginTop = spacing.md;}
  }';'';
}), []);