from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactFavoriteModel


async def get_contacts(user: User, limit: int, offset: int, db: Session):
    """
    The get_contacts function returns a list of contacts for the user.

    :param user: User: Get the user's contacts
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip before starting to return rows
    :param db: Session: Get the database session
    :return: A list of contacts for a given user
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(Contact.user_id == user.id).limit(limit).offset(offset).all()
    return contacts


async def get_contact_by_id(user: User, contact_id: int, db: Session):
    """
    The get_contact_by_id function returns a contact from the database based on the user and contact id.
        Args:
            user (User): The User object that is requesting to get a Contact.
            contact_id (int): The id of the Contact being requested by the User.

    :param user: User: Get the user's id
    :param contact_id: int: Specify the contact id of the contact that we want to get
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()
    return contact


async def create(user: User, body: ContactModel, db: Session):
    """
    The create function creates a new contact in the database.


    :param user: User: Get the user_id from the token
    :param body: ContactModel: Pass the data from the request body to the function
    :param db: Session: Access the database
    :return: The contact object that was created
    :doc-author: Trelent
    """
    contact = Contact(**body.dict(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update(user: User, contact_id: int, body: ContactModel, db: Session):
    """
    The update function updates a contact in the database.
        Args:
            user (User): The user who is making the request.
            contact_id (int): The id of the contact to update.
            body (ContactModel): A ContactModel object containing all of the information for this new contact, including an id field that will be ignored by this function.

    :param user: User: Get the user id from the token
    :param contact_id: int: Get the contact by id
    :param body: ContactModel: Get the data from the request body
    :param db: Session: Access the database
    :return: A contact object, which is the same as the one we get from get_contact_by_id
    :doc-author: Trelent
    """
    contact = await get_contact_by_id(user, contact_id, db)
    if contact:
        contact.firstname = body.firstname
        contact.lastname = body.lastname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.additional_info = body.additional_info
        contact.is_favorite = body.is_favorite
        db.commit()
    return contact


async def remove(user: User, contact_id: int, db: Session):
    """
    The remove function removes a contact from the database.


    :param user: User: Identify the user who is making the request
    :param contact_id: int: Specify which contact to remove from the database
    :param db: Session: Pass the database session to the function
    :return: The contact that was just removed
    :doc-author: Trelent
    """
    contact = await get_contact_by_id(user, contact_id, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def set_favorite(user: User, contact_id: int, body: ContactFavoriteModel, db: Session):
    """
    The set_favorite function is used to set a contact as favorite or not.
        Args:
            user (User): The current user.
            contact_id (int): The id of the contact to be updated.
            body (ContactFavoriteModel): A model containing the new value for is_favorite field in Contact table.

    :param user: User: Identify the user that is making the request
    :param contact_id: int: Identify the contact to be updated
    :param body: ContactFavoriteModel: Pass the is_favorite value to the function
    :param db: Session: Pass the database session to the function
    :return: The contact object
    :doc-author: Trelent
    """
    contact = await get_contact_by_id(user, contact_id, db)
    if contact:
        contact.is_favorite = body.is_favorite
        db.commit()
    return contact
