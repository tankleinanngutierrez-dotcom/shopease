document.addEventListener('htmx:afterRequest', function (event) {
  if (event.detail.successful) {
    document.querySelectorAll('.toast').forEach(function (el) {
      setTimeout(function(){ el.classList.add('hide'); }, 3200);
    });
  }
});
