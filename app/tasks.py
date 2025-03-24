from celery import shared_task
from .utils import handle_uploaded_file, scramble_text


@shared_task(bind=True)
def process_file_task(self, file_content, original_filename):
    try:
        file_path = handle_uploaded_file(file_content, original_filename)

        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        scrambled_text = scramble_text(text)

        return {
            'status': 'success',
            'result': scrambled_text,
        }
    except Exception as e:

        raise self.retry(exc=e, countdown=60)