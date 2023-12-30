import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.repository.contacts import (
    get_contacts, get_contact_by_id, create, update, remove, set_favorite
)
from src.schemas import ContactModel, ContactFavoriteModel


class TestContacts(IsolatedAsyncioTestCase):
    def setUp(self):
        """
        The setUp function is called before each test function.
        It creates a mock session object and a user object with an id of 1.

        :param self: Represent the instance of the class
        :return: A user object with id= 1
        :doc-author: Trelent
        """
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.contacts = [Contact(id=i, firstname=f"firstname{i}", lastname=f"lastname{i}") for i in range(10)]
        self.body = ContactModel(firstname="firstname",
                                 lastname="lastname",
                                 email="email@example.com",
                                 phone="1234567890",
                                 birthday="2021-01-01",
                                 additional_info="additional_info",
                                 is_favorite=True)
        self.favorite_body = ContactFavoriteModel(firstname="firstname",
                                 lastname="lastname",
                                 email="email@example.com",
                                 phone="1234567890",
                                 birthday="2021-01-01",
                                 additional_info="additional_info",
                                 is_favorite=True)

    def tearDown(self):
        """
        The tearDown function is called after each test.
        It deletes the session, user and contacts objects created in setUp.

        :param self: Represent the instance of the class
        :return: A delete function to remove the session, user and contacts
        :doc-author: Trelent
        """
        self.session.delete()
        self.user = None
        self.contacts = None
        self.body = None

    async def test_get_contacts(self):
        """
        The test_get_contacts function tests the get_contacts function.
        It does this by mocking out the session object and setting it to return a list of contacts when its query method is called.
        The test then calls get_contacts with a user, limit, offset, and session object as arguments. It asserts that the result of calling
        get_contacts is equal to self.contacts.

        :param self: Access the instance of the class
        :return: A list of contacts
        :doc-author: Trelent
        """
        user = self.user
        limit = 10
        offset = 0
        self.session.query().filter().limit().offset().all.return_value = self.contacts
        result = await get_contacts(user, limit, offset, self.session)
        self.assertEqual(result, self.contacts)

    async def test_get_contact_by_id(self):
        """
        The test_get_contact_by_id function tests the get_contact_by_id function.
            It does this by creating a mock user, contact id, and contact object.
            Then it creates a mock database session and sets the return value of
            db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first() to be equal to the
            created contact object (which is what we want returned from get_contact by id). Finally it calls await on
            get-contact-by-id with our mocked objects as arguments and asserts that result

        :param self: Represent the instance of the class
        :return: The contact object if it exists
        :doc-author: Trelent
        """
        user = self.user
        contact_id = 1
        contact = Contact(id=contact_id, firstname="firstname", lastname="lastname", user_id=user.id)
        db = self.session
        db.query(Contact).filter(
            and_(Contact.user_id == user.id, Contact.id == contact_id)).first.return_value = contact
        result = await get_contact_by_id(user, contact_id, db)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        """
        The test_create_contact function tests the create function in the contacts.py file.
        It creates a user, body, and db object to pass into the create function. It then asserts that
        the result of calling create with those objects is equal to what we expect it to be.

        :param self: Represent the instance of the class
        :return: The result of the create function, which is a contact object
        :doc-author: Trelent
        """
        user = self.user
        body = self.body
        db = self.session

        result = await create(user, body, db)
        self.assertEqual(result.firstname, body.firstname)
        self.assertEqual(result.lastname, body.lastname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.additional_info, body.additional_info)
        self.assertEqual(result.is_favorite, body.is_favorite)
        self.assertTrue(hasattr(result, "id"))
        self.assertTrue(hasattr(result, "user_id"))
        self.assertTrue(hasattr(result, "created_at"))
        self.assertTrue(hasattr(result, "updated_at"))

    async def test_update(self):
        """
        The test_update function tests the update function.
        It does so by creating a mock user, body and db object.
        The contact_id is set to 1 and the contact is created with old values for all fields except id, which is set to 1 as well as user_id which is set to the mock user's id.
        The db query returns this contact when queried for a Contact with an id of 1 that belongs to our mock user (user_id == self.user).
        Then we call update(self) on our mocked objects and assert that it returned our mocked Contact object (result == self). We also assert that

        :param self: Represent the instance of the class
        :return: The contact object
        :doc-author: Trelent
        """
        user = self.user
        body = self.body
        db = self.session
        contact_id = 1
        contact = Contact(id=contact_id, firstname="old_firstname", lastname="old_lastname",
                          email="old_email@example.com", user_id=user.id)
        db.query(Contact).filter(
            and_(Contact.user_id == user.id, Contact.id == contact_id)).first.return_value = contact
        result = await update(user, contact_id, body, db)

        self.assertEqual(result, contact)
        self.assertEqual(contact.firstname, body.firstname)
        self.assertEqual(contact.lastname, body.lastname)
        self.assertEqual(contact.email, body.email)
        self.assertEqual(contact.phone, body.phone)
        self.assertEqual(contact.birthday, body.birthday)
        self.assertEqual(contact.additional_info, body.additional_info)
        self.assertEqual(contact.is_favorite, body.is_favorite)
        self.assertTrue(hasattr(result, "id"))
        self.assertTrue(hasattr(result, "user_id"))
        self.assertTrue(hasattr(result, "created_at"))
        self.assertTrue(hasattr(result, "updated_at"))

    async def test_remove(self):
        """
        The test_remove function tests the remove function in the contacts.py file.
        It does this by creating a mock user, contact_id, and database session object.
        The test then creates a mock Contact object with an id of 1 and assigns it to
        the variable 'contact'. The test then sets up the return value for when
        db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first() is called to be equal to 'contact'. The result of calling await remove(user, contact_id) is assigned to result which should be equal

        :param self: Access the attributes and methods of the class
        :return: The contact that was removed
        :doc-author: Trelent
        """
        user = self.user
        contact_id = 1
        db = self.session
        contact = Contact(id=contact_id, user_id=user.id)
        db.query(Contact).filter(
            and_(Contact.user_id == user.id, Contact.id == contact_id)).first.return_value = contact
        result = await remove(user, contact_id, db)
        self.assertEqual(result, contact)

    async def test_set_favorite(self):
        """
        The test_set_favorite function tests the set_favorite function in the contacts.py file.
        It does this by creating a user, contact_id, and db object to pass into the function as parameters.
        The test then creates a Contact object with an id of 1 and sets its is_favorite attribute to False.
        The test then calls set_favorite with these objects as parameters and asserts that it returns True.

        :param self: Make the function a method of the class
        :return: The contact object
        :doc-author: Trelent
        """
        user = self.user
        contact_id = 1
        db = self.session
        contact = Contact(id=contact_id, user_id=user.id, is_favorite=False)
        db.query(Contact).filter(
            and_(Contact.user_id == user.id, Contact.id == contact_id)).first.return_value = contact
        result = await set_favorite(user, contact_id, self.favorite_body, db)
        self.assertEqual(result, contact)
        self.assertTrue(result.is_favorite)


if __name__ == '__main__':
    unittest.main()