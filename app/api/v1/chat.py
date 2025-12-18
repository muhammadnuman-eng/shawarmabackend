from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from math import ceil
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.security import generate_uuid
from app.models.user import User, Chat, ChatParticipant, ChatMessage

router = APIRouter()

# Request Models
class SendMessageRequest(BaseModel):
    content: str
    type: str = "text"  # 'text', 'image', 'file'

class CreateDirectChatRequest(BaseModel):
    participantIds: List[str]
    type: str = "direct"

class CreateGroupChatRequest(BaseModel):
    name: str
    participantIds: List[str]
    description: Optional[str] = None

@router.get("/chats")
async def get_chat_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's chat list"""
    # Get all chats where user is a participant
    participant_chats = db.query(ChatParticipant).filter(
        ChatParticipant.user_id == current_user.id
    ).all()
    
    chats_list = []
    for participant in participant_chats:
        chat = participant.chat
        
        # Get other participants
        other_participants = db.query(ChatParticipant).filter(
            ChatParticipant.chat_id == chat.id,
            ChatParticipant.user_id != current_user.id
        ).all()
        
        # Get last message
        last_message = db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat.id
        ).order_by(ChatMessage.created_at.desc()).first()
        
        # Count unread messages
        unread_count = db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat.id,
            ChatMessage.sender_id != current_user.id,
            ChatMessage.is_read == False
        ).count()
        
        participants_list = [
            {
                "id": current_user.id,
                "name": current_user.name,
                "avatar": current_user.avatar,
                "isOnline": current_user.is_online
            }
        ]
        
        for p in other_participants:
            user = p.user
            participants_list.append({
                "id": user.id,
                "name": user.name,
                "avatar": user.avatar,
                "isOnline": user.is_online
            })
        
        last_msg_dict = None
        if last_message:
            sender = last_message.sender
            last_msg_dict = {
                "id": last_message.id,
                "content": last_message.content,
                "senderId": last_message.sender_id,
                "senderName": sender.name if sender else "Unknown",
                "timestamp": last_message.created_at.isoformat() if last_message.created_at else None,
                "type": last_message.type
            }
        
        chats_list.append({
            "id": chat.id,
            "type": chat.type,
            "name": chat.name,
            "participants": participants_list,
            "lastMessage": last_msg_dict,
            "unreadCount": unread_count,
            "updatedAt": chat.updated_at.isoformat() if chat.updated_at else None
        })
    
    return {"chats": chats_list}

@router.get("/chats/{chat_id}/messages")
async def get_chat_messages(
    chat_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat messages"""
    # Verify user is participant
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.chat_id == chat_id,
        ChatParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this chat"
        )
    
    query = db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id)
    total = query.count()
    offset = (page - 1) * limit
    messages = query.order_by(ChatMessage.created_at.desc()).offset(offset).limit(limit).all()
    
    messages_list = []
    for msg in reversed(messages):  # Reverse to show oldest first
        sender = msg.sender
        messages_list.append({
            "id": msg.id,
            "chatId": msg.chat_id,
            "senderId": msg.sender_id,
            "senderName": sender.name if sender else "Unknown",
            "content": msg.content,
            "type": msg.type,
            "timestamp": msg.created_at.isoformat() if msg.created_at else None,
            "isRead": msg.is_read
        })
    
    return {
        "messages": messages_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": ceil(total / limit) if total > 0 else 0
        }
    }

@router.post("/chats/{chat_id}/messages")
async def send_message(
    chat_id: str,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send message in chat"""
    # Verify user is participant
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.chat_id == chat_id,
        ChatParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this chat"
        )
    
    message = ChatMessage(
        id=generate_uuid(),
        chat_id=chat_id,
        sender_id=current_user.id,
        content=request.content,
        type=request.type
    )
    
    db.add(message)
    
    # Update chat updated_at
    chat = participant.chat
    from datetime import datetime
    chat.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(message)
    
    return {
        "id": message.id,
        "chatId": message.chat_id,
        "senderId": message.sender_id,
        "senderName": current_user.name,
        "content": message.content,
        "type": message.type,
        "timestamp": message.created_at.isoformat() if message.created_at else None,
        "isRead": message.is_read
    }

@router.post("/chats")
async def create_direct_chat(
    request: CreateDirectChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create direct chat"""
    if len(request.participantIds) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Direct chat requires exactly one other participant"
        )
    
    other_user_id = request.participantIds[0]
    
    # Check if chat already exists
    existing_chats = db.query(Chat).filter(Chat.type == "direct").all()
    for chat in existing_chats:
        participants = db.query(ChatParticipant).filter(ChatParticipant.chat_id == chat.id).all()
        participant_ids = {p.user_id for p in participants}
        if {current_user.id, other_user_id} == participant_ids:
            # Return existing chat
            return {
                "id": chat.id,
                "type": chat.type,
                "participants": [
                    {
                        "id": p.user.id,
                        "name": p.user.name,
                        "avatar": p.user.avatar
                    }
                    for p in participants
                ],
                "createdAt": chat.created_at.isoformat() if chat.created_at else None
            }
    
    # Create new chat
    chat = Chat(
        id=generate_uuid(),
        type="direct"
    )
    db.add(chat)
    db.flush()
    
    # Add participants
    participants_list = []
    for user_id in [current_user.id] + request.participantIds:
        participant = ChatParticipant(
            id=generate_uuid(),
            chat_id=chat.id,
            user_id=user_id
        )
        db.add(participant)
        participants_list.append(participant)
    
    db.commit()
    db.refresh(chat)
    
    return {
        "id": chat.id,
        "type": chat.type,
        "participants": [
            {
                "id": p.user.id,
                "name": p.user.name,
                "avatar": p.user.avatar
            }
            for p in participants_list
        ],
        "createdAt": chat.created_at.isoformat() if chat.created_at else None
    }

@router.post("/chats/group")
async def create_group_chat(
    request: CreateGroupChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create group chat"""
    chat = Chat(
        id=generate_uuid(),
        type="group",
        name=request.name,
        description=request.description
    )
    db.add(chat)
    db.flush()
    
    # Add participants (creator is admin)
    participants_list = []
    
    # Add creator as admin
    creator = ChatParticipant(
        id=generate_uuid(),
        chat_id=chat.id,
        user_id=current_user.id,
        role="admin"
    )
    db.add(creator)
    participants_list.append(creator)
    
    # Add other participants
    for user_id in request.participantIds:
        participant = ChatParticipant(
            id=generate_uuid(),
            chat_id=chat.id,
            user_id=user_id,
            role="member"
        )
        db.add(participant)
        participants_list.append(participant)
    
    db.commit()
    db.refresh(chat)
    
    return {
        "id": chat.id,
        "type": chat.type,
        "name": chat.name,
        "description": chat.description,
        "participants": [
            {
                "id": p.user.id,
                "name": p.user.name,
                "avatar": p.user.avatar,
                "role": p.role
            }
            for p in participants_list
        ],
        "createdAt": chat.created_at.isoformat() if chat.created_at else None
    }

