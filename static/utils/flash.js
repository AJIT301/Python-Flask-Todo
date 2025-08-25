document.addEventListener('DOMContentLoaded', () => {
    const debug_time = false;
    const messages = document.querySelectorAll('.flash-message');

    // Create container if it doesn't exist
    let container = document.querySelector('.flash-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-container';
        document.body.appendChild(container);
    }

    // Position messages manually
    function positionMessages() {
    const visibleMessages = Array.from(container.querySelectorAll('.flash-message:not(.hide)'));
    let totalHeight = 0;
    
    visibleMessages.forEach((msg, index) => {
        // Get actual height of the message
        const height = msg.offsetHeight || 60; // fallback to 60px if not rendered
        const spacing = 10; // spacing between messages
        msg.style.top = `${totalHeight}px`;
        totalHeight += height + spacing;
    });
}

    messages.forEach((msg, index) => {
        // Move message to container
        container.appendChild(msg);

        // Add dynamic elements
        const blob1 = document.createElement('div');
        blob1.className = 'blob b1';
        const blob2 = document.createElement('div');
        blob2.className = 'blob b2';
        const blob3 = document.createElement('div');
        blob3.className = 'blob b3';
        const particle1 = document.createElement('div');
        particle1.className = 'particle p1';
        const particle2 = document.createElement('div');
        particle2.className = 'particle p2';
        const particle3 = document.createElement('div');
        particle3.className = 'particle p3';
        msg.appendChild(blob1);
        msg.appendChild(blob2);
        msg.appendChild(blob3);
        msg.appendChild(particle1);
        msg.appendChild(particle2);
        msg.appendChild(particle3);

        const startTime = debug_time ? performance.now() : null;

        setTimeout(() => {
            msg.classList.add('show');
            positionMessages(); // Position when showing
            if (debug_time) console.log("showing flash msg", msg.textContent.trim(), "at", performance.now());

            setTimeout(() => {
                msg.classList.remove('show');
                msg.classList.add('hide');
                if (debug_time) console.log("timeout set for message:", msg.textContent.trim());
                
                // Reposition remaining messages after this one starts hiding
                setTimeout(positionMessages, 50);
            }, 2500);

            const onTransitionEnd = (e) => {
                if (e.propertyName === 'opacity' && msg.classList.contains('hide')) {
                    if (debug_time) {
                        const endTime = performance.now();
                        const calculated_in_seconds = ((endTime - startTime) / 1000).toFixed(2);
                        console.log("transition finished for message:", msg.textContent.trim());
                        console.log(`messages appeared for ${calculated_in_seconds} sec`);
                    }

                    msg.remove();
                    msg.removeEventListener('transitionend', onTransitionEnd);
                    positionMessages(); // Reposition when removing
                }
            };

            msg.addEventListener('transitionend', onTransitionEnd);
        }, index * 500);
    });
});