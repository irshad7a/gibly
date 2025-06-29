document.addEventListener('DOMContentLoaded', function() {
    // Like button logic
    document.querySelectorAll('.like-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            let postId = btn.getAttribute('data-post-id');
            // Send request to backend to toggle like
            fetch(`/like_post/${postId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            }).then(response => {
                if (response.ok) {
                    // Toggle UI on success
                    return response.json();
                } else {
                    alert('Failed to update like. Please try again.');
                }
            }).then(data => {
                if (data) {
                    let icon = btn.querySelector('i');
                    let countSpan = btn.querySelector('.like-count');
                    let liked = data.liked;
                    btn.classList.toggle('liked', liked);
                    countSpan.textContent = data.like_count;
                }
            }).catch(() => {
                alert('Failed to update like. Please try again.');
            });
        });
    });

    // Comment button logic - updated to redirect to post_detail page
    document.querySelectorAll('.comment-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            let postId = btn.getAttribute('data-post-id');
            // Redirect to post detail page
            window.location.href = `/post/${postId}/`;
        });
    });

    // Other existing code for chat, comment form submission, follow/unfollow, etc.
    // (Omitted here for brevity, but should be included in the actual file)

    // Add event listener for "+" button in chat sidebar
    const chatNewBtn = document.getElementById('chatNewBtn');
    if (chatNewBtn) {
        chatNewBtn.addEventListener('click', function() {
            // Redirect to user list page to start a new chat
            window.location.href = '/user_list/';
        });
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
