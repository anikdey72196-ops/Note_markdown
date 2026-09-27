from io import BytesIO
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from .models import Notes

class NoteAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.note = Notes.objects.create(
            title="Intro",
            content="# Hello World\nThis is a test note."
        )

    # Feature 1: Grammar Check
    def test_grammar_check_empty(self):
        response = self.client.post('/check-grammar/', {'text': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_grammar_check_saved_note_by_id(self):
        response = self.client.get(f'/notes/{self.note.id}/grammar/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['note_id'], self.note.id)
        self.assertIn('grammar_errors_count', response.data)

    def test_grammar_check_endpoint_with_note_id(self):
        response = self.client.post('/check-grammar/', {'note_id': self.note.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('grammar_errors_count', response.data)

    # Features 2 & 3: Save and List Notes
    def test_get_notes(self):
        response = self.client.get('/notes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_note_with_content(self):
        response = self.client.post('/notes/', {'title': 'Heading Note', 'content': '## Another note'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], '## Another note')
        self.assertEqual(response.data['title'], 'Heading Note')

    def test_create_note_with_file_upload(self):
        uploaded_file = SimpleUploadedFile("readme.md", b"# Markdown from file\nThis is uploaded.", content_type="text/markdown")
        response = self.client.post('/notes/', {'file': uploaded_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'readme.md')
        self.assertIn('# Markdown from file', response.data['content'])

    def test_note_detail_and_delete(self):
        # Retrieve
        detail_resp = self.client.get(f'/notes/{self.note.id}/')
        self.assertEqual(detail_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_resp.data['id'], self.note.id)

        # Delete
        del_resp = self.client.delete(f'/notes/{self.note.id}/')
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)

    # Feature 4: Render Markdown to HTML
    def test_render_markdown_json(self):
        response = self.client.get(f'/notes/{self.note.id}/render/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('<h1>Hello World</h1>', response.data['html'])

    def test_render_markdown_raw_html(self):
        response = self.client.get(f'/notes/{self.note.id}/render/?raw=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/html')
        self.assertIn('<h1>Hello World</h1>', response.content.decode('utf-8'))

