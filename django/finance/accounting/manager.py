import importlib
import logging

from django.conf import settings

logger = logging.getLogger("finance_accounting")


class AccountingManager:
    backends = {}
    default_backend_label = None

    @classmethod
    def register(cls, settings_label, backend_class):
        if settings_label in cls.backends:
            raise KeyError(f"Accounting backend with label {settings_label} already registered.")
        cls.backends[settings_label] = backend_class
        if not cls.default_backend_label:
            cls.default_backend_label = settings_label
        if settings_label == cls.default_backend_label:
            logger.info(
                f"Registered DEFAULT accounting backend: {settings_label} [{backend_class.__name__}]"
            )
        else:
            logger.info(
                f"Registered accounting backend: {settings_label} [{backend_class.__name__}]"
            )

    @classmethod
    def unregister(cls, settings_label):
        if settings_label not in cls.backends:
            raise KeyError(f"Accounting backend with label {settings_label} not registered.")
        class_name = cls.backends[settings_label].__name__
        del cls.backends[settings_label]
        if settings_label == cls.default_backend_label:
            cls.default_backend_label = None
            logger.info(
                f"Unregistered DEFAULT accounting backend: {settings_label} [{class_name}]"
            )
        else:
            logger.info(f"Unregistered accounting backend: {settings_label} [{class_name}]")

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
            cls.register(label, backend_class)

    @classmethod
    def get_backend_label_from_book_type_id(cls, book_type_id):
        matching_backend = None
        for label, backend_class in cls.backends.items():
            if backend_class.book_type_id == book_type_id:
                if matching_backend:
                    raise KeyError(
                        f"Mehrere Buchhaltungen mit dem gleichen book_type_id {book_type_id} gefunden."
                    )
                matching_backend = label
        return matching_backend

    def __init__(
        self,
        messages: list | None = None,
        backend_label: str | None = None,
        book_type_id: str | None = None,
    ):
        self.messages = messages
        self.backend_obj = None
        if book_type_id:
            backend_label = self.get_backend_label_from_book_type_id(book_type_id)
        if not backend_label:
            backend_label = self.default_backend_label
        self.backend_class = self.backends.get(backend_label, None)
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
                self.backend_obj = self.backend_class(self.backend_label)
                return self.backend_obj
            except Exception as e:
                logger.error(f"Couldn't initialize accounting backend {self.backend_class}: {e}")
                if self.messages:
                    self.messages.append(f"Konnte Buchhaltung nicht initialisieren: {e}")
                    return None
                raise e

    def __exit__(self, exc_type, exc_value, traceback):
        if self.backend_obj:
            self.backend_obj.close()
