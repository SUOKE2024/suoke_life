class TCMFiveDiagnosisTask(BaseTask):
    """中医五诊诊断任务"""
    
    def __init__(self):
        super().__init__()
        self.task_name = "tcm_five_diagnosis"
        self.description = "中医五诊（望、闻、问、切、算）综合诊断评估"
        self.categories = ["望诊", "闻诊", "问诊", "切诊", "算诊"] 