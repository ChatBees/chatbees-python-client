import os
from croniter import croniter
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, model_validator
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


__all__ = [
    "IngestionType",
    "IngestionStatus",
    "ScheduleSpec",
    "IngestionSpec",
    "ConfluenceSpec",
    "GDriveSpec",
    "NotionSpec",
]


class IngestionType(Enum):
    CONFLUENCE = 'CONFLUENCE'
    GDRIVE = 'GDRIVE'
    NOTION = 'NOTION'
    HUBSPOT_TICKET = 'HUBSPOT_TICKET'


class IngestionStatus(Enum):
    RUNNING = 1
    SUCCEEDED = 2
    FAILED = 3


class ScheduleSpec(BaseModel):
    # same format with cron, like '0 0 * * 0' means midnight every Sunday
    # only support >= daily
    cron_expr: str
    # timezone string, such as UTC, America/Los_Angeles
    timezone: str

    @model_validator(mode='after')
    def validate_input(self) -> 'ScheduleSpec':
        try:
            # validate timezone
            tz = ZoneInfo(self.timezone)

            # validate cron_expr
            base_time = datetime.now(tz)
            croniter(self.cron_expr, base_time)

            # verify cron expr >= daily
            fields = self.cron_expr.split()
            if fields[0].startswith('*') or fields[1].startswith('*'):
                if os.environ.get('ENV_TEST_CRON', default='False').lower() == "true":
                    return self
                raise ValueError("minimal schedule internval is daily")
        except ZoneInfoNotFoundError as e:
            raise ValueError("Invalid timezone string")
        except Exception as e:
            raise ValueError("Invalid cron string")
        return self


class IngestionSpec(BaseModel):
    # API token for ingestion. If not set, server will get the access token
    # from the connector that is oauthed via UI.
    token: Optional[str] = None
    # periodical ingestion scheduling. run once if None.
    schedule: Optional[ScheduleSpec] = None


class ConfluenceSpec(IngestionSpec):
    url: str
    # if you connect Confluence via OAuth, no need to set username.
    # if you don't connect via OAuth, you can pass a confluence user and api token.
    username: Optional[str] = None
    # Specify space to ingest all pages in the space, or cql to ingest the
    # selected pages. Please specify either space or cql, not both.
    space: Optional[str] = None
    cql: Optional[str] = None

    @model_validator(mode='after')
    def validate_input(self) -> 'ConfluenceSpec':
        if self.space is None and self.cql is None:
            raise ValueError("Please specify space or cql")
        if self.space is not None and self.cql is not None:
            raise ValueError("Please specify only space or cql, not both")
        return self


class GDriveSpec(IngestionSpec):
    folder_name: Optional[str] = None


class NotionSpec(IngestionSpec):
    page_ids: Optional[List[str]] = None
