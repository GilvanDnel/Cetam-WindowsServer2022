/* ========================================================
   CONTROLE DA APRESENTAÇÃO: NAVEGAÇÃO, ATALHOS E INTERATIVIDADE
   ======================================================== */
(function() {
    let currentSlide = 1;
    const slides = document.querySelectorAll('.slide');
    const totalSlides = slides.length || 5;
    const currentSlideNum = document.getElementById('currentSlideNum');
    const totalSlidesNum = document.getElementById('totalSlidesNum');
    const progressBarFill = document.getElementById('progressBarFill');

    if (totalSlidesNum) {
        totalSlidesNum.textContent = totalSlides;
    }

    function updateSlide() {
        slides.forEach((s, idx) => {
            const sIndex = idx + 1;
            if (sIndex === currentSlide) {
                s.classList.add('active');
            } else {
                s.classList.remove('active');
            }
        });

        if (currentSlideNum) {
            currentSlideNum.textContent = currentSlide;
        }

        if (progressBarFill) {
            const progressPct = (currentSlide / totalSlides) * 100;
            progressBarFill.style.width = `${progressPct}%`;
        }
    }

    function nextSlide() {
        if (currentSlide < totalSlides) {
            currentSlide++;
            updateSlide();
        }
    }

    function prevSlide() {
        if (currentSlide > 1) {
            currentSlide--;
            updateSlide();
        }
    }

    window.goToSlide = function(num) {
        if (num >= 1 && num <= totalSlides) {
            currentSlide = num;
            updateSlide();
        }
    };

    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => console.log(err));
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    }

    window.copyText = function(text, btnElement) {
        navigator.clipboard.writeText(text).then(() => {
            if (btnElement) {
                const originalText = btnElement.textContent;
                btnElement.textContent = '✓ Copiado';
                btnElement.style.background = '#00B354';
                setTimeout(() => {
                    btnElement.textContent = originalText;
                    btnElement.style.background = '';
                }, 1800);
            } else {
                alert(`Comando copiado:\n\n${text}`);
            }
        }).catch(() => {
            prompt("Copie o comando:", text);
        });
    };

    // Navegação via Teclado
    window.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
            nextSlide();
        } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
            prevSlide();
        } else if (e.key.toLowerCase() === 'f') {
            toggleFullscreen();
        } else if (e.key.toLowerCase() === 'h' || e.key === 'Home') {
            goToSlide(1);
        } else if (e.key >= '1' && e.key <= '6') {
            goToSlide(parseInt(e.key));
        }
    });

    // Navegação por Toque / Swipe (Mobile / Tablets)
    let touchStartX = 0;
    let touchEndX = 0;

    window.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    window.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, { passive: true });

    function handleSwipe() {
        const swipeThreshold = 50;
        if (touchEndX < touchStartX - swipeThreshold) {
            nextSlide(); // Deslizou para a esquerda -> próximo
        }
        if (touchEndX > touchStartX + swipeThreshold) {
            prevSlide(); // Deslizou para a direita -> anterior
        }
    }

    // Eventos dos Botões do Header
    const btnNext = document.getElementById('btnNext');
    const btnPrev = document.getElementById('btnPrev');
    const btnHome = document.getElementById('btnHome');
    const btnFullscreen = document.getElementById('btnFullscreen');

    if (btnNext) btnNext.addEventListener('click', nextSlide);
    if (btnPrev) btnPrev.addEventListener('click', prevSlide);
    if (btnHome) btnHome.addEventListener('click', () => goToSlide(1));
    if (btnFullscreen) btnFullscreen.addEventListener('click', toggleFullscreen);

    // Inicialização
    updateSlide();
})();
