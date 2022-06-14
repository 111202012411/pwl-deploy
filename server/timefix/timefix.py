#!/usr/bin/env python

import csv
import io
import os
import datetime as dt
import tempfile
import time

from typing import Any, Dict, List, Tuple, TypeVar, Union
from .singletons import CSVTimeZoneLoaderInitError, CSVTimeZoneLoaderType, DateTimeInitError, DateTimeType, TimeFixType


CSVTimeZoneLoader: Any
CSVTimeZoneLoader = TypeVar('CSVTimeZoneLoader', bound='CSVTimeZoneLoader')

# ZERO: dt.timedelta
# ZERO = dt.timedelta(0)

class CSVTimeZoneLoader(CSVTimeZoneLoaderType):

    DIGITS: str
    DIGITS = "1234567890"

    TZ_FILE_PATH: str
    TZ_FILE_STREAM: Union[io.TextIOWrapper, io.BytesIO, io.StringIO, tempfile._TemporaryFileWrapper, None]

    TZ_TABLE_DATA: List[Dict[str, str]]

    def __init__(self: CSVTimeZoneLoader, tzfile: Union[str, io.TextIOWrapper, io.BytesIO, io.StringIO, tempfile._TemporaryFileWrapper]) -> None:
        
        if isinstance(tzfile, str):
        
            self.TZ_FILE_STREAM = None
            self.TZ_FILE_PATH = tzfile

        elif type(tzfile) in (io.TextIOWrapper, io.BytesIO, io.StringIO, tempfile._TemporaryFileWrapper):

            self.TZ_FILE_STREAM = tzfile
            self.TZ_FILE_PATH = ""

        self.init()

    def init(self: CSVTimeZoneLoader) -> None:

        text_stream: Union[io.TextIOWrapper, io.BytesIO, io.StringIO, tempfile._TemporaryFileWrapper, None]
        text_stream = None

        if self.TZ_FILE_STREAM:

            text_stream = self.TZ_FILE_STREAM

        elif self.TZ_FILE_PATH:

            if self.TZ_FILE_PATH.endswith(".csv"):

                if os.path.exists(self.TZ_FILE_PATH):

                    text_stream = open(self.TZ_FILE_PATH, "r")

        if text_stream:

            with text_stream as csvfile:

                ##* tricky, and bypassing
                if isinstance(csvfile, io.BytesIO) or not getattr(csvfile, "mode", "r") in ("r", "r+", "w+"):

                    ##* tricky, and bypassing
                    if not "b" in getattr(csvfile, "mode", "rb"):

                        raise CSVTimeZoneLoaderInitError(f"Invalid file mode.")

                    csvfile = io.TextIOWrapper(csvfile, encoding="utf-8")

                datz: csv.DictReader
                datz = csv.DictReader(
                    f=csvfile,
                    delimiter=',',
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                    fieldnames=["country_code","tzname","tzinfo","timedelta"],
                    restkey=None,
                    restval=None
                )

                ##* normalize the data
                self.TZ_TABLE_DATA = [ row for row in datz ]
        else:

            raise CSVTimeZoneLoaderInitError(f"No timezone file specified.")

    def timezone(self: CSVTimeZoneLoader, td_str: str) -> dt.timezone:

        if not td_str:

            raise CSVTimeZoneLoaderInitError(f"No timezone specified.")

        tzname: str
        tzname = self.get_tzname(td_str=td_str)
        return dt.timezone(offset=self.timedelta(td_str=td_str), name=tzname)

    def timedelta(self: CSVTimeZoneLoader, td_str: str) -> dt.timedelta:

        if not td_str:

            raise CSVTimeZoneLoaderInitError(f"No timezone specified.")

        pv: bool
        nv: bool

        pv = td_str.startswith("+")
        nv = td_str.startswith("-")
            
        hours: int
        minutes: int

        td_str = td_str.__getitem__(slice(1, None, 1)) if pv or nv else td_str
        
        #* checker is a string of digits
        for i in range(4):

            if td_str.__getitem__(slice(i, i + 1, 1)) not in self.DIGITS:

                raise CSVTimeZoneLoaderInitError(f"Invalid timezone string {td_str}")

        hours = int(td_str.__getitem__(slice(0, 2, 1)))
        minutes = int(td_str.__getitem__(slice(2, 4, 1)))

        td: dt.timedelta
        td = dt.timedelta(hours=hours, minutes=minutes)

        return td if pv or not nv else -td

    def get_tzname(self: CSVTimeZoneLoader, td_str: str) -> str:

        if not td_str:

            raise CSVTimeZoneLoaderInitError(f"No timezone specified.")

        _: str

        d: Any
        d = td_str.split(",")
        
        tz: str

        if len(d) == 2:

            _, tz = d

            return tz

        else:

            raise CSVTimeZoneLoaderInitError(f"Invalid timezone string {td_str}")

    def get_td(self: CSVTimeZoneLoader, country_code: str = "", tzname: str = "", tzinfo: str = "", timedelta: str = "") -> str:

        if hasattr(self, "TZ_TABLE_DATA"):

            fieldnames: List[str, Any, Any]
            fieldnames = []

            checker: List[str, Any, Any]
            checker = []

            if country_code:

                fieldnames.append("country_code")
                checker.append(country_code)

            if tzname:
                
                fieldnames.append("tzname")
                checker.append(tzname)

            if tzinfo:
                
                fieldnames.append("tzinfo")
                checker.append(tzinfo)

            if timedelta:

                fieldnames.append("timedelta")
                checker.append(timedelta)

            fieldnum: int
            fieldnum = len(fieldnames)

            checknum: int
            checknum = len(checker)

            if checknum == 0:

                raise CSVTimeZoneLoaderInitError(f"No country_code, tzname, or tzinfo specified.")

            for row in self.TZ_TABLE_DATA:

                passing: bool
                passing = True

                ##* checker is a list of strings
                for i in range(fieldnum):

                    if i < checknum:

                        key: str
                        value: str

                        key = fieldnames[i]
                        value = checker[i]

                        if row[key].lower() != value.lower():

                            passing = False
                            break

                    else:

                        break

                if passing:

                    if row["timedelta"] == "":

                        raise CSVTimeZoneLoaderInitError(f"No timedelta found!")

                    if row["tzname"] == "":

                        raise CSVTimeZoneLoaderInitError(f"No timezone name found!")

                    return row["timedelta"] + "," + row["tzname"]

                    # if not tzname:

                    #     if row["tzname"] == "":

                    #         raise CSVTimeZoneLoaderInitError(f"No timezone name found!")

                    #     return row["timedelta"] + "," + row["tzname"]

                    # else:

                    #     return row["timedelta"] + "," + tzname

        else:

            raise CSVTimeZoneLoaderInitError(f"CSVTimeZoneLoader has not been initialized.")
        
        return ""

    def get_tzinfo(self: CSVTimeZoneLoader, country_code: str = "", tzname: str = "") -> str:

        if hasattr(self, "TZ_TABLE_DATA"):

            fieldnames: List[str, Any, Any]
            fieldnames = []

            checker: List[str, Any, Any]
            checker = []

            if country_code:

                fieldnames.append("country_code")
                checker.append(country_code)

            if tzname:
                
                fieldnames.append("tzname")
                checker.append(tzname)

            fieldnum: int
            fieldnum = len(fieldnames)

            checknum: int
            checknum = len(checker)

            if checknum == 0:

                raise CSVTimeZoneLoaderInitError(f"No country_code, tzname, or tzinfo specified.")

            for row in self.TZ_TABLE_DATA:

                passing: bool
                passing = True

                ##* checker is a list of strings
                for i in range(fieldnum):

                    if i < checknum:

                        key: str
                        value: str

                        key = fieldnames[i]
                        value = checker[i]

                        if row[key].lower() != value.lower():

                            passing = False
                            break

                    else:

                        break

                if passing:

                    if row["tzinfo"] == "":

                        raise CSVTimeZoneLoaderInitError(f"No timezone info found!")

                    return row["tzinfo"]

        else:

            raise CSVTimeZoneLoaderInitError(f"CSVTimeZoneLoader has not been initialized.")
        
        return ""


