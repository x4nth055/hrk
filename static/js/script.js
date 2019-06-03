function addEditedSelectionEvent(changedElement, toChangeElement, url) {
    $(changedElement).on("click", function() {
        var fd = new FormData();
        fd.append("id", $(changedElement).val());
        $.ajax({
            type: "POST",
            url: url,
            cache: false,
            processData: false,
            contentType: false,
            data: fd
        }).done(function(data) {
            // clear previous options
            $(toChangeElement + " option").remove();
            data = JSON.parse(data);
            $.each(data, function(index, value) {
                var item = value;
                var id = item[0];
                var name = item[1];
                var option = new Option(name, id);
                $(option).html(name);
                $(toChangeElement).append(option);
            });
        });
    });
}