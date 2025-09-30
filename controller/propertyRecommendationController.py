import uuid
from typing import List, Optional, Dict
from datetime import datetime, date
from fastapi import HTTPException, Query
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_200_OK,
    HTTP_201_CREATED
)
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.transactions import in_transaction

from model.propertyRecommendationModel import PropertyRecommendation
from model.propertyModel import Property
from model.screeningQuestionModel import ScreeningQuestion
from schemas.propertyRecommendationSchemas import (
    RecommendationCreate, 
    RecommendationUpdate, 
    PropertyMatch
)


class PropertyMatchingService:
    """Service to match properties with user requirements"""
    
    @staticmethod
    async def calculate_property_match_score(property_obj, user_criteria: dict) -> tuple:
        """Calculate match score for a property against user criteria"""
        score = 0.0
        max_score = 0.0
        match_reasons = []
        
        # Budget matching (30% weight)
        if user_criteria.get('budget_min') and user_criteria.get('budget_max'):
            max_score += 30
            if user_criteria['budget_min'] <= property_obj.price <= user_criteria['budget_max']:
                score += 30
                match_reasons.append("Price within budget")
            elif property_obj.price <= user_criteria['budget_max'] * 1.1:  # 10% tolerance
                score += 20
                match_reasons.append("Price close to budget")
        
        # Location matching (25% weight)
        if user_criteria.get('preferred_location'):
            max_score += 25
            if (property_obj.city and 
                user_criteria['preferred_location'].lower() in property_obj.city.lower()):
                score += 25
                match_reasons.append("Location match")
            elif (property_obj.state and 
                  user_criteria['preferred_location'].lower() in property_obj.state.lower()):
                score += 15
                match_reasons.append("State match")
        
        # Bedrooms matching (20% weight)
        if user_criteria.get('bedrooms_required'):
            max_score += 20
            if property_obj.bedrooms and property_obj.bedrooms >= user_criteria['bedrooms_required']:
                score += 20
                match_reasons.append(f"{property_obj.bedrooms} bedrooms available")
            elif property_obj.bedrooms and property_obj.bedrooms == user_criteria['bedrooms_required'] - 1:
                score += 10
                match_reasons.append("Close to bedroom requirement")
        
        # Bathrooms matching (15% weight)  
        if user_criteria.get('bathrooms_required'):
            max_score += 15
            if property_obj.bathrooms and property_obj.bathrooms >= user_criteria['bathrooms_required']:
                score += 15
                match_reasons.append(f"{property_obj.bathrooms} bathrooms available")
        
        # Property type matching (10% weight)
        if user_criteria.get('property_type_preference'):
            max_score += 10
            if (property_obj.property_type and 
                user_criteria['property_type_preference'].lower() in property_obj.property_type.lower()):
                score += 10
                match_reasons.append("Property type match")
        
        # Calculate percentage score
        if max_score > 0:
            final_score = (score / max_score) * 100
        else:
            final_score = 0.0
            
        return final_score, match_reasons

    @staticmethod
    async def find_matching_properties(user_criteria: dict, limit: int = 10) -> List[Dict]:
        """Find properties matching user criteria"""
        try:
            # Build query filters
            query = Property.filter(status="available")
            
            # Apply budget filter
            if user_criteria.get('budget_min') and user_criteria.get('budget_max'):
                # Allow 10% over budget for more options
                query = query.filter(
                    price__gte=user_criteria['budget_min'],
                    price__lte=user_criteria['budget_max'] * 1.1
                )
            
            # Apply location filter
            if user_criteria.get('preferred_location'):
                location = user_criteria['preferred_location']
                query = query.filter(
                    city__icontains=location
                ) | query.filter(
                    state__icontains=location
                )
            
            # Get properties
            properties = await query.prefetch_related('media').limit(limit * 2)  # Get more to allow for scoring
            
            # Calculate match scores for each property
            property_matches = []
            for prop in properties:
                match_score, match_reasons = await PropertyMatchingService.calculate_property_match_score(
                    prop, user_criteria
                )
                
                if match_score >= 30:  # Only include properties with decent match
                    # Get cover image
                    cover_image = None
                    for media in prop.media:
                        if media.is_cover:
                            cover_image = media.url
                            break
                    
                    property_matches.append({
                        "property_id": str(prop.id),
                        "title": prop.title,
                        "property_type": prop.property_type,
                        "price": float(prop.price),
                        "location": f"{prop.city}, {prop.state}" if prop.city and prop.state else (prop.city or prop.state or "Location TBD"),
                        "bedrooms": prop.bedrooms,
                        "bathrooms": prop.bathrooms,
                        "match_score": round(match_score, 1),
                        "match_reasons": match_reasons,
                        "cover_image": cover_image,
                        "description": prop.description[:200] + "..." if prop.description and len(prop.description) > 200 else prop.description
                    })
            
            # Sort by match score (highest first)
            property_matches.sort(key=lambda x: x['match_score'], reverse=True)
            
            return property_matches[:limit]
            
        except Exception as e:
            print(f"❌ Error finding matching properties: {e}")
            return []


