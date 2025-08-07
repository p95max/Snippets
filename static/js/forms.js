// Подсчет количества символов в поле код у форм доб. и ред. сниппетов
document.addEventListener('DOMContentLoaded', function () {
      const codeField = document.getElementById('id_code');
      const counter = document.getElementById('code-char-count');
      const maxLength = 5000;

      function updateCount() {
        if (!codeField || !counter) return;

        const length = codeField.value.length;
        counter.textContent = `${length}/${maxLength}`;

        counter.classList.remove('text-success', 'text-warning', 'text-danger');

        if (length <= 1000) {
          counter.classList.add('text-success');
        } else if (length <= 1200) {
          counter.classList.add('text-warning');
        } else {
          counter.classList.add('text-danger');
        }

        // Ограничение длины: если превышено, обрезаем
        if (length > maxLength) {
          codeField.value = codeField.value.slice(0, maxLength);
          counter.textContent = `${maxLength}/${maxLength}`;
        }
      }


      if (codeField && counter) {
        updateCount();
        codeField.addEventListener('input', updateCount);
      }
});

// Логика автосохранения добавления сниппета
document.addEventListener('DOMContentLoaded', function() {
    const DRAFT_KEY = 'snippet_draft_create';
    const name = document.getElementById('id_name');
    const code = document.getElementById('id_code');
    const description = document.getElementById('id_description');
    const form = document.querySelector('form');
    let intervalId = null;

    const draft = localStorage.getItem(DRAFT_KEY);
    if (draft) {
        try {
            const data = JSON.parse(draft);
            if (data) {
                if (name) name.value = data.name || '';
                if (code) code.value = data.code || '';
                if (description) description.value = data.description || '';
            }
        } catch (e) {}
    }

    function isFormFilled() {
        return (name && name.value.trim()) ||
               (code && code.value.trim()) ||
               (description && description.value.trim());
    }

    function saveDraft() {
        if (isFormFilled()) {
            const data = {
                name: name ? name.value : '',
                code: code ? code.value : '',
                description: description ? description.value : '',
            };
            localStorage.setItem(DRAFT_KEY, JSON.stringify(data));
        }
    }

    intervalId = setInterval(saveDraft, 10000);

    form.addEventListener('submit', function() {
        localStorage.removeItem(DRAFT_KEY);
        clearInterval(intervalId);
    });

    window.addEventListener('beforeunload', function() {
        clearInterval(intervalId);
    });
});

// Логика автосохранения редакт сниппета
document.addEventListener('DOMContentLoaded', function() {
    const DRAFT_KEY = 'snippet_draft_edit';
    const name = document.getElementById('id_name');
    const code = document.getElementById('id_code');
    const description = document.getElementById('id_description');
    const form = document.querySelector('form');
    let intervalId = null;

    // Автоматическое восстановление черновика
    const draft = localStorage.getItem(DRAFT_KEY);
    if (draft) {
        try {
            const data = JSON.parse(draft);
            if (data) {
                if (name) name.value = data.name || '';
                if (code) code.value = data.code || '';
                if (description) description.value = data.description || '';
            }
        } catch (e) {}
    }

    // Автосохранение
    function isFormFilled() {
        return (name && name.value.trim()) ||
               (code && code.value.trim()) ||
               (description && description.value.trim());
    }

    function saveDraft() {
        if (isFormFilled()) {
            const data = {
                name: name ? name.value : '',
                code: code ? code.value : '',
                description: description ? description.value : '',
            };
            localStorage.setItem(DRAFT_KEY, JSON.stringify(data));
        }
    }

    intervalId = setInterval(saveDraft, 10000);

    form.addEventListener('submit', function() {
        localStorage.removeItem(DRAFT_KEY);
        clearInterval(intervalId);
    });

    window.addEventListener('beforeunload', function() {
        clearInterval(intervalId);
    });
});

// переключение видимости пароля в форме регистрации
document.addEventListener('DOMContentLoaded', function() {
    const passwordFields = document.querySelectorAll('input[type="password"]');

    passwordFields.forEach(field => {

        const container = document.createElement('div');
        container.style.position = 'relative';
        field.parentNode.insertBefore(container, field);
        container.appendChild(field);


        const toggleButton = document.createElement('button');
        toggleButton.type = 'button';
        toggleButton.innerHTML = '👁️';
        toggleButton.setAttribute('aria-label', 'Показать/скрыть пароль');
        toggleButton.style.cssText = `
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            cursor: pointer;
            font-size: 18px;
            padding: 0;
        `;

        container.appendChild(toggleButton);

        toggleButton.addEventListener('click', function() {
            if (field.type === 'password') {
                field.type = 'text';
                toggleButton.innerHTML = '🙈';
            } else {
                field.type = 'password';
                toggleButton.innerHTML = '👁️';
            }
        });
    });
});


