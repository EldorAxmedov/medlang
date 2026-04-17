from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from grammar.services import GrammarService
from grammar.models import GrammarCheck

grammar_service = GrammarService()

@login_required
def grammar_list(request):
    """Barcha tahlillar ro'yxati va yangi tahlil yuborish."""
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        try:
            check = grammar_service.process_check(request.user, text)
            messages.success(request, "Matn tahlili muvaffaqiyatli yakunlandi!")
            return redirect('grammar_detail_view', pk=check.id)
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")

    checks = grammar_service.get_history(request.user.id)
    return render(request, 'grammar/index.html', {'checks': checks})

@login_required
def grammar_detail(request, pk):
    """Tahlil natijalarining batafsil ko'rinishi."""
    check = get_object_or_404(GrammarCheck, id=pk, user=request.user)
    return render(request, 'grammar/detail.html', {'check': check})
