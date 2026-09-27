import markdown
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Notes
from .Serializer import NotesSerializer
import language_tool_python

# Lazy load LanguageTool with remote server so Java is not required locally
_tool = None

def get_tool():
    global _tool
    if _tool is None:
        try:
            
            _tool = language_tool_python.LanguageTool('en-US', remote_server='https://api.languagetool.org/')
        except Exception:
           
            _tool = language_tool_python.LanguageTool('en-US')
    return _tool


def analyze_grammar(text):
    """
    Performs multi-pass grammar and spell check using LanguageTool.
    Pass 1: Detects spelling and grammar issues.
    Pass 2: Replaces spelling errors with top suggestions to uncover dependent grammar errors.
    """
    tool = get_tool()
    matches = tool.check(text)

    issues = []
    if matches:
        for match in matches:
            error_word = text[match.offset:match.offset + match.error_length]
            issues.append({
                'error_word': error_word,
                'rule_id': match.rule_id,
                'message': match.message,
                'suggestions': match.replacements[:5],
                'offset': match.offset,
                'error_length': match.error_length,
                'context': match.context
            })

    spelling_matches = [m for m in matches if getattr(m, 'category', '') in ['TYPOS', 'SPELLING'] or 'MORFOLOGIK' in m.rule_id]
    if spelling_matches:
        try:
            corrected = text
            for m in sorted(spelling_matches, key=lambda x: x.offset, reverse=True):
                if m.replacements:
                    best = m.replacements[0]
                    corrected = corrected[:m.offset] + best + corrected[m.offset + m.error_length:]

            pass2_matches = tool.check(corrected)
            for m2 in pass2_matches:
                overlaps = any(
                    max(m2.offset, iss['offset']) < min(m2.offset + m2.error_length, iss['offset'] + iss['error_length'])
                    for iss in issues
                )
                if not overlaps:
                    word = text[m2.offset:m2.offset + m2.error_length] if m2.offset + m2.error_length <= len(text) else corrected[m2.offset:m2.offset + m2.error_length]
                    issues.append({
                        'error_word': word,
                        'rule_id': m2.rule_id,
                        'message': m2.message,
                        'suggestions': m2.replacements[:5],
                        'offset': m2.offset,
                        'error_length': m2.error_length,
                        'context': text
                    })
        except Exception as e:
            pass

    issues.sort(key=lambda x: x['offset'])
    return issues

@api_view(['POST'])
def check_grammar(request):
    """
    Check the grammar of text or an existing note.
    Accepts:
      - {"text": "Your markdown or text note"}
      OR
      - {"note_id": 1}
    """
    text = request.data.get('text', '')
    note_id = request.data.get('note_id')

    if note_id:
        note = get_object_or_404(Notes, id=note_id)
        text = note.content

    if not text:
        return Response({'error': 'No text or valid note_id provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        issues = analyze_grammar(text)
    except Exception as e:
        return Response({
            'error': 'Grammar check failed. LanguageTool service is unavailable.',
            'details': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response({
        'text': text,
        'grammar_errors_count': len(issues),
        'issues': issues
    })


@api_view(['GET', 'POST'])
def check_note_grammar(request, id):
    """
    Check grammar directly for a saved note by its ID.
    GET/POST /notes/<id>/grammar/
    """
    note = get_object_or_404(Notes, id=id)
    try:
        issues = analyze_grammar(note.content)
    except Exception as e:
        return Response({
            'error': 'Grammar check failed. LanguageTool service is unavailable.',
            'details': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response({
        'note_id': note.id,
        'title': note.title,
        'text': note.content,
        'grammar_errors_count': len(issues),
        'issues': issues
    })

@api_view(['GET', 'POST'])
def notes_list(request):
    """
    GET: List all saved notes (i.e. uploaded markdown files and text notes).
    POST: Save a new note via JSON (content/title) or uploaded .md file (multipart/form-data).
    """
    if request.method == 'GET':
        notes = Notes.objects.all().order_by('-timestamp')
        serializer = NotesSerializer(notes, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)

        # Handle uploaded markdown file (.md / .txt)
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            file_content = uploaded_file.read().decode('utf-8', errors='ignore')
            data['content'] = file_content
            if 'title' not in data or not data['title']:
                data['title'] = uploaded_file.name

        serializer = NotesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def note_detail(request, id):
    """
    Retrieve, update or delete a specific note.
    """
    note = get_object_or_404(Notes, id=id)

    if request.method == 'GET':
        serializer = NotesSerializer(note)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = NotesSerializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        note.delete()
        return Response({'message': f'Note {id} deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Feature 4: Render Markdown Note as HTML
# ---------------------------------------------------------------------------

@api_view(['GET'])
def markdown_html(request, id):
    """
    Return the HTML version of the Markdown note.
    Returns JSON by default: {'id': note.id, 'title': note.title, 'markdown': note.content, 'html': html_content}
    If format=raw query param is set, returns direct text/html response.
    """
    note = get_object_or_404(Notes, id=id)
    html_content = markdown.markdown(note.content)

    if request.query_params.get('raw') == 'true' or request.query_params.get('view') == 'html':
        return HttpResponse(html_content, content_type='text/html')

    return Response({
        'id': note.id,
        'title': note.title,
        'markdown': note.content,
        'html': html_content
    })