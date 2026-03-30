from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from tests.models import Test
from tests.services import TestService

test_service = TestService()

@login_required
def student_test_list(request):
    """Barcha mavjud testlar ro'yxati talabalar uchun."""
    tests = test_service.list_tests()
    results = test_service.get_user_results(request.user.id)
    return render(request, 'tests/student_list.html', {
        'tests': tests,
        'results': results
    })

@login_required
def test_take(request, pk):
    """Testni yechish sahifasi."""
    test = test_service.get_test_with_questions(pk)
    if not test:
        messages.error(request, "Test topilmadi.")
        return redirect('student_test_list')

    if request.method == 'POST':
        # Javoblarni yig'amiz: {'question_id': 'answer_id'}
        answers_map = {}
        for q in test.questions.all():
            if q.question_type == 'matching':
                user_matches = []
                for idx, ans in enumerate(q.answers.all()):
                    term_part = ans.text.split(' :: ')[0]
                    user_selected_def = request.POST.get(f'q_{q.id}_pair_{idx}')
                    user_matched_string = f"{term_part} :: {user_selected_def}"
                    matched_ans = q.answers.filter(text=user_matched_string).first()
                    if matched_ans:
                        user_matches.append(str(matched_ans.id))
                answers_map[str(q.id)] = user_matches
            
            elif q.question_type == 'gap_fill':
                user_text = request.POST.get(f'q_{q.id}', '').strip().lower()
                matched_ans = q.answers.filter(text__iexact=user_text).first()
                if matched_ans:
                    answers_map[str(q.id)] = str(matched_ans.id)
                else:
                    answers_map[str(q.id)] = 'wrong'
            elif q.question_type == 'mcq':
                # Multiple Choice: we collect all checked values as a list
                ans_ids = request.POST.getlist(f'q_{q.id}')
                if ans_ids:
                    answers_map[str(q.id)] = ans_ids
            
            else:
                # True/False
                ans_id = request.POST.get(f'q_{q.id}')
                if ans_id:
                    answers_map[str(q.id)] = ans_id
        
        try:
            result = test_service.submit_test(request.user, str(test.id), answers_map)
            messages.success(request, f"Test yakunlandi! Sizning natijangiz: {result.score}%")
            return render(request, 'tests/result.html', {'result': result, 'test': test})
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
            return redirect('student_test_list')

    return render(request, 'tests/take.html', {'test': test})
