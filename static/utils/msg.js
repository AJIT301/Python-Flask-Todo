document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('.flash-message').forEach(msg => {
        const createElement = (cls, sizeRange, positionRange, animDelayRange) => {
            const el = document.createElement('span');
            el.className = cls;

            if(cls.startsWith('blob')) {
                const size = Math.floor(Math.random() * (sizeRange[1]-sizeRange[0])) + sizeRange[0];
                el.style.width = el.style.height = size + 'px';
                el.style.top = (Math.random()*positionRange[0]) + '%';
                el.style.left = (Math.random()*positionRange[1]) + '%';
                el.style.animationDelay = (Math.random()*animDelayRange) + 's';
            }

            if(cls.startsWith('particle')) {
                el.style.top = (Math.random()*positionRange[0]) + '%';
                el.style.left = (Math.random()*positionRange[1]) + '%';
                el.style.animationDelay = (Math.random()*animDelayRange) + 's';
            }

            return el;
        };

        for(let i=0; i<3; i++){
            msg.appendChild(createElement('blob b'+(i+1), [30,60], [80,80], 5));
            msg.appendChild(createElement('particle p'+(i+1), null, [100,100], 3));
        }

        setTimeout(() => {
            msg.classList.remove('show');
            msg.classList.add('hide');
        }, 4000);
    });
});