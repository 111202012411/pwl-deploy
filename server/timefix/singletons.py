#!/usr/bin/env python

import datetime as dt
import io
import tempfile
import time

from abc import ABC, abstractclassmethod, abstractmethod
from typing import Any, Dict, List, Tuple, TypeVar, Union


class DateInitError(Exception): pass
class CSVTimeZoneLoaderInitError(Exception): pass

CSVTimeZoneLoaderType: Any
CSVTimeZoneLoaderType = TypeVar('CSVTimeZoneLoaderType', bound='CSVTimeZoneLoaderType')

class CSVTimeZoneLoaderType(ABC):

    DIGITS: str

    TZ_FILE_PATH: str
    TZ_FILE_STREAM: Union[io.TextIOWrapper, io.BytesIO, io.StringIO, tempfile._TemporaryFileWrapper, None]

    TZ_TABLE_DATA: List[Dict[str, str]]
    
    @abstractmethod
    def __init__(self: CSVTimeZoneLoaderType, tzfile: Union[str, io.TextIOWrapper, io.BytesIO, io.StringIO, tempfile._TemporaryFileWrapper]) -> None: pass

    @abstractmethod
    def init(self: CSVTimeZoneLoaderType) -> None: pass

    @abstractmethod
    def timezone(self: CSVTimeZoneLoaderType, td_str: str) -> dt.timezone: pass

    @abstractmethod
    def timedelta(self: CSVTimeZoneLoaderType, td_str: str) -> dt.timedelta: pass

    @abstractmethod
    def get_tzname(self: CSVTimeZoneLoaderType, td_str: str) -> str: pass

    @abstractmethod
    def get_td(self: CSVTimeZoneLoaderType, country_code: str = "", tzname: str = "", tzinfo: str = "", timedelta: str = "") -> str: pass

    @abstractmethod
    def get_tzinfo(self: CSVTimeZoneLoaderType, country_code: str = "", tzname: str = "") -> str: pass

class DateTimeInitError(Exception): pass

DateTimeType: Any
DateTimeType = TypeVar("DateTimeType", bound="DateTimeType")

class DateTimeType(ABC):

    COUNTRY_CODE: str

    DATETIME: dt.datetime

    TZ_NAME: str
    TZ_INFO: str
    
    TIMEDELTA: str
    # TIMESTAMP: int

    CTZ: CSVTimeZoneLoaderType

    @abstractmethod
    def __init__(self: DateTimeType) -> None: pass

    @abstractmethod
    def __repr__(self: DateTimeType) -> str: pass

    @abstractmethod
    def __str__(self: DateTimeType) -> str: pass

    @abstractmethod
    def init(self: DateTimeType) -> None: pass

    @abstractmethod
    def set_ctz(self: DateTimeType, ctz: CSVTimeZoneLoaderType) -> bool: pass

    @abstractmethod
    def ch_tz(self: DateTimeType, country_code: str = "", tzinfo: str = "", tzname: str = "") -> bool: pass

    @abstractmethod
    def str_to_dt(self: DateTimeType, context: str, tz: Union[dt.timezone, None] = None) -> dt.datetime: pass

    @abstractmethod
    def to_dt(self: DateTimeType, td_str: str = "") -> dt.datetime: pass

    @abstractmethod
    def set_dt_from(self: DateTimeType, dt: dt.datetime) -> None: pass

    @abstractmethod
    def ch_dt_from(self: DateTimeType, dt: dt.datetime) -> None: pass

    @abstractmethod
    def to_str(self: DateTimeType, years: int = 0, month: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0, microseconds: int = 0) -> str: pass

    @abstractmethod
    def date_fix(self: DateTimeType, years: int = 0, month: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0, microseconds: int = 0) -> Tuple[int, ...]: pass
    
    @abstractmethod
    def enhance_tm_sec(self: DateTimeType, sec: int) -> DateTimeType: pass

    @abstractmethod
    def enhance_tm_ms(self: DateTimeType, ms: int) -> DateTimeType: pass

    @abstractmethod
    def enhance_tm_us(self: DateTimeType, us: int) -> DateTimeType: pass

    @abstractmethod
    def enhance_tm_auto(self: DateTimeType, years: int = 0, month: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, sec: int = 0, ms: int = 0, us: int = 0) -> DateTimeType: pass

    @abstractmethod
    def get_struct_tm(self: DateTimeType, years: int = 0, month: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, weekdays: int = 0, yeardays: int = 0, is_dst: int = -1) -> time.struct_time: pass

    @abstractmethod
    def get_year(self: DateTimeType) -> int: pass

    @abstractmethod
    def get_month(self: DateTimeType) -> int: pass

    @abstractmethod
    def get_mon(self: DateTimeType, years: int = 0, month: int = 0) -> int: pass

    @abstractmethod
    def get_weekday(self: DateTimeType, years: int = 0, month: int = 0, days: int = 0) -> int: pass

    # @abstractmethod
    # def __get_weekday(self: DateTimeType, years: int, month: int, days: int, start_at_years: int, start_at_wdays: int) -> int: pass

    @abstractmethod
    def get_day(self: DateTimeType) -> int: pass

    @abstractmethod
    def get_yearday(self: DateTimeType, years: int = 0, month: int = 0, days: int = 0) -> int: pass

    @abstractmethod
    def get_hours(self: DateTimeType) -> int: pass

    @abstractmethod
    def get_minutes(self: DateTimeType) -> int: pass

    @abstractmethod
    def get_seconds(self: DateTimeType) -> int: pass

    @abstractmethod
    def get_milliseconds(self: DateTimeType) -> int: pass

    @abstractmethod
    def get_microseconds(self: DateTimeType) -> int: pass

    @abstractmethod
    def is_dst(self: DateTimeType) -> int: pass


TimeFixType: Any
TimeFixType = TypeVar('TimeFixType', bound='TimeFixType')


class TimeFixType(ABC):

    MONTH_FULLNAMES: List[str]

    MONTH_NAMES: List[str]

    WEEKDAY_FULLNAMES: str

    WEEKDAY_NAMES: str

    TZ_DATA_BUFFER: io.BytesIO

    CTZ: CSVTimeZoneLoaderType

    @abstractmethod
    def __init__(self: TimeFixType, tzfile: Union[str, io.TextIOWrapper, io.BytesIO, io.StringIO, tempfile._TemporaryFileWrapper, None] = None) -> None: pass

    @abstractclassmethod
    def create_dt(cls: TimeFixType, dt: Union[int, float, str, dt.datetime, None] = None, tzname: str = "", tzinfo: str = "") -> DateTimeType: pass

    @abstractclassmethod
    def get_month(cls: TimeFixType, dt: DateTimeType) -> Tuple[int, str, str]: pass

    @abstractclassmethod
    def get_weekdays(cls: TimeFixType, dt: DateTimeType) -> Tuple[int, str, str]: pass

    @abstractclassmethod
    def enhance_tm_sec(cls: TimeFixType, dt: DateTimeType, sec: int) -> DateTimeType: pass

    @abstractclassmethod
    def enhance_tm_ms(cls: TimeFixType, dt: DateTimeType, ms: int) -> DateTimeType: pass

    @abstractclassmethod
    def enhance_tm_us(cls: TimeFixType, dt: DateTimeType, us: int) -> DateTimeType: pass

    @abstractclassmethod
    def to_str(cls: TimeFixType, dt: DateTimeType) -> DateTimeType: pass
