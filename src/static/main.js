async function fetchPosts() {
    //get the posts 
    const res = await fetch("/get_posts");
    const posts = await res.json();
    console.log(posts)
    //modify div with id "posts" in index.html by adding child elements to it
    const postDiv = document.getElementById("posts");
    postDiv.innerHTML = "";

    posts.forEach(post => {
        const curDiv = document.createElement("div");
        curDiv.className = "bg-white p-4 rounded shadow-sm"
        const likeCount = post.like_count !== undefined ? post.like_count : 0; 
        const thumbsUpSVG = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="16px" height="16px" class="inline-block mr-1 align-middle">
              <path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/>
            </svg>
        `;

        curDiv.innerHTML = `
            <div class="flex justify-between items-start mb-1">
                <h3 class="text-xl font-bold">${post.title}</h3>
                <div class="flex">
                    <button id="editBtn" class="ml-2 px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 edit-button" data-post-id="${post.post_id}">Edit</button>
                    <button id="deleteBtn" class="ml-2 px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600 delete-button" data-post-id="${post.post_id}">Delete</button>
                </div>
            </div>
            <div class="text-sm text-gray-500 mb-1"> 
                By ${post.author} 
                <span style="float: right;">${post.date_posted}</span>
            </div>
            <div class="text-sm text-gray-500 mb-2" style="clear: both;"> 
                <span style="float: right;">${thumbsUpSVG}${likeCount}</span>
            </div>
            <p class="text-gray-700 whitespace-pre-wrap">${post.content}</p>
        `

        postDiv.appendChild(curDiv);
    });

    // Add event listeners to delete buttons
    const deleteButtons = document.querySelectorAll('.delete-button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            //get the btn element, then get the post id
            const postId = event.target.dataset.postId;
            //console.log(`postID: ${postId}`);
            if (confirm("Are you sure you want to delete this post?")) {
                console.log(`delete post of postid ${postId}`);
                    const response = await fetch(`/delete_post/${postId}`, {
                        method: 'DELETE',
                    });
                if (response.ok) {
                    fetchPosts();
                } else {
                    const errorData = await response.json()
                    alert(errorData.message || 'Failed to delete post.');
                    if (errorData.message == "Login required"){
                        window.location.href = `/`
                    }
                }
            }
        });
    });

    // event listeners for edit btns
    const editBtns = document.querySelectorAll('.edit-button');
    editBtns.forEach(btn => {
        btn.addEventListener('click', async()=> {
            const postId = btn.dataset.postId;
            console.log(`TODO edit a post with postID: ${postId}`);
            

            const response = await fetch(`/edit_post/${postId}`, { method: 'GET', }); // ??? Diff btw this and the fetch(...).then functional programming style?
            if (response.ok) {
                window.location.href = `/edit_post/${postId}`
            } else {
                const errorData = await response.text()
                alert(errorData.message || 'You are not authorized to edit this post.');
            }
        })
    })
}

document.addEventListener("DOMContentLoaded", fetchPosts);