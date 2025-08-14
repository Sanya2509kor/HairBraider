function initializeCarousels() {
    const carousels = document.querySelectorAll('.carousel');
    
    carousels.forEach(carousel => {
        const imagesContainer = carousel.querySelector('.images');
        const images = carousel.querySelectorAll('.images img');
        let currentIndex = 0;
        let startX = 0;
        let isDragging = false;
        let animationFrameId = null;
        let startTime = null;
        const animationDuration = 200;
        
        const desktopCounter = carousel.querySelector('.current-image');
        const mobileCounter = carousel.querySelector('.mobile-counter');
        
        function animateTransition(targetIndex) {
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
            }
            
            const startIndex = currentIndex;
            const startOffset = -startIndex * 100;
            const targetOffset = -targetIndex * 100;
            startTime = performance.now();
            
            function step(timestamp) {
                if (!startTime) startTime = timestamp;
                const elapsed = timestamp - startTime;
                const progress = Math.min(elapsed / animationDuration, 1);
                
                const easeProgress = 1 - Math.pow(1 - progress, 3);
                const currentOffset = startOffset + (targetOffset - startOffset) * easeProgress;
                
                imagesContainer.style.transform = `translateX(${currentOffset}%)`;
                
                if (progress < 1) {
                    animationFrameId = requestAnimationFrame(step);
                } else {
                    animationFrameId = null;
                    currentIndex = targetIndex;
                    updateCounter();
                }
            }
            
            animationFrameId = requestAnimationFrame(step);
        }
        
        function updateCounter() {
            const counterText = (currentIndex + 1) + ' / ' + images.length;
            if (desktopCounter) desktopCounter.textContent = counterText;
            if (mobileCounter) mobileCounter.textContent = counterText;
        }
        
        const prevButton = carousel.querySelector('.prev');
        const nextButton = carousel.querySelector('.next');
        
        prevButton?.addEventListener('click', function() {
            if (animationFrameId) return;
            const newIndex = (currentIndex - 1 + images.length) % images.length;
            animateTransition(newIndex);
        });
        
        nextButton?.addEventListener('click', function() {
            if (animationFrameId) return;
            const newIndex = (currentIndex + 1) % images.length;
            animateTransition(newIndex);
        });
        
        carousel.addEventListener('touchstart', handleTouchStart, {passive: true});
        carousel.addEventListener('touchmove', handleTouchMove, {passive: false});
        carousel.addEventListener('touchend', handleTouchEnd);
        
        function handleTouchStart(e) {
            if (animationFrameId) return;
            startX = e.touches[0].clientX;
            isDragging = true;
            imagesContainer.style.transition = 'none';
        }
        
        function handleTouchMove(e) {
            if (!isDragging) return;
            e.preventDefault();
            
            const x = e.touches[0].clientX;
            const diff = x - startX;
            
            const offset = -currentIndex * 100 + (diff / carousel.offsetWidth) * 100;
            imagesContainer.style.transform = `translateX(${offset}%)`;
        }
        
        function handleTouchEnd(e) {
            if (!isDragging) return;
            isDragging = false;
            
            imagesContainer.style.transition = 'transform 0.5s ease';
            
            const endX = e.changedTouches[0].clientX;
            const diff = endX - startX;
            const threshold = carousel.offsetWidth * 0.2;
            
            let newIndex = currentIndex;
            if (diff > threshold && currentIndex > 0) {
                newIndex = currentIndex - 1;
            } else if (diff < -threshold && currentIndex < images.length - 1) {
                newIndex = currentIndex + 1;
            }
            
            animateTransition(newIndex);
        }
        
        updateCounter();
    });
}


function initializeModal() {
    document.querySelectorAll('.clickable-image').forEach(img => {
        img.addEventListener('click', function() {
            document.getElementById('modalImage').src = this.dataset.fullsize;
            document.getElementById('modalImage').alt = this.alt;
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initializeCarousels();
    initializeModal();
});