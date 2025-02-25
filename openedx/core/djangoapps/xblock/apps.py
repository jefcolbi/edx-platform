"""
Django app configuration for the XBlock Runtime django app
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from django.apps import AppConfig, apps
from django.conf import settings
from xblock.runtime import DictKeyValueStore, KvsFieldData

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.xblock.runtime.blockstore_field_data import BlockstoreFieldData


class XBlockAppConfig(AppConfig):
    """
    Django app configuration for the new XBlock Runtime django app
    """
    name = 'openedx.core.djangoapps.xblock'
    verbose_name = 'New XBlock Runtime'
    label = 'xblock_new'  # The name 'xblock' is already taken by ORA2's 'openassessment.xblock' app :/

    # If this is True, users must have 'edit' permission to be allowed even to
    # view content. (It's only true in Studio)
    require_edit_permission = False

    def get_runtime_system_params(self):
        """
        Get the XBlockRuntimeSystem parameters appropriate for viewing and/or
        editing XBlock content.
        """
        raise NotImplementedError

    def get_site_root_url(self):
        """
        Get the absolute root URL to this site, e.g. 'https://courses.example.com'
        Should not have any trailing slash.
        """
        raise NotImplementedError

    def get_learning_context_params(self):
        """
        Get additional kwargs that are passed to learning context implementations
        (LearningContext subclass constructors). For example, this can be used to
        specify that the course learning context should load the course's list of
        blocks from the _draft_ version of the course in studio, but from the
        published version of the course in the LMS.
        """
        return {}


class LmsXBlockAppConfig(XBlockAppConfig):
    """
    LMS-specific configuration of the XBlock Runtime django app.
    """

    def get_runtime_system_params(self):
        """
        Get the XBlockRuntimeSystem parameters appropriate for viewing and/or
        editing XBlock content in the LMS
        """
        return dict(
            authored_data_store=BlockstoreFieldData(),
            student_data_store=KvsFieldData(kvs=DictKeyValueStore()),
        )

    def get_site_root_url(self):
        """
        Get the absolute root URL to this site, e.g. 'https://courses.example.com'
        Should not have any trailing slash.
        """
        return configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL)


class StudioXBlockAppConfig(XBlockAppConfig):
    """
    Studio-specific configuration of the XBlock Runtime django app.
    """
    # In Studio, users must have 'edit' permission to be allowed even to view content
    require_edit_permission = True

    BLOCKSTORE_DRAFT_NAME = "studio_draft"

    def get_runtime_system_params(self):
        """
        Get the XBlockRuntimeSystem parameters appropriate for viewing and/or
        editing XBlock content in Studio
        """
        return dict(
            authored_data_store=BlockstoreFieldData(),
            student_data_store=KvsFieldData(kvs=DictKeyValueStore()),
        )

    def get_site_root_url(self):
        """
        Get the absolute root URL to this site, e.g. 'https://studio.example.com'
        Should not have any trailing slash.
        """
        scheme = "https" if settings.HTTPS == "on" else "http"
        return scheme + '://' + settings.CMS_BASE
        # or for the LMS version: configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL)

    def get_learning_context_params(self):
        """
        Get additional kwargs that are passed to learning context implementations
        (LearningContext subclass constructors). For example, this can be used to
        specify that the course learning context should load the course's list of
        blocks from the _draft_ version of the course in studio, but from the
        published version of the course in the LMS.
        """
        return {
            "use_draft": self.BLOCKSTORE_DRAFT_NAME,
        }


def get_xblock_app_config():
    """
    Get whichever of the above AppConfig subclasses is active.
    """
    return apps.get_app_config(XBlockAppConfig.label)
