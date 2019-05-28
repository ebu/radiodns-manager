from unittest import TestCase

from plugIt.bridge.utilities import check_permissions


class FakeUser:
    def __init__(self, is_authenticated, is_staff, is_superuser):
        self.is_authenticated = is_authenticated
        self.is_staff = is_staff
        self.is_superuser = is_superuser


class FakeRequest:
    def __init__(self, is_authenticated=False, is_staff=False, is_superuser=False):
        self.user = FakeUser(is_authenticated, is_staff, is_superuser)


class TestCheckPermission(TestCase):

    def test_user_must_be_logged(self):
        assert check_permissions(FakeRequest(is_authenticated=False), {"only_logged_user": True},
                                 {}) == "only_logged_user"
        assert check_permissions(FakeRequest(is_authenticated=True), {"only_logged_user": True}, {}) is None
        assert check_permissions(FakeRequest(is_authenticated=True, is_staff=True), {"only_logged_user": True},
                                 {}) is None
        assert check_permissions(FakeRequest(is_authenticated=True, is_superuser=True), {"only_logged_user": True},
                                 {}) is None

    def test_user_must_be_part_of_orga(self):
        assert check_permissions(FakeRequest(is_authenticated=False), {"only_orga_member_user": True},
                                 {}) == "only_orga_member_user"
        assert check_permissions(FakeRequest(is_authenticated=True), {"only_orga_member_user": True},
                                 {}) == "only_orga_member_user"
        assert check_permissions(FakeRequest(is_authenticated=True, is_staff=True), {"only_orga_member_user": True},
                                 {}) is None
        assert check_permissions(FakeRequest(is_authenticated=True, is_superuser=True), {"only_orga_member_user": True},
                                 {}) is None

    def test_user_must_be_orga_staff(self):
        assert check_permissions(FakeRequest(is_authenticated=False), {"only_orga_admin_user": True},
                                 {}) == "only_orga_admin_user"
        assert check_permissions(FakeRequest(is_authenticated=True), {"only_orga_admin_user": True},
                                 {}) == "only_orga_admin_user"
        assert check_permissions(FakeRequest(is_authenticated=True, is_staff=True), {"only_orga_admin_user": True},
                                 {}) == "only_orga_admin_user"
        assert check_permissions(FakeRequest(is_authenticated=True, is_superuser=True), {"only_orga_admin_user": True},
                                 {}) is None
