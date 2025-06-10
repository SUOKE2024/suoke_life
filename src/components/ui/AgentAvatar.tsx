
import React from "react";"";"";
;/importText from "./Text";/    importReact from "react;""/;"/g"/;
// * 索克生活 - AgentAvatar组件;/;/g/;
* 智能体头像组件，为四个智能体提供特色头像";,"";
export interface AgentAvatarProps {";,}const agent = "xiaoai" | "xiaoke" | "laoke" | "soer";";,"";
size?: "small" | "medium" | "large" | "xlarge" | number;";,"";
online?: boolean;
style?: ViewStyle;
}
}
  testID?: string;}";"";
}";,"";
const AgentAvatar: React.FC<AgentAvatarProps  /> = ({/   performanceMonitor: usePerformanceMonitor(AgentAvatar", { /    ";))"}""/;,"/g,"/;
  trackRender: true,trackMemory: false,warnThreshold: 100;};);";,"";
agent,";,"";
size = 'medium','';
online,;
style,;
testID;
}) => {}
  const  getSize = useCallback => {}
  const  getAgentConfig = useCallback() => {';,}switch (agent) {";,}case "xiaoai": ";,"";
return {";}";,"";
case "xiaoke": ";,"";
return {";}";,"";
case "laoke": ";,"";
return {";}";,"";
case "soer": ";,"";
return {default: return {,;}}
}
    ;}
  };
agentConfig: useMemo() => getAgentConfig(), []);)))));
const avatarStyle = useMemo() => [;];);
styles.base,;
    {width: avatarSize}height: avatarSize,;
}
      borderRadius: avatarSize / 2,/          backgroundColor: agentConfig.backgroundColor;}/;/g/;
    }
style;
];
  ].filter(Boolean); as ViewStyle[], []);
performanceMonitor.recordRender();
return (;);
    <View style={styles.container} testID={testID}  />/      <View style={avatarStyle}}  />/            <Text;  />/;,/g/;
style={";}}"";
            fontSize: avatarSize * 0.4,"}";
const textAlign = "center";}} />/              {agentConfig.emoji}"/;"/g"/;
        </Text>/      </View>//;/g/;
      {online !== undefined  && <View;  />/;,}style={[;,]styles.statusIndicator,;}            {width: avatarSize * 0.25}height: avatarSize * 0.25,;,/g,/;
  borderRadius: (avatarSize * 0.25) / 2,/              backgroundColor: online ? colors.success : colors.gray400,/;/g/;
}
              right: avatarSize * 0.05,}
              const bottom = avatarSize * 0.05;}}
];
          ]};
        />/          )};/;/g/;
    </View>/      ;);"/;"/g"/;
};";,"";
styles: useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => StyleSheet.create({ container: {position: "relative";},)";,"";
base: {,";,}alignItems: "center";","";"";
}
    justifyContent: "center";","}";,"";
overflow: "hidden";},";,"";
statusIndicator: {,";,}position: "absolute";","";"";
}
    borderWidth: 2,}
    const borderColor = colors.white;}
}), []);";,"";
export default React.memo(AgentAvatar);""";