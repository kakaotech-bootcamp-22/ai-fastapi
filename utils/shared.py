# shared.py
tasks = {}

# tasks 형태 예시
'''

tasks = {
    "task_id_1": {
        "status": "COMPLETED",  # 작업 상태
        "result": {
            "requestId": "task_id_1",
            "blogUrl": "https://example.com",
            "summaryTitle": "<SUMMARY TITLE>",
            "summaryText": "<SUMMARY TEXT>",
            "score": 90,
            "evidence": "Minimal promotional language found"
        }
    },
    "task_id_2": {
        "status": "IN_PROGRESS",  # 작업 상태
        "result": None  # 아직 작업 결과가 없는 상태
    }
}


'''
