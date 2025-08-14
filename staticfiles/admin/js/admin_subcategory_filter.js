(function($) {
    $(document).ready(function() {
        // Получаем элементы выбора
        var $category = $('#id_category');
        var $subcategory = $('#id_subcategory');
        
        // Функция для обновления подкатегорий
        function updateSubcategories() {
            var categoryId = $category.val();
            if (categoryId) {
                // Загружаем подкатегории через AJAX
                $.ajax({
                    url: '/admin/get_subcategories/',
                    data: {
                        'category_id': categoryId
                    },
                    success: function(data) {
                        $subcategory.empty();
                        $.each(data, function(key, value) {
                            $subcategory.append($('<option></option>').attr('value', value.id).text(value.name));
                        });
                    }
                });
            } else {
                $subcategory.empty();
            }
        }
        
        // Обновляем при изменении категории
        $category.change(updateSubcategories);
        
        // Инициализация при загрузке
        updateSubcategories();
    });
})(django.jQuery);