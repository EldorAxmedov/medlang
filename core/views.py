import os
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from users.models import User
from vocabulary.models import Word, Category, Translation, Definition, Example
from tests.models import Test, Question, Answer
from simulation.models import Scenario, Session, SimulationMessage
from chat.models import ChatRoom

def is_admin(user):
    return user.is_authenticated and user.is_staff

def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Email yoki parol noto\'g\'ri.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@user_passes_test(is_admin)
def dashboard(request):
    # Retrieve some stats for the dashboard
    stats = {
        'users_count': User.objects.count(),
        'words_count': Word.objects.count(),
        'tests_count': Test.objects.count(),
        'scenarios_count': Scenario.objects.count(),
        'chats_count': ChatRoom.objects.count(),
    }
    
    # Recent users
    recent_users = User.objects.all().order_by('-created_at')[:5]
    
    # Recent words
    recent_words = Word.objects.all().order_by('-created_at')[:5]

    context = {
        'stats': stats,
        'recent_users': recent_users,
        'recent_words': recent_words,
    }
    return render(request, 'dashboard/index.html', context)

# --- Vocabulary Management ---

@user_passes_test(is_admin)
def vocabulary_list(request):
    words = Word.objects.all().order_by('term')
    return render(request, 'dashboard/vocabulary/list.html', {'words': words})

@user_passes_test(is_admin)
def vocabulary_edit(request, pk=None):
    if pk:
        word = get_object_or_404(Word, pk=pk)
    else:
        word = None

    if request.method == 'POST':
        term = request.POST.get('term')
        transcription = request.POST.get('transcription', '')
        difficulty = int(request.POST.get('difficulty', 1))
        category_ids = request.POST.getlist('categories')
        
        if not term:
            messages.error(request, 'Term is required.')
        else:
            if not word:
                word = Word.objects.create(term=term, transcription=transcription, difficulty=difficulty)
            else:
                word.term = term
                word.transcription = transcription
                word.difficulty = difficulty
                word.save()
            
            # Categories
            word.categories.set(category_ids)
            
            # Primary translation
            translation_text = request.POST.get('translation')
            if translation_text:
                translation, _ = Translation.objects.get_or_create(word=word, language='uz', is_primary=True)
                translation.text = translation_text
                translation.save()
            
            # Simple definition handling
            definition_text = request.POST.get('definition')
            if definition_text:
                definition, _ = Definition.objects.get_or_create(word=word)
                definition.text = definition_text
                definition.save()

            messages.success(request, f'Word "{word.term}" saved successfully.')
            return redirect('manage_vocabulary')
    
    context = {
        'word': word,
        'categories': Category.objects.all(),
    }
    return render(request, 'dashboard/vocabulary/form.html', context)

@user_passes_test(is_admin)
def vocabulary_delete(request, pk):
    word = get_object_or_404(Word, pk=pk)
    term = word.term
    word.delete()
    messages.success(request, f'Word "{term}" removed.')
    return redirect('manage_vocabulary')

# --- User Management (Brief) ---
@user_passes_test(is_admin)
def user_delete(request, pk):
    u = get_object_or_404(User, pk=pk)
    if u == request.user:
        messages.error(request, 'O\'zingizni o\'chira olmaysiz.')
    else:
        email = u.email
        u.delete()
        messages.success(request, f'Foydalanuvchi "{email}" o\'chirildi.')
    return redirect('manage_users')

# --- Test Management ---

@login_required
def tests_list(request):
    tests = Test.objects.all().order_by('-created_at')
    return render(request, 'dashboard/tests/list.html', {'tests': tests})

@login_required
def tests_edit(request, pk=None):
    if pk:
        test = get_object_or_404(Test, pk=pk)
    else:
        test = None

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        difficulty = int(request.POST.get('difficulty', 1))
        category_id = request.POST.get('category')

        if not title:
            messages.error(request, 'Title is required.')
        else:
            if not test:
                test = Test.objects.create(title=title, description=description, difficulty=difficulty)
                test.category_id = category_id
                test.save()
                messages.success(request, f'Test "{test.title}" yaratildi. Endi savollar qo\'shishingiz mumkin.')
                return redirect('manage_questions', test_id=test.id)
            else:
                test.title = title
                test.description = description
                test.difficulty = difficulty
                test.category_id = category_id
                test.save()
                messages.success(request, f'Test "{test.title}" saqlandi.')
                return redirect('manage_tests')

    context = {
        'test': test,
        'categories': Category.objects.all(),
    }
    return render(request, 'dashboard/tests/form.html', context)

@user_passes_test(is_admin)
def tests_delete(request, pk):
    test = get_object_or_404(Test, pk=pk)
    title = test.title
    test.delete()
    messages.success(request, f'Test "{title}" removed.')
    return redirect('manage_tests')

