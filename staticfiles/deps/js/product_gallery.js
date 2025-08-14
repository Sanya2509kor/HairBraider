// product_gallery.js

class ProductGallery {
    constructor(productImages) {
        this.images = productImages;
        this.currentIndex = 0;
        this.mainImage = document.getElementById('mainImage');
        this.thumbnails = document.querySelectorAll('.thumbnail');
        this.swipeContainer = document.getElementById('swipeContainer') || this.mainImage;
        
        this.initEvents();
        this.updateGallery();
    }
    
    initEvents() {
        // Обработчики для миниатюр
        this.thumbnails.forEach((thumb, index) => {
            thumb.addEventListener('click', () => this.changeImage(index));
        });
        
        // Обработчики клавиатуры
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') this.nextImage();
            if (e.key === 'ArrowLeft') this.prevImage();
        });
        
        // Обработчики свайпа
        this.swipeContainer.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].screenX;
        }, {passive: true});
        
        this.swipeContainer.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe();
        }, {passive: true});
    }
    
    changeImage(index) {
        this.currentIndex = index;
        this.updateGallery();
    }
    
    nextImage() {
        this.currentIndex = (this.currentIndex + 1) % this.images.length;
        this.updateGallery();
    }
    
    prevImage() {
        this.currentIndex = (this.currentIndex - 1 + this.images.length) % this.images.length;
        this.updateGallery();
    }
    
    handleSwipe() {
        const swipeThreshold = 50;
        
        if (this.touchStartX - this.touchEndX > swipeThreshold) {
            this.nextImage();
        } else if (this.touchEndX - this.touchStartX > swipeThreshold) {
            this.prevImage();
        }
    }
    
    updateGallery() {
        this.mainImage.classList.add('flip');
        
        setTimeout(() => {
            this.mainImage.src = this.images[this.currentIndex];
            this.mainImage.classList.remove('flip');
            
            this.thumbnails.forEach((thumb, index) => {
                thumb.classList.toggle('active', index === this.currentIndex);
            });
        }, 500);
    }
}

// Когда DOM полностью загружен
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, есть ли галерея на странице
    if (document.getElementById('mainImage')) {
        // Получаем изображения из data-атрибута
        const galleryContainer = document.getElementById('gallery-container');
        const productImages = JSON.parse(galleryContainer.dataset.images);
        
        // Инициализируем галерею
        new ProductGallery(productImages);
    }
});