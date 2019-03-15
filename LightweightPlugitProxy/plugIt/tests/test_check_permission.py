from unittest import TestCase

from plugIt.bridge.utilities import check_permissions


class FakeOrga:
    def __init__(self, codops="default"):
        self.codops = codops


class FakeUser:
    def __init__(self, is_authenticated, is_staff, is_superuser, organization):
        self.is_authenticated = is_authenticated
        self.is_staff = is_staff
        self.is_superuser = is_superuser
        self.organization = organization


class FakeRequest:
    def __init__(self, is_authenticated=False, is_staff=False, is_superuser=False, organization=FakeOrga()):
        self.user = FakeUser(is_authenticated, is_staff, is_superuser, organization)


class TestCheckPermission(TestCase):

    def test_user_must_be_logged(self):
        assert check_permissions(FakeRequest(is_authenticated=False), {"only_logged_user": True},
                                 {}) == "only_logged_user"
        assert check_permissions(FakeRequest(is_authenticated=True), {"only_logged_user": True}, {}) is None

    def test_user_must_be_part_of_orga(self):
        assert check_permissions(FakeRequest(is_authenticated=True), {"only_orga_member_user": True},
                                 {"ebu_codops": "zzebu"}) == "only_orga_member_user"
        assert check_permissions(FakeRequest(is_authenticated=True, organization=FakeOrga("zzebu")),
                                 {"only_orga_member_user": True}, {"ebu_codops": "zzebu"}) is None
        assert check_permissions(FakeRequest(is_authenticated=True), {"only_orga_member_user": True}, {}) is None

    def test_user_must_be_orga_staff(self):
        assert check_permissions(FakeRequest(is_authenticated=True), {"only_orga_admin_user": True},
                                 {}) == "only_orga_admin_user"
        assert check_permissions(FakeRequest(is_authenticated=True, is_staff=True), {"only_orga_admin_user": True},
                                 {}) is None
        assert check_permissions(FakeRequest(is_authenticated=True, is_superuser=True), {"only_orga_admin_user": True},
                                 {}) is None
        assert check_permissions(FakeRequest(is_authenticated=True, is_superuser=True), {"only_orga_admin_user": True},
                                 {"ebu_codops": "zzebu"}) == "only_orga_admin_user"
        assert check_permissions(FakeRequest(is_authenticated=True, is_superuser=True, organization=FakeOrga("zzebu")),
                                 {"only_orga_admin_user": True}, {"ebu_codops": "zzebu"}) is None