@login_required
def question_list(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all()
    return render(request, 'dashboard/tests/questions/list.html', {'test': test, 'questions': questions})
@login_required
def question_edit(request, test_id, pk=None):
    test = get_object_or_404(Test, id=test_id)
    if pk:
        question = get_object_or_404(Question, pk=pk, test=test)
    else:
        question = None

    if request.method == 'POST':
        text = request.POST.get('text')
        q_type = request.POST.get('question_type')
        rationale = request.POST.get('rationale', '')
        
        if not text:
            messages.error(request, 'Question text is required.')
        else:
            image = request.FILES.get('image')
            if not question:
                question = Question.objects.create(test=test, text=text, question_type=q_type, rationale=rationale)
                if image:
                    question.image = image
                    question.save()
            else:
                question.text = text
                question.question_type = q_type
                question.rationale = rationale
                if image:
                    question.image = image
                question.save()
            
            # Handle answers for all types (MCQ, True/False, Gap Fill, Matching)
            if q_type in ['mcq', 'true_false', 'gap_fill', 'matching']:
                answers_text = request.POST.getlist('answers')
                correct_indices = request.POST.getlist('correct_answer')
                
                # Clear existing for simplicity
                question.answers.all().delete()
                
                if correct_indices:
                    # Convert to integers for comparison
                    correct_indices = [int(i) for i in correct_indices]
                    for idx, a_text in enumerate(answers_text):
                        if a_text.strip():
                            Answer.objects.create(
                                question=question, 
                                text=a_text.strip(), 
                                is_correct=(idx in correct_indices)
                            )
                else:
                    # Default: none correct
                    for idx, a_text in enumerate(answers_text):
                        if a_text.strip():
                            Answer.objects.create(question=question, text=a_text.strip(), is_correct=False)

            messages.success(request, 'Savol muvaffaqiyatli saqlandi.')
            return redirect('manage_questions', test_id=test.id)

    return render(request, 'dashboard/tests/questions/form.html', {'test': test, 'question': question})

@user_passes_test(is_admin)
def question_delete(request, test_id, pk):
    question = get_object_or_404(Question, pk=pk, test_id=test_id)
    question.delete()
    messages.success(request, 'Savol muvaffaqiyatli o\'chirildi.')
    return redirect('manage_questions', test_id=test_id)

# --- Simulation Management ---

@user_passes_test(is_admin)
def simulations_list(request):
    scenarios = Scenario.objects.all().order_by('-created_at')
    return render(request, 'dashboard/simulations/list.html', {'scenarios': scenarios})

@user_passes_test(is_admin)
def simulations_edit(request, pk=None):
    if pk:
        scen = get_object_or_404(Scenario, pk=pk)
    else:
        scen = None
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        difficulty = request.POST.get('difficulty', 1)
        system_prompt = request.POST.get('system_prompt', '')
        
        if not title:
            messages.error(request, 'Title is required.')
        else:
            if not scen:
                scen = Scenario.objects.create(title=title, description=description, difficulty=difficulty, system_prompt=system_prompt)
            else:
                scen.title = title
                scen.description = description
                scen.difficulty = difficulty
                scen.system_prompt = system_prompt
                scen.save()
            
            # Patient Profile handling
            patient_name = request.POST.get('patient_name')
            patient_age = request.POST.get('patient_age', 30)
            patient_gender = request.POST.get('patient_gender', 'M')
            patient_complaint = request.POST.get('patient_complaint', '')
            patient_history = request.POST.get('patient_history', '')

            from simulation.models import PatientProfile
            patient_profile, created = PatientProfile.objects.get_or_create(scenario=scen)
            patient_profile.name = patient_name
            patient_profile.age = patient_age
            patient_profile.gender = patient_gender
            patient_profile.complaint = patient_complaint
            patient_profile.history = patient_history
            patient_profile.save()

            messages.success(request, f'Scenario "{scen.title}" saved.')
            return redirect('manage_simulations')

    return render(request, 'dashboard/simulations/form.html', {'scen': scen})

@user_passes_test(is_admin)
def simulations_delete(request, pk):
    scen = get_object_or_404(Scenario, pk=pk)
    title = scen.title
    scen.delete()
    messages.success(request, f'Scenario "{title}" removed.')
    return redirect('manage_simulations')

# --- Chat Management ---

@user_passes_test(is_admin)
def chats_list(request):
    rooms = ChatRoom.objects.all().order_by('-created_at')
    return render(request, 'dashboard/chats/list.html', {'rooms': rooms})

@user_passes_test(is_admin)
def chats_edit(request, pk=None):
    from chat.models import ChatRoom, ChatParticipant
    if pk:
        room = get_object_or_404(ChatRoom, pk=pk)
        current_participants = room.participants.values_list('user_id', flat=True)
    else:
        room = None
        current_participants = []
        
    if request.method == 'POST':
        name = request.POST.get('name', '')
        room_type = request.POST.get('type', ChatRoom.RoomType.GROUP)
        participant_ids = request.POST.getlist('participants')
        
        if not name and room_type != ChatRoom.RoomType.PRIVATE:
            messages.error(request, 'Chat nomi kiritilishi shart.')
        else:
            if not room:
                room = ChatRoom.objects.create(name=name, type=room_type)
                messages.success(request, f'Chat "{room.name}" yaratildi.')
            else:
                room.name = name
                room.type = room_type
                room.save()
                messages.success(request, f'Chat "{room.name}" yangilandi.')
                
            # Manage Participants (simple overwrite)
            if participant_ids:
                # Remove those who are no longer selected
                room.participants.exclude(user_id__in=participant_ids).delete()
                # Add new ones
                for uid in participant_ids:
                    if not room.participants.filter(user_id=uid).exists():
                        # default role MEMBER
                        user_obj = User.objects.get(pk=uid)
                        role = ChatParticipant.Role.TEACHER if user_obj.role == 'admin' else ChatParticipant.Role.MEMBER
                        ChatParticipant.objects.create(chat_room=room, user=user_obj, role=role)
            else:
                room.participants.all().delete()
                
            return redirect('manage_chats')

    context = {
        'room': room,
        'room_types': ChatRoom.RoomType.choices,
        'users': User.objects.all().order_by('full_name'),
        'current_participants': list(current_participants)
    }
    return render(request, 'dashboard/chats/form.html', context)

@user_passes_test(is_admin)
def chats_delete(request, pk):
    room = get_object_or_404(ChatRoom, pk=pk)
    name = room.name or 'Private Chat'
    room.delete()
    messages.success(request, f'Chat "{name}" o\'chirildi.')
    return redirect('manage_chats')

# --- User Management ---

@user_passes_test(is_admin)
def simulation_session_list(request, scenario_id):
    scenario = get_object_or_404(Scenario, id=scenario_id)
    sessions = scenario.sessions.all().order_by('-created_at')
    return render(request, 'dashboard/simulations/sessions.html', {'scenario': scenario, 'sessions': sessions})

@user_passes_test(is_admin)
def simulation_session_detail(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    messages = session.messages.all().order_by('timestamp')
    return render(request, 'dashboard/simulations/session_detail.html', {'session': session, 'msgs': messages})

@user_passes_test(is_admin)
def users_list(request):
    users = User.objects.all().order_by('-created_at')
    return render(request, 'dashboard/users/list.html', {'users': users})

@user_passes_test(is_admin)
def user_edit(request, pk=None):
    from users.models import Specialty, Profile
    from django.db import transaction
    
    if pk:
        edit_user = get_object_or_404(User, pk=pk)
        profile = getattr(edit_user, 'profile', None)
    else:
        edit_user = None
        profile = None

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', User.Roles.USER)
        specialty_id = request.POST.get('specialty')

        if not email:
            messages.error(request, 'Email is required.')
        else:
            try:
                with transaction.atomic():
                    if not edit_user:
                        # New User
                        if not password:
                            messages.error(request, 'Password is required for new users.')
                            raise ValueError('No password')
                        
                        edit_user = User.objects.create_user(email=email, password=password, full_name=full_name, role=role)
                        messages.success(request, f'Foydalanuvchi "{edit_user.email}" yaratildi.')
                    else:
                        # Update User
                        edit_user.email = email
                        edit_user.full_name = full_name
                        edit_user.role = role
                        if password:
                            edit_user.set_password(password)
                        edit_user.save()
                        messages.success(request, f'Foydalanuvchi "{edit_user.email}" ma\'lumotlari yangilandi.')

                    # Profile & Specialty
                    if specialty_id:
                        spec = Specialty.objects.filter(id=specialty_id).first()
                        p, created = Profile.objects.get_or_create(user=edit_user)
                        p.specialty = spec
                        p.save()
                    elif not edit_user:
                        # Create empty profile for new users if no specialty selected
                        Profile.objects.create(user=edit_user)

                return redirect('manage_users')
            except Exception as e:
                if str(e) != 'No password':
                    messages.error(request, f'Xatolik yuz berdi: {str(e)}')

    context = {
        'edit_user': edit_user,
        'profile': profile,
        'specialties': Specialty.objects.all(),
        'roles': User.Roles.choices
    }
    return render(request, 'dashboard/users/form.html', context)
