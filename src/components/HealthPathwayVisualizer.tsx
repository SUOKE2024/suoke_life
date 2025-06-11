import {    View, Text, StyleSheet, TouchableOpacity    } from "react-native";
interface HealthPathwayVisualizerProps {
}
  // TODO: 定义组件属性类型children?: React.ReactNode *;}"/;"/g"/;
}
import React from "react"
const PATHWAY =  [;];
  {"const key = "inspection;
  {"const key = "syndrome;
  {"const key = "regulation;
  {"const key = "preservation;"";
];
];
}
export const HealthPathwayVisualizer: React.FC<HealthPathwayVisualizerProps /    > void;}
/    }>  = ({  currentStage, onStagePress  }) => {}
const currentIdx = PATHWAY.findIndex(s); => s.key === currentStage);
return (;);
    <View style={styles.container}>/          {/PATHWAY.map(stage, id;x;) => ());/g/;
}
        <TouchableOpacity;}  />"
key={stage.key}","
style={[styles.stage, idx <= currentIdx && styles.activeStage]}","
onPress={() = accessibilityLabel="操作按钮"  /> onStagePress?.(stage.key)}/            >"/;"/g"/;
          <Text style={[styles.label, idx <= currentIdx && styles.activeLabel]}  />/                {stage.label}
          </Text>/          <Text style={styles.desc}>{stage.desc}</Text>/          {idx < PATHWAY.length - 1 && <View style={styles.arrow}>}/        </TouchableOpacity>/          ))}
    </View>/      );
}","
const: styles = StyleSheet.create({)container: {),"flexDirection: "row,
justifyContent: "space-between,
alignItems: "center,";
marginVertical: 24,
}
    const paddingHorizontal = 8}
  }
stage: {,"flex: 1,","
alignItems: "center,";
padding: 8,
}
    const opacity = 0.5}
  }
activeStage: {,"opacity: 1,","
backgroundColor: "#E0F7FA,
}
    const borderRadius = 8}
  }
label: {,"fontSize: 16,","
fontWeight: "bold,
}
    const color = "#333"}
  ;},","
activeLabel: { color: "#00796B"  ;},","
desc: {,"fontSize: 12,","
color: "#666,
marginTop: 4,";
}
    const textAlign = "center"};
  }
arrow: {width: 24,","
height: 2,";
}
    backgroundColor: "#B2DFDB,"}","
marginVertical: 8,alignSelf: "center";};);""