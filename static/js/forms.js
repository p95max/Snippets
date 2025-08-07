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


