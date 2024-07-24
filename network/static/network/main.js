document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.edit-button').forEach(button => {
      button.onclick = () => {
        edit(button);         
      };
  });

  document.querySelectorAll('.save-button').forEach(button => {
    button.onclick = () => {        
        saveEdit(button);
    };
  });

  document.querySelectorAll('.like-btn').forEach(button => {
    button.onclick = () => {            
        likePost(button);
    };
  });  
});

function getCookie(name){
  const regex = new RegExp(`(^| )${name}=([^;]+)`)
  const match = document.cookie.match(regex)
  if (match) {
    return match[2]
  }
}

function edit(button){
    const postId = button.dataset.postId;      
    const save_btn = document.querySelector(`.save-button[data-post-id="${postId}"]`)
    //hide old content
    document.getElementById(`content-${postId}`).style.display = 'none';
    //display teaxtarea
    document.getElementById(`edit-content-${postId}`).style.display = 'block';
    //insert old content into teaxtarea
    document.getElementById(`edit-content-${postId}`).value = document.getElementById(`content-${postId}`).innerText;
    //display save button instead of edit button
    button.style.display = 'none';
    save_btn.style.display = 'inline';
}

function saveEdit(button){ 
    const postId = button.dataset.postId; 
    const newContent = document.getElementById(`edit-content-${postId}`).value;
    const csrfToken = getCookie('csrftoken');
    fetch(`/edit_post/${postId}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ 
            post: newContent 
        })
    })
    .then(response =>{
        if (response.ok){
            //insert new content into post
            document.getElementById(`content-${postId}`).innerText = newContent;        
            document.getElementById(`content-${postId}`).style.display = 'block';          
            //hide textarea and error
            document.getElementById(`edit-content-${postId}`).style.display = 'none';
            document.getElementById(`error-${postId}`).style.display = 'none';
            //display edit btn instead of save btn
            document.querySelector(`.edit-button[data-post-id="${postId}"]`).style.display = 'inline';
            button.style.display = 'none';     
        } else {
            document.getElementById(`error-${postId}`).style.display = 'block';
            document.getElementById(`error-${postId}`).innerText = "This field can not be empty";            
        }                   
    })
    document.getElementById(`edited-${postId}`).style.display = 'block'; 
 }    

function likePost(button) {
  //get post and user id
  const postId = button.dataset.postId;
  const userId = button.dataset.userId;
  const csrfToken = getCookie('csrftoken');
  
  fetch(`/like_post/${postId}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ 
            user_id: userId,
        })
  })
  .then(response => response.json())
  .then(data => {
    //update count    
    const likeCount = document.querySelector(`#like-count-${postId}`);
    likeCount.textContent = data.like_count;
    //update the icon 
    const likedIcon = document.querySelector(`.liked-${postId}`);
    const unlikeIcon = document.querySelector(`.unliked-${postId}`);   
    if (data.liked) {
        likedIcon.style.display = 'block';
        unlikeIcon.style.display = 'none';
    } else {
        likedIcon.style.display = 'none';
        unlikeIcon.style.display = 'block';
    }
  })
}
