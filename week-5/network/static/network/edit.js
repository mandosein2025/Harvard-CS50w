document.addEventListener('DOMContentLoaded', function() {
    edit_buttons = document.querySelectorAll('.edit_post');
    cancel_buttons = document.querySelectorAll('.cancel-button');
    save_buttons = document.querySelectorAll('.save-button');

    edit_buttons.forEach(function(edit_button) {
        edit_button.addEventListener('click', function() {
            post_id = this.dataset.editid;
            post_container = document.querySelector(`div[data-post_container_id="${post_id}"]`);
            edit_container = document.querySelector(`div[data-edit_container_id="${post_id}"]`);
            
            original_post_message = document.querySelector(`div[data-message="${post_id}"]`).innerHTML;
            edit_post_message = document.querySelector(`#text_${[post_id]}`);
            edit_post_message.value = original_post_message;
             
            post_container.style.display = 'none';
            edit_container.style.display = 'block';

            post_box = document.querySelector(`#text_${post_id}`);
            setTimeout(function () {
                post_box.focus();
                post_box.setSelectionRange(post_box.value.length, post_box.value.length);
            }, 0);

            characters_remaining = document.querySelector(`#post-chars-remaining-message_${post_id}`);

            characters_remaining.innerHTML = `<b>${post_box.maxLength - edit_post_message.value.length}</b> characters remaining`;
            edit_post_message.onkeyup = function () {
                characters_remaining.innerHTML = `<b>${post_box.maxLength - edit_post_message.value.length}</b> characters remaining`;
            }
        });
    });

    cancel_buttons.forEach(function(cancel_button) {
        cancel_button.addEventListener('click', function() {
            post_id = this.dataset.cancelid;

            post_container = document.querySelector(`div[data-post_container_id="${post_id}"]`);
            edit_container = document.querySelector(`div[data-edit_container_id="${post_id}"]`);

            post_container.style.display = 'block';
            edit_container.style.display = 'none';
        });
    });

    save_buttons.forEach(function(save_button) {
        save_button.addEventListener('click', function() {
            post_id = this.dataset.saveid;
            
            post_box = document.querySelector(`#text_${post_id}`);
            
            text = post_box.value; 

            post_container = document.querySelector(`div[data-post_container_id="${post_id}"]`);
            edit_container = document.querySelector(`div[data-edit_container_id="${post_id}"]`);

            post = document.querySelector(`div[data-message="${post_id}"]`);
           
            fetch(`/post/${post_id}`, {
                credentials: 'include',
                method: 'POST',
                mode: 'same-origin',
                headers: {
                  'Accept': 'application/json',
                  'Content-Type': 'application/json',
                  'X-CSRFToken': getCookie('csrftoken') 
                },
                body: JSON.stringify({message: text}),
            })
            .then(response => response.json())
            .then(result => {
                if (result.message != undefined && result.message.length > 0) {
                    message_container = document.getElementById('result-message');
                    message_container.innerHTML = result.message;
                }
                else {
                    message_container = document.getElementById('result-message');
                    message_container.innerHTML = '';
                    post.innerHTML = text;
                    post_container.style.display = 'block';
                    edit_container.style.display = 'none';
                }
            });
        });
    });
});

// from https://docs.djangoproject.com/en/3.0/ref/csrf/#ajax
function getCookie(name) {
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
