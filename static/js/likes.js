$(function() {
    $('.like-btn, .dislike-btn').click(function() {
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
        });
    });
});