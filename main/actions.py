# -*- coding: utf-8 -*-

# Utils
from utils import action, only_orga_member_user


# Include homepage
@action(route="/", template="main/home.html")
@only_orga_member_user()
def main_home(request):
    """Show the home page."""
    
    return {}