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

