from fastapi import APIRouter, Query, Depends
from typing import Optional
from model.contactModel import ContactStatus
from controller.contactController import (
    create_contact_message,
    get_all_contact_messages,
    get_contact_message_by_id,
    reply_to_contact_message,
    update_contact_status,
    delete_contact_message
)

router = APIRouter(tags=["Contact"])

# Public endpoint - anyone can submit contact form
router.post("/contact", summary="Submit contact form (public)")(create_contact_message)

# Admin only endpoints - require admin authentication
router.get("/contacts", summary="Get all contact messages (admin only)")(get_all_contact_messages)

router.get("/contacts/{contact_id}", summary="Get contact message by ID (admin only)")(get_contact_message_by_id)

router.post("/contacts/{contact_id}/reply", summary="Reply to contact message (admin only)")(reply_to_contact_message)

router.put("/contacts/{contact_id}/status", summary="Update contact status (admin only)")(update_contact_status)

router.delete("/contacts/{contact_id}", summary="Delete contact message (admin only)")(delete_contact_message)