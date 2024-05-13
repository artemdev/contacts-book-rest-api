import unittest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Contact, User
from src.schemas import ContactModel
from datetime import datetime, date
from unittest.mock import ANY
from src.repository.contacts import (
    get_contacts,
    get_upcoming_birthdays,
    get_contact,
    create_contact,
    update_contact,
    remove_contact,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1, username='test_user',
                         password="qwerty", is_confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [Contact(id=1, first_name='first_name', last_name='last_name', email="artem.zimovets@gmail.com", phone="123123123", birthday="25.04.1990", additional_note="test", user=self.user),
                    Contact(id=2, first_name='first_name2', last_name='last_name2', email="artem2.zimovets@gmail.com", phone="123123123", birthday="25.04.1990", additional_note="test2", user=self.user)]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, user_id=self.user.id)
        self.assertEqual(result, contacts)

    async def test_get_upcoming_birthdays(self):
        contacts = [Contact(id=1, first_name='first_name', last_name='last_name', email="artem.zimovets@gmail.com", phone="123123123", birthday="25.04.1990", additional_note="test", user=self.user),
                    Contact(id=2, first_name='first_name2', last_name='last_name2', email="artem2.zimovets@gmail.com", phone="123123123", birthday="25.04.1990", additional_note="test2", user=self.user)]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_upcoming_birthdays(self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact = Contact(id=1, first_name='first_name', last_name='last_name', email="artem.zimovets@gmail.com",
                          phone="123123123", birthday="25.04.1990", additional_note="test", user=self.user)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(1, 1, self.session)
        self.assertEqual(result, contact)

    async def test_create_todo(self):
        body = ContactModel(first_name="John", last_name="Doe", email="john.doe@example.com",
                            phone="1234567890", birthday=date.today(), additional_note="Test", created_at=datetime.now())
        result = await create_contact(body, self.session)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.additional_note, body.additional_note)

    async def test_delete_contact(self):
        mocked_todo = MagicMock()
        mocked_todo.scalar_one_or_none.return_value = Contact(first_name="John", last_name="Doe", email="john.doe@example.com",
                                                              phone="1234567890", birthday=date.today(), additional_note="Test", created_at=datetime.now())
        self.session.execute.return_value = mocked_todo
        result = await remove_contact(1, self.user.id, self.session)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()

        self.assertIsInstance(result, Contact)

    async def test_update_contact(self):
        contact_id = 1
        user_id = 1
        body = ContactModel(first_name="John", last_name="Doe", email="john.doe@example.com",
                            phone="1234567890", birthday=date.today(), additional_note="Test", created_at=datetime.now())
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=contact_id, user_id=user_id, first_name=body.first_name[0],
                                                                 last_name=body.last_name, email=body.email, phone=body.phone,
                                                                 birthday=body.birthday, additional_note=body.additional_note,
                                                                 created_at=body.created_at)
        self.session.execute.return_value = mocked_contact
        result = await update_contact(contact_id, user_id, body, self.session)

        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name[0], body.first_name)
        self.assertEqual(result.last_name[0], body.last_name)
        self.assertEqual(result.email[0], body.email)
        self.assertEqual(result.phone[0], body.phone)
        self.assertEqual(result.birthday[0], body.birthday)
        self.assertEqual(result.additional_note, body.additional_note)

    # async def test_create_note(self):
    #     body = NoteModel(title="test", description="test note", tags=[1, 2])
    #     tags = [Contact(id=1, user_id=1), Contact(id=2, user_id=1)]
    #     self.session.query().filter().all.return_value = tags
    #     result = await get_contact(body=body, user=self.user, db=self.session)
    #     self.assertEqual(result.title, body.title)
    #     self.assertEqual(result.description, body.description)
    #     self.assertEqual(result.tags, tags)
    #     self.assertTrue(hasattr(result, "id"))

    # async def test_remove_note_found(self):
    #     note = Contact()
    #     self.session.query().filter().first.return_value = note
    #     result = await remove_contact(note_id=1, user=self.user, db=self.session)
    #     self.assertEqual(result, note)

    # async def test_remove_note_not_found(self):
    #     self.session.query().filter().first.return_value = None
    #     result = await remove_contact(note_id=1, user=self.user, db=self.session)
    #     self.assertIsNone(result)

    # async def test_update_note_found(self):
    #     body = NoteUpdate(title="test", description="test note",
    #                       tags=[1, 2], done=True)
    #     tags = [Tag(id=1, user_id=1), Tag(id=2, user_id=1)]
    #     note = Contact(tags=tags)
    #     self.session.query().filter().first.return_value = note
    #     self.session.query().filter().all.return_value = tags
    #     self.session.commit.return_value = None
    #     result = await update_contact(note_id=1, body=body, user=self.user, db=self.session)
    #     self.assertEqual(result, note)

    # async def test_update_note_not_found(self):
    #     body = NoteUpdate(title="test", description="test note",
    #                       tags=[1, 2], done=True)
    #     self.session.query().filter().first.return_value = None
    #     self.session.commit.return_value = None
    #     result = await update_contact(note_id=1, body=body, user=self.user, db=self.session)
    #     self.assertIsNone(result)

    # async def test_update_status_note_found(self):
    #     body = NoteStatusUpdate(done=True)
    #     note = Note()
    #     self.session.query().filter().first.return_value = note
    #     self.session.commit.return_value = None
    #     result = await update_status_note(note_id=1, body=body, user=self.user, db=self.session)
    #     self.assertEqual(result, note)

    # async def test_update_status_note_not_found(self):
    # body = NoteStatusUpdate(done=True)
    # self.session.query().filter().first.return_value = None
    # self.session.commit.return_value = None
    # result = await update_status_note(note_id=1, body=body, user=self.user, db=self.session)
    # self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
