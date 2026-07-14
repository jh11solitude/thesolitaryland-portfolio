/* ═══════════════════════════════════════════════════════════════
   JEROME KOH PORTFOLIO — MAIN JS
   ─────────────────────────────────────────────────────────────── */

'use strict';

/* ── Nav: become opaque on scroll ───────────────────────────── */
(function () {
  const nav = document.getElementById('jk-nav');
  if (!nav) return;

  const onScroll = () => {
    nav.classList.toggle('jk-nav--scrolled', window.scrollY > 40);
  };

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll(); // run once on load
}());


/* ── Mobile nav toggle ──────────────────────────────────────── */
(function () {
  const toggle = document.getElementById('nav-toggle');
  const links  = document.getElementById('nav-links');
  if (!toggle || !links) return;

  toggle.addEventListener('click', () => {
    const isOpen = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', isOpen);

    // Animate hamburger → ✕
    const spans = toggle.querySelectorAll('span');
    if (isOpen) {
      spans[0].style.transform = 'translateY(7px) rotate(45deg)';
      spans[1].style.transform = 'translateY(-7px) rotate(-45deg)';
    } else {
      spans[0].style.transform = '';
      spans[1].style.transform = '';
    }
  });

  // Close menu when a link is clicked (SPA-style navigation)
  links.querySelectorAll('.jk-nav__link').forEach(link => {
    link.addEventListener('click', () => {
      links.classList.remove('open');
      toggle.setAttribute('aria-expanded', false);
    });
  });
}());


/* ── Scroll reveal ──────────────────────────────────────────── */
(function () {
  const els = document.querySelectorAll('.reveal');
  if (!els.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        // Stagger reveals: each element waits a little longer
        setTimeout(() => {
          entry.target.classList.add('revealed');
        }, i * 80);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  els.forEach(el => observer.observe(el));
}());


/* ── Auto-dismiss flash messages after 5s ───────────────────── */
(function () {
  document.querySelectorAll('.jk-message').forEach(msg => {
    setTimeout(() => {
      msg.style.transition = 'opacity 0.4s';
      msg.style.opacity = '0';
      setTimeout(() => msg.remove(), 400);
    }, 5000);
  });
}());


/* ── Video card: hover-preview for self-hosted MP4 ─────────── */
(function () {
  document.querySelectorAll('.jk-video-card[data-preview]').forEach(card => {
    const previewSrc = card.dataset.preview;
    let video = null;
    const thumb = card.querySelector('.jk-video-card__thumb');

    card.addEventListener('mouseenter', () => {
      if (!video) {
        video = document.createElement('video');
        video.src = previewSrc;
        video.muted = true;
        video.loop = true;
        video.playsInline = true;
        video.className = 'jk-video-card__thumb';
        video.style.position = 'absolute';
        video.style.inset = '0';
        video.style.objectFit = 'cover';
        video.style.width = '100%';
        video.style.height = '100%';
        card.insertBefore(video, thumb);
      }
      video.play().catch(() => {});
    });

    card.addEventListener('mouseleave', () => {
      if (video) {
        video.pause();
        video.currentTime = 0;
      }
    });
  });
}());


// ==========================================================================
// LIGHTBOX ENGINE INTERACTION FUNCTIONALITY
// ==========================================================================

document.addEventListener("DOMContentLoaded", function() {
  const lightbox = document.getElementById("jkLightbox");
  const lightboxImg = document.getElementById("jkLightboxImg");
  const lightboxCaption = document.getElementById("jkLightboxCaption");
  const closeBtn = document.querySelector(".jk-lightbox__close");
  const prevBtn = document.getElementById("jkPrevBtn");
  const nextBtn = document.getElementById("jkNextBtn");

  // Creates active array tracking index reference maps
  const triggers = Array.from(document.querySelectorAll(".js-lightbox-trigger"));
  let currentIndex = -1;

  // Active parameter updates handler function
  function showImage(index) {
    if (index < 0 || index >= triggers.length) return;
    
    currentIndex = index;
    const targetTrigger = triggers[currentIndex];
    const img = targetTrigger.querySelector("img");
    const captionText = targetTrigger.getAttribute("data-caption");
    
    if (img) {
      lightboxImg.src = img.src;
      lightboxImg.alt = img.alt;
      lightboxCaption.textContent = captionText || "";
    }
  }

  // Intercept trigger selection mechanisms
  triggers.forEach((trigger, index) => {
    trigger.addEventListener("click", function(event) {
      event.preventDefault();
      showImage(index);
      lightbox.style.display = "flex";
      document.body.style.overflow = "hidden";
    });
  });

  // Backward navigation tracking logic 
  function navigatePrev() {
    let targetIndex = currentIndex - 1;
    if (targetIndex < 0) {
      targetIndex = triggers.length - 1;
    }
    showImage(targetIndex);
  }

  // Forward navigation tracking logic
  function navigateNext() {
    let targetIndex = currentIndex + 1;
    if (targetIndex >= triggers.length) {
      targetIndex = 0;
    }
    showImage(targetIndex);
  }

  // Event mappings 
  prevBtn.addEventListener("click", function(e) {
    e.stopPropagation();
    navigatePrev();
  });

  nextBtn.addEventListener("click", function(e) {
    e.stopPropagation();
    navigateNext();
  });

  closeBtn.addEventListener("click", closeLightbox);

  // Close lightboxes dynamically on background container selection
  lightbox.addEventListener("click", function(event) {
    if (event.target === lightbox || event.target.id === "jkLightboxCaption") {
      if (event.offsetX < lightbox.clientWidth / 2) {
        prevBtn.click(); // Clicked left side
      } else {
        nextBtn.click(); // Clicked right side
      }
    }
  });

  // Hardware hotkey binding mappings
  document.addEventListener("keydown", function(event) {
    if (lightbox.style.display === "flex") {
      if (event.key === "Escape") {
        closeLightbox();
      } else if (event.key === "ArrowLeft") {
        navigatePrev();
      } else if (event.key === "ArrowRight") {
        navigateNext();
      }
    }
  });

  function closeLightbox() {
    lightbox.style.display = "none";
    document.body.style.overflow = "auto";
  }
});