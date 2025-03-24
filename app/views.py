from django.shortcuts import render
from .forms import UploadFileForm
from .utils import handle_uploaded_file, scramble_text

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file_path = handle_uploaded_file(request.FILES['file'])
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                modified_text = scramble_text(text)
                return render(request, 'result.html', {'modified_text': modified_text})
            except Exception as e:
                error = f"Błąd przetwarzania pliku: {str(e)}"
                return render(request, 'upload.html', {'form': form, 'error': error})
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})