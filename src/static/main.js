async function fetchPosts() {
    //get the posts 
    const res = await fetch("/get_posts");
    if (!res.ok) {
        console.error("Failed to fetch posts:", res.status, await res.text());
        document.getElementById("posts").innerHTML = "<p class='text-red-500'>Error loading posts. Please try again later.</p>";
        return;
    }

    const resJson = await res.json();
    const posts = resJson.posts || []
    const curUserLikedPostIds = resJson.current_user_liked_post_ids || []
    console.log(posts)

    //modify div with id "posts" in index.html by adding child elements to it
    const postDiv = document.getElementById("posts");
    postDiv.innerHTML = "";

    posts.forEach(post => {
        // create post element, append to the index page posts area
        const curDiv = document.createElement("div");
        curDiv.className = "bg-white p-4 rounded shadow-sm"
        const likeCount = post.like_count !== undefined ? post.like_count : 0; 
        const isLikedByCurrentUser = curUserLikedPostIds.includes(post.post_id)
        const iconFillColor = isLikedByCurrentUser ? "black" : "grey"; // Example: blue if liked

        const thumbsUpSVG = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${iconFillColor}" width="16px" height="16px" class="inline-block mr-1 align-middle">
              <path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/>
            </svg>
        `;

        // TODO prevent injection from user with post title/ post content
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
                <span
                data-post-id="${post.post_id}"
                data-is-liked-by-cur-user="${isLikedByCurrentUser}"
                class="
                    like-btn-span
                    hover:bg-gray-200
                    inline-flex items-center justify-center    /* Flexbox for centering content */
                    px-2 py-1                                 /* Padding to make it bigger */
                    rounded-full                              /* Rounded corners */
                    text-gray-600                             /* Adjust text/icon color if needed for contrast */
                    text-xs                                   /* Adjust text size if needed */
                    cursor-pointer
                "
                style="float: right;"
                >
                ${thumbsUpSVG}<span class="like-count">${likeCount}</span>
                </span>
            </div>
            <p class="text-gray-700 whitespace-pre-wrap">${post.content}</p>
        `

        postDiv.appendChild(curDiv);
    });

    attachAllEventListeners();
}

/**
 * Attach event listeners for delete, edit, and like btns
 */
function attachAllEventListeners() {
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
            // console.log(`TODO edit a post with postID: ${postId}`);

            const response = await fetch(`/edit_post/${postId}`, { method: 'GET', }); // ??? Diff btw this and the `fetch(...).then` functional programming style?
            if (response.ok) {
                window.location.href = `/edit_post/${postId}`
            } else {
                const errorData = await response.json()
                alert(errorData.message || 'You are not authorized to edit this post.');
            }
        })
    })

    // event listerns for the like btns
    const likeBtns = document.querySelectorAll(".like-btn-span");
    likeBtns.forEach(btn_span => {
        btn_span.addEventListener("click", async()=> {
            // setup
            const postId = btn_span.dataset.postId;
            // console.log('%cis liked already:', 'font-weight: bold;');
            // console.log(isLikedAlready)
            const svgIcon = btn_span.querySelector('svg'); // More robust selector
            const likeCntSpanElement = btn_span.querySelector('.like-count');

            //time
            const timerLabel = `Like/Unlike Post ${postId}`; // Unique label for the timer
            console.time(timerLabel); // Start timing
            console.log(`like btn of post id ${postId} clicked!`);

            // validation
            if (!svgIcon || !likeCntSpanElement) {
                console.error("Could not find SVG icon or like count span for post:", postId);
                console.timeEnd(timerLabel);
                return;
            }
            
            //save og state and new state
            const originalLikeCount = parseInt(likeCntSpanElement.textContent, 10);
            const originalFillColor = svgIcon.getAttribute("fill");
            const isCurrentlyLiked = originalFillColor === "black";

            const newOptimisticLikedState = !isCurrentlyLiked;
            const newOptimisticLikeCount = newOptimisticLikedState ? originalLikeCount + 1 : Math.max(0, originalLikeCount - 1);

            console.log(`new (optimistic like count: ${newOptimisticLikeCount}`)

            // render the optimistic UI update
            svgIcon.setAttribute("fill", newOptimisticLikedState ? "black": "grey");
            likeCntSpanElement.textContent = newOptimisticLikeCount;

            // console.timeEnd(timerLabel);
            
            // TODO how to write the HTTP request more elegantly?
            //call the api endpoint to toggle like/ dislike a post 
            try {
                const response = await fetch(`/like_post/${postId}`, { method: 'POST', }); 
                const responseJson = await response.json();
                if (response.ok) {
                    console.log("Response from /like_post/<post_id> endpoint ok")
                    console.log("Like/Unlike response:", responseJson);

                    // check if state differ, if so update
                    if (responseJson.new_like_count !== newOptimisticLikeCount || responseJson.liked_by_user !== newOptimisticLikedState) {
                        console.warn("Server state differs from optimistic update. Syncing UI with server.");
                        likeCntSpanElement.textContent = responseJson.new_like_count;
                        svgIcon.setAttribute("fill", responseJson.liked_by_user ? "black" : "grey");
                    }
                } else {
                    // alert and console log
                    console.log(responseJson)
                    alert(responseJson.message || "Somehow can't like/ dislike the post");

                    // Revert UI to original state
                    likeCntSpanElement.textContent = originalLikeCount;
                    svgIcon.setAttribute("fill", originalFillColor);
                }
            } catch (error) {
                // Network error or other fetch-related issue, revert UI changes
                console.error("Fetch error:", error);
                alert("A network error occurred. Please try again.");

                // Revert UI to original state
                likeCntSpanElement.textContent = originalLikeCount;
                svgIcon.setAttribute("fill", originalFillColor);
            } finally {
                console.timeEnd(timerLabel);    
            }
        })
    })
}

document.addEventListener("DOMContentLoaded", fetchPosts);