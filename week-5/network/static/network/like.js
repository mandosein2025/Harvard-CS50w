document.addEventListener('DOMContentLoaded', function() {
  like_buttons = document.querySelectorAll('i');
  like_buttons.forEach(function(like_button) {
    like_button.addEventListener('click', function() {

      fetch(`/like_post/${this.dataset.id}`, {
        credentials: 'include',
        method: 'POST',
        mode: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': get_cookie('csrftoken') 
        },
      })
      .then(response => response.json())
      .then(result => {
        if (result.liked === "True") {
          document.querySelector(`i[data-id="${this.dataset.id}"]`).className = "fas fa-heart";
          like_count = document.querySelector(`div[data-id="${this.dataset.id}"]`).innerHTML;
          like_count = parseInt(like_count) + 1;
          like_count = document.querySelector(`div[data-id="${this.dataset.id}"]`).innerHTML = like_count;
        }
        else {
          document.querySelector(`i[data-id="${this.dataset.id}"]`).className = "far fa-heart";
          like_count = document.querySelector(`div[data-id="${this.dataset.id}"]`).innerHTML;
          like_count = parseInt(like_count) - 1;
          like_count = document.querySelector(`div[data-id="${this.dataset.id}"]`).innerHTML = like_count;
        }
      });
    });
  });
});
  

function get_cookie(name) {
  if (!document.cookie) {
    return null;
  }
  
  const token = document.cookie.split(';')
  .map(c => c.trim())
  .filter(c => c.startsWith(name + '='));

  if (token.length === 0) {
    return null;
  }
  
  return decodeURIComponent(token[0].split('=')[1]);
}