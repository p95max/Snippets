//  Таймаут всплывающих всех сообщений
// document.addEventListener('DOMContentLoaded', function () {
//     const notifications = document.querySelectorAll('.notification');
//
//     notifications.forEach((notification) => {
//         setTimeout(() => {
//             notification.classList.add('hide');
//             setTimeout(() => {
//                 notification.style.display = 'none';
//             }, 500);
//         }, 5000);
//     });
// });

//  Таймаут всплывающих блока сообщений в базовом шаблоне
const alertsBox = document.getElementById('alerts_box');

function closeMessage(message) {
    message.classList.add('hide');
    setTimeout(() => message.remove(), 500);
}

function closeMessages() {
    const messages = alertsBox.querySelectorAll('div');
    let step = 600;
    let delay = 0;

    messages.forEach((message) => {
        setTimeout(() => closeMessage(message), delay);
        delay += step;
    });
}

setTimeout(closeMessages, 3000);

// подсчет символов и валидацию к форме комментариев
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('id_text');
    const counter = document.getElementById('char-counter');
    const submitBtn = document.getElementById('submit-btn');
    const MAX_LENGTH = 500;

    function validate() {
        const value = textarea.value;
        const length = value.length;
        counter.textContent = `${length}/${MAX_LENGTH}`;


        const isValid = value.trim().length > 0 && length <= MAX_LENGTH;
        submitBtn.disabled = !isValid;

        if (length > MAX_LENGTH) {
            counter.classList.add('text-danger');
        } else {
            counter.classList.remove('text-danger');
        }
    }

    textarea.addEventListener('input', validate);

    validate();
});

