import UIKit
// 暂时注释掉React_Native导入，使用本地定义的类
// import React_Native

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
  var window: UIWindow?

  func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    // 创建窗口
    self.window = UIWindow(frame: UIScreen.main.bounds)
    
    // 创建一个视图控制器作为根控制器
    let rootViewController = UIViewController()
    rootViewController.view.backgroundColor = UIColor.white
    
    // 创建并配置标签
    let label = UILabel(frame: CGRect(x: 0, y: 0, width: 280, height: 120))
    label.center = CGPoint(x: UIScreen.main.bounds.width / 2, y: UIScreen.main.bounds.height / 2)
    label.backgroundColor = UIColor(red: 0.95, green: 0.95, blue: 1.0, alpha: 1.0)
    label.layer.cornerRadius = 10
    label.layer.masksToBounds = true
    label.textAlignment = .center
    label.text = "SuokeLife App 正在加载中...\n请等待"
    label.textColor = UIColor.darkGray
    label.font = UIFont.systemFont(ofSize: 18, weight: .medium)
    label.numberOfLines = 0
    
    // 添加一个边框使其更明显
    label.layer.borderWidth = 1.0
    label.layer.borderColor = UIColor.lightGray.cgColor
    
    // 添加标签到根视图
    rootViewController.view.addSubview(label)
    
    // 设置根控制器并显示窗口
    self.window?.rootViewController = rootViewController
    self.window?.makeKeyAndVisible()
    
    // 添加日志输出以便调试
    print("SuokeLife App已启动，显示加载中标签")
    
    return true
  }
}
