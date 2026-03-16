// static/js/main.js

// Поиск по нажатию Ctrl+/ или Cmd+/
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
});

// Подтверждение удаления
document.querySelectorAll('.delete-confirm').forEach(button => {
    button.addEventListener('click', function(e) {
        if (!confirm('Вы уверены, что хотите удалить?')) {
            e.preventDefault();
        }
    });
});

// Предпросмотр изображений перед загрузкой
document.querySelector('input[type="file"][multiple]')?.addEventListener('change', function(e) {
    const preview = document.createElement('div');
    preview.className = 'image-preview';
    preview.innerHTML = '<h4>Предпросмотр:</h4>';

    for (let i = 0; i < this.files.length; i++) {
        const file = this.files[i];
        const reader = new FileReader();

        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.style.width = '100px';
            img.style.height = '100px';
            img.style.objectFit = 'cover';
            img.style.margin = '5px';
            img.style.borderRadius = '5px';
            preview.appendChild(img);
        }

        reader.readAsDataURL(file);
    }

    const oldPreview = document.querySelector('.image-preview');
    if (oldPreview) {
        oldPreview.remove();
    }

    this.parentNode.appendChild(preview);
});

// Автодополнение поиска
const searchInput = document.querySelector('input[name="q"]');
if (searchInput) {
    let autocompleteDiv = document.createElement('div');
    autocompleteDiv.className = 'autocomplete-items';
    searchInput.parentNode.style.position = 'relative';
    searchInput.parentNode.appendChild(autocompleteDiv);

    searchInput.addEventListener('input', function() {
        const query = this.value;
        if (query.length < 2) {
            autocompleteDiv.innerHTML = '';
            return;
        }

        fetch(`/api/autocomplete/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                autocompleteDiv.innerHTML = '';
                data.forEach(item => {
                    const div = document.createElement('div');
                    div.innerHTML = item.replace(new RegExp(query, 'gi'), match => `<strong>${match}</strong>`);
                    div.addEventListener('click', function() {
                        searchInput.value = item.replace(/<[^>]*>/g, '');
                        autocompleteDiv.innerHTML = '';
                        searchInput.form.submit();
                    });
                    autocompleteDiv.appendChild(div);
                });
            });
    });

    // Закрываем автодополнение при клике вне
    document.addEventListener('click', function(e) {
        if (e.target !== searchInput) {
            autocompleteDiv.innerHTML = '';
        }
    });
}