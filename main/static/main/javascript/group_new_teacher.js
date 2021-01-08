$(document).ready(function() {
    var load_group_names = function(){
        $.ajax({
            url: '/api/group_name/',
            method: 'GET',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                var group_name = data.group_name;
                var group_slug = data.group_slug;
                $('#id_username').val(group_slug);
                $('#id_group_public_name').val(group_name);
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error('Error recuperant nom de grup');
            }
        });
    };

    $(".js-upload-photos").click(function () {
        $("#fileupload").click();
    });

    $("#fileupload").fileupload({
        dataType: 'json',
        formData: [
            { name: "csrfmiddlewaretoken", value: "{{ csrf_token }}"}
        ],
        done: function (e, data) {  /* 3. PROCESS THE RESPONSE FROM THE SERVER */
          if (data.result.is_valid) {
            $("#gallery tbody").html(
            "<tr id='tr_" + data.result.id + "'>" +
                "<td>" +
                    "<a target='_blank' href='" + data.result.url +  "'>" +
                        "<img id="+ data.result.id +" style='height: 150px;' src='" + data.result.url + "'>" +
                    "</a>" +
                "</td>" +
                "<td>" +
                    "<a href='#' class='btn btn-danger btn-sm btn-del btn-del-img imatgeRodal deleteFoto' id="+ data.result.id +">Eliminar</a>" +
                "</td>" +
            "<tr>");
            //setJSONFotos(data.result.id);
            $('#id_photo_path').val(data.result.url);
          }else{
            alert(data.result.error_imagen);
          }
        }
    });

    $(document).on('click', '.deleteFoto', function() {
        if( confirm("Eliminar la foto?") ){
            $("#gallery tbody").html('');
        }
    });

    $(document).on('click', '.suggest-fields', function() {
        $('#id_password1').val(utils.generate_random_password_4());
        load_group_names();
    });

    $('#id_select_alum').select2({
      ajax: {
        url: '/alum/search/',
        dataType: 'json',
        delay: 250,
        processResults: function (data) {
            return {
                results: data
            };
        },
        data: function(term,page){
            return {
                q: term
            };
        }
      }
    });

    $('#group_form').submit(function() {
        $('#alum_ids').val('');
        var alum_ids = $("#id_select_alum").select2('data');
        var ids = [];
        for(var i = 0; i < alum_ids.length; i++){
            ids.push( alum_ids[i].id );
        }
        $('#alum_ids').val( ids.join(',') );
    });
});