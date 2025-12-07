document.addEventListener('DOMContentLoaded', function() {
  follow_button = document.querySelector('#follow-user');
  if (follow_button != undefined) {
    follow_button.addEventListener('click', function() {

      fetch(`/follow_user/${this.dataset.userid}`, {
        credentials: 'include',
        method: 'POST',
        mode: 'same-origin',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') 
        },
      })
      .then(response => response.json())
      .then(result => {
        if (result.followed === true) {
          follow_button.innerHTML = 'Unfollow user';
          number_of_followers = parseInt(document.querySelector('#number_of_followers').innerHTML);
          number_of_followers = number_of_followers + 1;
          document.querySelector('#number_of_followers').innerHTML = number_of_followers;
        }
        else {
          follow_button.innerHTML = 'Follow user';
          number_of_followers = parseInt(document.querySelector('#number_of_followers').innerHTML);
          number_of_followers = number_of_followers - 1;
          document.querySelector('#number_of_followers').innerHTML = number_of_followers; 
        }
      });
    });
  }
});
    
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