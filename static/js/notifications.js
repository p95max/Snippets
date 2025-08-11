function pollUnreadNotifications() {
    fetch('/api/unread-notifications-longpoll/')
      .then(response => response.json())
      .then(data => {
        document.getElementById('notif-badge').innerText = data.unread_count;

        pollUnreadNotifications();
      })
      .catch(() => {
        setTimeout(pollUnreadNotifications, 5000);
      });
}

pollUnreadNotifications();