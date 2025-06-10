
import React from "react";
;/importText from "./Text";/    importReact from "react;
// * 索克生活 - AgentAvatar组件;
* 智能体头像组件，为四个智能体提供特色头像
export interface AgentAvatarProps {
  agent: "xiaoai" | "xiaoke" | "laoke" | "soer";
  size?: "small" | "medium" | "large" | "xlarge" | number;
  online?: boolean;
  style?: ViewStyle;
  testID?: string;
}
const AgentAvatar: React.FC<AgentAvatarProps /> = ({/   const performanceMonitor = usePerformanceMonitor(AgentAvatar", { /    ";))
    trackRender: true,trackMemory: false,warnThreshold: 100;};);
  agent,
  size = "medium",
  online,
  style,
  testID;
}) => {}
  const getSize = useCallback => {}
  const getAgentConfig = useCallback() => {
    switch (agent) {
      case "xiaoai":
        return {


      case "xiaoke":
        return {


      case "laoke":
        return {


      case "soer":
        return {


      default:
        return {,


    ;}
  };
  const agentConfig = useMemo() => getAgentConfig(), []);)))));
  const avatarStyle = useMemo() => [;)
    styles.base,
    {
      width: avatarSize;
      height: avatarSize;
      borderRadius: avatarSize / 2,/          backgroundColor: agentConfig.backgroundColor;
    },
    style;
  ].filter(Boolean); as ViewStyle[], []);
  performanceMonitor.recordRender();
  return (;)
    <View style={styles.container} testID={testID} />/      <View style={avatarStyle}} />/            <Text;
style={
            fontSize: avatarSize * 0.4;
            textAlign: "center";}} />/              {agentConfig.emoji}
        </Text>/      </View>/
      {online !== undefined  && <View;
style={[
            styles.statusIndicator,
            {
              width: avatarSize * 0.25;
              height: avatarSize * 0.25;
              borderRadius: (avatarSize * 0.25) / 2,/              backgroundColor: online ? colors.success : colors.gray400;
              right: avatarSize * 0.05;
              bottom: avatarSize * 0.05;}}
          ]};
        />/          )};
    </View>/      ;);
};
const styles = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => StyleSheet.create({ container: {position: "relative";},)
  base: {,
  alignItems: "center";
    justifyContent: "center";
    overflow: "hidden";},
  statusIndicator: {,
  position: "absolute";
    borderWidth: 2;
    borderColor: colors.white;}
}), []);
export default React.memo(AgentAvatar);