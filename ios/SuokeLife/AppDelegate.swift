import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
  var window: UIWindow?

  func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {

    // 创建窗口
    self.window = UIWindow(frame: UIScreen.main.bounds)

    // 创建一个简单的视图控制器
    let rootViewController = UIViewController()
    rootViewController.view.backgroundColor = UIColor.systemBackground

    // 创建主界面
    let stackView = UIStackView()
    stackView.axis = .vertical
    stackView.alignment = .center
    stackView.spacing = 20
    stackView.translatesAutoresizingMaskIntoConstraints = false

    // 标题
    let titleLabel = UILabel()
    titleLabel.text = "索克生活"
    titleLabel.font = UIFont.systemFont(ofSize: 32, weight: .bold)
    titleLabel.textColor = UIColor.label

    // 副标题
    let subtitleLabel = UILabel()
    subtitleLabel.text = "你的智慧健康管理伙伴"
    subtitleLabel.font = UIFont.systemFont(ofSize: 18, weight: .medium)
    subtitleLabel.textColor = UIColor.secondaryLabel

    // 状态标签
    let statusLabel = UILabel()
    statusLabel.text = "React Native界面已准备就绪"
    statusLabel.font = UIFont.systemFont(ofSize: 16)
    statusLabel.textColor = UIColor.systemBlue

    // 进入按钮
    let enterButton = UIButton(type: .system)
    enterButton.setTitle("进入应用", for: .normal)
    enterButton.titleLabel?.font = UIFont.systemFont(ofSize: 18, weight: .medium)
    enterButton.backgroundColor = UIColor.systemBlue
    enterButton.setTitleColor(UIColor.white, for: .normal)
    enterButton.layer.cornerRadius = 8
    enterButton.addTarget(self, action: #selector(enterAppTapped), for: .touchUpInside)

    // 设置按钮约束
    enterButton.translatesAutoresizingMaskIntoConstraints = false
    NSLayoutConstraint.activate([
      enterButton.widthAnchor.constraint(equalToConstant: 200),
      enterButton.heightAnchor.constraint(equalToConstant: 50)
    ])

    // 添加到堆栈视图
    stackView.addArrangedSubview(titleLabel)
    stackView.addArrangedSubview(subtitleLabel)
    stackView.addArrangedSubview(statusLabel)
    stackView.addArrangedSubview(enterButton)

    // 添加欢迎卡片
    let welcomeCard = createWelcomeCard()
    stackView.insertArrangedSubview(welcomeCard, at: 0)

    // 添加智能体助手区域
    let agentSection = createAgentSection()
    stackView.addArrangedSubview(agentSection)

    // 添加健康数据概览
    let healthSection = createHealthSection()
    stackView.addArrangedSubview(healthSection)

    // 添加快捷功能
    let quickActions = createQuickActions()
    stackView.addArrangedSubview(quickActions)

    // 添加到主视图
    rootViewController.view.addSubview(stackView)

    // 设置约束
    NSLayoutConstraint.activate([
      stackView.centerXAnchor.constraint(equalTo: rootViewController.view.centerXAnchor),
      stackView.centerYAnchor.constraint(equalTo: rootViewController.view.centerYAnchor),
      stackView.leadingAnchor.constraint(greaterThanOrEqualTo: rootViewController.view.leadingAnchor, constant: 20),
      stackView.trailingAnchor.constraint(lessThanOrEqualTo: rootViewController.view.trailingAnchor, constant: -20)
    ])

    self.window?.rootViewController = rootViewController
    self.window?.makeKeyAndVisible()

    return true
  }

  @objc func enterAppTapped() {
    // 这里可以跳转到React Native界面或其他功能
    print("用户点击了进入应用按钮")
    
    // 显示提示
    let alert = UIAlertController(title: "欢迎", message: "欢迎使用索克生活！", preferredStyle: .alert)
    alert.addAction(UIAlertAction(title: "确定", style: .default))
    window?.rootViewController?.present(alert, animated: true)
  }

  // 创建欢迎卡片
  func createWelcomeCard() -> UIView {
    let cardView = UIView()
    cardView.backgroundColor = UIColor.systemBlue.withAlphaComponent(0.1)
    cardView.layer.cornerRadius = 12
    cardView.translatesAutoresizingMaskIntoConstraints = false

    let label = UILabel()
    label.text = "🌟 欢迎来到索克生活"
    label.font = UIFont.systemFont(ofSize: 20, weight: .semibold)
    label.textColor = UIColor.systemBlue
    label.textAlignment = .center
    label.translatesAutoresizingMaskIntoConstraints = false

    cardView.addSubview(label)
    NSLayoutConstraint.activate([
      label.centerXAnchor.constraint(equalTo: cardView.centerXAnchor),
      label.centerYAnchor.constraint(equalTo: cardView.centerYAnchor),
      cardView.widthAnchor.constraint(equalToConstant: 300),
      cardView.heightAnchor.constraint(equalToConstant: 60)
    ])

    return cardView
  }

  // 创建智能体助手区域
  func createAgentSection() -> UIView {
    let sectionView = UIView()
    sectionView.translatesAutoresizingMaskIntoConstraints = false

    let titleLabel = UILabel()
    titleLabel.text = "🤖 智能体助手"
    titleLabel.font = UIFont.systemFont(ofSize: 18, weight: .semibold)
    titleLabel.translatesAutoresizingMaskIntoConstraints = false

    let agentStackView = UIStackView()
    agentStackView.axis = .horizontal
    agentStackView.distribution = .fillEqually
    agentStackView.spacing = 10
    agentStackView.translatesAutoresizingMaskIntoConstraints = false

    // 创建四个智能体卡片
    let agents: [(name: String, emoji: String, role: String)] = [
      ("小艾", "💊", "健康顾问"),
      ("小克", "🏃‍♂️", "运动教练"),
      ("老克", "🌿", "中医专家"),
      ("索儿", "📊", "数据分析")
    ]

    for (index, agent) in agents.enumerated() {
      let agentCard = createAgentCard(name: agent.name, emoji: agent.emoji, role: agent.role, tagIndex: index)
      agentStackView.addArrangedSubview(agentCard)
    }

    sectionView.addSubview(titleLabel)
    sectionView.addSubview(agentStackView)

    NSLayoutConstraint.activate([
      titleLabel.topAnchor.constraint(equalTo: sectionView.topAnchor),
      titleLabel.centerXAnchor.constraint(equalTo: sectionView.centerXAnchor),
      agentStackView.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 10),
      agentStackView.leadingAnchor.constraint(equalTo: sectionView.leadingAnchor),
      agentStackView.trailingAnchor.constraint(equalTo: sectionView.trailingAnchor),
      agentStackView.bottomAnchor.constraint(equalTo: sectionView.bottomAnchor),
      agentStackView.widthAnchor.constraint(equalToConstant: 320),
      agentStackView.heightAnchor.constraint(equalToConstant: 80)
    ])

    return sectionView
  }

  // 创建智能体卡片
  func createAgentCard(name: String, emoji: String, role: String, tagIndex: Int) -> UIView {
    let cardView = UIView()
    cardView.backgroundColor = UIColor.systemGray6
    cardView.layer.cornerRadius = 8
    cardView.translatesAutoresizingMaskIntoConstraints = false

    let stackView = UIStackView()
    stackView.axis = .vertical
    stackView.alignment = .center
    stackView.spacing = 4
    stackView.translatesAutoresizingMaskIntoConstraints = false

    let emojiLabel = UILabel()
    emojiLabel.text = emoji
    emojiLabel.font = UIFont.systemFont(ofSize: 24)

    let nameLabel = UILabel()
    nameLabel.text = name
    nameLabel.font = UIFont.systemFont(ofSize: 14, weight: .medium)

    let roleLabel = UILabel()
    roleLabel.text = role
    roleLabel.font = UIFont.systemFont(ofSize: 10)
    roleLabel.textColor = UIColor.secondaryLabel

    stackView.addArrangedSubview(emojiLabel)
    stackView.addArrangedSubview(nameLabel)
    stackView.addArrangedSubview(roleLabel)

    cardView.addSubview(stackView)
    NSLayoutConstraint.activate([
      stackView.centerXAnchor.constraint(equalTo: cardView.centerXAnchor),
      stackView.centerYAnchor.constraint(equalTo: cardView.centerYAnchor)
    ])

    // 添加点击手势
    let tapGesture = UITapGestureRecognizer(target: self, action: #selector(agentCardTapped(_:)))
    cardView.addGestureRecognizer(tapGesture)
    cardView.tag = tagIndex

    return cardView
  }

  @objc func agentCardTapped(_ gesture: UITapGestureRecognizer) {
    guard let cardView = gesture.view else { return }
    let agentNames = ["小艾", "小克", "老克", "索儿"]
    let agentName = agentNames[cardView.tag]
    
    let alert = UIAlertController(title: "智能体", message: "您选择了\(agentName)！", preferredStyle: .alert)
    alert.addAction(UIAlertAction(title: "确定", style: .default))
    window?.rootViewController?.present(alert, animated: true)
  }

  // 创建健康数据概览
  func createHealthSection() -> UIView {
    let sectionView = UIView()
    sectionView.translatesAutoresizingMaskIntoConstraints = false

    let titleLabel = UILabel()
    titleLabel.text = "📊 健康数据概览"
    titleLabel.font = UIFont.systemFont(ofSize: 18, weight: .semibold)
    titleLabel.translatesAutoresizingMaskIntoConstraints = false

    let dataStackView = UIStackView()
    dataStackView.axis = .horizontal
    dataStackView.distribution = .fillEqually
    dataStackView.spacing = 10
    dataStackView.translatesAutoresizingMaskIntoConstraints = false

    // 创建健康数据卡片
    let healthData = [
      ("步数", "8,234", "👟"),
      ("心率", "72 bpm", "❤️"),
      ("睡眠", "7.5h", "😴")
    ]

    for data in healthData {
      let dataCard = createHealthDataCard(title: data.0, value: data.1, emoji: data.2)
      dataStackView.addArrangedSubview(dataCard)
    }

    sectionView.addSubview(titleLabel)
    sectionView.addSubview(dataStackView)

    NSLayoutConstraint.activate([
      titleLabel.topAnchor.constraint(equalTo: sectionView.topAnchor),
      titleLabel.centerXAnchor.constraint(equalTo: sectionView.centerXAnchor),
      dataStackView.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 10),
      dataStackView.leadingAnchor.constraint(equalTo: sectionView.leadingAnchor),
      dataStackView.trailingAnchor.constraint(equalTo: sectionView.trailingAnchor),
      dataStackView.bottomAnchor.constraint(equalTo: sectionView.bottomAnchor),
      dataStackView.widthAnchor.constraint(equalToConstant: 300),
      dataStackView.heightAnchor.constraint(equalToConstant: 70)
    ])

    return sectionView
  }

  // 创建健康数据卡片
  func createHealthDataCard(title: String, value: String, emoji: String) -> UIView {
    let cardView = UIView()
    cardView.backgroundColor = UIColor.systemGreen.withAlphaComponent(0.1)
    cardView.layer.cornerRadius = 8
    cardView.translatesAutoresizingMaskIntoConstraints = false

    let stackView = UIStackView()
    stackView.axis = .vertical
    stackView.alignment = .center
    stackView.spacing = 2
    stackView.translatesAutoresizingMaskIntoConstraints = false

    let emojiLabel = UILabel()
    emojiLabel.text = emoji
    emojiLabel.font = UIFont.systemFont(ofSize: 20)

    let valueLabel = UILabel()
    valueLabel.text = value
    valueLabel.font = UIFont.systemFont(ofSize: 14, weight: .semibold)

    let titleLabel = UILabel()
    titleLabel.text = title
    titleLabel.font = UIFont.systemFont(ofSize: 10)
    titleLabel.textColor = UIColor.secondaryLabel

    stackView.addArrangedSubview(emojiLabel)
    stackView.addArrangedSubview(valueLabel)
    stackView.addArrangedSubview(titleLabel)

    cardView.addSubview(stackView)
    NSLayoutConstraint.activate([
      stackView.centerXAnchor.constraint(equalTo: cardView.centerXAnchor),
      stackView.centerYAnchor.constraint(equalTo: cardView.centerYAnchor)
    ])

    // 添加点击手势
    let tapGesture = UITapGestureRecognizer(target: self, action: #selector(healthDataTapped))
    cardView.addGestureRecognizer(tapGesture)

    return cardView
  }

  @objc func healthDataTapped() {
    let alert = UIAlertController(title: "健康数据", message: "查看详细健康数据", preferredStyle: .alert)
    alert.addAction(UIAlertAction(title: "确定", style: .default))
    window?.rootViewController?.present(alert, animated: true)
  }

  // 创建快捷功能
  func createQuickActions() -> UIView {
    let sectionView = UIView()
    sectionView.translatesAutoresizingMaskIntoConstraints = false

    let titleLabel = UILabel()
    titleLabel.text = "⚡ 快捷功能"
    titleLabel.font = UIFont.systemFont(ofSize: 18, weight: .semibold)
    titleLabel.translatesAutoresizingMaskIntoConstraints = false

    let actionStackView = UIStackView()
    actionStackView.axis = .horizontal
    actionStackView.distribution = .fillEqually
    actionStackView.spacing = 10
    actionStackView.translatesAutoresizingMaskIntoConstraints = false

    // 创建快捷功能按钮
    let actions = [
      ("四诊", "🔍"),
      ("体质", "🧬"),
      ("记录", "📝"),
      ("设置", "⚙️")
    ]

    for action in actions {
      let actionButton = createActionButton(title: action.0, emoji: action.1)
      actionStackView.addArrangedSubview(actionButton)
    }

    sectionView.addSubview(titleLabel)
    sectionView.addSubview(actionStackView)

    NSLayoutConstraint.activate([
      titleLabel.topAnchor.constraint(equalTo: sectionView.topAnchor),
      titleLabel.centerXAnchor.constraint(equalTo: sectionView.centerXAnchor),
      actionStackView.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 10),
      actionStackView.leadingAnchor.constraint(equalTo: sectionView.leadingAnchor),
      actionStackView.trailingAnchor.constraint(equalTo: sectionView.trailingAnchor),
      actionStackView.bottomAnchor.constraint(equalTo: sectionView.bottomAnchor),
      actionStackView.widthAnchor.constraint(equalToConstant: 280),
      actionStackView.heightAnchor.constraint(equalToConstant: 60)
    ])

    return sectionView
  }

  // 创建功能按钮
  func createActionButton(title: String, emoji: String) -> UIView {
    let buttonView = UIView()
    buttonView.backgroundColor = UIColor.systemOrange.withAlphaComponent(0.1)
    buttonView.layer.cornerRadius = 8
    buttonView.translatesAutoresizingMaskIntoConstraints = false

    let stackView = UIStackView()
    stackView.axis = .vertical
    stackView.alignment = .center
    stackView.spacing = 4
    stackView.translatesAutoresizingMaskIntoConstraints = false

    let emojiLabel = UILabel()
    emojiLabel.text = emoji
    emojiLabel.font = UIFont.systemFont(ofSize: 20)

    let titleLabel = UILabel()
    titleLabel.text = title
    titleLabel.font = UIFont.systemFont(ofSize: 12, weight: .medium)

    stackView.addArrangedSubview(emojiLabel)
    stackView.addArrangedSubview(titleLabel)

    buttonView.addSubview(stackView)
    NSLayoutConstraint.activate([
      stackView.centerXAnchor.constraint(equalTo: buttonView.centerXAnchor),
      stackView.centerYAnchor.constraint(equalTo: buttonView.centerYAnchor)
    ])

    // 添加点击手势
    let tapGesture = UITapGestureRecognizer(target: self, action: #selector(quickActionTapped(_:)))
    buttonView.addGestureRecognizer(tapGesture)
    buttonView.accessibilityLabel = title

    return buttonView
  }

  @objc func quickActionTapped(_ gesture: UITapGestureRecognizer) {
    guard let buttonView = gesture.view,
          let title = buttonView.accessibilityLabel else { return }
    
    let alert = UIAlertController(title: "功能", message: "您选择了\(title)功能！", preferredStyle: .alert)
    alert.addAction(UIAlertAction(title: "确定", style: .default))
    window?.rootViewController?.present(alert, animated: true)
  }
}