async def create_property_recommendation_from_screening(screening_id: str) -> dict:
    """Create property recommendations based on screening questionnaire"""
    try:
        print(f"🔍 Creating recommendations for screening: {screening_id}")
        
        # Get screening data
        screening_uuid = uuid.UUID(screening_id)
        screening = await ScreeningQuestion.get_or_none(id=screening_uuid)
        
        if not screening:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Screening questionnaire not found"
            )
        
        # Extract user criteria from screening responses
        responses = screening.responses or {}
        user_criteria = {
            'budget_min': responses.get('budget_min'),
            'budget_max': responses.get('budget_max'), 
            'preferred_location': responses.get('preferred_location'),
            'bedrooms_required': responses.get('bedrooms_required'),
            'bathrooms_required': responses.get('bathrooms_required'),
            'property_type_preference': responses.get('property_type_preference'),
            'move_in_date': responses.get('move_in_date')
        }
        
        # Find matching properties
        matching_properties = await PropertyMatchingService.find_matching_properties(user_criteria)
        
        # Calculate overall match score
        if matching_properties:
            overall_score = sum(prop['match_score'] for prop in matching_properties) / len(matching_properties)
        else:
            overall_score = 0.0
        
        # Create recommendation record
        async with in_transaction():
            recommendation = await PropertyRecommendation.create(
                screening_id=screening_uuid,
                user_email=screening.email,
                user_name=screening.name,
                user_phone=screening.phone,
                budget_min=user_criteria.get('budget_min'),
                budget_max=user_criteria.get('budget_max'),
                preferred_location=user_criteria.get('preferred_location'),
                bedrooms_required=user_criteria.get('bedrooms_required'),
                bathrooms_required=user_criteria.get('bathrooms_required'),
                property_type_preference=user_criteria.get('property_type_preference'),
                recommended_properties=matching_properties,
                match_score=round(overall_score, 1),
                match_criteria=user_criteria,
                status="pending"
            )
        
        print(f"✅ Created recommendation with {len(matching_properties)} properties (score: {overall_score:.1f})")
        
        return {
            "success": True,
            "message": f"Found {len(matching_properties)} matching properties",
            "data": {
                "recommendation_id": str(recommendation.id),
                "screening_id": screening_id,
                "match_score": overall_score,
                "property_count": len(matching_properties),
                "properties": matching_properties
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating recommendations: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recommendations: {str(e)}"
        )


async def get_recommendations_by_email(email: str):
    """Get all recommendations for a user by email"""
    try:
        recommendations = await PropertyRecommendation.filter(
            user_email=email
        ).order_by('-created_at')
        
        recommendation_list = []
        for rec in recommendations:
            recommendation_list.append({
                "id": str(rec.id),
                "screening_id": str(rec.screening_id) if rec.screening_id else None,
                "user_email": rec.user_email,
                "user_name": rec.user_name,
                "match_score": rec.match_score,
                "property_count": len(rec.recommended_properties),
                "status": rec.status,
                "email_sent": rec.email_sent,
                "email_sent_at": rec.email_sent_at.isoformat() if rec.email_sent_at else None,
                "user_response": rec.user_response,
                "created_at": rec.created_at.isoformat(),
                "recommended_properties": rec.recommended_properties[:3]  # Show top 3 for preview
            })
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "data": {
                    "recommendations": recommendation_list,
                    "total": len(recommendation_list)
                }
            }
        )
        
    except Exception as e:
        print(f"❌ Error fetching recommendations: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recommendations"
        )


