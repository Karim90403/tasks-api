from __future__ import annotations

from datetime import date, datetime
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, root_validator

from schemas.brigade_member import BrigadeMember


class TimeInterval(BaseModel):
    start_time: Optional[datetime] = Field(None, description="Начало интервала (ISO datetime)")
    end_time: Optional[datetime] = Field(None, description="Конец интервала (ISO datetime)")
    status: Optional[str] = Field(None, description="Статус интервала")


class DateRange(BaseModel):
    start: Optional[date] = Field(None, description="Дата начала")
    end: Optional[date] = Field(None, description="Дата окончания")


class DeadlineRange(BaseModel):
    start_time: Optional[date] = Field(None, description="Дата начала дедлайна")
    end_time: Optional[date] = Field(None, description="Дата окончания дедлайна")


class MachineInfo(BaseModel):
    hours: Optional[float] = Field(None, description="Количество часов работы техники")
    number: Optional[str] = Field(None, description="Идентификатор или номер техники")


class ReportLink(BaseModel):
    title: Optional[str] = Field(None, description="Название файла")
    href: Optional[str] = Field(None, description="Ссылка на файл")


class BrigadeSnapshot(BaseModel):
    brigade_name: Optional[str] = Field(None, description="Имя бригады на момент назначения")
    members: List[BrigadeMember] = Field(default_factory=list, description="Состав бригады")


class Subtask(BaseModel):
    subtask_id: str = Field(..., description="Идентификатор подзадачи")
    subtask_name: Optional[str] = Field(None, description="Название подзадачи")
    subtask_status: Optional[str] = Field(None, description="Статус подзадачи")
    subtask_description: Optional[str] = Field(None, description="Описание подзадачи")
    brigade_id: Optional[str] = Field(None, description="ID бригады, назначенной на подзадачу")
    brigade_snapshot: Optional[BrigadeSnapshot] = Field(
        None, description="Состав бригады на момент назначения"
    )
    properties: Optional[DateRange] = Field(None, description="Плановые даты выполнения")
    deadline: Optional[DeadlineRange] = Field(None, description="Дедлайн выполнения подзадачи")
    plannedQty: Optional[float] = Field(None, description="Плановый объём работ")
    actualQty: Optional[float] = Field(None, description="Фактический объём работ")
    machine: Optional[MachineInfo] = Field(None, description="Информация о задействованной технике")
    reportLinks: List[ReportLink] = Field(default_factory=list, description="Ссылки на отчёты")
    time_intervals: List[TimeInterval] = Field(default_factory=list, description="Интервалы работы по подзадаче")

    @root_validator(pre=True)
    def _merge_deadline(cls, values: dict) -> dict:
        deadline = values.get("deadline")
        properties = values.get("properties")
        if properties is None and isinstance(deadline, dict):
            if {"start", "end"}.issubset(deadline.keys()):
                values["properties"] = deadline
            else:
                values["properties"] = {
                    "start": deadline.get("start_time"),
                    "end": deadline.get("end_time"),
                }
        if deadline is None and isinstance(properties, dict):
            values["deadline"] = {
                "start_time": properties.get("start"),
                "end_time": properties.get("end"),
            }
        return values

    class Config:
        extra = "allow"


class Task(BaseModel):
    task_id: str = Field(..., description="Идентификатор задачи")
    task_name: Optional[str] = Field(None, description="Название задачи")
    task_description: Optional[str] = Field(None, description="Описание задачи")
    task_status: Optional[str] = Field(None, description="Статус задачи")
    time_intervals: List[TimeInterval] = Field(default_factory=list, description="Интервалы работы по задаче")
    subtasks: List[Subtask] = Field(default_factory=list, description="Подзадачи")

    class Config:
        extra = "allow"


class WorkType(BaseModel):
    work_type_id: Optional[str] = Field(None, description="Идентификатор вида работ")
    work_type_name: Optional[str] = Field(None, description="Название вида работ")
    work_type_status: Optional[str] = Field(None, description="Статус вида работ")
    work_kind: List["WorkKind"] = Field(
        default_factory=list,
        description="Типы работ внутри вида работ",
    )
    tasks: List[Task] = Field(default_factory=list, description="Задачи вида работ (устаревшее поле)")

    class Config:
        extra = "allow"


class WorkKind(BaseModel):
    work_kind_id: Optional[str] = Field(None, description="Идентификатор типа работ")
    work_kind_name: Optional[str] = Field(None, description="Название типа работ")
    tasks: List[Task] = Field(default_factory=list, description="Задачи типа работ")

    class Config:
        extra = "allow"


class WorkStage(BaseModel):
    stage_id: str = Field(..., description="Идентификатор этапа")
    stage_name: Optional[str] = Field(None, description="Название этапа")
    stage_status: Optional[str] = Field(None, description="Статус этапа")
    work_types: List[WorkType] = Field(
        default_factory=list, description="Детализация по видам работ (если присутствует)"
    )

    class Config:
        extra = "allow"


class ConstructionProject(BaseModel):
    project_id: str = Field(..., description="Идентификатор проекта")
    project_name: Optional[str] = Field(None, description="Название проекта")
    foreman_id: Optional[str] = Field(None, description="Идентификатор прораба")
    foreman_email: Optional[str] = Field(None, description="Email прораба")
    work_stages: List[WorkStage] = Field(default_factory=list, description="Этапы проекта")

    class Config:
        extra = "allow"


class ProjectSummary(BaseModel):
    project_id: str = Field(..., description="Идентификатор проекта")
    project_name: Optional[str] = Field(None, description="Название проекта")

class StageWithProject(WorkStage):
    project_id: str = Field(..., description="Идентификатор проекта")
    project_name: Optional[str] = Field(None, description="Название проекта")

    class Config:
        extra = "allow"


class ShiftEntryBase(BaseModel):
    project_id: Optional[str] = Field(None, description="Идентификатор проекта")
    project_name: Optional[str] = Field(None, description="Название проекта")
    task_id: Optional[str] = Field(None, description="Идентификатор задачи")
    task_name: Optional[str] = Field(None, description="Название задачи")
    work_type_id: Optional[str] = Field(None, description="Идентификатор вида работ")
    work_type_name: Optional[str] = Field(None, description="Название вида работ")
    work_kind_id: Optional[str] = Field(None, description="Идентификатор типа работ")
    work_kind_name: Optional[str] = Field(None, description="Название типа работ")
    start_time: Optional[datetime] = Field(None, description="Начало работы")
    end_time: Optional[datetime] = Field(None, description="Окончание работы")
    status: Optional[str] = Field(None, description="Статус интервала")


class TaskShiftEntry(ShiftEntryBase):
    type: Literal["task"] = Field("task", description="Тип записи — задача")


class SubtaskShiftEntry(ShiftEntryBase):
    type: Literal["subtask"] = Field("subtask", description="Тип записи — подзадача")
    subtask_id: Optional[str] = Field(None, description="Идентификатор подзадачи")
    subtask_name: Optional[str] = Field(None, description="Название подзадачи")


ShiftHistoryEntry = Union[TaskShiftEntry, SubtaskShiftEntry]


class ShiftStatus(BaseModel):
    status: Literal["working", "not_working"] = Field(..., description="Текущий статус смены")


class OperationResult(BaseModel):
    result: str = Field(..., description="Результат операции")
    project_id: Optional[str] = Field(None, description="Идентификатор проекта, если применимо")

    class Config:
        extra = "allow"


WorkKind.update_forward_refs()
WorkType.update_forward_refs()
WorkStage.update_forward_refs()
ConstructionProject.update_forward_refs()
StageWithProject.update_forward_refs()
