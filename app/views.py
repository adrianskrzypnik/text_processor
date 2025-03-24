from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import UploadFileForm
from .utils import handle_uploaded_file, scramble_text
from .tasks import process_file_task  # Import naszego zadania Celery
import logging

logger = logging.getLogger(__name__)


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            # Wersja synchroniczna dla małych plików (<10KB)
            if file.size < 1024 * 10:
                try:
                    file_path = handle_uploaded_file(file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()

                    scrambled_text = scramble_text(text)
                    logger.info(f"Successfully processed {file.name} synchronously")

                    return render(request, 'result.html', {
                        'scrambled_text': scrambled_text,
                        'processing_mode': 'synchronous'
                    })

                except Exception as e:
                    logger.error(f"Sync processing error: {str(e)}")
                    return render(request, 'upload.html', {
                        'form': form,
                        'error': f"Błąd przetwarzania: {str(e)}"
                    })

            # Wersja asynchroniczna dla większych plików
            else:
                try:
                    # Zapisz plik tymczasowo i uruchom zadanie
                    file_path = handle_uploaded_file(file)
                    task = process_file_task.delay(file_path)
                    logger.info(f"Started async task {task.id} for {file.name}")

                    return render(request, 'processing.html', {
                        'task_id': task.id,
                        'filename': file.name
                    })

                except Exception as e:
                    logger.error(f"Async task creation failed: {str(e)}")
                    return render(request, 'upload.html', {
                        'form': form,
                        'error': "Nie udało się rozpocząć przetwarzania"
                    })

    # GET request - wyświetl formularz
    form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


def check_task_status(request, task_id):
    """Endpoint dla AJAX do sprawdzania statusu zadania"""
    from celery.result import AsyncResult
    task_result = AsyncResult(task_id)

    response_data = {
        'status': task_result.status,
        'ready': task_result.ready(),
    }

    if task_result.ready():
        if task_result.successful():
            response_data['result'] = task_result.result
        else:
            response_data['error'] = str(task_result.result)

    return JsonResponse(response_data)


def result_view(request):
    task_id = request.GET.get('task_id')
    if not task_id:
        return redirect('upload_file')

    from celery.result import AsyncResult
    task_result = AsyncResult(task_id)

    if not task_result.ready():
        return render(request, 'processing.html', {
            'task_id': task_id,
            'message': 'Wynik jeszcze nie gotowy'
        })

    if task_result.failed():
        return render(request, 'error.html', {
            'error': 'Przetwarzanie pliku nie powiodło się',
            'details': str(task_result.result)
        })

    return render(request, 'result.html', {
        'scrambled_text': task_result.result.get('result', ''),
        'original_length': task_result.result.get('original_length', 0),
        'processed_length': task_result.result.get('processed_length', 0),
        'processing_mode': 'asynchronous',
        'task_id': task_id
    })