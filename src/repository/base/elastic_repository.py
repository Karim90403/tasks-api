from typing import Any, Dict, List, Optional


class BaseElasticRepository:
    def parse_shift_history(self, shifts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for hit in shifts:
            src = hit["_source"]
            project = {"project_id": src.get("project_id"), "project_name": src.get("project_name")}
            for stage in src.get("work_stages", []):
                for wk in stage.get("work_kinds", []):
                    for wt in wk.get("work_types", []):
                        self._collect_task_entries(
                            results=results,
                            project=project,
                            task_container=wt,
                            work_type=wt,
                            work_kind=wk,
                        )
        # необязательно, но удобно: сортировка по start_time
        results.sort(key=lambda x: (x.get("start_time") or ""))
        return results

    @staticmethod
    def _collect_task_entries(
        *,
        results: List[Dict[str, Any]],
        project: Dict[str, Any],
        task_container: Dict[str, Any],
        work_type: Optional[Dict[str, Any]],
        work_kind: Optional[Dict[str, Any]],
    ) -> None:
        tasks = task_container.get("tasks", [])
        if not tasks:
            return

        for task in tasks:
            for ti in task.get("time_intervals", []):
                results.append({
                    "type": "task",
                    "project_id": project.get("project_id"),
                    "project_name": project.get("project_name"),
                    "task_id": task.get("task_id"),
                    "task_name": task.get("task_name"),
                    "work_type_id": work_type.get("work_type_id") if work_type else None,
                    "work_type_name": work_type.get("work_type_name") if work_type else None,
                    "work_kind_id": work_kind.get("work_kind_id") if work_kind else None,
                    "work_kind_name": work_kind.get("work_kind_name") if work_kind else None,
                    "start_time": ti.get("start_time"),
                    "end_time": ti.get("end_time"),
                    "status": ti.get("status"),
                })
            for sub in task.get("subtasks", []):
                for ti in sub.get("time_intervals", []):
                    results.append({
                        "type": "subtask",
                        "project_id": project.get("project_id"),
                        "project_name": project.get("project_name"),
                        "task_id": task.get("task_id"),
                        "task_name": task.get("task_name"),
                        "subtask_id": sub.get("subtask_id"),
                        "subtask_name": sub.get("subtask_name"),
                        "work_type_id": work_type.get("work_type_id") if work_type else None,
                        "work_type_name": work_type.get("work_type_name") if work_type else None,
                        "work_kind_id": work_kind.get("work_kind_id") if work_kind else None,
                        "work_kind_name": work_kind.get("work_kind_name") if work_kind else None,
                        "start_time": ti.get("start_time"),
                        "end_time": ti.get("end_time"),
                        "status": ti.get("status"),
                    })