DateTime: Any
DateTime = TypeVar("DateTime", bound="DateTime")

class DateTime(DateTimeType):

    COUNTRY_CODE: str

    DATETIME: dt.datetime

    TZ_NAME: str
    TZ_INFO: str
    
    TIMEDELTA: str
    # TIMESTAMP: int

    CTZ: CSVTimeZoneLoaderType

    def __init__(self: DateTime) -> None:

        self.init()

    def __repr__(self: DateTime) -> str:

        return f"<DateTime bound dt.datetime(\"{self.DATETIME}\") at {hex(id(self))}>"

    def __str__(self: DateTime) -> str:

        return self.to_str(
            years=self.get_year(),
            month=self.get_month(),
            days=self.get_day(),
            hours=self.get_hours(),
            minutes=self.get_minutes(),
            seconds=self.get_seconds(),
            milliseconds=0,
            microseconds=0,
        )

    def init(self: DateTime) -> None:

        if not hasattr(self, "COUNTRY_CODE"):
        
            self.COUNTRY_CODE = ""

        ##* priority
        ##* TZ_INFO
        ##* TZ_NAME

        ## todos: TZ_INFO ^ TZ_NAME (Logic if-statement)

        ##* looks like having fun Bugs
        if not hasattr(self, "TZ_INFO") and not hasattr(self, "TZ_NAME"):

            ##* default timezone
            self.TZ_INFO = "Etc/Universal"
            self.TZ_NAME = "UTC"
            self.TIMEDELTA = "+0000,UTC"
            self.DATETIME = dt.datetime.now(dt.timezone.utc)

        else:

            if hasattr(self, "TZ_NAME"):

                if hasattr(self, "CTZ"):

                    td_str: str
                    td_str = self.CTZ.get_td(tzname=self.TZ_NAME)

                    if td_str:

                        TIMEDELTA: str
                        TIMEDELTA = getattr(self, "TIMEDELTA", "+0000,UTC")

                        self.TZ_INFO = self.CTZ.get_tzinfo(tzname=self.TZ_NAME)
                        self.TIMEDELTA = td_str

                        ##* Optional
                        if not hasattr(self, "DATETIME"):
                            
                            self.DATETIME = dt.datetime.now(tz=self.CTZ.timezone(td_str=self.TIMEDELTA))

                        else:

                            self.DATETIME = self.DATETIME.replace(tzinfo=self.CTZ.timezone(td_str=self.TIMEDELTA)) -\
                                self.CTZ.timezone(td_str=TIMEDELTA).utcoffset(self.DATETIME) +\
                                    self.CTZ.timedelta(td_str=self.TIMEDELTA)


                    elif self.TZ_NAME == "UTC":

                        self.TZ_INFO = "Etc/Universal"
                        self.TIMEDELTA = "+0000,UTC"

                        ##* Optional
                        if not hasattr(self, "DATETIME"):

                            self.DATETIME = self.DATETIME = dt.datetime.now(dt.timezone.utc)

                    else:

                        raise CSVTimeZoneLoaderInitError(f"No timezone found for {self.TZ_INFO}.")

                else:

                    raise CSVTimeZoneLoaderInitError(f"No CSVTimeZoneLoader found.")

            elif hasattr(self, "TZ_INFO"):

                if hasattr(self, "CTZ"):

                    td_str: str
                    td_str = self.CTZ.get_td(tzinfo=self.TZ_INFO)

                    if td_str:

                        TIMEDELTA: str
                        TIMEDELTA = getattr(self, "TIMEDELTA", "+0000,UTC")

                        self.TZ_NAME = self.CTZ.get_tzname(td_str=td_str)
                        self.TIMEDELTA = td_str
                        
                        ##* Optional
                        if not hasattr(self, "DATETIME"):
                        
                            self.DATETIME = dt.datetime.now(tz=self.CTZ.timezone(td_str=self.TIMEDELTA))

                        else:

                            self.DATETIME = self.DATETIME.replace(tzinfo=self.CTZ.timezone(td_str=self.TIMEDELTA)) -\
                                self.CTZ.timezone(td_str=TIMEDELTA).utcoffset(self.DATETIME) +\
                                    self.CTZ.timedelta(td_str=self.TIMEDELTA)

                    elif self.TZ_INFO == "Etc/Universal":

                        self.TZ_NAME = "UTC"
                        self.TIMEDELTA = "+0000,UTC"

                        ##* Optional
                        if not hasattr(self, "DATETIME"):
                        
                            self.DATETIME = self.DATETIME = dt.datetime.now(dt.timezone.utc)

                    else:

                        raise CSVTimeZoneLoaderInitError(f"No timezone found for {self.TZ_INFO}.")

                else:

                    raise CSVTimeZoneLoaderInitError(f"No CSVTimeZoneLoader found.")

            else:

                raise CSVTimeZoneLoaderInitError(f"No country_code, tzname, or tzinfo specified.")
        
        pass

    def set_ctz(self: DateTime, ctz: CSVTimeZoneLoaderType) -> bool:

        if isinstance(ctz, CSVTimeZoneLoader):
        
            self.CTZ = ctz

            return True

        return False

    def ch_tz(self: DateTime, country_code: str = "", tzinfo: str = "", tzname: str = "") -> bool:

        if country_code:

            self.COUNTRY_CODE = country_code

        if tzinfo:

            self.TZ_INFO = tzinfo
            self.TZ_NAME = self.CTZ.get_tzname(td_str=self.CTZ.get_td(tzinfo=tzinfo))

        if tzname:

            self.TZ_INFO = self.CTZ.get_tzinfo(tzname=tzname)
            self.TZ_NAME = tzname

        return True if country_code or tzinfo or tzname else False

    def str_to_dt(self: DateTime, context: str, tz: Union[dt.timezone, None] = None) -> dt.datetime:

        n: int
        n = len(context)

        z: str
        z = ""

        ##* debug
        # print(context, n)

        # todos: make it possible to use a timezone

        ##* 23:56:36.345
        ##* 23:56:36.345+07:00
        ##* 23:56:36.345987
        ##* 23:56:36.345987+07:00
        ##* Zulu

        ##* change mid empty string
        if n > 10 and context[10] == " ": context = context[:10] +  "T" + context[11:]

        if n == 8:

            d: dt.datetime
            d = dt.datetime.strptime(context, "%H:%M:%S")
            return d.replace(tzinfo=tz) if tz else d

        elif n == 9:

            d: dt.datetime
            d = dt.datetime.strptime(context, "%H:%M:%SZ")
            return d.replace(tzinfo=tz) if tz else d

        elif n == 10:

            d: dt.datetime
            d = dt.datetime.strptime(context, "%Y-%m-%d")
            return d.replace(tzinfo=tz) if tz else d

        elif n == 11:

            d: dt.datetime
            d = dt.datetime.strptime(context, "%Y-%m-%dZ")
            return d.replace(tzinfo=tz) if tz else d

        elif n == 19:

            d: dt.datetime
            d = dt.datetime.strptime(context, "%Y-%m-%dT%H:%M:%S")
            return d.replace(tzinfo=tz) if tz else d
        
        elif n == 20:
        
            d: dt.datetime
            d = dt.datetime.strptime(context, "%Y-%m-%dT%H:%M:%SZ")
            return d.replace(tzinfo=tz) if tz else d

        elif n == 23 or n == 26:

            d: dt.datetime
            d = dt.datetime.strptime(context, "%Y-%m-%dT%H:%M:%S.%f")
            return d.replace(tzinfo=tz) if tz else d

        elif n == 24 or n == 27:

            d: dt.datetime
            d = dt.datetime.strptime(context, "%Y-%m-%dT%H:%M:%S.%fZ")
            return d.replace(tzinfo=tz) if tz else d

        elif (n == 28 or n == 29) and context[26] == "0":

            z = context[23:28]
            context = context[:23] + context[28:]

            tz: dt.timezone
            tz = self.CTZ.timezone(td_str=self.CTZ.get_td(timedelta=z))

            ##* fallback
            return self.str_to_dt(context=context, tz=tz)

        elif (n == 29 or n == 30) and context[26] == ":":

            z = context[23:29]
            z = z[:3] + z[4:]
            context = context[:23] + context[29:]

            tz: dt.timezone
            tz = self.CTZ.timezone(td_str=self.CTZ.get_td(timedelta=z))

            ##* fallback
            return self.str_to_dt(context=context, tz=tz)

        elif (n == 31 or n == 32) and context[29] == "0":

            z = context[26:31]            
            context = context[:26] + context[31:]

            tz: dt.timezone
            tz = self.CTZ.timezone(td_str=self.CTZ.get_td(timedelta=z))

            ##* fallback
            return self.str_to_dt(context=context, tz=tz)

        elif (n == 32 or n == 33) and context[29] == ":":

            z = context[26:32]
            z = z[:3] + z[4:]
            
            context = context[:26] + context[32:]

            tz: dt.timezone
            tz = self.CTZ.timezone(td_str=self.CTZ.get_td(timedelta=z))

            ##* fallback
            return self.str_to_dt(context=context, tz=tz)

        else:

            raise DateTimeInitError(f"Invalid datetime string.")

    def to_dt(self: DateTime, td_str: str = "") -> dt.datetime:

        if td_str:

            ## todos: CTZ maybe is None

            return self.DATETIME.replace(tzinfo=self.CTZ.timezone(td_str=td_str)) \
                + self.CTZ.timedelta(td_str=td_str) \
                    - self.CTZ.timedelta(td_str=self.TIMEDELTA)

        return self.DATETIME

    def set_dt_from(self: DateTime, dt: dt.datetime) -> None:

        tzname: str
        tzname = dt.tzname()

        if tzname:

            td: str
            td = self.CTZ.get_td(tzname=tzname)

            # self.DATETIME = dt.replace(tzinfo=self.CTZ.timezone(td_str=self.TIMEDELTA)) \
            #     + self.CTZ.timedelta(td_str=self.TIMEDELTA) \
            #         - self.CTZ.timedelta(td_str=td)

            self.DATETIME = dt

            self.TZ_INFO = self.CTZ.get_tzinfo(tzname=tzname)
            self.TZ_NAME = tzname

            self.TIMEDELTA = td

        else:

            raise DateTimeInitError(f"No timezone specified.")

    def ch_dt_from(self: DateTime, dt: dt.datetime) -> None:

        tzname: str
        tzname = dt.tzname()

        if tzname:

            td: str
            td = self.CTZ.get_td(tzname=tzname)

            ## todos: CTZ maybe is None

            self.DATETIME = dt.replace(tzinfo=self.CTZ.timezone(td_str=self.TIMEDELTA)) \
                + self.CTZ.timedelta(td_str=self.TIMEDELTA) \
                    - self.CTZ.timedelta(td_str=td)

            # self.TZ_INFO = self.CTZ.get_tzname(td_str=td)
            # self.TZ_NAME = tzname

            # self.TIMEDELTA = td

        else:

            raise DateTimeInitError(f"No timezone specified.")

    def to_str(self: DateTime, years: int = 0, month: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0, microseconds: int = 0) -> str:

        _Y: int
        _m: int
        _d: int
        _H: int
        _M: int
        _S: int
        _s: int
        _f: int

        ##* normalize datetime
        _Y, _m, _d, _H, _M, _S, _s, _f = self.date_fix(
            years=years,
            month=month,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds,
            microseconds=microseconds
        )

        Y: str
        Y = str(_Y).zfill(4)

        m: str
        m = str(_m).zfill(2)
        
        d: str
        d = str(_d).zfill(2)

        H: str
        H = str(_H).zfill(2)
        
        M: str
        M = str(_M).zfill(2)

        S: str
        S = str(_S).zfill(2)

        s: str
        s = str(_s).zfill(3)

        f: str
        f = str(_f).zfill(3)

        context: str

        if s != "000":

            if f != "000":
                
                context = f"{Y}-{m}-{d}T{H}:{M}:{S}.{s}{f}"

            else:

                context = f"{Y}-{m}-{d}T{H}:{M}:{S}.{s}"

        else:

            context = f"{Y}-{m}-{d}T{H}:{M}:{S}"

        context = context + "Z" if self.TZ_NAME == "UTC" else context

        return context

    def date_fix(self: DateTime, years: int = 0, month: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0, microseconds: int = 0) -> Tuple[int, ...]:

        # m: int
        # m = 0

        milliseconds += microseconds // 1000
        microseconds = microseconds % 1000

        # m = microseconds // 1000
        # milliseconds += m
        # microseconds = microseconds - (m * 1000)

        seconds += milliseconds // 1000
        milliseconds = milliseconds % 1000

        # m = milliseconds // 1000
        # seconds += m
        # milliseconds = milliseconds - (m * 1000)

        minutes += seconds // 60
        seconds = seconds % 60

        # m = seconds // 60
        # minutes += m
        # seconds = seconds - (m * 60)

        hours += minutes // 60
        minutes = minutes % 60

        # m = minutes // 60
        # hours += m
        # minutes = minutes - (m * 60)

        days += hours // 24
        hours = hours % 24

        # m = hours // 24
        # days += m
        # hours = hours - (m * 24)

        ##* new schema to handle it

        k: int

        while True:

            years += month // 12
            month = month % 12

            k = self.get_mon(years=years, month=month)

            if days > k:

                days = days - k
                month = month + 1

            else:

                break

        ##* maybe not bad, but tricky can do
        # years += month // 12
        # month = month % 12
