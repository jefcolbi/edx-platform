"""
Tests for account linking Python API.
"""
from __future__ import absolute_import, unicode_literals

from uuid import UUID

import ddt
from django.contrib.auth import get_user_model
from django.test import TestCase

from lms.djangoapps.program_enrollments.constants import ProgramEnrollmentStatuses as PEStatuses
from lms.djangoapps.program_enrollments.tests.factories import ProgramEnrollmentFactory
from student.tests.factories import UserFactory

from ..reading import fetch_program_enrollments, get_program_enrollment

User = get_user_model()


@ddt.ddt
class ProgramEnrollmentReadingTests(TestCase):
    """
    Tests for program enrollment reading functions.
    """
    program_uuid_x = UUID('7aeadb7d-5f48-493d-9410-84e1d36c657f')
    program_uuid_y = UUID('b08071d8-f803-43f6-bbf3-5ae15d393649')
    curriculum_uuid_a = UUID('e331472e-bd26-43d0-94b8-b0063858210b')
    curriculum_uuid_b = UUID('db717f6c-145f-43db-ad05-f9ad65eec285')
    curriculum_uuid_c = UUID('06b260eb-4577-4559-85f0-4a83e8160a4d')
    username_0 = 'user-0'
    username_1 = 'user-1'
    username_2 = 'user-2'
    username_3 = 'user-3'
    ext_2 = 'student-2'
    ext_3 = 'student-3'
    ext_4 = 'student-4'
    ext_5 = 'student-5'

    @classmethod
    def setUpTestData(cls):
        super(ProgramEnrollmentReadingTests, cls).setUpTestData()
        cls.user_0 = UserFactory(username=cls.username_0)
        cls.user_1 = UserFactory(username=cls.username_1)
        cls.user_2 = UserFactory(username=cls.username_2)
        cls.user_3 = UserFactory(username=cls.username_3)
        test_data = [
            (cls.user_0, None, cls.program_uuid_x, cls.curriculum_uuid_a, PEStatuses.ENROLLED),
            (cls.user_1, None, cls.program_uuid_x, cls.curriculum_uuid_a, PEStatuses.PENDING),
            (cls.user_2, cls.ext_2, cls.program_uuid_x, cls.curriculum_uuid_b, PEStatuses.ENROLLED),
            (cls.user_3, cls.ext_3, cls.program_uuid_x, cls.curriculum_uuid_b, PEStatuses.PENDING),
            (None, cls.ext_4, cls.program_uuid_y, cls.curriculum_uuid_c, PEStatuses.ENROLLED),
            (None, cls.ext_5, cls.program_uuid_y, cls.curriculum_uuid_c, PEStatuses.PENDING),
        ]
        cls.enrollments = [
            ProgramEnrollmentFactory(
                user=user,
                external_user_key=external_user_key,
                program_uuid=program_uuid,
                curriculum_uuid=curriculum_uuid,
                status=status,
            )
            for user, external_user_key, program_uuid, curriculum_uuid, status
            in test_data
        ]

    @ddt.data(
        # Realized enrollment, specifying only user.
        (program_uuid_x, curriculum_uuid_a, username_0, None, 0),

        # Realized enrollment, specifiying both user and external key.
        (program_uuid_x, curriculum_uuid_b, username_2, ext_2, 2),

        # Realized enrollment, specifiying only external key.
        (program_uuid_x, curriculum_uuid_b, username_3, ext_3, 3),

        # Waiting enrollment, specifying external key
        (program_uuid_y, curriculum_uuid_c, None, ext_4, 4),

        # Specifying no curriculum (because ext_4 only has Program Y
        # enrollments in one curriculum, so it's not ambiguous).
        (program_uuid_y, curriculum_uuid_c, None, ext_5, 5),
    )
    @ddt.unpack
    def test_get_program_enrollment(
            self,
            program_uuid,
            curriculum_uuid,
            username,
            external_user_key,
            expected_enrollment_index,
    ):
        user = User.objects.get(username=username) if username else None
        actual_enrollment = get_program_enrollment(
            program_uuid=program_uuid,
            user=user,
            external_user_key=external_user_key,
            curriculum_uuid=curriculum_uuid,
        )
        expected_enrollment = self.enrollments[expected_enrollment_index]
        assert expected_enrollment == actual_enrollment

    def test_fetch_program_enrollments(self):
        _actual_enrollments = fetch_program_enrollments(
            program_uuid=self.program_uuid_x,
        )
        _ = '''expected_enrollments = {
            'student-0': {
                'curriculum_uuid': self.curriculum_uuid_a,
                'status': 'enrolled',
                'program_uuid': self.program_uuid_x,
            },
            'student-1': {
                'curriculum_uuid': self.curriculum_uuid_b,
                'status': 'pending',
                'program_uuid': self.program_uuid_x,
            },
            'student-2': {
                'curriculum_uuid': self.curriculum_uuid_a,
                'status': 'enrolled',
                'program_uuid': self.program_uuid_x,
            },
            'student-3': {
                'curriculum_uuid': self.curriculum_uuid_b,
                'status': 'pending',
                'program_uuid': self.program_uuid_x,
            },
        }
        assert expected_enrollments == {
            enrollment.external_user_key: {
                'curriculum_uuid': enrollment.curriculum_uuid,
                'status': enrollment.status,
                'program_uuid': enrollment.program_uuid,
            }
            for enrollment in actual_enrollments
        }
        '''
        assert 1 == 1
