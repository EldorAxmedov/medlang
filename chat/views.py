from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from chat.services import ChatService
from chat.models import ChatRoom

chat_service = ChatService()

@login_required
def chat_list(request):
    """Foydalanuvchi a'zo bo'lgan chatlar ro'yxati."""
    rooms = chat_service.list_user_rooms(request.user.id)
    return render(request, 'chat/list.html', {'rooms': rooms})

@login_required
def chat_room(request, room_id):
    """Chat xonasi va xabarlar almashinuvi."""
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # User room ishtirokchisi ekanligini tekshirish
    if not room.participants.filter(user=request.user).exists():
        messages.error(request, "Siz ushbu chat a'zosi emassiz.")
        return redirect('chat_list_view')

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            chat_service.send_message(request.user, str(room.id), text)
            # AJAX emas, oddiy refresh hozircha
            return redirect('chat_room_view', room_id=room.id)

    # Xabarlarni o'qilgan deb belgilash
    chat_service.read_all_messages(str(room.id), request.user.id)
    
    # Tarixni olish
    history = chat_service.list_history(str(room.id))
    
    return render(request, 'chat/room.html', {
        'room': room,
        'history': reversed(history) # Eng oxirgisi pastda bo'lishi uchun
    })

@login_required
def start_p2p_chat(request, user_id):
    """Boshqa user bilan shaxsiy chat boshlash."""
    try:
        room = chat_service.get_or_create_private_chat(request.user, user_id)
        return redirect('chat_room_view', room_id=room.id)
    except Exception as e:
        messages.error(request, f"Chat boshlashda xatolik: {str(e)}")
        return redirect('chat_list_view')
