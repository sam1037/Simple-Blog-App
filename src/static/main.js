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
        curDiv.innerHTML = `
            <div class="flex justify-between items-start mb-1">
                <h3 class="text-xl font-bold">${post.title}</h3>
                <div class="flex">
                    <button id="editBtn" class="ml-2 px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 edit-button" data-post-id="${post.post_id}">Edit</button>
                    <button id="deleteBtn" class="ml-2 px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600 delete-button" data-post-id="${post.post_id}">Delete</button>
                </div>
            </div>
            <div class="text-sm text-gray-500 mb-2">By ${post.author} <span style="float: right;">${post.date_posted}</span></div>
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