# 
        # k: int
        # leap: bool
# 
        # while True:
# 
            # ##* leap init
# 
            # leap = True
# 
            # ##* leap init
# 
            # if month == 2:
# 
                # if leap:
# 
                    # if days > 29: pass
# 
                # else:
# 
                    # if days > 28: pass
# 
            # else:
# 
                # if month == 1: pass
                # elif month == 3: pass
                # else: pass
        
        #**********************************************************************#
        #* LEAP YEAR                                                          *#
        #**********************************************************************#

        return (years, month, days, hours, minutes, seconds, milliseconds, microseconds)

    def enhance_tm_sec(self: DateTime, sec: int) -> DateTimeType:

        return self.enhance_tm_auto(sec=sec)

    def enhance_tm_ms(self: DateTime, ms: int) -> DateTimeType:

        return self.enhance_tm_auto(ms=ms)

    def enhance_tm_us(self: DateTime, us: int) -> DateTimeType:

        return self.enhance_tm_auto(us=us)

    def enhance_tm_auto(self: DateTime, years: int = 0, month: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, sec: int = 0, ms: int = 0, us: int = 0) -> DateTimeType:

        if not hasattr(self, "CTZ"):

            raise DateTimeInitError(f"No timezone specified.")

        Y: int
        m: int
        d: int
        H: int
        M: int
        S: int
        s: int
        f: int

        Y = self.get_year() + years
        m = self.get_month() + month
        d = self.get_day() + days
        H = self.get_hours() + hours
        M = self.get_minutes() + minutes
        S = self.get_seconds() + sec
        s = ms
        f = us

        ##* date normalize to stringify
        # context: str
        # context = self.to_str(
        #     years=Y,
        #     month=m,
        #     days=d,
        #     hours=H,
        #     minutes=M,
        #     seconds=S,
        #     milliseconds=s,
        #     microseconds=f
        # )

        ##* date normalize
        Y, m, d, H, M, S, s, f = self.date_fix(
            years=Y,
            month=m,
            days=d,
            hours=H,
            minutes=M,
            seconds=S,
            milliseconds=s,
            microseconds=f
        )

        ##* make it milliseconds in microseconds
        f = s * 1000 + f
        
        tm: time.struct_time
        tm = self.get_struct_tm(
            years=Y,
            month=m,
            days=d,
            hours=H,
            minutes=M,
            seconds=S,
            weekdays=self.get_weekday(years=Y, month=m, days=d),
            yeardays=self.get_yearday(years=Y, month=m, days=d),

            ##* tricky, idk, but still works necessary
            is_dst=self.is_dst()
        )

        DT: DateTime
        DT = self.__class__

        d = DT()
        d.COUNTRY_CODE = self.COUNTRY_CODE

        ##* cause UTC, just addition of timedelta from TZ

        # tz: str
        # tz = "UTC"

        # td: str
        # td = self.CTZ.get_td(tzname=tz)

        # print(dt.datetime.fromtimestamp(tm))

        # d.DATETIME = dt.datetime.utcfromtimestamp(tm) + dt.timedelta(milliseconds=s, microseconds=f)
        # d.DATETIME = d.DATETIME.replace(tzinfo=self.CTZ.timezone(td_str=self.TIMEDELTA))
        # d.DATETIME = d.DATETIME + self.CTZ.timedelta(td_str=self.TIMEDELTA)

        ##* fix no duplicated

        d.DATETIME = dt.datetime.fromtimestamp(tm) + dt.timedelta(microseconds=f)

        d.TZ_INFO = self.TZ_INFO
        d.TZ_NAME = self.TZ_NAME
        d.TIMEDELTA = self.TIMEDELTA
        d.CTZ = self.CTZ
        
        # if hasattr(self, "CTZ"):

        #     d.CTZ = self.CTZ

        # else:

        #     raise DateTimeInitError(f"{self.__class__.__name__} object has no CTZ attribute.")

        return d

    def get_struct_tm(self: DateTime, years: int = 0, month: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, weekdays: int = 0, yeardays: int = 0, is_dst: int = -1) -> time.struct_time:
        
        years = self.get_year() if years == 0 else years
        month = self.get_month() if month == 0 else month
        days = self.get_day() if days == 0 else days
        hours = self.get_hours() if hours == 0 else hours
        minutes = self.get_minutes() if minutes == 0 else minutes
        seconds = self.get_seconds() if seconds == 0 else seconds
        weekdays = self.get_weekday(years=years, month=month, days=days) if weekdays == 0 else weekdays
        yeardays = self.get_yearday(years=years, month=month, days=days) if yeardays == 0 else yeardays
        is_dst = self.is_dst() if is_dst == -1 else is_dst

        return time.mktime((
            years,
            month,
            days,
            hours,
            minutes,
            seconds,
            weekdays,
            yeardays,
            is_dst
        ))

    def get_year(self: DateTime) -> int:

        """year(1, Infinity)"""

        return self.DATETIME.year

    def get_month(self: DateTime) -> int:

        """month(1, 12)"""

        return self.DATETIME.month

    ##* get max days in month
    def get_mon(self: DateTime, years: int = 0, month: int = 0) -> int:

        """mon(28, 29, 30, 31)"""

        years = self.get_year() if years == 0 else years
        month = self.get_month() if month == 0 else month

        if month == 1: return 31

        if month == 2: return (28 if years % 400 and not (years % 100) else 29) if not years % 4 else 28

        ##* start at march
        if month <= 12:

            ##* 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
            ##* 31, 30, 31, 30, 31
            ##* 31, 30
        
            # return (31, 30, 31, 30, 31).__getitem__((month - 3) % 5)

            k: int

            ##* start at march
            k = (month - 3) % 5
            # k = k + 1

            ##* odd is 31 and even is 30
            # return 31 if k & 1 else 30
            return 31 if not k & 1 else 30

        raise DateTimeInitError(f"Invalid month")

    def get_weekday(self: DateTime, years: int = 0, month: int = 0, days: int = 0) -> int:

        """weekday(0, 6)"""

        years = self.get_year() if years == 0 else years
        month = self.get_month() if month == 0 else month
        days = self.get_day() if days == 0 else days

        ##* same fast way
        # return dt.datetime(years, month, days).weekday()

        ##* 365 default, 28 + 337, 337 is constant
        ##* start at 1900, 1, 1
        ##* (1900, years - 1) + yearday
        ##* self.get_yearday(years=1900,month=12,days=31)
        ##* if years lt 100 than start_at_years = 1, start_at_wdays=0

        if years < 100:

            return self.__get_weekday(
                years=years,
                month=month,
                days=days,
                start_at_years=1,
                start_at_wdays=0
            )

        ##* pattern per 100 years
        ##* 4, 2, 0, 5

        i: int
        k: int
        k = years // 100

        ##* alternative Modulo
        ##* x % y
        ##* x - ((x // y) * y)
        i = (k - 1) % 4
        # i = k - (((k - 1) // 4) * 4) - 1

        w: int
        w = (4, 2, 0, 5).__getitem__(i)

        return self.__get_weekday(
            years=years,
            month=month,
            days=days,
            start_at_years=k * 100,
            start_at_wdays=w
        )
    
    def __get_weekday(self: DateTime, years: int, month: int, days: int, start_at_years: int, start_at_wdays: int) -> int:

        if years < start_at_years:

            raise DateTimeInitError(f"Invalid year")

        Y: int
        Y = 0

        wday: int

        ##* start at monday (index)
        wday = start_at_wdays

        ##* monday 1
        ##* 0 1 2 ...
        ##* sunday monday
        ##* 1 monday
        ##* next year is tuesday

        for Y in range(start_at_years, years):

            yday: int
            yday = self.get_yearday(years=Y, month=12, days=31)

            ##* if yday 366 than wday is equals 2
            wday += 1 if yday == 365 or not yday == 366 else 2

            wday = wday % 7

        ##* addition in current year
        wday = wday + self.get_yearday(years=years, month=month, days=days)
        wday = wday % 7

        ##* make it zero is monday, and six is sunday
        wday = 6 if wday == 0 else wday - 1

        return wday

    def get_day(self: DateTime) -> int:

        """day(0, 30)"""

        return self.DATETIME.day

    def get_yearday(self: DateTime, years: int = 0, month: int = 0, days: int = 0) -> int:

        """yearday(0, 365, 366)"""

        years = self.get_year() if years == 0 else years
        month = self.get_month() if month == 0 else month
        days = self.get_day() if days == 0 else days

        z: int
        z = 0

        m: int
        m = 0

        for m in range(1, month):

            z += self.get_mon(years=years, month=m)

        return z + days
        

    def get_hours(self: DateTime) -> int:

        """hours(1, 0, 24)"""

        return self.DATETIME.hour

    def get_minutes(self: DateTime) -> int:

        """minutes(0, 59)"""

        return self.DATETIME.minute

    def get_seconds(self: DateTime) -> int:

        """seconds(0, 59)"""

        return self.DATETIME.second

    def get_milliseconds(self: DateTime) -> int:

        """milliseconds(0, 999)"""
        
        return self.DATETIME.microsecond // 1000

    def get_microseconds(self: DateTime) -> int:

        """microseconds(0, 999999)"""

        return self.DATETIME.microsecond

    def is_dst(self: DateTime) -> int:

        """is_dst(0, 1, -1)"""

        return 0


