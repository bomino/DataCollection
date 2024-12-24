// static/js/data_collection.js

class DataCollectionUI {
    constructor() {
        this.initializeTooltips();
        this.handleMobileTooltips();
        this.initializeEventListeners();
    }

    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        this.tooltipList = tooltipTriggerList.map(tooltipTriggerEl =>
            new bootstrap.Tooltip(tooltipTriggerEl, {
                trigger: 'hover focus'
            })
        );
    }

    handleMobileTooltips() {
        if (window.innerWidth < 768) {
            this.tooltipList?.forEach(tooltip => tooltip.disable());
        }
    }

    initializeEventListeners() {
        // Handle window resize for tooltips
        window.addEventListener('resize', () => {
            this.handleMobileTooltips();
        });

        // Handle card hover effects
        const featureCards = document.querySelectorAll('.feature-card');
        featureCards.forEach(card => {
            card.addEventListener('mouseenter', this.handleCardHover);
            card.addEventListener('mouseleave', this.handleCardHover);
        });
    }

    handleCardHover(event) {
        const icon = event.currentTarget.querySelector('.feature-icon i');
        if (icon) {
            icon.style.transform = event.type === 'mouseenter' ? 'scale(1.1)' : 'scale(1)';
        }
    }

    // Method to destroy tooltips (useful for cleanup)
    destroyTooltips() {
        this.tooltipList?.forEach(tooltip => tooltip.dispose());
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dataCollectionUI = new DataCollectionUI();
});

// Cleanup on page unload
window.addEventListener('unload', () => {
    if (window.dataCollectionUI) {
        window.dataCollectionUI.destroyTooltips();
    }
});