(function () {
    function escapeHtml(str) {
        return String(str == null ? '' : str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    const $modal = document.getElementById('video-modal');
    const $frameWrap = document.getElementById('video-frame-wrap');

    function openVideoModal(videoId) {
        $frameWrap.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + encodeURIComponent(videoId)
            + '?autoplay=1" title="YouTube video player" frameborder="0"'
            + ' allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"'
            + ' allowfullscreen></iframe>';
        $modal.classList.remove('hidden');
    }
    function closeVideoModal() {
        $modal.classList.add('hidden');
        $frameWrap.innerHTML = '';
    }
    document.getElementById('video-modal-close').addEventListener('click', closeVideoModal);
    $modal.addEventListener('click', function (e) { if (e.target === $modal) closeVideoModal(); });

    fetch('./videos.json')
        .then(function (res) { return res.json(); })
        .then(renderVideos)
        .catch(function (err) {
            console.error('videos.json の読み込みに失敗しました', err);
            document.getElementById('video-list').innerHTML = '<p class="error">動画一覧の読み込みに失敗しました。</p>';
        });

    function renderVideos(videos) {
        const $list = document.getElementById('video-list');
        const byYear = {};
        videos.forEach(function (v) {
            const y = v.year || '不明';
            if (!byYear[y]) byYear[y] = [];
            byYear[y].push(v);
        });
        const years = Object.keys(byYear).sort(function (a, b) { return b - a; });

        let html = '';
        years.forEach(function (year) {
            html += '<section class="year-group">';
            html += '<h2 class="year-heading">' + escapeHtml(year) + (year !== '不明' ? '年度' : '') + '</h2>';
            html += '<div class="video-grid">';
            byYear[year].forEach(function (v) {
                html += '<button type="button" class="video-card" data-id="' + escapeHtml(v.id) + '">'
                    + '<span class="video-thumb-wrap">'
                    + '<img src="' + escapeHtml(v.thumbnail) + '" alt="' + escapeHtml(v.title) + '" loading="lazy">'
                    + '<span class="play-badge" aria-hidden="true">&#9658;</span>'
                    + '</span>'
                    + '<span class="video-title">' + escapeHtml(v.title) + '</span>'
                    + '</button>';
            });
            html += '</div></section>';
        });
        $list.innerHTML = html;

        $list.addEventListener('click', function (e) {
            const card = e.target.closest('.video-card');
            if (card) openVideoModal(card.getAttribute('data-id'));
        });
    }
})();
