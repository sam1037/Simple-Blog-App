async function fetchPosts() {
    //get the posts 
    const res = await fetch("/get_posts");
    const posts = await res.json();

    //modify div with id "posts" in index.html by adding child elements to it
    const postDiv = document.getElementById("posts");
    postDiv.innerHTML = "";

    posts.forEach(post => {
        const curDiv = document.createElement("div");
        curDiv.className = "bg-white p-4 rounded shadow-sm"
        curDiv.innerHTML = `
            <h3 class="text-xl font-bold mb-2">${post.title}</h3>
            <div class="text-sm text-gray-500 mb-2">By ${post.author} <span style="float: right;">${post.date}</span></div>
            <p class="text-gray-700 whitespace-pre-wrap">${post.content}</p>
        `

        postDiv.appendChild(curDiv);
    });
}

document.addEventListener("DOMContentLoaded", fetchPosts);