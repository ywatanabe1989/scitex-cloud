// File editor functionality

function showEdit() {
    document.getElementById('editorTextarea').style.display = 'block';
    document.getElementById('previewContainer').style.display = 'none';
    document.getElementById('editBtn').classList.add('active');
    document.getElementById('previewBtn').classList.remove('active');
}

function showPreview() {
    const content = document.getElementById('editorTextarea').value;
    const html = marked.parse(content);
    document.getElementById('previewContainer').innerHTML = html;

    document.getElementById('editorTextarea').style.display = 'none';
    document.getElementById('previewContainer').style.display = 'block';
    document.getElementById('editBtn').classList.remove('active');
    document.getElementById('previewBtn').classList.add('active');
}
