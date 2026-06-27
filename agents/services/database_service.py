import logging
from django.apps import apps

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Service to help database analysis, schema inspection, and model metadata generation.
    """
    
    @staticmethod
    def get_all_models_meta():
        """
        Retrieves database schema metadata for all models in the active Django apps.
        """
        models_meta = {}
        for app_config in apps.get_app_configs():
            # Skip standard Django system apps for brevity unless they are project models
            if app_config.name in ['admin', 'auth', 'contenttypes', 'sessions', 'messages', 'staticfiles']:
                continue
                
            models_meta[app_config.name] = {}
            for model in app_config.get_models():
                fields = []
                for field in model._meta.fields:
                    fields.append({
                        "name": field.name,
                        "type": field.get_internal_type(),
                        "null": field.null,
                        "blank": field.blank,
                        "unique": field.unique,
                        "is_relation": field.is_relation
                    })
                
                # Check for ManyToManyFields
                m2m_fields = []
                for field in model._meta.many_to_many:
                    m2m_fields.append({
                        "name": field.name,
                        "type": "ManyToManyField",
                        "related_model": field.related_model._meta.label
                    })

                models_meta[app_config.name][model.__name__] = {
                    "table_name": model._meta.db_table,
                    "fields": fields,
                    "m2m_fields": m2m_fields,
                    "verbose_name": str(model._meta.verbose_name)
                }
        return models_meta
