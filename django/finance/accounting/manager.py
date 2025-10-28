class AccountingManager:
    backends = []

    @classmethod
    def register(cls, backend_class):
        cls.backends.append(backend_class)

    @classmethod
    def unregister(cls, backend_class):
        if not cls.backends:
            return
        cls.backends.remove(backend_class)

    @classmethod
    def unregister_all(cls):
        cls.backends = []

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
        if not self.backends:
            if self.messages is not None:
                self.messages.append("Keine Buchhaltungsanbindung konfiguriert.")
                return None
            raise RuntimeError("Keine Buchhaltungsanbindung konfiguriert.")
        else:
            try:
                self.backend_obj = self.backends[0]()
                return self.backend_obj
            except Exception as e:
                if self.messages:
                    self.messages.append(f"Konnte Buchhaltung nicht initialisieren: {e}")
                    return None
                raise e

    def __exit__(self, exc_type, exc_value, traceback):
        if self.backend_obj:
            self.backend_obj.close()
