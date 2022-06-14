#!/usr/bin/env python

import hashlib
import os
import sqlite3 as sql

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, List, Optional, Tuple, TypeVar, Union

from pydantic import BaseModel

from .utils import password_hash
from .timefix import timefix

def md5sum(context):

    return hashlib.md5(context).hexdigest()

def timestamp(context):

    return timefix.TimeFix.create_dt(context).DATETIME.timestamp()

def dict_factory(cursor: sql.Cursor, row: sql.Row) -> dict:
    
    d: dict
    d = {}

    idx: int
    col: Tuple[str, Any]
    
    for idx, col in enumerate(cursor.description):
    
        d[col[0]] = row[idx]
    
    return d

##* Simple Database Type
SimpleDatabaseType: Any
SimpleDatabaseType = TypeVar("SimpleDatabaseType", bound="SimpleDatabaseType")

class SimpleDatabaseType(ABC):

    @abstractmethod
    def init(self: SimpleDatabaseType) -> None: pass

    @abstractmethod
    def get_cursor(self: SimpleDatabaseType) -> sql.Cursor: pass

    @abstractmethod
    def commit(self: SimpleDatabaseType) -> None: pass

    @abstractmethod
    def close(self: SimpleDatabaseType) -> None: pass


SimpleDatatableType: Any
SimpleDatatableType = TypeVar("SimpleDatatableType", bound="SimpleDatatableType")

##* Simple Datatable Type
class SimpleDatatableType(ABC):

    @abstractmethod
    def init(self: SimpleDatatableType) -> None: pass

    @abstractmethod
    def append(self: SimpleDatatableType, data: Union[BaseModel, dict]) -> Optional[bool]: pass

    @abstractmethod
    def get(self: SimpleDatatableType, id: int) -> Optional[dict]: pass

    @abstractmethod
    def set(self: SimpleDatatableType, id: int, data: Union[BaseModel, dict]) -> Optional[bool]: pass

    @abstractmethod
    def remove(self: SimpleDatatableType, id: int) -> Optional[bool]: pass

    @abstractmethod
    def drop(self: SimpleDatatableType) -> Optional[bool]: pass


ConnectDB: Any
ConnectDB = TypeVar("ConnectDB", bound="ConnectDB")

class ConnectDB(SimpleDatabaseType):

    uri: Union[str, None]
    conn: sql.Connection
    cursor: sql.Cursor
    
    def __init__(self: ConnectDB, uri: str = None):

        self.uri = uri
        self.conn = None
        self.cursor = None
        self.init()

    def init(self: ConnectDB) -> None:

        if self.uri is None:

            src: str
            src = os.path.join(os.path.dirname(__file__), "../db/sqlite3.db")

            #* make dirs
            os.makedirs(os.path.dirname(src), mode = 0o755, exist_ok = True)

            #* make file
            if not os.path.exists(src): open(src, "wb").close()

            #* make uri
            self.uri = "file://{PATH}?mode=rw&cache=shared".format(PATH = src)

        self.conn = sql.connect(self.uri, uri=True)
        self.conn.create_function("md5sum", 1, md5sum)
        self.conn.create_function("timestamp", 1, timestamp)
        self.conn.row_factory = dict_factory
        # self.conn.row_factory = sql.Row
        self.cursor = self.conn.cursor()

    def get_cursor(self: ConnectDB) -> sql.Cursor:

        return self.cursor

    def commit(self: ConnectDB) -> None:

        self.conn.commit()

    def close(self: ConnectDB) -> None:

        if self.cursor is not None:
            
            self.cursor.close()
            self.cursor = None

        self.conn.close()

    def __enter__(self: ConnectDB) -> sql.Cursor:

        return self.cursor

    def __exit__(self, exc_type: Optional[type], exc_value: Optional[str], traceback: Optional[TracebackType]) -> None:

        self.commit()
        self.close()


