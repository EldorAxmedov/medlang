from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Scenario, Session, SimulationMessage
from .services import SimulationService

service = SimulationService()

@login_required
def simulation_list(request):
    """Barcha mavjud ssenariylar ro'yxati."""
    scenarios = Scenario.objects.filter(patient__isnull=False).order_by('difficulty')
    context = {
        'scenarios': scenarios,
        'title': 'Simulation Scenarios',
        'subtitle': 'Practice your medical English with AI-powered patient simulations.'
    }
    return render(request, 'simulation/list.html', context)

@login_required
def start_simulation(request, scenario_id):
    """Ssenariy bo'yicha yangi sessiya boshlash."""
    scenario = get_object_or_404(Scenario, id=scenario_id)
    session = service.start_session(request.user, scenario.id)
    return redirect('simulation_detail', session_id=session.id)

@login_required
def simulation_detail(request, session_id):
    """Chat interfeysi - simulyatsiya jarayoni."""
    session = get_object_or_404(Session, id=session_id, user=request.user)
    
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            service.send_user_message(session.id, message_text)
            return redirect('simulation_detail', session_id=session.id)

    messages = session.messages.all().order_by('timestamp')
    context = {
        'session': session,
        'messages': messages,
        'patient': session.scenario.patient,
        'title': f'{session.scenario.title} — Chat',
    }
    return render(request, 'simulation/detail.html', context)

@login_required
def complete_simulation(request, session_id):
    """Simulyatsiyani yakunlash va feedback olish."""
    session = get_object_or_404(Session, id=session_id, user=request.user)
    
    # AI orqali tahlil qilish
    analysis_text = service.ai_service.evaluate_session(session)
    
    # Bahoni parslash (soddalashtirilgan)
    # Amalda AI JSON qaytarsa yaxshiroq
    score = 80 # default
    if "SCORE:" in analysis_text:
        try:
            score_line = [l for l in analysis_text.split('\n') if "SCORE:" in l][0]
            score = int(''.join(filter(str.isdigit, score_line)))
        except:
            pass
            
    session = service.complete_session(session.id, score, analysis_text)
    
    return render(request, 'simulation/feedback.html', {'session': session, 'feedback': analysis_text})
