from typing import List

from fastapi import Depends, HTTPException, status, Path, APIRouter, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.repository import contacts as repository_contacts
from src.schemas import ContactResponse, ContactModel, ContactFavoriteModel
from src.services.auth import auth_service
from src.services.role import RoleAccess

router = APIRouter(prefix="/api/contacts", tags=['contacts'])

allowed_operation_get = RoleAccess([Role.admin, Role.moderator, Role.user])  # noqa
allowed_operation_create = RoleAccess([Role.admin, Role.moderator, Role.user])  # noqa
allowed_operation_update = RoleAccess([Role.admin, Role.moderator])  # noqa
allowed_operation_remove = RoleAccess([Role.admin])  # noqa


@router.get("/", response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts(limit: int = Query(10, le=500), offset: int = 0, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts function returns a list of contacts.

    :param limit: int: Limit the number of contacts returned
    :param le: Limit the number of contacts returned to 500
    :param offset: int: Skip a number of records
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts(current_user, limit, offset, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(allowed_operation_get)])
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function is a GET request that returns the contact with the given ID.
    The function takes in an optional contact_id parameter, which defaults to 1 if not provided.
    It also takes in a db Session object and current_user User object as parameters, both of which are injected by FastAPI.

    :param contact_id: int: Get the contact id from the url path
    :param db: Session: Get the database session
    :param current_user: User: Get the user who is logged in
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_id(current_user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_operation_create)])
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactModel: Get the data from the request body
    :param db: Session: Get the database session
    :param current_user: User: Get the user from the database
    :return: A contactmodel object
    :doc-author: Trelent
    """
    contact = await repository_contacts.create(current_user, body, db)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(allowed_operation_update)],
            description='Only moderators and admin')
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        The function takes an id and a body as input, and returns the updated contact.
        If no such contact exists, it raises an HTTPException with status code 404.

    :param body: ContactModel: Pass the contact model to the function
    :param contact_id: int: Specify the contact id in the url
    :param db: Session: Get the database session
    :param current_user: User: Get the user that is currently logged in
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.update(current_user, contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_operation_remove)])
async def remove_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_contact function removes a contact from the database.

    :param contact_id: int: Pass the contact_id to the function
    :param db: Session: Get a database session
    :param current_user: User: Get the current user from the database
    :return: The deleted contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.remove(current_user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.patch("/{contact_id}/favorite", response_model=ContactResponse,
              dependencies=[Depends(allowed_operation_update)])
async def favorite_contact(body: ContactFavoriteModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                           current_user: User = Depends(auth_service.get_current_user)):
    """
    The favorite_contact function is used to set a contact as favorite or not.
        The function takes the following parameters:
            body (ContactFavoriteModel): A ContactFavoriteModel object containing the new favorite status of the contact.
            contact_id (int): The id of the contact to be updated. This parameter is optional and defaults to 1 if not provided, but must be greater than 0 when provided.
            It can also be passed in via path variable using /{contact_id}. If it's passed in via both path variable and query string, then an error will occur.

    :param body: ContactFavoriteModel: Get the data from the request body
    :param contact_id: int: Get the contact id from the url
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user who is currently logged in
    :return: A contactmodel object
    :doc-author: Trelent
    """
    contact = await repository_contacts.set_favorite(current_user, contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact
