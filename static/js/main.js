(function () {
  const selectFields = Array.from(document.querySelectorAll('[data-select]'));
  const form = document.querySelector('[data-prediction-form]');
  const formMessage = document.querySelector('[data-form-message]');

  function closeAllSelects() {
    selectFields.forEach((field) => {
      field.classList.remove('is-open');
      const trigger = field.querySelector('.select-trigger');
      trigger.setAttribute('aria-expanded', 'false');
    });
  }

  function syncSelect(field) {
    const nativeSelect = field.querySelector('.select-native');
    const selectedOption = field.querySelector('[data-value="' + nativeSelect.value + '"]');
    const label = field.querySelector('[data-select-label]');

    label.textContent = selectedOption
      ? selectedOption.dataset.label
      : nativeSelect.options[0].text;

    field.querySelectorAll('.select-option').forEach((option) => {
      const isSelected = option.dataset.value === nativeSelect.value;
      option.classList.toggle('is-selected', isSelected);
      option.setAttribute('aria-selected', String(isSelected));
    });

    field.classList.toggle('has-value', Boolean(nativeSelect.value));
    field.classList.remove('has-error');
  }

  selectFields.forEach((field) => {
    const nativeSelect = field.querySelector('.select-native');
    const trigger = field.querySelector('.select-trigger');

    syncSelect(field);

    trigger.addEventListener('click', () => {
      const isOpening = !field.classList.contains('is-open');
      closeAllSelects();

      if (isOpening) {
        field.classList.add('is-open');
        trigger.setAttribute('aria-expanded', 'true');
      }
    });

    field.querySelectorAll('.select-option').forEach((option) => {
      option.addEventListener('click', () => {
        nativeSelect.value = option.dataset.value;
        nativeSelect.dispatchEvent(new Event('change', { bubbles: true }));
        closeAllSelects();
        trigger.focus();
      });
    });

    nativeSelect.addEventListener('change', () => syncSelect(field));
  });

  document.addEventListener('click', (event) => {
    if (!event.target.closest('[data-select]')) {
      closeAllSelects();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeAllSelects();
    }
  });

  if (form) {
    const scoreInputs = Array.from(form.querySelectorAll('.score-control'));

    form.addEventListener('submit', (event) => {
      const emptySelect = selectFields.find((field) => !field.querySelector('.select-native').value);
      const invalidScore = scoreInputs.find((input) => {
        const value = Number(input.value);
        return !input.value || Number.isNaN(value) || value < 0 || value > 100;
      });

      selectFields.forEach((field) => field.classList.remove('has-error'));
      scoreInputs.forEach((input) => input.classList.remove('has-error'));

      if (!emptySelect && !invalidScore) {
        return;
      }

      event.preventDefault();

      if (emptySelect) {
        emptySelect.classList.add('has-error');
        emptySelect.querySelector('.select-trigger').focus();
        formMessage.textContent = 'Choose an option for each student detail before forecasting.';
      } else {
        invalidScore.classList.add('has-error');
        invalidScore.focus();
        formMessage.textContent = 'Reading and writing scores must be numbers from 0 to 100.';
      }

      formMessage.classList.add('is-visible');
    });

    scoreInputs.forEach((input) => {
      input.addEventListener('input', () => {
        input.classList.remove('has-error');
        if (!form.querySelector('.has-error')) {
          formMessage.classList.remove('is-visible');
        }
      });
    });
  }

  const meter = document.querySelector('.score-meter');
  if (meter) {
    const score = parseFloat(meter.dataset.pct || '0');
    const color =
      score >= 75 ? '#4e8f71' :
      score >= 50 ? '#315f95' :
      score >= 25 ? '#d98a3e' : '#d2614c';

    requestAnimationFrame(() => {
      meter.style.setProperty('--pct', score + '%');
      meter.style.setProperty('--color', color);
    });
  }

  const resultModal = document.querySelector('[data-prediction-modal]');
  if (resultModal && typeof resultModal.showModal === 'function') {
    resultModal.showModal();

    resultModal.querySelectorAll('[data-modal-close]').forEach((button) => {
      button.addEventListener('click', () => resultModal.close());
    });

    resultModal.addEventListener('click', (event) => {
      if (event.target === resultModal) {
        resultModal.close();
      }
    });
  }
})();