class TimeFix(TimeFixType):

    MONTH_FULLNAMES: List[str]
    MONTH_FULLNAMES = [ "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december" ]

    MONTH_NAMES: List[str]
    MONTH_NAMES = [ "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec" ]

    WEEKDAY_FULLNAMES: str
    WEEKDAY_FULLNAMES = [ "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday" ]

    WEEKDAY_NAMES: str
    WEEKDAY_NAMES = [ "mon", "tue", "wed", "thu", "fri", "sat", "sun" ]

    TZ_DATA_BUFFER: io.BytesIO
    TZ_DATA_BUFFER = io.BytesIO(b"AD,CEST,Europe/Andorra,+0200\nAG,AST,America/Antigua,-0400\nAI,AST,America/Anguilla,-0400\nAL,CEST,Europe/Tirane,+0200\nAO,WAT,Africa/Luanda,+0100\nAQ,NZST,Antarctica/McMurdo,+1200\nAT,CEST,Europe/Vienna,+0200\nAU,ACST,Australia/Adelaide,+0930\nAU,ACST,Australia/Broken_Hill,+0930\nAU,ACST,Australia/Darwin,+0930\nAU,AEST,Antarctica/Macquarie,+1000\nAU,AEST,Australia/Brisbane,+1000\nAU,AEST,Australia/Hobart,+1000\nAU,AEST,Australia/Lindeman,+1000\nAU,AEST,Australia/Melbourne,+1000\nAU,AEST,Australia/Sydney,+1000\nAU,AWST,Australia/Perth,+0800\nAW,AST,America/Aruba,-0400\nAX,EEST,Europe/Mariehamn,+0300\nBA,CEST,Europe/Sarajevo,+0200\nBB,AST,America/Barbados,-0400\nBE,CEST,Europe/Brussels,+0200\nBF,GMT,Africa/Ouagadougou,+0000\nBG,EEST,Europe/Sofia,+0300\nBI,CAT,Africa/Bujumbura,+0200\nBJ,WAT,Africa/Porto_Novo,+0100\nBL,AST,America/St_Barthelemy,-0400\nBQ,AST,America/Kralendijk,-0400\nBR,CDT,America/Bahia,-0500\nBS,EDT,America/Nassau,-0400\nBW,CAT,Africa/Gaborone,+0200\nBZ,CST,America/Belize,-0600\nCA,ADT,America/Glace_Bay,-0300\nCA,ADT,America/Goose_Bay,-0300\nCA,ADT,America/Halifax,-0300\nCA,ADT,America/Moncton,-0300\nCA,AST,America/Blanc_Sablon,-0400\nCA,CDT,America/Rainy_River,-0500\nCA,CDT,America/Rankin_Inlet,-0500\nCA,CDT,America/Resolute,-0500\nCA,CDT,America/Winnipeg,-0500\nCA,CST,America/Regina,-0600\nCA,CST,America/Swift_Current,-0600\nCA,EDT,America/Iqaluit,-0400\nCA,EDT,America/Nipigon,-0400\nCA,EDT,America/Pangnirtung,-0400\nCA,EDT,America/Thunder_Bay,-0400\nCA,EDT,America/Toronto,-0400\nCA,EST,America/Atikokan,-0500\nCA,MDT,America/Cambridge_Bay,-0600\nCA,MDT,America/Edmonton,-0600\nCA,MDT,America/Inuvik,-0600\nCA,MDT,America/Yellowknife,-0600\nCA,MST,America/Creston,-0700\nCA,MST,America/Dawson,-0700\nCA,MST,America/Dawson_Creek,-0700\nCA,MST,America/Fort_Nelson,-0700\nCA,MST,America/Whitehorse,-0700\nCA,NDT,America/St_Johns,-0230\nCA,PDT,America/Vancouver,-0700\nCD,CAT,Africa/Lubumbashi,+0200\nCD,WAT,Africa/Kinshasa,+0100\nCF,WAT,Africa/Bangui,+0100\nCG,WAT,Africa/Brazzaville,+0100\nCH,CEST,Europe/Zurich,+0200\nCI,GMT,Africa/Abidjan,+0000\nCM,WAT,Africa/Douala,+0100\nCN,CST,Asia/Shanghai,+0800\nCR,CST,America/Costa_Rica,-0600\nCU,CDT,America/Havana,-0400\nCW,AST,America/Curacao,-0400\nCY,EEST,Asia/Famagusta,+0300\nCY,EEST,Asia/Nicosia,+0300\nCZ,CEST,Europe/Prague,+0200\nDE,CEST,Europe/Berlin,+0200\nDE,CEST,Europe/Busingen,+0200\nDJ,EAT,Africa/Djibouti,+0300\nDK,CEST,Europe/Copenhagen,+0200\nDM,AST,America/Dominica,-0400\nDO,AST,America/Santo_Domingo,-0400\nDZ,CET,Africa/Algiers,+0100\nEE,EEST,Europe/Tallinn,+0300\nEG,EET,Africa/Cairo,+0200\nER,EAT,Africa/Asmara,+0300\nES,CEST,Africa/Ceuta,+0200\nES,CEST,Europe/Madrid,+0200\nET,EAT,Africa/Addis_Ababa,+0300\nFI,EEST,Europe/Helsinki,+0300\nFR,CEST,Europe/Paris,+0200\nGA,WAT,Africa/Libreville,+0100\nGB,BST,Europe/London,+0100\nGD,AST,America/Grenada,-0400\nGG,BST,Europe/Guernsey,+0100\nGH,GMT,Africa/Accra,+0000\nGI,CEST,Europe/Gibraltar,+0200\nGL,ADT,America/Thule,-0300\nGL,GMT,America/Danmarkshavn,+0000\nGM,GMT,Africa/Banjul,+0000\nGN,GMT,Africa/Conakry,+0000\nGP,AST,America/Guadeloupe,-0400\nGQ,WAT,Africa/Malabo,+0100\nGR,EEST,Europe/Athens,+0300\nGT,CST,America/Guatemala,-0600\nGW,GMT,Africa/Bissau,+0000\nHK,HKT,Asia/Hong_Kong,+0800\nHN,CST,America/Tegucigalpa,-0600\nHR,CEST,Europe/Zagreb,+0200\nHT,EDT,America/Port_au_Prince,-0400\nHU,CEST,Europe/Budapest,+0200\nID,WIB,Asia/Jakarta,+0700\nID,WIB,Asia/Pontianak,+0700\nID,WITA,Asia/Makassar,+0800\nID,WIT,Asia/Jayapura,+0900\nIE,IST,Europe/Dublin,+0100\nIL,IDT,Asia/Jerusalem,+0300\nIM,BST,Europe/Isle_of_Man,+0100\nIN,IST,Asia/Kolkata,+0530\nIT,CEST,Europe/Rome,+0200\nJE,BST,Europe/Jersey,+0100\nJM,EST,America/Jamaica,-0500\nJO,EEST,Asia/Amman,+0300\nJP,JST,Asia/Tokyo,+0900\nKE,EAT,Africa/Nairobi,+0300\nKN,AST,America/St_Kitts,-0400\nKP,KST,Asia/Pyongyang,+0900\nKR,KST,Asia/Seoul,+0900\nKY,EST,America/Cayman,-0500\nLB,EEST,Asia/Beirut,+0300\nLC,AST,America/St_Lucia,-0400\nLI,CEST,Europe/Vaduz,+0200\nLR,GMT,Africa/Monrovia,+0000\nLS,SAST,Africa/Maseru,+0200\nLT,EEST,Europe/Vilnius,+0300\nLU,CEST,Europe/Luxembourg,+0200\nLV,EEST,Europe/Riga,+0300\nLY,EET,Africa/Tripoli,+0200\nMC,CEST,Europe/Monaco,+0200\nMD,EEST,Europe/Chisinau,+0300\nME,CEST,Europe/Podgorica,+0200\nMF,AST,America/Marigot,-0400\nMK,CEST,Europe/Skopje,+0200\nML,GMT,Africa/Bamako,+0000\nMO,CST,Asia/Macau,+0800\nMQ,AST,America/Martinique,-0400\nMR,GMT,Africa/Nouakchott,+0000\nMS,AST,America/Montserrat,-0400\nMT,CEST,Europe/Malta,+0200\nMW,CAT,Africa/Blantyre,+0200\nMX,CDT,America/Bahia_Banderas,-0500\nMX,CDT,America/Matamoros,-0500\nMX,CDT,America/Merida,-0500\nMX,CDT,America/Mexico_City,-0500\nMX,CDT,America/Monterrey,-0500\nMX,EST,America/Cancun,-0500\nMX,MDT,America/Chihuahua,-0600\nMX,MDT,America/Mazatlan,-0600\nMX,MDT,America/Ojinaga,-0600\nMX,MST,America/Hermosillo,-0700\nMX,PDT,America/Tijuana,-0700\nMZ,CAT,Africa/Maputo,+0200\nNA,CAT,Africa/Windhoek,+0200\nNE,WAT,Africa/Niamey,+0100\nNG,WAT,Africa/Lagos,+0100\nNI,CST,America/Managua,-0600\nNL,CEST,Europe/Amsterdam,+0200\nNO,CEST,Europe/Oslo,+0200\nPA,EST,America/Panama,-0500\nPH,PST,Asia/Manila,+0800\nPK,PKT,Asia/Karachi,+0500\nPL,CEST,Europe/Warsaw,+0200\nPR,AST,America/Puerto_Rico,-0400\nPS,EEST,Asia/Gaza,+0300\nPS,EEST,Asia/Hebron,+0300\nPT,WEST,Europe/Lisbon,+0100\nRO,EEST,Europe/Bucharest,+0300\nRS,CEST,Europe/Belgrade,+0200\nRU,EET,Europe/Kaliningrad,+0200\nRU,MSK,Europe/Moscow,+0300\nRW,CAT,Africa/Kigali,+0200\nSD,CAT,Africa/Khartoum,+0200\nSE,CEST,Europe/Stockholm,+0200\nSI,CEST,Europe/Ljubljana,+0200\nSK,CEST,Europe/Bratislava,+0200\nSL,GMT,Africa/Freetown,+0000\nSM,CEST,Europe/San_Marino,+0200\nSN,GMT,Africa/Dakar,+0000\nSO,EAT,Africa/Mogadishu,+0300\nSS,CAT,Africa/Juba,+0200\nST,GMT,Africa/Sao_Tome,+0000\nSV,CST,America/El_Salvador,-0600\nSX,AST,America/Lower_Princes,-0400\nSY,EEST,Asia/Damascus,+0300\nSZ,SAST,Africa/Mbabane,+0200\nTC,EDT,America/Grand_Turk,-0400\nTD,WAT,Africa/Ndjamena,+0100\nTG,GMT,Africa/Lome,+0000\nTN,CET,Africa/Tunis,+0100\nTT,AST,America/Port_of_Spain,-0400\nTW,CST,Asia/Taipei,+0800\nTZ,EAT,Africa/Dar_es_Salaam,+0300\nUA,EEST,Europe/Kiev,+0300\nUA,EEST,Europe/Uzhgorod,+0300\nUA,EEST,Europe/Zaporozhye,+0300\nUA,MSK,Europe/Simferopol,+0300\nUG,EAT,Africa/Kampala,+0300\nUS,AKDT,America/Anchorage,-0800\nUS,AKDT,America/Juneau,-0800\nUS,AKDT,America/Metlakatla,-0800\nUS,AKDT,America/Nome,-0800\nUS,AKDT,America/Sitka,-0800\nUS,AKDT,America/Yakutat,-0800\nUS,CDT,America/Chicago,-0500\nUS,CDT,America/Menominee,-0500\nUS,EDT,America/Detroit,-0400\nUS,EDT,America/New_York,-0400\nUS,HDT,America/Adak,-0900\nUS,MDT,America/Boise,-0600\nUS,MDT,America/Denver,-0600\nUS,MST,America/Phoenix,-0700\nUS,PDT,America/Los_Angeles,-0700\nVA,CEST,Europe/Vatican,+0200\nVC,AST,America/St_Vincent,-0400\nVG,AST,America/Tortola,-0400\nVI,AST,America/St_Thomas,-0400\nZA,SAST,Africa/Johannesburg,+0200\nZM,CAT,Africa/Lusaka,+0200\nZW,CAT,Africa/Harare,+0200")

    CTZ: CSVTimeZoneLoaderType
    CTZ = CSVTimeZoneLoader(tzfile=TZ_DATA_BUFFER)

    __dt_datetime: type
    __dt_datetime = dt.datetime

    def __init__(self: TimeFixType, tzfile: Union[str, io.TextIOWrapper, io.BytesIO, io.StringIO, tempfile._TemporaryFileWrapper, None] = None) -> None:

        if tzfile:

            self.CTZ = CSVTimeZoneLoader(tzfile=tzfile)

        ##* Initialized

    @classmethod
    def create_dt(cls: TimeFixType, dt: Union[int, float, str, dt.datetime, None] = None, tzname: str = "", tzinfo: str = "") -> DateTimeType:

        d = DateTime()
        d.set_ctz(cls.CTZ)

        if type(dt) in (int, float):

            d.DATETIME = d.DATETIME.fromtimestamp(dt)

        elif isinstance(dt, str):

            d.DATETIME = d.str_to_dt(dt)

        elif isinstance(dt, cls.__dt_datetime):

            d.DATETIME = dt

        else:

            pass

        #************************************************************************************************#
        #* re-initialized                                                                               *#
        #************************************************************************************************#
        tzname = d.DATETIME.tzname() if not tzname else tzname

        if tzname:

            d.TZ_NAME = tzname

        if tzinfo:
                
            d.TZ_INFO = tzinfo

        ##* re-initialized
        d.init()
        #************************************************************************************************#
        #* re-initialized                                                                               *#
        #************************************************************************************************#

        return d

    @classmethod
    def get_month(cls: TimeFixType, dt: DateTimeType) -> Tuple[int, str, str]:

        month: int

        ##* make it index (0, 11)
        month = dt.get_month() - 1

        ##* start at 1 from (index)
        return (month + 1, cls.MONTH_NAMES[month], cls.MONTH_FULLNAMES[month])

    @classmethod
    def get_weekdays(cls: TimeFixType, dt: DateTimeType) -> Tuple[int, str, str]:

        wday: int
        wday = dt.get_weekday()

        return (wday, cls.WEEKDAY_NAMES[wday], cls.WEEKDAY_FULLNAMES[wday])

    @classmethod
    def enhance_tm_sec(cls: TimeFixType, dt: DateTimeType, sec: int) -> DateTimeType:

        dt.DATETIME = dt.enhance_tm_sec(sec).DATETIME

        return dt

    @classmethod
    def enhance_tm_ms(cls: TimeFixType, dt: DateTimeType, ms: int) -> DateTimeType:

        dt.DATETIME = dt.enhance_tm_ms(ms).DATETIME
        
        return dt

    @classmethod
    def enhance_tm_us(cls: TimeFixType, dt: DateTimeType, us: int) -> DateTimeType:

        dt.DATETIME = dt.enhance_tm_us(us).DATETIME
        
        return dt

    @classmethod
    def to_str(cls: TimeFixType, dt: DateTimeType) -> DateTimeType:

        return str(dt)
