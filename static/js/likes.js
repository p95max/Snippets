$(function() {
    $('.like-form').on('click', '.like-btn, .dislike-btn', function() {
        var form = $(this).closest('.like-form');
        var object_id = form.data('object-id');
        var vote = $(this).hasClass('like-btn') ? 1 : -1;

        $.post(form.data('url'), {
            object_id: object_id,
            vote: vote,
            csrfmiddlewaretoken: form.find('[name=csrfmiddlewaretoken]').val()
        }, function(data) {
            form.find('.like-count').text(data.likes);
            form.find('.dislike-count').text(data.dislikes);

            // Сбросить активные классы только в этой форме!
            form.find('.like-btn, .dislike-btn').removeClass('active');
            // Подсветить только нужную кнопку
            if (data.user_vote == 1) {
                form.find('.like-btn').addClass('active');
            } else if (data.user_vote == -1) {
                form.find('.dislike-btn').addClass('active');
            }
        });
    });
});