from typing import Any


class DBRouter:
    """
    A router to control all database operations on models in the
    accounts and project applications.
    """

    def db_for_read(self, model: Any, **hints: Any) -> str | None:
        """
        Attempts to read accounts models go to users db.
        """
        if model._meta.app_label == "accounts":  # type: ignore
            return "default"
        elif model._meta.app_label == "project":  # type: ignore
            return "projects"
        return None

    def db_for_write(self, model: Any, **hints: Any) -> str | None:
        """
        Attempts to write accounts models go to users db.
        """
        if model._meta.app_label == "accounts":  # type: ignore
            return "default"
        elif model._meta.app_label == "project":  # type: ignore
            return "projects"
        return None

    def allow_relation(self, obj1: Any, obj2: Any, **hints: Any) -> bool | None:
        """
        Allow relations if a model in the accounts app is involved.
        """
        if obj1._meta.app_label == "accounts" or obj2._meta.app_label == "accounts":  # type: ignore
            return True
        return None

    def allow_migrate(
        self, db: str, app_label: str, model_name: str | None = None, **hints: Any
    ) -> bool | None:
        """
        Make sure the accounts app only appears in the 'default' database
        and project app only in 'projects' database.
        """
        if app_label == "accounts":
            return db == "default"
        elif app_label == "project":
            return db == "projects"
        return None
