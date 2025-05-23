import Foundation

// 这个文件是一个临时解决方案，用于解决"No such module 'React'"错误
// 它在Pod安装成功后应该被移除

// 创建一个桥接类，模拟React-Native中的类型
@objc class RCTAppDelegate: NSObject {
    @objc func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        return true
    }
}

@objc class RCTBridge: NSObject {}

@objc class RCTBundleURLProvider: NSObject {
    @objc static func sharedSettings() -> RCTBundleURLProvider {
        return RCTBundleURLProvider()
    }
    
    @objc func jsBundleURL(forBundleRoot bundleRoot: String) -> URL? {
        // 返回开发服务器URL或本地Bundle
        let defaultURL = Bundle.main.url(forResource: "main", withExtension: "jsbundle")
        return defaultURL
    }
}

@objc class RCTDefaultReactNativeFactoryDelegate: NSObject {
    @objc func sourceURL(for bridge: RCTBridge) -> URL? {
        return nil
    }
    
    @objc func bundleURL() -> URL? {
        return nil
    }
}

@objc class RCTReactNativeFactory: NSObject {} 