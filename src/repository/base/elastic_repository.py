from typing import Any, Dict, List


class BaseElasticRepository:
    @staticmethod
    def parse_shift_history(shifts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for hit in shifts:
            src = hit["_source"]
            project = {"project_id": src.get("project_id"), "project_name": src.get("project_name")}
            ws = src.get("work_stages", [])
            for stage in ws:
                for wt in stage.get("work_types", []):
                    for task in wt.get("tasks", []):
                        # интервалы задач
                        for ti in task.get("time_intervals", []):
                            results.append({
                                "type": "task",
                                "project_id": project["project_id"],
                                "project_name": project["project_name"],
                                "task_id": task.get("task_id"),
                                "task_name": task.get("task_name"),
                                "start_time": ti.get("start_time"),
                                "end_time": ti.get("end_time"),
                                "status": ti.get("status"),
                            })
                        # интервалы подзадач
                        for sub in task.get("subtasks", []):
                            for ti in sub.get("time_intervals", []):
                                results.append({
                                    "type": "subtask",
                                    "project_id": project["project_id"],
                                    "project_name": project["project_name"],
                                    "task_id": task.get("task_id"),
                                    "task_name": task.get("task_name"),
                                    "subtask_id": sub.get("subtask_id"),
                                    "subtask_name": sub.get("subtask_name"),
                                    "start_time": ti.get("start_time"),
                                    "end_time": ti.get("end_time"),
                                    "status": ti.get("status"),
                                })
        # необязательно, но удобно: сортировка по start_time
        results.sort(key=lambda x: (x.get("start_time") or ""))
        return results


