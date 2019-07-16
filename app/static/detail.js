$("#reload").click(function() {
    $("#message").attr('src', '/static/source.gif');
    $("#decoded_message").attr('src', '/static/source.gif');
    $.ajax({
        type: 'POST',
        url: '/viewMessage',
        success: function(data) {
            $("#message").attr('src', 'data:image/jpg' + ';base64, ' +
                    data['message']);
            $("#decoded_message").attr('src', 'data:image/jpg' + ';base64, ' +
                    data['decoded_message']);
            $('#bit_error').text(data['bit_error']);
            $("#message_length").text(data['message_length']);
            $("#accr").text(data['accr']);
        },
        error: function() {
            alrt('Error');
        },
    });
});
