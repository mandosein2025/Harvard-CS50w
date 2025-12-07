document.addEventListener('DOMContentLoaded', function() {
  document.querySelector('#post-message').onkeyup = function () {
    // max length comes from model.py, passed through the view to the template
    // creates a dynamic characters remaining counter
    document.querySelector('#post-chars-remaining-message').innerHTML = `<b>${this.maxLength - this.value.length}</b> characters remaining`;
  }
});
