// Копирование кода из просмотра сниппетов в буфер обмена
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.copy-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const code = btn.parentElement.querySelector('.snippet-code').textContent;
            navigator.clipboard.writeText(code).then(() => {
                btn.innerText = '✔';
                btn.title = 'Скопировано!';
                setTimeout(() => {
                    btn.innerText = '📋';
                    btn.title = 'Скопировать';
                }, 2000);
            }).catch(err => {
                console.error('Ошибка копирования:', err);
            });
        });
    });
});