ProductData: Any
ProductData = TypeVar("ProductData", bound="ProductData")

class ProductData(SimpleDatatableType):

    cursor: sql.Cursor

    def __init__(self: ProductData, connect_db: SimpleDatabaseType):

        self.cursor = connect_db.get_cursor()
        self.init()

    def init(self: ProductData):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS `products`(
                `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                `name` TEXT NOT NULL,
                `photo` TEXT NULL,
                `description` TEXT NOT NULL,
                `categories` TEXT NOT NULL,
                `period_of_time` TEXT NOT NULL,
                `license` TEXT NULL,
                `author` TEXT NOT NULL,
                `vendor` TEXT NOT NULL,
                `price` REAL NULL,
                `sale` REAL NULL,
                `created` DATETIME NOT NULL,
                `modified` DATETIME NOT NULL
        );
        """)

    def append(
            self: ProductData, 
            data: Union[BaseModel, dict]
        ) -> Optional[bool]:

        try:

            data = data if not isinstance(data, BaseModel) else data.dict()

            name: str
            photo: Optional[str]
            description: str
            categories: List[str] 
            period_of_time: str
            license: Optional[str] 
            author: str
            vendor: Optional[str]
            price: Optional[float] 
            sale: Optional[float]

            name = data.get("name", "")
            photo = data.get("photo", None)
            description = data.get("description", "")
            categories = data.get("categories", [])
            period_of_time = data.get("period_of_time", "")
            license = data.get("license", None)
            author = data.get("author", "")
            vendor = data.get("vendor", None)
            price = data.get("price", None)
            sale = data.get("sale", None)

            if isinstance(categories, str):

                if ";" in categories:

                    categories = categories.split(";")

                elif "," in categories:
                
                    categories = categories.split(",")

                else:

                    categories = [categories]

            self.cursor.execute("""
            INSERT INTO `products`(
                `name`, 
                `photo`, 
                `description`, 
                `categories`, 
                `period_of_time`, 
                `license`, 
                `author`, 
                `vendor`, 
                `price`, 
                `sale`, 
                `created`, 
                `modified`
            ) VALUES (
                ?, ?, ?, ?, 
                ?, ?, ?, ?, 
                ?, ?, ?, ?
            );
            """, (
                name,
                photo,
                description,
                str.join(",", categories),
                period_of_time if period_of_time in ("annually", "monthly", "lifetime") else "unknown",
                license if license else "",
                author if author else "anonymous",
                vendor if vendor else "unknown",
                price if price else 0.,
                sale if sale else 0.,
                str(timefix.TimeFix.create_dt()),
                str(timefix.TimeFix.create_dt())
            ))

            return True

        except Exception as e:

            print(e)

            return None

    def get(self: ProductData, id: int) -> Optional[dict]:

        try:

            self.cursor.execute("""
            SELECT * FROM `products` WHERE `id` = ? LIMIT 1;
            """, (id,))

            return self.cursor.fetchone()

        except Exception as e:

            print(e)

            return None

    def set(
            self: ProductData, 
            id: int, 
            data: Union[BaseModel, dict]
        ) -> Optional[bool]:

        try:

            data = data if not isinstance(data, BaseModel) else data.dict()

            name: Optional[str] 
            photo: Optional[str]
            description: Optional[str]
            categories: Optional[List[str]] 
            period_of_time: Optional[str] 
            license: Optional[str] 
            author: Optional[str] 
            vendor: Optional[str]
            price: Optional[int]
            sale: Optional[int]

            name = data.get("name", None)
            photo = data.get("photo", None)
            description = data.get("description", None)
            categories = data.get("categories", None)
            period_of_time = data.get("period_of_time", None)
            license = data.get("license", None)
            author = data.get("author", None)
            vendor = data.get("vendor", None)
            price = data.get("price", None)
            sale = data.get("sale", None)

            field_names: List[str]
            field_names = []

            field_values: List[Any]
            field_values = []

            if name is not None:

                field_names.append("`name` = ?")
                field_values.append(name)

            if photo is not None:

                field_names.append("`photo` = ?")
                field_values.append(photo)

            if description is not None:

                field_names.append("`description` = ?")
                field_values.append(description)

            if categories is not None:

                field_names.append("`categories` = ?")
                field_values.append(str.join(",", categories))

            if period_of_time is not None:

                if period_of_time in ("annually", "monthly", "lifetime"):

                    field_names.append("`period_of_time` = ?")
                    field_values.append(period_of_time)

            if license is not None:

                field_names.append("`license` = ?")
                field_values.append(license)

            if author is not None:

                field_names.append("`author` = ?")
                field_values.append(author)

            if vendor is not None:

                field_names.append("`vendor` = ?")
                field_values.append(vendor)

            if price is not None:

                field_names.append("`price` = ?")
                field_values.append(price)

            if sale is not None:

                field_names.append("`sale` = ?")
                field_values.append(sale)

            field_names.append("`modified` = ?")
            field_values.append(str(timefix.TimeFix.create_dt()))
            
            #* where
            field_values.append(id)

            self.cursor.execute("""
            UPDATE 
                `products` 
            SET 
                {SET} 
            WHERE 
                `id` = ?;
            """.format(SET=str.join(",", field_names)), tuple(field_values))

            return True

        except Exception as e:

            print(e)

            return None

    def remove(self: ProductData, id: int) -> Optional[bool]:

        try:

            self.cursor.execute("""
            DELETE FROM `products` WHERE `id` = ?;
            """, (id,))

            return True

        except Exception as e:

            print(e)

            return None

    def drop(self: ProductData) -> Optional[bool]:

        try:

            self.cursor.execute("""
            DROP TABLE IF EXISTS `products`;
            """)

            return True
        
        except Exception as e:

            print(e)
            
            return None

    def get_all_products(self: ProductData, start_at: int = 0, count: int = 20) -> Optional[List[dict]]:

        try:

            self.cursor.execute("""
            SELECT * FROM `products` LIMIT {OFFSET},{COUNT};
            """.format(OFFSET=start_at, COUNT=count))

            return self.cursor.fetchmany(size=count)

        except Exception as e:

            print(e)

            return None

    def get_by_name(self: ProductData, name: str) -> Optional[dict]:

        try:

            self.cursor.execute("""
            SELECT `id`, `name`, `photo`, `description`, `categories`, `period_of_time`, `license`, `author`, `vendor`, `price`, `sale`, timestamp(`created`) as `created`, timestamp(`modified`) as `modified` FROM `products` WHERE `name` = ? LIMIT 1;
            """, (name,))

            return self.cursor.fetchone()

        except Exception as e:

            print(e)

            return None

    def splitter_categories(self: ProductData, data: Union[BaseModel, dict]) -> Optional[dict]:

        try:

            data = data if not isinstance(data, BaseModel) else data.dict()

            categories: Optional[Union[List[str], str]] = data.get("categories", None)

            if categories is not None:

                if isinstance(categories, str):

                    if ";" in categories:

                        categories = categories.split(";")

                    elif "," in categories:
                    
                        categories = categories.split(",")

                    else:

                        categories = [categories]
                
                data.update({"categories": categories})

            return data

        except Exception as e:

            print(e)

            return None

UserData: Any
UserData = TypeVar("UserData", bound="UserData")


class UserData(SimpleDatatableType):

    cursor: sql.Cursor

    def __init__(self: UserData, connect_db: SimpleDatabaseType):

        self.cursor = connect_db.get_cursor()
        self.init()

    def init(self: UserData):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS `users`(
                `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                `username` TEXT UNIQUE NOT NULL,
                `name` TEXT NOT NULL,
                `photo` TEXT NULL,
                `password` TEXT NULL,
                `gender` TEXT NOT NULL,
                `day_of_birthday` DATETIME NOT NULL,
                `email` TEXT NOT NULL,
                `email_verified` BOOLEAN NULL,
                `phone` TEXT NOT NULL,
                `phone_verified` BOOLEAN NULL,
                `address` TEXT NOT NULL,
                `postal_code` TEXT NOT NULL,
                `country` TEXT NOT NULL,
                `language` TEXT NOT NULL,
                `verified` BOOLEAN NULL,
                `admin` BOOLEAN NULL,
                `created` DATETIME NOT NULL,
                `modified` DATETIME NOT NULL
        );
        """)

    def append(
            self: ProductData, 
            data: Union[BaseModel, dict]
        ) -> Optional[bool]:

        try:

            data = data if not isinstance(data, BaseModel) else data.dict()

            username: str
            name: str
            photo: Optional[str]
            password: Optional[str]
            gender: str
            day_of_birthday: str
            email: str
            email_verified: bool
            phone: str
            phone_verified: bool
            address: str
            postal_code: str
            country: str
            language: str
            verified: bool
            admin: bool

            username = data.get("username", "")
            name = data.get("name", "")
            photo = data.get("photo", None)
            password = data.get("password", "")
            gender = data.get("gender", "")
            day_of_birthday = data.get("day_of_birthday", "")
            email = data.get("email", "")
            email_verified = data.get("email_verified", False)
            phone = data.get("phone", "")
            phone_verified = data.get("phone_verified", False)
            address = data.get("address", "")
            postal_code = data.get("postal_code", "")
            country = data.get("country", "")
            language = data.get("language", "")
            verified = data.get("verified", False)
            admin = data.get("admin", False)

            password = password_hash(password) if password else password

            self.cursor.execute("""
            INSERT INTO `users`(
                `username`, 
                `name`, 
                `photo`, 
                `password`, 
                `gender`, 
                `day_of_birthday`, 
                `email`, 
                `email_verified`, 
                `phone`, 
                `phone_verified`, 
                `address`, 
                `postal_code`, 
                `country`, 
                `language`, 
                `verified`,
                `admin`,
                `created`,
                `modified`
            ) VALUES (
                ?, ?, ?, ?, 
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?
            )
            """, (
                username,
                name,
                photo,
                password,
                gender,
                day_of_birthday,
                email,
                email_verified,
                phone,
                phone_verified,
                address,
                postal_code,
                country,
                language,
                verified,
                admin,
                str(timefix.TimeFix.create_dt()),
                str(timefix.TimeFix.create_dt())
            ))

            return True

        except Exception as e:

            print(e)

            return None

    def get(self: UserData, id: int) -> Optional[dict]:

        try:

            self.cursor.execute("""
            SELECT * FROM `users` WHERE `id` = ? LIMIT 1;
            """, (id,))

            return self.cursor.fetchone()

        except Exception as e:

            print(e)

            return None

    def set(
            self: UserData, 
            id: int, 
            data: Union[BaseModel, dict]
        ) -> Optional[bool]:

        try:

            data = data if not isinstance(data, BaseModel) else data.dict()

            username: Optional[str]
            name: Optional[str]
            photo: Optional[str]
            password: Optional[str]
            gender: Optional[str]
            day_of_birthday: Optional[str]
            email: Optional[str]
            email_verified: Optional[bool]
            phone: Optional[str]
            phone_verified: Optional[bool]
            address: Optional[str]
            postal_code: Optional[str]
            country: Optional[str]
            language: Optional[str]
            verified: Optional[bool]
            admin: Optional[bool]

            name = data.get("name", None)
            photo = data.get("photo", None)
            password = data.get("password", None)
            gender = data.get("gender", None)
            day_of_birthday = data.get("day_of_birthday", None)
            email = data.get("email", None)
            email_verified = data.get("email_verified", None)
            phone = data.get("phone", None)
            phone_verified = data.get("phone_verified", None)
            address = data.get("address", None)
            postal_code = data.get("postal_code", None)
            country = data.get("country", None)
            language = data.get("language", None)
            verified = data.get("verified", None)
            admin = data.get("admin", None)

            field_names: List[str]
            field_names = []

            field_values: List[Any]
            field_values = []

            if username is not None:

                field_names.append("`username` = ?")
                field_values.append(username)

            if name is not None:

                field_names.append("`name` = ?")
                field_values.append(name)

            if photo is not None:

                field_names.append("`photo` = ?")
                field_values.append(photo)

            if password is not None:

                field_names.append("`password` = ?")
                field_values.append(password_hash(password))

            if gender is not None:

                field_names.append("`gender` = ?")
                field_values.append(gender)
            
            if day_of_birthday is not None:

                field_names.append("`day_of_birthday` = ?")
                field_values.append(day_of_birthday)

            if email is not None:

                field_names.append("`email` = ?")
                field_values.append(email)

            if email_verified is not None:

                field_names.append("`verified` = ?")
                field_values.append(email_verified)
            
            if phone is not None:

                field_names.append("`phone` = ?")
                field_values.append(phone)

            if phone_verified is not None:

                field_names.append("`verified` = ?")
                field_values.append(phone_verified)

            if address is not None:

                field_names.append("`address` = ?")
                field_values.append(address)
                
            if postal_code is not None:

                field_names.append("`postal_code` = ?")
                field_values.append(postal_code)
            
            if country is not None:

                field_names.append("`country` = ?")
                field_values.append(country)

            if language is not None:

                field_names.append("`language` = ?")
                field_values.append(language)

            if verified is not None:

                field_names.append("`verified` = ?")
                field_values.append(verified)

            if admin is not None:

                field_names.append("`admin` = ?")
                field_values.append(admin)

            ##* modified
            field_names.append("`modified` = ?")
            field_values.append(str(timefix.TimeFix.create_dt()))
            
            #* where
            field_values.append(id)

            self.cursor.execute("""
            UPDATE 
                `users` 
            SET 
                {SET} 
            WHERE 
                `id` = ?;
            """.format(SET=str.join(",", field_names)), tuple(field_values))

            return True

        except Exception as e:

            print(e)

            return None

    def remove(self: UserData, id: int) -> Optional[bool]:

        try:

            self.cursor.execute("""
            DELETE FROM `users` WHERE `id` = ?;
            """, (id,))

            return True

        except Exception as e:

            print(e)

            return None

    def drop(self: UserData) -> Optional[bool]:

        try:

            self.cursor.execute("""
            DROP TABLE IF EXISTS `users`;
            """)

            return True
        
        except Exception as e:

            print(e)
            
            return None

    def get_by_username(self: UserData, username: str) -> Optional[dict]:

        try:

            self.cursor.execute("""
            SELECT * FROM `users` WHERE `username` = ? LIMIT 1;
            """, (username,))

            return self.cursor.fetchone()
        
        except Exception as e:

            print(e)
            
            return None


TransactionData: Any
TransactionData = TypeVar("TransactionData", bound="TransactionData")

class TransactionData(SimpleDatatableType):

    cursor: sql.Cursor

    def __init__(self: TransactionData, connect_db: SimpleDatabaseType):

        self.cursor = connect_db.get_cursor()
        self.init()

    def init(self: TransactionData) -> None:

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS `transactions`(
                `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                `user_id` INTEGER NOT NULL,
                `product_id` INTEGER NOT NULL,
                `payment_type` TEXT NOT NULL,
                `payment_paid` BOOLEAN NOT NULL,
                `activate` BOOLEAN NULL,
                `created` DATETIME NOT NULL,
                `expired` DATETIME NULL,
                `modified` DATETIME NOT NULL,
                FOREIGN KEY(`user_id`) REFERENCES `users`(`id`) ON UPDATE RESTRICT ON DELETE CASCADE,
                FOREIGN KEY(`product_id`) REFERENCES `products`(`id`) ON UPDATE RESTRICT ON DELETE CASCADE
        );
        """)

    def append(
            self: TransactionData, 
            data: Union[BaseModel, dict]
        ) -> Optional[bool]:
        
        try:

            data = data if not isinstance(data, BaseModel) else data.dict()

            user_id: int
            product_id: int
            payment_type: str
            payment_paid: bool
            activate: Optional[bool]
            expired: Optional[str]

            user_id = data.get("user_id", 0)
            product_id = data.get("product_id", 0)
            payment_type = data.get("payment_type", "")
            payment_paid = data.get("payment_paid", False)
            activate = data.get("activate", None)
            expired = data.get("expired", "")

            self.cursor.execute("""
            INSERT INTO `transactions`(
                `user_id`,
                `product_id`,
                `payment_type`,
                `payment_paid`,
                `activate`,
                `created`,
                `expired`,
                `modified`
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                user_id,
                product_id,
                payment_type,
                payment_paid,
                activate,
                str(timefix.TimeFix.create_dt()),
                expired,
                str(timefix.TimeFix.create_dt())
            ))

            return True

        except Exception as e:

            print(e)

            return None

    def get(self: TransactionData, id: int) -> Optional[dict]:

        try:

            self.cursor.execute("""
            SELECT * FROM `transactions` WHERE `id` = ? LIMIT 1;
            """, (id,))

            return self.cursor.fetchone()

        except Exception as e:

            print(e)

            return None

    def set(
            self: TransactionData, 
            id: int, 
            data: Union[BaseModel, dict]
        ) -> Optional[bool]:
        
        try:

            data = data if not isinstance(data, BaseModel) else data.dict()

            user_id: Optional[int]
            product_id: Optional[int]
            payment_type: Optional[str]
            payment_paid: Optional[bool]
            activate: Optional[bool]
            expired: Optional[str]

            user_id = data.get("user_id", None)
            product_id = data.get("product_id", None)
            payment_type = data.get("payment_type", None)
            payment_paid = data.get("payment_paid", None)
            activate = data.get("activate", None)
            expired = data.get("expired", None)
            
            field_names: List[str]
            field_values: List[Any]

            if user_id is not None:

                field_names.append("`user_id` = ?")
                field_values.append(user_id)

            if product_id is not None:

                field_names.append("`product_id` = ?")
                field_values.append(product_id)

            if payment_type is not None:

                field_names.append("`payment_type` = ?")
                field_values.append(payment_type)

            if payment_paid is not None:

                field_names.append("`payment_paid` = ?")
                field_values.append(payment_paid)

            if activate is not None:

                field_names.append("`activate` = ?")
                field_values.append(activate)

            if expired is not None:

                field_names.append("`expired` = ?")
                field_values.append(expired)

            #* modified
            field_names.append("`modified` = ?")
            field_values.append(str(timefix.TimeFix.create_dt()))

            #* where
            field_values.append(id)

            self.cursor.execute("""
            UPDATE
                `transactions`
            SET
                {SET}
            WHERE
                `id` = ?;
            """.format(SET=str.join(",", field_names)), tuple(field_values))

            return True

        except Exception as e:

            print(e)

            return False
    
    def remove(self: TransactionData, id: int) -> Optional[bool]:
        
        try:

            self.cursor.execute("""
            DELETE FROM `transactions` WHERE `id` = ?;
            """, (id,))

            return True

        except Exception as e:

            print(e)

            return None
    
    def drop(self: TransactionData) -> Optional[bool]:
        
        try:

            self.cursor.execute("""
            DROP TABLE IF EXISTS `transactions`;
            """)

            return True

        except Exception as e:

            print(e)

            return None
    
    def get_transactions(self: TransactionData, wheres: dict) -> Optional[List[dict]]:

        try:

            wheres_key: str
            wheres_value: Tuple[Any]

            wheres_key, wheres_value = self.__get_wheres_map(wheres)

            print(wheres_key)

            self.cursor.execute("""
            SELECT 
                `products`.`name` AS `product_name`,
                `users`.`name` AS `user_name`,
                `transactions`.*
            FROM 
                `products`, 
                `users`, 
                `transactions` 
            WHERE 
                `products`.`id` = `transactions`.`product_id` AND
                `users`.`id` = `transactions`.`user_id` AND
                {WHERE}
            ORDER BY
                timestamp(`transactions`.`created`) ASC
            LIMIT 
                {OFFSET}, 20;
            """.format(
                WHERE=wheres_key,
                OFFSET=0
            ), tuple(wheres_value))

            return self.cursor.fetchmany(size=20)

        except Exception as e:

            print(e)

            return None

    def get_all_transactions(self: TransactionData, start_at: int = 0, count: int = 20) -> Optional[List[dict]]:

        try:

            self.cursor.execute("""
            SELECT 
                `p`.`name` AS `product_name`,
                `p`.`price` AS `product_price`,
                `p`.`sale` AS `product_sale`,
                `u`.`name` AS `user_name`,
                `t`.*
            FROM 
                `products` `p`, 
                `users` `u`, 
                `transactions` `t` 
            WHERE 
                `p`.`id` = `t`.`product_id` AND
                `u`.`id` = `t`.`user_id`
            ORDER BY
                timestamp(`t`.`created`) ASC
            LIMIT 
                {OFFSET}, {COUNT};
            """.format(
                OFFSET=start_at,
                COUNT=count
            ))

            return self.cursor.fetchmany(size=count)

        except Exception as e:
                
                print(e)
    
                return None

    def __get_wheres_map(self: TransactionData, wheres: dict) -> Tuple[str, str]:

        ## todos: make groups
        ##* groups.foo.bar.baz groups.groups.bar.foo groups.groups.bar.baz
        ##* result must be (foo.bar.baz ( bar.foo bar.baz ))

        try:

            first: bool
            context: str

            first = True
            context = ""

            key: str
            value: Any

            for key, value in wheres.items():

                operation: str
                operation = "AND"

                like: bool
                like = False

                maynot: bool
                maynot = False

                ##* start at 2
                if key.startswith("&!") or \
                    key.startswith("!&"):

                    operation = "AND"
                    maynot = True
                    key = key[2:]

                if key.startswith("|!") or \
                    key.startswith("!|"):

                    operation = "OR"
                    maynot = True
                    key = key[2:]

                ##* start at 1
                if key.startswith("&"):

                    operation = "AND"
                    key = key[1:]

                if key.startswith("|"):

                    operation = "OR"
                    key = key[1:]

                if key.startswith("!"):

                    operation = "AND"
                    maynot = True
                    key = key[1:]

                ##* end at 1
                if key.endswith("^") and \
                    "%" in value:

                    like = True
                    key = key[:-1]

                if key.endswith("*") and \
                    (isinstance(value, tuple) or \
                        isinstance(value, list)):

                    like = True
                    key = key[1:]
                    
                    wheres[key] = "(" + str.join(",", value) + ")"

                if isinstance(value, dict):

                    raise ValueError("Not Implemented")

                ##* final operations

                if first:

                    operation = ""

                else:

                    operation = " " + operation + "\n"

                if "." in key:

                    key = "`" + str.join("`.`", key.split(".")) + "`"

                else:

                    key = "`" + key + "`"

                if maynot:

                    operation += "NOT "

                if like:
                
                    context += operation + key + " LIKE ?"

                else:

                    context += operation + key + " = ?"

                first = False

            if not len(context):

                raise ValueError("No wheres")

            return context, tuple(wheres.values())

        except Exception as e:

            print(e)

            return None, None
