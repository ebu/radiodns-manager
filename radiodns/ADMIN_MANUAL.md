## Admin Manual

All RadioDNS Manager administration is handled in the django admin panel, which is available on `/admin/`. 
If the expected functionality is not present, send a request to Paweł Glimos - `glimos@ebu.ch`

### FAQ - Frequently Asked Questions

* **How to add a new user?**

Go to `Administration Panel -> Radiodns_Auth -> Users -> Press Add` or visit `/admin/radiodns_auth/user/add/`

Fill out the form. Username and password are required. 
WARNING: The user will not be automatically associated with the SSO user using the same email address.
We are working on fixing that. 

* **How to delete an user?**

Go to `Administration Panel -> Radiodns_Auth -> Users` or visit `/admin/radiodns_auth/user/`

Select users you want to delete and choose action `Delete selected users`. Verify your choice on the confirmation screen, and when you are sure confirm.

* **How to grant user the admin rights?**

Go to `Administration Panel -> Radiodns_Auth -> Users` or visit `/admin/radiodns_auth/user/`

Select the user you want to grant admin rights to. In the edit user form mark: `is_staff` and `is_superuser`. Press save.

* **How to create an organization?**

Go to `Administration Panel -> Manager -> Organization -> Press Add` or visit `/admin/manager/organization/add/`

Fill out the form. Required fields are bold. Press save.

* **How to delete an organization?**

Go to `Administration Panel -> Manager -> Organization` or visit `/admin/manager/organization/`

Select organization you want to delete and choose action `Delete selected organizations`. Verify your choice on the confirmation screen, and when you are sure confirm.

* **How to change organization's logo?**

Go to `Administration Panel -> Manager -> Organization` or visit `/admin/manager/organization/`

Using form, pick a logo from the available list, and insert it in the `default image id` field. Press save.

* **How to add a new user to an organization?**

Go to `Administration Panel -> Manager -> Organization` or visit `/admin/manager/organization/`

Select an organization. On the bottom of the form you can find user selection part, where you can find and add existing users to the organization. 

You can also find the user, then add the organization using the user form. 

* **How to check which organizations a user is a part of?**

Go to `Administration Panel -> Radiodns_Auth -> Users` or visit `/admin/radiodns_auth/user/`

Select the user you want to verify. The list of all organizations that the user is added to is at the bottom of the form. 

