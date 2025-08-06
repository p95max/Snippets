// Подсчет количества символов в поле код у форм доб. и ред. сниппетов
document.addEventListener('DOMContentLoaded', function () {
const codeField = document.getElementById('id_code');
const counter = document.getElementById('code-char-count');

function updateCount() {
  if (!codeField || !counter) return;

  const length = codeField.value.length;
  counter.textContent = length;

  counter.classList.remove('text-success', 'text-warning', 'text-danger');

  if (length < 1000) {
    counter.classList.add('text-success');
  } else if (length <= 1200) {
    counter.classList.add('text-warning');
  } else {
    counter.classList.add('text-danger');
  }
}

if (codeField && counter) {
  updateCount();
  codeField.addEventListener('input', updateCount);
}
});


