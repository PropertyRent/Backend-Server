from fastapi import APIRouter, Query, UploadFile, File, Form
from typing import Optional
from controller.teamController import (
    add_team_member,
    add_team_member_with_photo,
    update_team_member,
    update_team_member_with_photo,
    delete_team_member,
    get_all_team_members,
    get_team_member_by_id
)

router = APIRouter(tags=["Team"])

# Team CRUD operations
router.post("/team", summary="Create a new team member (JSON)")(add_team_member)

router.post("/team/upload", summary="Create a new team member with photo upload")(add_team_member_with_photo)

router.put("/team/{member_id}", summary="Update a team member (JSON)")(update_team_member)

router.put("/team/{member_id}/upload", summary="Update a team member with photo upload")(update_team_member_with_photo)

router.delete("/team/{member_id}", summary="Delete a team member")(delete_team_member)

router.get("/team", summary="Get all team members with filtering and pagination")(get_all_team_members)

router.get("/team/{member_id}", summary="Get a team member by ID")(get_team_member_by_id)