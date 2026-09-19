document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('video-modal');
    const btn = document.getElementById('watch-demo');
    const span = document.getElementsByClassName('close-modal')[0];
    const video = document.getElementById('demo-video');

    if (btn && modal) {
        btn.onclick = function() {
            modal.style.display = 'flex';
            // Placeholder BMW video
            video.src = 'https://www.youtube.com/embed/-Lt-ntUDj-g';
        }
    }

    if (span) {
        span.onclick = function() {
            modal.style.display = 'none';
            video.src = ''; // Stop video when closing
        }
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
            video.src = '';
        }
    }
});