async def get_recommendation_by_id(recommendation_id: str):
    """Get detailed recommendation by ID"""
    try:
        recommendation_uuid = uuid.UUID(recommendation_id)
        recommendation = await PropertyRecommendation.get_or_none(id=recommendation_uuid)
        
        if not recommendation:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "data": {
                    "id": str(recommendation.id),
                    "screening_id": str(recommendation.screening_id) if recommendation.screening_id else None,
                    "user_email": recommendation.user_email,
                    "user_name": recommendation.user_name,
                    "user_phone": recommendation.user_phone,
                    "budget_range": f"${recommendation.budget_min} - ${recommendation.budget_max}" if recommendation.budget_min and recommendation.budget_max else None,
                    "preferred_location": recommendation.preferred_location,
                    "bedrooms_required": recommendation.bedrooms_required,
                    "bathrooms_required": recommendation.bathrooms_required,
                    "property_type_preference": recommendation.property_type_preference,
                    "match_score": recommendation.match_score,
                    "match_criteria": recommendation.match_criteria,
                    "recommended_properties": recommendation.recommended_properties,
                    "status": recommendation.status,
                    "email_sent": recommendation.email_sent,
                    "email_sent_at": recommendation.email_sent_at.isoformat() if recommendation.email_sent_at else None,
                    "user_response": recommendation.user_response,
                    "user_responded_at": recommendation.user_responded_at.isoformat() if recommendation.user_responded_at else None,
                    "admin_reviewed": recommendation.admin_reviewed,
                    "admin_notes": recommendation.admin_notes,
                    "priority_level": recommendation.priority_level,
                    "created_at": recommendation.created_at.isoformat(),
                    "updated_at": recommendation.updated_at.isoformat()
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching recommendation: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recommendation"
        )


async def update_recommendation_status(recommendation_id: str, status: str, user_response: str = None):
    """Update recommendation status and user response"""
    try:
        recommendation_uuid = uuid.UUID(recommendation_id)
        recommendation = await PropertyRecommendation.get_or_none(id=recommendation_uuid)
        
        if not recommendation:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )
        
        update_data = {"status": status}
        if user_response:
            update_data["user_response"] = user_response
            update_data["user_responded_at"] = datetime.now()
        
        await PropertyRecommendation.filter(id=recommendation_uuid).update(**update_data)
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Recommendation status updated successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating recommendation: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update recommendation"
        )


async def send_recommendation_email(recommendation_id: str):
    """Send property recommendations via email"""
    try:
        from emailService.recommendationEmail import send_property_recommendations_email, send_recommendation_notification_to_admin
        
        recommendation_uuid = uuid.UUID(recommendation_id)
        recommendation = await PropertyRecommendation.get_or_none(id=recommendation_uuid)
        
        if not recommendation:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )
        
        if recommendation.email_sent:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Email already sent for this recommendation"
            )
        
        # Send email to user
        try:
            await send_property_recommendations_email(
                to_email=recommendation.user_email,
                user_name=recommendation.user_name,
                recommendations=recommendation.recommended_properties,
                match_score=recommendation.match_score,
                recommendation_id=recommendation_id
            )
            
            # Update email sent status
            await PropertyRecommendation.filter(id=recommendation_uuid).update(
                email_sent=True,
                email_sent_at=datetime.now(),
                status="sent"
            )
            
            # Send notification to admin
            try:
                await send_recommendation_notification_to_admin(
                    user_email=recommendation.user_email,
                    user_name=recommendation.user_name,
                    property_count=len(recommendation.recommended_properties),
                    match_score=recommendation.match_score,
                    recommendation_id=recommendation_id
                )
            except Exception as admin_email_error:
                print(f"⚠️ Failed to send admin notification: {admin_email_error}")
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": f"Recommendation email sent successfully to {recommendation.user_email}",
                    "data": {
                        "recommendation_id": recommendation_id,
                        "recipient": recommendation.user_email,
                        "property_count": len(recommendation.recommended_properties),
                        "match_score": recommendation.match_score
                    }
                }
            )
            
        except Exception as email_error:
            print(f"❌ Failed to send recommendation email: {email_error}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send email: {str(email_error)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error sending recommendation email: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send recommendation email"
        )


async def get_all_recommendations_admin(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None)
):
    """Get all recommendations for admin with filtering"""
    try:
        query = PropertyRecommendation.all()
        
        if status:
            query = query.filter(status=status)
        if priority:
            query = query.filter(priority_level=priority)
        
        total = await query.count()
        recommendations = await query.offset(offset).limit(limit).order_by('-created_at')
        
        recommendation_list = []
        for rec in recommendations:
            recommendation_list.append({
                "id": str(rec.id),
                "user_email": rec.user_email,
                "user_name": rec.user_name,
                "match_score": rec.match_score,
                "property_count": len(rec.recommended_properties),
                "status": rec.status,
                "priority_level": rec.priority_level,
                "email_sent": rec.email_sent,
                "user_response": rec.user_response,
                "admin_reviewed": rec.admin_reviewed,
                "created_at": rec.created_at.isoformat()
            })
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "data": {
                    "recommendations": recommendation_list,
                    "pagination": {
                        "total": total,
                        "limit": limit,
                        "offset": offset,
                        "has_next": offset + limit < total,
                        "has_prev": offset > 0
                    }
                }
            }
        )
        
    except Exception as e:
        print(f"❌ Error fetching admin recommendations: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recommendations"
        )