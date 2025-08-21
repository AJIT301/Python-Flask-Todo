
document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', e => {
        e.preventDefault();
        const url = e.target.href;
        fetch(url)
            .then(res => res.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                document.querySelector('.content').innerHTML = doc.querySelector('.content').innerHTML;
            });
    });
});
