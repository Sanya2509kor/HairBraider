// Когда html документ готов (прорисован)
$(document).ready(function () {
    // Берем из разметки элемент по id - оповещения от django
    var notification = $('#notification');
    // И через 7 сек. убираем
    if (notification.length > 0) {
        setTimeout(function () {
            notification.alert('close');
        }, 5000);
    }

    // // Анимация при скролле
    window.addEventListener('scroll', function() {
        const scrollPosition = window.scrollY;
        const navbar = document.querySelector('.navbar');
    
        if (scrollPosition > 100) {
            navbar.classList.add('shadow-sm');
            navbar.classList.add('bg-white');
        } else {
            navbar.classList.remove('shadow-sm');
            navbar.classList.remove('bg-white');
        }
    });

    // Плавная прокрутка для якорных ссылок
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });


    if (typeof ProductGallery !== 'undefined' && document.getElementById('mainImage')) {
        const galleryContainer = document.getElementById('gallery-container');
        const images = [
            galleryContainer.dataset.main,
            ...JSON.parse(galleryContainer.dataset.additional)
        ];
        new ProductGallery(images);
    }



    

    // перелистывание изображений в index
    document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('.images img');
    let currentIndex = 0;
    
    function updateImage() {
        images.forEach((img, index) => {
            img.style.display = index === currentIndex ? 'block' : 'none';
        });
        
        const currentImageSpan = document.querySelector('.current-image');
        currentImageSpan.textContent = (currentIndex + 1) + ' / ' + images.length;
    }
    
    const prevButton = document.querySelector('.prev');
    const nextButton = document.querySelector('.next');
    
    prevButton.addEventListener('click', function() {
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        updateImage();
    });
    
    nextButton.addEventListener('click', function() {
        currentIndex = (currentIndex + 1) % images.length;
        updateImage();
    });
    
    updateImage();
});


});