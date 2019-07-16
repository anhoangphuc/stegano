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
		url: '/processImage',
		data: formData,
		success: function(data) {
			$('#grayImage').attr('src', 'data:image/' + data['image_type']						+ ';base64, ' + data['b64_image']);
		},
		contentType: false,
		cache: false,
		processData: false,
		error: function() {
			alert('Error')
		} 
	});	 
});

$('button.dropdown-item').click(function(e) {
	e.preventDefault();
	$('#encodedImage').attr('src', "/static/source.gif");
	var dataSent = {config_type: $(this).attr('value')}; 
	$.ajax({
		type: 'POST',
		url: '/encodeImage',
		data: JSON.stringify(dataSent),	
		contentType: 'application/json',
		success: function(data) {
			$('#encodedImage').attr('src', 'data:image/' + data['image_type'] + ';base64, ' + data['b64_image']);
		},
		error: function() {
			alert('Error');
		},
	});
});
