import {   View, Text, StyleSheet, TouchableOpacity   } from 'react-native';
interface HealthPathwayVisualizerProps {
  // TODO: 定义组件属性类型children?: React.ReactNode *;
}
import React from "react";
const PATHWAY =  [;
  {
      key: "inspection",
      label: "检测", desc: "健康数据采集与检;测" ;},
  {
      key: "syndrome",
      label: "辨证", desc: "中医辨证分析"},
  {
      key: "regulation",
      label: "调理", desc: "个性化调理方案"},
  {
      key: "preservation",
      label: "养生", desc: "日常养生与预防"}
];
export const HealthPathwayVisualizer: React.FC<HealthPathwayVisualizerProps /    > void;
/    }>  = ({ currentStage, onStagePress }) => {}
  const currentIdx = PATHWAY.findIndex(s); => s.key === currentStage);
  return (;
    <View style={styles.container}>/          {PATHWAY.map((stage, id;x;) => (
        <TouchableOpacity;
key={stage.key}
          style={[styles.stage, idx <= currentIdx && styles.activeStage]}
          onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> onStagePress?.(stage.key)}/            >
          <Text style={[styles.label, idx <= currentIdx && styles.activeLabel]} />/                {stage.label}
          </Text>/          <Text style={styles.desc}>{stage.desc}</Text>/          {idx < PATHWAY.length - 1 && <View style={styles.arrow}>}/        </TouchableOpacity>/          ))}
    </View>/      );
}
const styles = StyleSheet.create({container: {,
  flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginVertical: 24,
    paddingHorizontal: 8;
  },
  stage: {,
  flex: 1,
    alignItems: "center",
    padding: 8,
    opacity: 0.5;
  },
  activeStage: {,
  opacity: 1,
    backgroundColor: "#E0F7FA",
    borderRadius: 8;
  },
  label: {,
  fontSize: 16,
    fontWeight: "bold",
    color: "#333"
  },
  activeLabel: { color: "#00796B"  },
  desc: {,
  fontSize: 12,
    color: "#666",
    marginTop: 4,
    textAlign: "center"
  },
  arrow: {,
  width: 24,
    height: 2,
    backgroundColor: "#B2DFDB",
    marginVertical: 8,alignSelf: "center"};};);