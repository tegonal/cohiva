## For backwards compatibility with Python 3.9 (to support the | operator for types)
from __future__ import annotations

import importlib
import logging

from django.conf import settings

logger = logging.getLogger("finance_accounting")


class AccountingManager:
    backends = {}
    default_backend_label = None

    @classmethod
    def register(cls, settings_label, backend_class, db_id=0):
        if settings_label in cls.backends:
            raise KeyError(f"Accounting backend with label {settings_label} already registered.")
        for backend in cls.backends.values():
            if backend["class"] == backend_class and backend["db_id"] == db_id:
                raise KeyError(
                    f"Accounting backend {backend_class.__name__} with "
                    f"DB id {db_id} already registered."
                )
        cls.backends[settings_label] = {"class": backend_class, "db_id": db_id}
        if not cls.default_backend_label:
            cls.default_backend_label = settings_label
        if settings_label == cls.default_backend_label:
            default_txt = "DEFAULT "
        else:
            default_txt = ""
        logger.info(
            f"Registered {default_txt}accounting backend: {settings_label} "
            f"[{backend_class.__name__}, db_id={db_id}]"
        )

    @classmethod
    def unregister(cls, settings_label):
        if settings_label not in cls.backends:
            raise KeyError(f"Accounting backend with label {settings_label} not registered.")
        class_name = cls.backends[settings_label]["class"].__name__
        db_id = cls.backends[settings_label]["db_id"]
        del cls.backends[settings_label]
        if settings_label == cls.default_backend_label:
            cls.default_backend_label = None
            default_txt = "DEFAULT "
        else:
            default_txt = ""
        logger.info(
            f"Unregistered {default_txt}accounting backend: {settings_label} "
            f"[{class_name}, db_id={db_id}]"
        )

    @classmethod
    def unregister_all(cls):
        backend_labels = list(cls.backends.keys())
        for label in backend_labels:
            cls.unregister(label)

    @classmethod
    def register_backends_from_settings(cls):
        cls.unregister_all()
        cls.default_backend_label = getattr(settings, "FINANCIAL_ACCOUNTING_DEFAULT_BACKEND", None)
        for label, config in getattr(settings, "FINANCIAL_ACCOUNTING_BACKENDS", {}).items():
            module_name, class_name = config["BACKEND"].rsplit(".", 1)
            module = importlib.import_module(module_name)
            backend_class = getattr(module, class_name)
            db_id = config.get("DB_ID", 0)
            cls.register(label, backend_class, db_id)

    @classmethod
    def get_backend_label_from_book_ids(cls, book_type_id, db_id=0):
        matching_backend = None
        for label, backend in cls.backends.items():
            if backend["class"].book_type_id == book_type_id and backend["db_id"] == db_id:
                if matching_backend:
                    raise KeyError(
                        f"Mehrere Buchhaltungen mit dem gleichen book_type_id {book_type_id} "
                        f"und gleicher DB id {db_id} gefunden."
                    )
                matching_backend = label
        if not matching_backend:
            raise KeyError(
                f"Keine Buchhaltung mit book_type_id {book_type_id} und DB id {db_id} gefunden."
            )
        return matching_backend

    def __init__(
        self,
        messages: list | None = None,
        backend_label: str | None = None,
        book_type_id: str | None = None,
        db_id: int = 0,
    ):
        self.messages = messages
        self.backend_obj = None
        if book_type_id:
            backend_label = self.get_backend_label_from_book_ids(book_type_id, db_id)
        if not backend_label:
            backend_label = self.default_backend_label
        backend = self.backends.get(backend_label, None)
        if backend:
            self.backend_class = backend["class"]
            self.db_id = backend["db_id"]
        else:
            self.backend_class = None
            self.db_id = 0
        self.backend_label = backend_label

    def __enter__(self):
        if not self.backend_class:
            logger.error("No financial accounting backend configured.")
            if self.messages is not None:
                self.messages.append("Keine Buchhaltungsanbindung konfiguriert.")
                return None
            raise RuntimeError("Keine Buchhaltungsanbindung konfiguriert.")
        else:
            try:
                self.backend_obj = self.backend_class(self.backend_label, self.db_id)
                return self.backend_obj
            except Exception as e:
                logger.error(f"Couldn't initialize accounting backend {self.backend_class}: {e}")
                if self.messages is not None:
                    self.messages.append(f"Konnte Buchhaltung nicht initialisieren: {e}")
                    return None
                raise e

    def __exit__(self, exc_type, exc_value, traceback):
        if self.backend_obj:
            self.backend_obj.close()
