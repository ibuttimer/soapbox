#  MIT License
#
#  Copyright (c) 2022 Ian Buttimer
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM,OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#
import os
import unittest
import django

# 'allauth' checks for 'django.contrib.sites', so django must be setup before
# test
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soapbox.settings")
django.setup()

from user.forms import UserSignupForm   # noqa


class TestUserSignupForm(unittest.TestCase):
    """ Test user signup form """

    # based on allauth defaults
    REQUIRED_FIELDS = [
        UserSignupForm.FIRST_NAME_FF,
        UserSignupForm.LAST_NAME_FF,
        UserSignupForm.USERNAME_FF,
        UserSignupForm.PASSWORD_FF,
        UserSignupForm.PASSWORD_CONFIRM_FF,
    ]
    NOT_REQUIRED_FIELDS = [
        UserSignupForm.EMAIL_FF,
    ]
    # django default for password is; min 8, not too similar to username etc.
    VALID_DATA = {
        UserSignupForm.FIRST_NAME_FF: "Firstname",
        UserSignupForm.LAST_NAME_FF: "Lastname",
        UserSignupForm.USERNAME_FF: "username",
        UserSignupForm.PASSWORD_FF: "shhh-v3ry_secret",
        UserSignupForm.PASSWORD_CONFIRM_FF: "shhh-v3ry_secret",
    }

    def test_signup_form_required(self):
        """ Test setup form required fields """
        for field in TestUserSignupForm.REQUIRED_FIELDS:
            with self.subTest(msg=f"required field {field}"):
                data = TestUserSignupForm.VALID_DATA.copy()
                data[field] = ""
                form = UserSignupForm(data)
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors.keys())
                self.assertEqual(form.errors[field][0],
                                 'This field is required.')

    def test_signup_form_not_required(self):
        """ Test setup form not required fields """
        data = TestUserSignupForm.VALID_DATA.copy()
        for key in UserSignupForm().fields.keys():
            if key not in TestUserSignupForm.VALID_DATA:
                data[key] = ""
        form = UserSignupForm(data)
        self.assertTrue(form.is_valid())

    def test_fields_explicit_in_meta(self):
        """ Test fields are explicitly declared in metaclass """
        form = UserSignupForm()
        self.assertEqual(form.Meta.fields, [
            "first_name", "last_name", "email", "username", "password1",
            "password2"
        ])


if __name__ == '__main__':
    unittest.main()
