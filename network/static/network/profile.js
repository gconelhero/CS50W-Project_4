function like(post) {
  fetch('/send-post', {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({post: post,})
  }).then(response => response.json())
  .then(data => {
    document.querySelector('#like-' + post).innerHTML = data['likes'].length
    document.querySelector('#like-' + post + '-like').innerHTML = data['like']
  });
};

function follow(user) {
  fetch('/follow', {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({user: user})
  }).then(response => response.json())
  .then(data => {
    document.querySelector('#follow').innerHTML = data['follow'];
    document.querySelector('#followers').innerHTML = "Followers " + data['followers'].length;
  });
};

function edit(post) {
  fetch('/send-post', {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({edit: post,})
  }).then(response => response.json())
  .then(data => {
    var edit = document.createElement('div')
    var edit_textarea = document.createElement('textarea');
    var save_btn = document.createElement('button');
    var content = document.getElementById('post-content-' + data['post_id']);
    edit.className = 'post-edit'
    save_btn.innerHTML = "Save"
    save_btn.className = "btn-primary"
    edit_textarea.style.marginRight = '100px';
    save_btn.style.marginRight = '100px';
    edit_textarea.value = data['post_content'];
    edit.append(edit_textarea)
    edit.append(save_btn)
    content.replaceWith(edit)
    save_btn.addEventListener('click', () => {
      fetch('/send-post', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({edit_content: post,
          content: edit_textarea.value,
        })
      }).then(response => response.json())
      .then(data => {
        content.innerHTML = data['post_content']
        edit.replaceWith(content)
      })
      
    })
  })
};
