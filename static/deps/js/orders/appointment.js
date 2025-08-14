$(document).ready(function() {
    // Добавьте отладку в JS
    $("#id_date").change(function() {
        console.log("Дате изменена, ID:", $(this).val());
        
        $.ajax({
            url: $("#id_date").data("url"),  // URL будем передавать через data-атрибут
            data: { 'date': $(this).val() },
            success: function(data) {
                console.log("Ответ сервера:", data);
                $("#id_time").html(data);
            },
            error: function(xhr) {
                console.error("Ошибка AJAX:", xhr.responseText);
            }
        });
    });
});