import logging

logger = logging.getLogger("finance_accounting")


class AccountingManager:
    backends = []

    @classmethod
    def register(cls, backend_class):
        cls.backends.append(backend_class)
        logger.info(f"Registered accounting backend: {backend_class}")

    @classmethod
    def unregister(cls, backend_class):
        if not cls.backends:
            return
        cls.backends.remove(backend_class)
        logger.info(f"Unregistered accounting backend: {backend_class}")

    @classmethod
    def unregister_all(cls):
        cls.backends = []
        logger.info("Unregistered all accounting backends.")

    def __init__(self, messages: list | None = None, book_type_id: str | None = None):
        self.messages = messages
        self.backend_obj = None
        if self.backends:
            self.backend_class = self.backends[0]
            if book_type_id:
                for backend in self.backends:
                    if backend.book_type_id == book_type_id:
                        self.backend_class = backend
        else:
            self.backend_class = None

    def __enter__(self):
        if not self.backends or not self.backend_class:
            logger.error("No financial accounting backend configured.")
            if self.messages is not None:
                self.messages.append("Keine Buchhaltungsanbindung konfiguriert.")
                return None
            raise RuntimeError("Keine Buchhaltungsanbindung konfiguriert.")
        else:
            try:
                self.backend_obj = self.backend_class()
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
