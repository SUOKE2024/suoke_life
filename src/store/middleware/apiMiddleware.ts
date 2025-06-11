 API中间件 - 统一处理API请求和响应 /     export const apiMiddleware: Middleware  = (store) => (next) => (action: unknown) => {;};
if (action.type && typeof action.type === "string") {const { type   } = acti;";"";
o;n;";"";
if (type.endsWith(" / pending")) {  可以在这里添加全局loading逻辑 // }"/;"/g"/;
if (type.endsWith(" / fulfilled")) {/;}if (shouldShowSuccessNotification(type)) {";}const message = getSuccessMessage(typ;e;);"/g"/;
if (message) {}}
          store.dispatch(showSuccessNotification(message);)}
        }
      }";
    }";"";
if (type.endsWith(" / rejected")) {/;}*/g"/;
}
      store.dispatch(showErrorNotification(errorMessage););}
    }
  }
  return next(actio;n;);
};
//"/;"/g"/;
const successNotificationActions = [;];";
];
    "auth/login/fulfilled",/    "auth/register/fulfilled",/    "user/updateProfile/fulfilled",/    "diagnosis/completeSession/fulfilled",/    "health/syncData/fulfilled",/      ;];"/;"/g"/;
return successNotificationActions.some(patter;n;) => {}";"";
actionType.includes(pattern.split("/")[0])/      );"/;"/g"/;
}";
//"/;"/g"/;
const messageMap: Record<string, string> = {"auth/login/fulfilled": "登录成功",/    "auth/register/fulfilled": "注册成功",/    "auth/logout/fulfilled": "退出登录成功",/    "user/updateProfile/fulfilled": "资料更新成功",/    "diagnosis/completeSession/fulfilled": "诊断完成",/    "health/syncData/fulfilled": "健康数据同步成功",/      ;}"/;"/g"/;
for (const [pattern, message] of Object.entries(messageMap);) {if (actionType.includes(pattern);) {}}
      return messa;g;e;}
    }
  }
  return nu;l;l;
}";"";
export default apiMiddleware;""";
