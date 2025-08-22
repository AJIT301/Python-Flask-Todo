document.addEventListener('DOMContentLoaded', () => {
    const debug_time = false; // toggle true/false

    const messages = document.querySelectorAll('.flash-message');

    messages.forEach(msg => {
        const startTime = performance.now();

        // find nearest wrapper container (login-container, dashboard-container, etc.)
        const wrapper = msg.closest('.container') || document.body;
        const wrapperRect = wrapper.getBoundingClientRect();


        // show message
        msg.classList.add('show');
        if (debug_time) console.log("showing flash msg", msg.textContent.trim(), "at", performance.now());

        // hide after 2.5s
        setTimeout(() => {
            msg.classList.remove('show');
            msg.classList.add('hide');
            if (debug_time) console.log("timeout set for message:", msg.textContent.trim());
        }, 2500);

        const onTransitionEnd = (e) => {
            if (e.propertyName === 'opacity' && msg.classList.contains('hide')) {
                const endTime = performance.now();
                const calculated_in_seconds = ((endTime - startTime) / 1000).toFixed(2);

                if (debug_time) {
                    console.log("transition finished for message:", msg.textContent.trim());
                    console.log(`messages appeared for ${calculated_in_seconds} sec`);
                }

                msg.remove();
                msg.removeEventListener('transitionend', onTransitionEnd);
            }
        };

        msg.addEventListener('transitionend', onTransitionEnd);
    });
});