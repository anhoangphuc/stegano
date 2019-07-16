$('#selectImage').change(function(e) {
    var fileName = this.files[0].name;
    $('.custom-file-label').html(fileName);
});

$('#uploadImage').submit(function(e) {
	$('#grayImage').attr('src', "/static/source.gif")
	e.preventDefault();
	var formData = new FormData($('#uploadImage')[0]);
	$.ajax({
		type: 'POST',
		url: '/hidepicture',
		data: formData,
		success: function(data) {
            alert(data['filename']);
			//$('#grayImage').attr('src', 'data:image/' + data['image_type']						+ ';base64, ' + data['b64_image']);
		},
		contentType: false,
		cache: false,
		processData: false,
		error: function() {
			alert('Error')
		} 
	});	 
});
